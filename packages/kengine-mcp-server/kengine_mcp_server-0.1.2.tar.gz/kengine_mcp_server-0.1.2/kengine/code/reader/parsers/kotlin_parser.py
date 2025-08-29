"""
Kotlin方法解析器
专门处理Kotlin代码的方法提取
"""

import logging
from typing import List, Tuple
from .base_parser import BaseMethodParser, MethodInfo
from ...language_loader import get_language_for_extension

logger = logging.getLogger(__name__)


class KotlinMethodParser(BaseMethodParser):
    """Kotlin方法解析器"""
    
    def __init__(self):
        super().__init__()
        # 获取Kotlin语言库
        self.lang_lib, _ = get_language_for_extension('.kt')
        if not self.lang_lib:
            logger.error("无法加载Kotlin语言库")
    
    def find_all_methods(self, tree, code_content: str) -> List[MethodInfo]:
        """查找所有Kotlin方法"""
        methods = []
        lines = code_content.split('\n')
        
        try:
            # 查找所有函数声明
            function_query = "(function_declaration) @function"
            captures = self.execute_query(function_query, tree.root_node)
            
            if 'function' in captures:
                for function_node in captures['function']:
                    method_info = self._parse_function_node(function_node, lines, code_content)
                    if method_info:
                        methods.append(method_info)
            
            # 查找构造函数
            constructor_query = "(primary_constructor) @constructor"
            captures = self.execute_query(constructor_query, tree.root_node)
            
            if 'constructor' in captures:
                for constructor_node in captures['constructor']:
                    method_info = self._parse_constructor_node(constructor_node, lines, code_content)
                    if method_info:
                        methods.append(method_info)
            
            # 查找次级构造函数
            secondary_constructor_query = "(secondary_constructor) @secondary_constructor"
            captures = self.execute_query(secondary_constructor_query, tree.root_node)
            
            if 'secondary_constructor' in captures:
                for constructor_node in captures['secondary_constructor']:
                    method_info = self._parse_secondary_constructor_node(constructor_node, lines, code_content)
                    if method_info:
                        methods.append(method_info)
            
            return methods
            
        except Exception as e:
            logger.error(f"查找Kotlin方法时发生错误: {e}")
            return []
    
    def _parse_function_node(self, function_node, lines: List[str], code_content: str) -> MethodInfo:
        """解析函数节点"""
        try:
            # 提取函数签名信息
            function_name, param_types, return_type = self.extract_method_signature(function_node, lines)
            
            # 提取函数代码
            method_code = self.extract_method_code(function_node, code_content)
            
            # 获取行范围
            start_line, end_line = self.get_line_range(function_node)
            
            return MethodInfo(
                name=function_name,
                parameters=param_types,
                return_type=return_type,
                start_line=start_line,
                end_line=end_line,
                code=method_code
            )
            
        except Exception as e:
            logger.error(f"解析Kotlin函数节点时发生错误: {e}")
            return None
    
    def _parse_constructor_node(self, constructor_node, lines: List[str], code_content: str) -> MethodInfo:
        """解析主构造函数节点"""
        try:
            # 主构造函数通常没有显式的名称，使用类名
            constructor_name = self._extract_class_name_from_constructor(constructor_node)
            
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
            logger.error(f"解析Kotlin主构造函数节点时发生错误: {e}")
            return None
    
    def _parse_secondary_constructor_node(self, constructor_node, lines: List[str], code_content: str) -> MethodInfo:
        """解析次级构造函数节点"""
        try:
            # 次级构造函数名称为constructor
            constructor_name = "constructor"
            
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
            logger.error(f"解析Kotlin次级构造函数节点时发生错误: {e}")
            return None
    
    def extract_method_signature(self, node, lines: List[str]) -> Tuple[str, List[str], str]:
        """
        提取Kotlin方法签名信息
        
        Returns:
            Tuple[str, List[str], str]: (方法名, 参数类型列表, 返回类型)
        """
        try:
            method_name = "unknown"
            param_types = []
            return_type = "Unit"
            
            # 提取方法名
            method_name = self._extract_method_name(node)
            
            # 提取参数信息
            param_types = self._extract_parameters(node, lines)
            
            # 提取返回类型
            return_type = self._extract_return_type(node)
            
            return method_name, param_types, return_type
            
        except Exception as e:
            logger.error(f"提取Kotlin方法签名时发生错误: {e}")
            return "unknown", [], "Unit"
    
    def _extract_method_name(self, function_node) -> str:
        """提取方法名"""
        try:
            for child in function_node.children:
                if child.type == 'identifier':
                    return child.text.decode('utf-8')
            return "unknown"
        except Exception as e:
            logger.error(f"提取Kotlin方法名时发生错误: {e}")
            return "unknown"
    
    def _extract_class_name_from_constructor(self, constructor_node) -> str:
        """从构造函数节点提取类名"""
        try:
            # 向上查找类声明节点
            parent = constructor_node.parent
            while parent and parent.type != 'class_declaration':
                parent = parent.parent
            
            if parent:
                for child in parent.children:
                    if child.type == 'identifier':
                        return child.text.decode('utf-8')
            
            return "unknown"
        except Exception as e:
            logger.error(f"从Kotlin构造函数提取类名时发生错误: {e}")
            return "unknown"
    
    def _extract_parameters(self, function_node, lines: List[str]) -> List[str]:
        """提取参数类型列表"""
        param_types = []
        
        try:
            # 查找形式参数列表
            for child in function_node.children:
                if child.type == 'parameter_list':
                    param_types = self._parse_parameter_list(child, lines)
                    break
            
            return param_types
            
        except Exception as e:
            logger.error(f"提取Kotlin参数时发生错误: {e}")
            return []
    
    def _parse_parameter_list(self, params_node, lines: List[str]) -> List[str]:
        """解析参数列表"""
        param_types = []
        
        try:
            for child in params_node.children:
                if child.type == 'parameter':
                    param_type = self._extract_parameter_type(child)
                    if param_type:
                        param_types.append(param_type)
                elif child.type == 'spread_parameter':
                    # 可变参数
                    param_type = self._extract_spread_parameter_type(child)
                    if param_type:
                        param_types.append(param_type)
            
            return param_types
            
        except Exception as e:
            logger.error(f"解析Kotlin参数列表时发生错误: {e}")
            return []
    
    def _extract_parameter_type(self, param_node) -> str:
        """提取参数类型"""
        try:
            # 查找类型节点
            for child in param_node.children:
                if child.type in ['type_identifier', 'integral_type', 'floating_point_type', 
                                'boolean_type', 'generic_type', 'array_type', 'nullable_type']:
                    return child.text.decode('utf-8')
            
            return "Any"  # 默认类型
            
        except Exception as e:
            logger.error(f"提取Kotlin参数类型时发生错误: {e}")
            return "Any"
    
    def _extract_spread_parameter_type(self, param_node) -> str:
        """提取可变参数类型"""
        try:
            # 可变参数格式：vararg name: Type
            for child in param_node.children:
                if child.type in ['type_identifier', 'integral_type', 'floating_point_type', 
                                'boolean_type', 'generic_type', 'array_type', 'nullable_type']:
                    base_type = child.text.decode('utf-8')
                    return f"{base_type}..."  # 标记为可变参数
            
            return "Any..."
            
        except Exception as e:
            logger.error(f"提取Kotlin可变参数类型时发生错误: {e}")
            return "Any..."
    
    def _extract_return_type(self, function_node) -> str:
        """提取返回类型"""
        try:
            # 查找返回类型节点
            for child in function_node.children:
                if child.type in ['type_identifier', 'integral_type', 'floating_point_type', 
                                'boolean_type', 'void_type', 'generic_type', 'array_type', 
                                'nullable_type']:
                    return child.text.decode('utf-8')
            
            # Kotlin中无返回值的函数返回Unit
            return "Unit"
            
        except Exception as e:
            logger.error(f"提取Kotlin返回类型时发生错误: {e}")
            return "Unit"
    
    def extract_dependencies(self, tree, code_content: str) -> List['DependencyInfo']:
        """
        提取Kotlin文件中的依赖关系
        
        Returns:
            List[DependencyInfo]: 依赖信息列表
        """
        from ..dependency_extractor import DependencyInfo
        
        dependencies = []
        
        try:
            # 查找import语句
            import_query = "(import_header) @import"
            captures = self.execute_query(import_query, tree.root_node)
            
            if 'import' in captures:
                for import_node in captures['import']:
                    dep = self._parse_import_declaration(import_node, code_content)
                    if dep:
                        dependencies.append(dep)
            
            return dependencies
            
        except Exception as e:
            logger.error(f"提取Kotlin依赖时发生错误: {e}")
            return []
    
    def _parse_import_declaration(self, import_node, code_content: str) -> 'DependencyInfo':
        """解析Kotlin import声明"""
        from ..dependency_extractor import DependencyInfo
        
        try:
            # 获取import语句的文本
            import_text = self.get_node_text(import_node, code_content)
            
            # 解析import语句：import package.ClassName 或 import package.ClassName as Alias
            import_text = import_text.strip()
            
            # 移除import关键字
            import_text = import_text.replace('import ', '').strip()
            
            # 处理as别名
            import_type = 'import'
            if ' as ' in import_text:
                import_type = 'aliased_import'
                import_text = import_text.split(' as ')[0].strip()
            
            # 提取包名和类名
            if import_text:
                return DependencyInfo(
                    import_name=import_text,
                    import_type=import_type
                )
            
            return None
            
        except Exception as e:
            logger.error(f"解析Kotlin import声明时发生错误: {e}")
            return None