"""
C#方法解析器
专门处理C#代码的方法提取
"""

import logging
from typing import List, Tuple
from .base_parser import BaseMethodParser, MethodInfo
from ...language_loader import get_language_for_extension

logger = logging.getLogger(__name__)


class CSharpMethodParser(BaseMethodParser):
    """C#方法解析器"""
    
    def __init__(self):
        super().__init__()
        self.lang_lib, _ = get_language_for_extension('.cs')
        if not self.lang_lib:
            logger.error("无法加载C#语言库")
    
    def find_all_methods(self, tree, code_content: str) -> List[MethodInfo]:
        """查找所有C#方法"""
        methods = []
        lines = code_content.split('\n')
        
        try:
            method_query = "(method_declaration) @method"
            captures = self.execute_query(method_query, tree.root_node)
            
            if 'method' in captures:
                for method_node in captures['method']:
                    method_info = self._parse_method_node(method_node, lines, code_content)
                    if method_info:
                        methods.append(method_info)
            
            return methods
        except Exception as e:
            logger.error(f"查找C#方法时发生错误: {e}")
            return []
    
    def _parse_method_node(self, method_node, lines: List[str], code_content: str) -> MethodInfo:
        """解析方法节点"""
        try:
            method_name, param_types, return_type = self.extract_method_signature(method_node, lines)
            method_code = self.extract_method_code(method_node, code_content)
            start_line, end_line = self.get_line_range(method_node)
            
            return MethodInfo(
                name=method_name,
                parameters=param_types,
                return_type=return_type,
                start_line=start_line,
                end_line=end_line,
                code=method_code
            )
        except Exception as e:
            logger.error(f"解析C#方法节点时发生错误: {e}")
            return None
    
    def extract_method_signature(self, node, lines: List[str]) -> Tuple[str, List[str], str]:
        """提取C#方法签名信息"""
        try:
            method_name = "unknown"
            param_types = []
            return_type = "void"
            
            # 提取方法名和类型信息
            for child in node.children:
                if child.type == 'identifier':
                    method_name = child.text.decode('utf-8')
                elif child.type == 'parameter_list':
                    param_types = self._extract_parameters_from_list(child)
                elif child.type in ['predefined_type', 'identifier']:
                    return_type = child.text.decode('utf-8')
            
            return method_name, param_types, return_type
        except Exception as e:
            logger.error(f"提取C#方法签名时发生错误: {e}")
            return "unknown", [], "void"
    
    def _extract_parameters_from_list(self, params_node) -> List[str]:
        """从参数列表提取参数类型"""
        param_types = []
        try:
            for child in params_node.children:
                if child.type == 'parameter':
                    param_type = self._extract_parameter_type(child)
                    if param_type:
                        param_types.append(param_type)
            return param_types
        except Exception:
            return []
    
    def _extract_parameter_type(self, param_node) -> str:
        """提取参数类型"""
        try:
            for child in param_node.children:
                if child.type in ['predefined_type', 'identifier']:
                    return child.text.decode('utf-8')
            return "object"
        except Exception:
            return "object"
    
    def extract_dependencies(self, tree, code_content: str) -> List['DependencyInfo']:
        """
        提取C#文件中的依赖关系
        
        Returns:
            List[DependencyInfo]: 依赖信息列表
        """
        from ..dependency_extractor import DependencyInfo
        
        dependencies = []
        
        try:
            # 查找using语句
            using_query = "(using_directive) @using"
            captures = self.execute_query(using_query, tree.root_node)
            
            if 'using' in captures:
                for using_node in captures['using']:
                    dep = self._parse_using_directive(using_node, code_content)
                    if dep:
                        dependencies.append(dep)
            
            return dependencies
            
        except Exception as e:
            logger.error(f"提取C#依赖时发生错误: {e}")
            return []
    
    def _parse_using_directive(self, using_node, code_content: str) -> 'DependencyInfo':
        """解析C# using指令"""
        from ..dependency_extractor import DependencyInfo
        
        try:
            # 获取using语句的文本
            using_text = self.get_node_text(using_node, code_content)
            
            # 解析using语句：using System.Collections;
            using_text = using_text.strip()
            
            # 移除using关键字和分号
            using_text = using_text.replace('using ', '').replace(';', '').strip()
            
            # 提取命名空间
            if using_text:
                return DependencyInfo(
                    import_name=using_text,
                    import_type='using'
                )
            
            return None
            
        except Exception as e:
            logger.error(f"解析C# using指令时发生错误: {e}")
            return None