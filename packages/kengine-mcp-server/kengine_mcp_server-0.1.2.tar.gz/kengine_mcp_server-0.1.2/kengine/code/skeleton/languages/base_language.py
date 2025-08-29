"""
语言处理器基础抽象类
定义所有语言处理器必须实现的接口
重构版本：添加字段提取功能支持
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

try:
    from tree_sitter import Query, QueryCursor
except ImportError:
    Query = None
    QueryCursor = None


class BaseLanguageHandler(ABC):
    """语言处理器抽象基类"""
    
    def __init__(self, lang_lib):
        self.lang_lib = lang_lib
    
    @abstractmethod
    def generate_skeleton(self, tree, code_content: str) -> str:
        """生成代码骨架"""
        pass
    
    @abstractmethod
    def extract_class_name(self, node, lines: List[str]) -> str:
        """提取类名 - 每种语言有不同的AST结构"""
        pass
    
    @abstractmethod
    def extract_function_signature(self, node, lines: List[str]) -> str:
        """提取函数签名 - 每种语言有不同的语法"""
        pass
    
    @abstractmethod
    def extract_method_signature(self, node, lines: List[str]) -> str:
        """提取方法签名 - 每种语言有不同的语法"""
        pass
    
    @abstractmethod
    def extract_field_info(self, node, lines: List[str]) -> Dict[str, Any]:
        """
        提取字段信息 - 每种语言有不同的字段声明语法
        
        Args:
            node: AST节点
            lines: 源代码行列表
            
        Returns:
            字段信息字典，包含以下标准字段：
            {
                'name': str,           # 字段名
                'type': str,           # 字段类型
                'modifiers': List[str], # 访问修饰符
                'is_static': bool,     # 是否静态
                'comment': str,        # 字段注释
                'declaration': str     # 完整声明
            }
        """
        pass
    
    def extract_docstring(self, node, lines: List[str]) -> str:
        """提取文档字符串 - 可以有默认实现"""
        return ""
    
    def is_method_in_class(self, func_node, class_nodes: List) -> bool:
        """检查函数是否是类中的方法 - 通用实现"""
        try:
            func_start = func_node.start_point
            func_end = func_node.end_point
            
            for class_node in class_nodes:
                class_start = class_node.start_point
                class_end = class_node.end_point
                
                # 检查函数是否在类的范围内
                if (class_start[0] <= func_start[0] <= class_end[0] and
                    class_start[0] <= func_end[0] <= class_end[0]):
                    return True
            return False
        except:
            return False
    
    def execute_query(self, query_string: str, node) -> Dict[str, List]:
        """执行tree-sitter查询并返回结果"""
        if not all([Query, QueryCursor]):
            logger.error("tree-sitter库未正确安装")
            return {}
            
        try:
            query = Query(self.lang_lib, query_string)
            cursor = QueryCursor(query)
            captures = cursor.captures(node)
            return captures
        except Exception as e:
            logger.error(f"执行查询失败: {query_string}, 错误: {e}")
            return {}
    
    def _extract_fields(self, class_node, lines: List[str], skeleton_lines: List[str]):
        """
        通用字段提取方法 - 子类可以重写以实现特定语言的字段提取逻辑
        
        Args:
            class_node: 类AST节点
            lines: 源代码行列表
            skeleton_lines: 骨架代码行列表（用于输出）
        """
        # 默认实现 - 子类应该重写此方法
        pass
    
    def create_field_info_template(self) -> Dict[str, Any]:
        """
        创建字段信息模板
        
        Returns:
            标准字段信息字典模板
        """
        return {
            'name': 'unknown',
            'type': 'unknown',
            'modifiers': [],
            'is_static': False,
            'comment': '',
            'declaration': ''
        }