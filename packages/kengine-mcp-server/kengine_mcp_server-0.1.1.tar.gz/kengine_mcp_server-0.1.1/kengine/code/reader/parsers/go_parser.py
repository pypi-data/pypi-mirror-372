"""
Go方法解析器
专门处理Go代码的方法提取
"""

import logging
from typing import List, Tuple
from .base_parser import BaseMethodParser, MethodInfo
from ...language_loader import get_language_for_extension

logger = logging.getLogger(__name__)


class GoMethodParser(BaseMethodParser):
    """Go方法解析器"""
    
    def __init__(self):
        super().__init__()
        # 获取Go语言库
        self.lang_lib, _ = get_language_for_extension('.go')
        if not self.lang_lib:
            logger.error("无法加载Go语言库")
    
    def find_all_methods(self, tree, code_content: str) -> List[MethodInfo]:
        """查找所有Go函数和方法"""
        methods = []
        lines = code_content.split('\n')
        
        try:
            # 查找函数声明
            function_query = "(function_declaration) @function"
            captures = self.execute_query(function_query, tree.root_node)
            
            if 'function' in captures:
                for func_node in captures['function']:
                    method_info = self._parse_function_node(func_node, lines, code_content)
                    if method_info:
                        methods.append(method_info)
            
            # 查找方法声明
            method_query = "(method_declaration) @method"
            captures = self.execute_query(method_query, tree.root_node)
            
            if 'method' in captures:
                for method_node in captures['method']:
                    method_info = self._parse_method_node(method_node, lines, code_content)
                    if method_info:
                        methods.append(method_info)
            
            return methods
            
        except Exception as e:
            logger.error(f"查找Go方法时发生错误: {e}")
            return []
    
    def _parse_function_node(self, func_node, lines: List[str], code_content: str) -> MethodInfo:
        """解析函数节点"""
        try:
            method_name, param_types, return_type = self.extract_method_signature(func_node, lines)
            method_code = self.extract_method_code(func_node, code_content)
            start_line, end_line = self.get_line_range(func_node)
            
            return MethodInfo(
                name=method_name,
                parameters=param_types,
                return_type=return_type,
                start_line=start_line,
                end_line=end_line,
                code=method_code
            )
        except Exception as e:
            logger.error(f"解析Go函数节点时发生错误: {e}")
            return None
    
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
            logger.error(f"解析Go方法节点时发生错误: {e}")
            return None
    
    def extract_method_signature(self, node, lines: List[str]) -> Tuple[str, List[str], str]:
        """提取Go方法签名信息"""
        try:
            method_name = "unknown"
            param_types = []
            return_type = ""
            
            # 提取方法名
            for child in node.children:
                if child.type == 'identifier':
                    method_name = child.text.decode('utf-8')
                    break
            
            # 提取参数和返回类型
            param_types = self._extract_parameters(node, lines)
            return_type = self._extract_return_type(node, lines)
            
            return method_name, param_types, return_type
            
        except Exception as e:
            logger.error(f"提取Go方法签名时发生错误: {e}")
            return "unknown", [], ""
    
    def _extract_parameters(self, node, lines: List[str]) -> List[str]:
        """提取参数类型列表"""
        param_types = []
        
        try:
            for child in node.children:
                if child.type == 'parameter_list':
                    param_types = self._parse_parameter_list(child)
                    break
            return param_types
        except Exception as e:
            logger.error(f"提取Go参数时发生错误: {e}")
            return []
    
    def _parse_parameter_list(self, params_node) -> List[str]:
        """解析参数列表"""
        param_types = []
        
        try:
            for child in params_node.children:
                if child.type == 'parameter_declaration':
                    param_type = self._extract_parameter_type(child)
                    if param_type:
                        param_types.append(param_type)
            return param_types
        except Exception as e:
            logger.error(f"解析Go参数列表时发生错误: {e}")
            return []
    
    def _extract_parameter_type(self, param_node) -> str:
        """提取参数类型"""
        try:
            for child in param_node.children:
                if child.type in ['type_identifier', 'pointer_type', 'slice_type', 'array_type']:
                    return child.text.decode('utf-8')
            return "interface{}"
        except Exception:
            return "interface{}"
    
    def _extract_return_type(self, node, lines: List[str]) -> str:
        """提取返回类型"""
        try:
            for child in node.children:
                if child.type in ['type_identifier', 'pointer_type', 'slice_type', 'array_type']:
                    # 简单的返回类型检测
                    return child.text.decode('utf-8')
            return ""
        except Exception:
            return ""
    
    def extract_dependencies(self, tree, code_content: str) -> List['DependencyInfo']:
        """
        提取Go文件中的依赖关系
        
        Returns:
            List[DependencyInfo]: 依赖信息列表
        """
        from ..dependency_extractor import DependencyInfo
        
        dependencies = []
        
        try:
            # 查找import声明
            import_query = "(import_declaration) @import"
            captures = self.execute_query(import_query, tree.root_node)
            
            if 'import' in captures:
                for import_node in captures['import']:
                    deps = self._parse_import_declaration(import_node, code_content)
                    dependencies.extend(deps)
            
            return dependencies
            
        except Exception as e:
            logger.error(f"提取Go依赖时发生错误: {e}")
            return []
    
    def _parse_import_declaration(self, import_node, code_content: str) -> List['DependencyInfo']:
        """解析Go import声明"""
        from ..dependency_extractor import DependencyInfo
        
        dependencies = []
        
        try:
            # 获取import声明的文本
            import_text = self.get_node_text(import_node, code_content)
            
            # 处理单个import：import "package"
            # 处理多个import：import ( "package1" "package2" )
            lines = import_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('"') and line.endswith('"'):
                    # 直接的包导入
                    package_name = line.strip('"')
                    if package_name:
                        dependencies.append(DependencyInfo(
                            import_name=package_name,
                            import_type='import'
                        ))
                elif '"' in line:
                    # 可能包含别名的导入：alias "package"
                    parts = line.split('"')
                    if len(parts) >= 2:
                        package_name = parts[1]
                        if package_name:
                            dependencies.append(DependencyInfo(
                                import_name=package_name,
                                import_type='import'
                            ))
            
            return dependencies
            
        except Exception as e:
            logger.error(f"解析Go import声明时发生错误: {e}")
            return []
        except Exception:
            return ""