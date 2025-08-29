"""
Java方法解析器
专门处理Java代码的方法提取
"""

import logging
from typing import List, Tuple
from .base_parser import BaseMethodParser, MethodInfo
from ...language_loader import get_language_for_extension

logger = logging.getLogger(__name__)


class JavaMethodParser(BaseMethodParser):
    """Java方法解析器"""
    
    def __init__(self):
        super().__init__()
        # 获取Java语言库
        self.lang_lib, _ = get_language_for_extension('.java')
        if not self.lang_lib:
            logger.error("无法加载Java语言库")
    
    def find_all_methods(self, tree, code_content: str) -> List[MethodInfo]:
        """查找所有Java方法"""
        methods = []
        lines = code_content.split('\n')
        
        try:
            # 查找所有方法声明
            method_query = "(method_declaration) @method"
            captures = self.execute_query(method_query, tree.root_node)
            
            if 'method' in captures:
                for method_node in captures['method']:
                    method_info = self._parse_method_node(method_node, lines, code_content)
                    if method_info:
                        methods.append(method_info)
            
            # 查找构造函数
            constructor_query = "(constructor_declaration) @constructor"
            captures = self.execute_query(constructor_query, tree.root_node)
            
            if 'constructor' in captures:
                for constructor_node in captures['constructor']:
                    method_info = self._parse_constructor_node(constructor_node, lines, code_content)
                    if method_info:
                        methods.append(method_info)
            
            return methods
            
        except Exception as e:
            logger.error(f"查找Java方法时发生错误: {e}")
            return []
    
    def _parse_method_node(self, method_node, lines: List[str], code_content: str) -> MethodInfo:
        """解析方法节点"""
        try:
            # 提取方法签名信息
            method_name, param_types, return_type = self.extract_method_signature(method_node, lines)
            
            # 提取方法代码
            method_code = self.extract_method_code(method_node, code_content)
            
            # 获取行范围
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
            logger.error(f"解析Java方法节点时发生错误: {e}")
            return None
    
    def _parse_constructor_node(self, constructor_node, lines: List[str], code_content: str) -> MethodInfo:
        """解析构造函数节点"""
        try:
            # 提取构造函数名（通常是类名）
            constructor_name = self._extract_constructor_name(constructor_node)
            
            # 提取参数类型
            param_types = self._extract_parameters(constructor_node, lines)
            
            # 提取构造函数代码
            method_code = self.extract_method_code(constructor_node, code_content)
            
            # 获取行范围
            start_line, end_line = self.get_line_range(constructor_node)
            
            return MethodInfo(
                name=constructor_name,
                parameters=param_types,
                return_type="",  # 构造函数没有返回类型
                start_line=start_line,
                end_line=end_line,
                code=method_code
            )
            
        except Exception as e:
            logger.error(f"解析Java构造函数节点时发生错误: {e}")
            return None
    
    def extract_method_signature(self, node, lines: List[str]) -> Tuple[str, List[str], str]:
        """
        提取Java方法签名信息
        
        Returns:
            Tuple[str, List[str], str]: (方法名, 参数类型列表, 返回类型)
        """
        try:
            method_name = "unknown"
            param_types = []
            return_type = "void"
            
            # 提取方法名
            method_name = self._extract_method_name(node)
            
            # 提取参数信息
            param_types = self._extract_parameters(node, lines)
            
            # 提取返回类型
            return_type = self._extract_return_type(node)
            
            return method_name, param_types, return_type
            
        except Exception as e:
            logger.error(f"提取Java方法签名时发生错误: {e}")
            return "unknown", [], "void"
    
    def _extract_method_name(self, method_node) -> str:
        """提取方法名"""
        try:
            for child in method_node.children:
                if child.type == 'identifier':
                    return child.text.decode('utf-8')
            return "unknown"
        except Exception as e:
            logger.error(f"提取Java方法名时发生错误: {e}")
            return "unknown"
    
    def _extract_constructor_name(self, constructor_node) -> str:
        """提取构造函数名"""
        try:
            for child in constructor_node.children:
                if child.type == 'identifier':
                    return child.text.decode('utf-8')
            return "unknown"
        except Exception as e:
            logger.error(f"提取Java构造函数名时发生错误: {e}")
            return "unknown"
    
    def _extract_parameters(self, method_node, lines: List[str]) -> List[str]:
        """提取参数类型列表"""
        param_types = []
        
        try:
            # 查找形式参数列表
            for child in method_node.children:
                if child.type == 'formal_parameters':
                    param_types = self._parse_formal_parameters(child, lines)
                    break
            
            return param_types
            
        except Exception as e:
            logger.error(f"提取Java参数时发生错误: {e}")
            return []
    
    def _parse_formal_parameters(self, params_node, lines: List[str]) -> List[str]:
        """解析形式参数列表"""
        param_types = []
        
        try:
            for child in params_node.children:
                if child.type == 'formal_parameter':
                    param_type = self._extract_formal_parameter_type(child)
                    if param_type:
                        param_types.append(param_type)
                elif child.type == 'spread_parameter':
                    # 可变参数 (varargs)
                    param_type = self._extract_spread_parameter_type(child)
                    if param_type:
                        param_types.append(param_type)
            
            return param_types
            
        except Exception as e:
            logger.error(f"解析Java形式参数时发生错误: {e}")
            return []
    
    def _extract_formal_parameter_type(self, param_node) -> str:
        """提取形式参数类型"""
        try:
            # 查找类型节点
            for child in param_node.children:
                if child.type in ['type_identifier', 'integral_type', 'floating_point_type', 
                                'boolean_type', 'generic_type', 'array_type']:
                    return child.text.decode('utf-8')
            
            return "Object"  # 默认类型
            
        except Exception as e:
            logger.error(f"提取Java形式参数类型时发生错误: {e}")
            return "Object"
    
    def _extract_spread_parameter_type(self, param_node) -> str:
        """提取可变参数类型"""
        try:
            # 可变参数格式：Type... name
            for child in param_node.children:
                if child.type in ['type_identifier', 'integral_type', 'floating_point_type', 
                                'boolean_type', 'generic_type', 'array_type']:
                    base_type = child.text.decode('utf-8')
                    return f"{base_type}..."  # 标记为可变参数
            
            return "Object..."
            
        except Exception as e:
            logger.error(f"提取Java可变参数类型时发生错误: {e}")
            return "Object..."
    
    def _extract_return_type(self, method_node) -> str:
        """提取返回类型"""
        try:
            # 查找返回类型节点
            for child in method_node.children:
                if child.type in ['type_identifier', 'integral_type', 'floating_point_type', 
                                'boolean_type', 'void_type', 'generic_type', 'array_type']:
                    return child.text.decode('utf-8')
            
            return "void"  # 默认返回类型
            
        except Exception as e:
            logger.error(f"提取Java返回类型时发生错误: {e}")
            return "void"
    
    def extract_dependencies(self, tree, code_content: str) -> List['DependencyInfo']:
        """
        提取Java文件中的依赖关系
        
        Returns:
            List[DependencyInfo]: 依赖信息列表
        """
        from ..dependency_extractor import DependencyInfo
        
        dependencies = []
        
        try:
            # 查找import语句
            import_query = "(import_declaration) @import"
            captures = self.execute_query(import_query, tree.root_node)
            
            if 'import' in captures:
                for import_node in captures['import']:
                    dep = self._parse_import_declaration(import_node, code_content)
                    if dep:
                        dependencies.append(dep)
            
            return dependencies
            
        except Exception as e:
            logger.error(f"提取Java依赖时发生错误: {e}")
            return []
    
    def _parse_import_declaration(self, import_node, code_content: str) -> 'DependencyInfo':
        """解析Java import声明"""
        from ..dependency_extractor import DependencyInfo
        
        try:
            # 获取import语句的文本
            import_text = self.get_node_text(import_node, code_content)
            
            # 解析import语句：import package.ClassName; 或 import static package.ClassName.method;
            import_text = import_text.strip()
            
            # 移除import关键字和分号
            import_text = import_text.replace('import ', '').replace(';', '').strip()
            
            # 处理static import
            import_type = 'import'
            if import_text.startswith('static '):
                import_type = 'static_import'
                import_text = import_text.replace('static ', '').strip()
            
            # 提取包名和类名
            if import_text:
                return DependencyInfo(
                    import_name=import_text,
                    import_type=import_type
                )
            
            return None
            
        except Exception as e:
            logger.error(f"解析Java import声明时发生错误: {e}")
            return None