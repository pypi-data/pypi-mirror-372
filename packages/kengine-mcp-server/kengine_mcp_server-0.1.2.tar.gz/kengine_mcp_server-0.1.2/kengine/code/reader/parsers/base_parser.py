"""
方法解析器基础抽象类
定义所有语言方法解析器必须实现的接口
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

try:
    from tree_sitter import Query, QueryCursor
except ImportError:
    Query = None
    QueryCursor = None


class MethodInfo:
    """方法信息类"""
    
    def __init__(self, name: str, parameters: List[str], return_type: str = "", 
                 start_line: int = 0, end_line: int = 0, code: str = ""):
        self.name = name
        self.parameters = parameters  # 参数类型列表
        self.return_type = return_type
        self.start_line = start_line
        self.end_line = end_line
        self.code = code
    
    def matches_signature(self, method_name: str, arg_types: List[str]) -> bool:
        """检查方法签名是否匹配"""
        if self.name != method_name:
            return False
        
        # 如果没有指定参数类型，只匹配方法名
        if not arg_types:
            return True
        
        # 精确匹配参数类型
        return self.parameters == arg_types
    
    def __str__(self):
        return f"{self.name}({', '.join(self.parameters)}) -> {self.return_type}"


class BaseMethodParser(ABC):
    """方法解析器抽象基类"""
    
    def __init__(self):
        self.lang_lib = None
    
    def extract_method(self, tree, code_content: str, method_name: str, arg_types: List[str]) -> str:
        """
        提取指定方法的代码
        
        Args:
            tree: tree-sitter解析树
            code_content: 源代码内容
            method_name: 方法名
            arg_types: 参数类型列表
            
        Returns:
            str: 方法的完整代码，如果未找到则返回空字符串
        """
        try:
            # 获取所有方法信息
            logger.info(f"开始查找所有方法，方法名: {method_name}")
            methods = self.find_all_methods(tree, code_content)
            logger.info(f"找到 {len(methods)} 个方法")
            for method in methods:
                logger.info(f"方法: {method.name}, 参数: {method.parameters}")
            
            # 查找匹配的方法
            target_method = self._find_matching_method(methods, method_name, arg_types)
            
            if target_method:
                return target_method.code
            else:
                logger.warning(f"未找到匹配的方法: {method_name}")
                return ""
                
        except Exception as e:
            logger.error(f"提取方法时发生错误: {e}")
            return ""
    
    def _find_matching_method(self, methods: List[MethodInfo], method_name: str, arg_types: List[str]) -> Optional[MethodInfo]:
        """
        查找匹配的方法
        
        Args:
            methods: 方法信息列表
            method_name: 要查找的方法名
            arg_types: 参数类型列表
            
        Returns:
            Optional[MethodInfo]: 匹配的方法信息，如果未找到则返回None
        """
        logger.debug(f"查找方法: {method_name}, 参数类型: {arg_types}")
        
        # 直接遍历查找第一个匹配的方法
        # matches_signature 方法已经处理了所有匹配逻辑（包括无参数和精确匹配）
        for method in methods:
            if method.matches_signature(method_name, arg_types):
                logger.debug(f"找到匹配方法: {method.name}({', '.join(method.parameters)})")
                return method
        
        logger.debug(f"未找到匹配的方法: {method_name}")
        return None
    
    @abstractmethod
    def find_all_methods(self, tree, code_content: str) -> List[MethodInfo]:
        """
        查找所有方法
        
        Args:
            tree: tree-sitter解析树
            code_content: 源代码内容
            
        Returns:
            List[MethodInfo]: 方法信息列表
        """
        pass
    
    @abstractmethod
    def extract_method_signature(self, node, lines: List[str]) -> Tuple[str, List[str], str]:
        """
        提取方法签名信息
        
        Args:
            node: AST节点
            lines: 源代码行列表
            
        Returns:
            Tuple[str, List[str], str]: (方法名, 参数类型列表, 返回类型)
        """
        pass
    
    def extract_method_code(self, node, code_content: str) -> str:
        """
        提取方法的完整代码（优化版本：基于Tree-sitter字节边界准确性）
        
        Args:
            node: AST节点
            code_content: 源代码内容
            
        Returns:
            str: 方法的完整代码
        """
        try:
            # 直接使用Tree-sitter字节边界提取（已验证准确性）
            code_bytes = code_content.encode('utf-8')
            start_byte = node.start_byte
            end_byte = node.end_byte
            
            # 边界检查
            if end_byte > len(code_bytes):
                logger.error(f"字节范围超出文件边界: end_byte={end_byte}, file_size={len(code_bytes)}")
                return ""
            
            # 提取代码
            method_code_bytes = code_bytes[start_byte:end_byte]
            method_code = method_code_bytes.decode('utf-8')
            
            # 确保以换行符结尾
            if method_code and not method_code.endswith('\n'):
                method_code += '\n'
                
            return method_code
            
        except UnicodeDecodeError as e:
            logger.error(f"字节范围解码失败: {e}")
            return ""
        except Exception as e:
            logger.error(f"提取方法代码时发生错误: {e}")
            return ""
    
    
    
    def execute_query(self, query_string: str, node) -> Dict[str, List]:
        """执行tree-sitter查询并返回结果"""
        logger.debug(f"执行查询: {query_string}")
        logger.debug(f"节点类型: {node.type}")
        
        if not all([Query, QueryCursor]):
            logger.error("tree-sitter库未正确安装")
            return {}
            
        try:
            # 解析查询字符串，提取节点类型和捕获名称
            # 支持格式：(node_type) @capture_name
            import re
            pattern = r'\(([^)]+)\)\s*@(\w+)'
            match = re.search(pattern, query_string)
            
            if not match:
                logger.error(f"无法解析查询字符串: {query_string}")
                return {}
            
            target_node_type = match.group(1)
            capture_name = match.group(2)
            
            logger.debug(f"查找节点类型: {target_node_type}, 捕获名称: {capture_name}")
            
            # 遍历节点查找匹配的类型
            captures = []
            
            def traverse_node(current_node):
                # 检查当前节点是否匹配目标类型
                if current_node.type == target_node_type:
                    captures.append((current_node, capture_name))
                    logger.debug(f"找到匹配节点: {current_node.type} at {current_node.start_point}")
                
                # 递归遍历子节点
                for child in current_node.children:
                    traverse_node(child)
            
            traverse_node(node)
            logger.info(f"找到 {len(captures)} 个匹配节点")
            
            # 组织查询结果
            result = {}
            for capture in captures:
                node_obj, cap_name = capture
                if cap_name not in result:
                    result[cap_name] = []
                result[cap_name].append(node_obj)
            
            return result
            
        except Exception as e:
            logger.error(f"执行查询失败: {query_string}, 错误: {e}")
            return {}
    
    def get_node_text(self, node, code_content: str) -> str:
        """获取节点的文本内容"""
        try:
            return code_content[node.start_byte:node.end_byte]
        except Exception:
            return ""
    
    def get_line_range(self, node) -> Tuple[int, int]:
        """获取节点的行范围"""
        try:
            start_line = node.start_point[0]
            end_line = node.end_point[0]
            return start_line, end_line
        except Exception:
            return 0, 0
    
    @abstractmethod
    def extract_dependencies(self, tree, code_content: str) -> List['DependencyInfo']:
        """
        提取代码文件中的依赖关系
        
        Args:
            tree: tree-sitter解析树
            code_content: 源代码内容
            
        Returns:
            List[DependencyInfo]: 依赖信息列表
        """
        pass