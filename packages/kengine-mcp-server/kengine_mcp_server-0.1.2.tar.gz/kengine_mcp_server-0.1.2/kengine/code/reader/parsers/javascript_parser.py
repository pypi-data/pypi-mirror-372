"""
JavaScript/TypeScript方法解析器
专门处理JavaScript和TypeScript代码的方法提取
"""

import logging
from typing import List, Tuple
from .base_parser import BaseMethodParser, MethodInfo
from ...language_loader import get_language_for_extension

logger = logging.getLogger(__name__)


class JavaScriptMethodParser(BaseMethodParser):
    """JavaScript/TypeScript方法解析器"""
    
    def __init__(self):
        super().__init__()
        # 获取JavaScript语言库
        self.lang_lib, _ = get_language_for_extension('.js')
        if not self.lang_lib:
            logger.error("无法加载JavaScript语言库")
    
    def find_all_methods(self, tree, code_content: str) -> List[MethodInfo]:
        """查找所有JavaScript/TypeScript方法和函数"""
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
            
            # 查找方法定义（在类中）
            method_query = "(method_definition) @method"
            captures = self.execute_query(method_query, tree.root_node)
            
            if 'method' in captures:
                for method_node in captures['method']:
                    method_info = self._parse_method_node(method_node, lines, code_content)
                    if method_info:
                        methods.append(method_info)
            
            # 查找箭头函数 - 使用lexical_declaration来获取完整的变量声明
            arrow_function_query = "(lexical_declaration) @lexical_declaration"
            captures = self.execute_query(arrow_function_query, tree.root_node)
            
            if 'lexical_declaration' in captures:
                for lexical_node in captures['lexical_declaration']:
                    # 检查是否包含箭头函数
                    if self._contains_arrow_function(lexical_node):
                        method_info = self._parse_arrow_function_declaration(lexical_node, lines, code_content)
                        if method_info:
                            methods.append(method_info)
            
            # 查找函数表达式
            function_expression_query = "(function_expression) @function_expression"
            captures = self.execute_query(function_expression_query, tree.root_node)
            
            if 'function_expression' in captures:
                for func_expr_node in captures['function_expression']:
                    method_info = self._parse_function_expression_node(func_expr_node, lines, code_content)
                    if method_info:
                        methods.append(method_info)
            
            return methods
            
        except Exception as e:
            logger.error(f"查找JavaScript方法时发生错误: {e}")
            return []
    
    def _parse_function_node(self, func_node, lines: List[str], code_content: str) -> MethodInfo:
        """解析函数声明节点"""
        try:
            # 提取方法签名信息
            method_name, param_types, return_type = self.extract_method_signature(func_node, lines)
            
            # 提取方法代码
            method_code = self.extract_method_code(func_node, code_content)
            
            # 获取行范围
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
            logger.error(f"解析JavaScript函数节点时发生错误: {e}")
            return None
    
    def _parse_method_node(self, method_node, lines: List[str], code_content: str) -> MethodInfo:
        """解析方法定义节点"""
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
            logger.error(f"解析JavaScript方法节点时发生错误: {e}")
            return None
    
    def _parse_arrow_function_node(self, arrow_func_node, lines: List[str], code_content: str) -> MethodInfo:
        """解析箭头函数节点"""
        try:
            # 箭头函数通常没有名字，需要从上下文推断
            method_name = self._extract_arrow_function_name(arrow_func_node, lines)
            
            # 提取参数类型
            param_types = self._extract_arrow_function_parameters(arrow_func_node, lines)
            
            # 提取返回类型
            return_type = self._extract_arrow_function_return_type(arrow_func_node, lines)
            
            # 提取方法代码
            method_code = self.extract_method_code(arrow_func_node, code_content)
            
            # 获取行范围
            start_line, end_line = self.get_line_range(arrow_func_node)
            
            return MethodInfo(
                name=method_name,
                parameters=param_types,
                return_type=return_type,
                start_line=start_line,
                end_line=end_line,
                code=method_code
            )
            
        except Exception as e:
            logger.error(f"解析JavaScript箭头函数节点时发生错误: {e}")
            return None
    
    def _parse_function_expression_node(self, func_expr_node, lines: List[str], code_content: str) -> MethodInfo:
        """解析函数表达式节点"""
        try:
            # 函数表达式可能有名字，也可能没有
            method_name = self._extract_function_expression_name(func_expr_node, lines)
            
            # 提取参数类型
            param_types = self._extract_parameters(func_expr_node, lines)
            
            # 提取返回类型
            return_type = self._extract_return_type(func_expr_node, lines)
            
            # 提取方法代码
            method_code = self.extract_method_code(func_expr_node, code_content)
            
            # 获取行范围
            start_line, end_line = self.get_line_range(func_expr_node)
            
            return MethodInfo(
                name=method_name,
                parameters=param_types,
                return_type=return_type,
                start_line=start_line,
                end_line=end_line,
                code=method_code
            )
            
        except Exception as e:
            logger.error(f"解析JavaScript函数表达式节点时发生错误: {e}")
            return None
    
    def _contains_arrow_function(self, lexical_node) -> bool:
        """检查lexical_declaration节点是否包含箭头函数"""
        try:
            # 遍历子节点查找arrow_function
            def check_node_recursive(node):
                if node.type == 'arrow_function':
                    return True
                for child in node.children:
                    if check_node_recursive(child):
                        return True
                return False
            
            return check_node_recursive(lexical_node)
        except Exception as e:
            logger.error(f"检查箭头函数时发生错误: {e}")
            return False
    
    def _parse_arrow_function_declaration(self, lexical_node, lines: List[str], code_content: str) -> MethodInfo:
        """解析包含箭头函数的lexical_declaration节点"""
        try:
            # 从lexical_declaration中提取箭头函数名称
            method_name = self._extract_arrow_function_name_from_declaration(lexical_node, lines)
            
            # 提取参数类型（从箭头函数节点）
            arrow_func_node = self._find_arrow_function_in_declaration(lexical_node)
            param_types = []
            return_type = "any"
            
            if arrow_func_node:
                param_types = self._extract_arrow_function_parameters(arrow_func_node, lines)
                return_type = self._extract_arrow_function_return_type(arrow_func_node, lines)
            
            # 使用lexical_declaration节点提取完整的方法代码（包含变量声明）
            method_code = self.extract_method_code(lexical_node, code_content)
            
            # 获取行范围
            start_line, end_line = self.get_line_range(lexical_node)
            
            return MethodInfo(
                name=method_name,
                parameters=param_types,
                return_type=return_type,
                start_line=start_line,
                end_line=end_line,
                code=method_code
            )
            
        except Exception as e:
            logger.error(f"解析箭头函数声明时发生错误: {e}")
            return None
    
    def _extract_arrow_function_name_from_declaration(self, lexical_node, lines: List[str]) -> str:
        """从lexical_declaration节点中提取箭头函数的变量名"""
        try:
            # 查找variable_declarator节点中的identifier
            def find_identifier(node):
                if node.type == 'identifier':
                    return node.text.decode('utf-8')
                for child in node.children:
                    result = find_identifier(child)
                    if result:
                        return result
                return None
            
            identifier = find_identifier(lexical_node)
            return identifier if identifier else "anonymous_arrow_function"
            
        except Exception as e:
            logger.error(f"提取箭头函数名称时发生错误: {e}")
            return "anonymous_arrow_function"
    
    def _find_arrow_function_in_declaration(self, lexical_node):
        """在lexical_declaration节点中查找arrow_function节点"""
        try:
            def find_arrow_function(node):
                if node.type == 'arrow_function':
                    return node
                for child in node.children:
                    result = find_arrow_function(child)
                    if result:
                        return result
                return None
            
            return find_arrow_function(lexical_node)
            
        except Exception as e:
            logger.error(f"查找箭头函数节点时发生错误: {e}")
            return None
    
    def extract_method_signature(self, node, lines: List[str]) -> Tuple[str, List[str], str]:
        """
        提取JavaScript/TypeScript方法签名信息
        
        Returns:
            Tuple[str, List[str], str]: (方法名, 参数类型列表, 返回类型)
        """
        try:
            method_name = "unknown"
            param_types = []
            return_type = "any"
            
            # 提取方法名
            method_name = self._extract_method_name(node)
            
            # 提取参数类型
            param_types = self._extract_parameters(node, lines)
            
            # 提取返回类型
            return_type = self._extract_return_type(node, lines)
            
            return method_name, param_types, return_type
            
        except Exception as e:
            logger.error(f"提取JavaScript方法签名时发生错误: {e}")
            return "unknown", [], "any"
    
    def _extract_method_name(self, node) -> str:
        """提取方法名"""
        try:
            # 查找identifier节点
            for child in node.children:
                if child.type == 'identifier':
                    return child.text.decode('utf-8')
                elif child.type == 'property_identifier':
                    return child.text.decode('utf-8')
            
            return "anonymous"
            
        except Exception as e:
            logger.error(f"提取方法名时发生错误: {e}")
            return "unknown"
    
    def _extract_arrow_function_name(self, arrow_func_node, lines: List[str]) -> str:
        """提取箭头函数名称（从上下文推断）"""
        try:
            # 箭头函数通常是赋值表达式的一部分
            # 需要向上查找父节点来获取变量名
            parent = arrow_func_node.parent
            while parent:
                if parent.type == 'variable_declarator':
                    # 查找identifier
                    for child in parent.children:
                        if child.type == 'identifier':
                            return child.text.decode('utf-8')
                elif parent.type == 'assignment_expression':
                    # 查找左侧的标识符
                    for child in parent.children:
                        if child.type == 'identifier':
                            return child.text.decode('utf-8')
                parent = parent.parent
            
            return "anonymous_arrow_function"
            
        except Exception as e:
            logger.error(f"提取箭头函数名称时发生错误: {e}")
            return "anonymous_arrow_function"
    
    def _extract_function_expression_name(self, func_expr_node, lines: List[str]) -> str:
        """提取函数表达式名称"""
        try:
            # 函数表达式可能有名字
            for child in func_expr_node.children:
                if child.type == 'identifier':
                    return child.text.decode('utf-8')
            
            # 如果没有名字，尝试从上下文推断
            parent = func_expr_node.parent
            while parent:
                if parent.type == 'variable_declarator':
                    for child in parent.children:
                        if child.type == 'identifier':
                            return child.text.decode('utf-8')
                elif parent.type == 'assignment_expression':
                    for child in parent.children:
                        if child.type == 'identifier':
                            return child.text.decode('utf-8')
                parent = parent.parent
            
            return "anonymous_function_expression"
            
        except Exception as e:
            logger.error(f"提取函数表达式名称时发生错误: {e}")
            return "anonymous_function_expression"
    
    def _extract_parameters(self, node, lines: List[str]) -> List[str]:
        """提取参数列表"""
        try:
            params = []
            
            # 查找formal_parameters节点
            for child in node.children:
                if child.type == 'formal_parameters':
                    params = self._parse_formal_parameters(child, lines)
                    break
            
            return params
            
        except Exception as e:
            logger.error(f"提取参数列表时发生错误: {e}")
            return []
    
    def _extract_arrow_function_parameters(self, arrow_func_node, lines: List[str]) -> List[str]:
        """提取箭头函数参数"""
        try:
            params = []
            
            # 箭头函数的参数可能是单个identifier或formal_parameters
            for child in arrow_func_node.children:
                if child.type == 'formal_parameters':
                    params = self._parse_formal_parameters(child, lines)
                    break
                elif child.type == 'identifier':
                    # 单个参数，没有括号
                    param_name = child.text.decode('utf-8')
                    params.append(f"{param_name}: any")
                    break
            
            return params
            
        except Exception as e:
            logger.error(f"提取箭头函数参数时发生错误: {e}")
            return []
    
    def _parse_formal_parameters(self, params_node, lines: List[str]) -> List[str]:
        """解析formal_parameters节点"""
        try:
            params = []
            
            for child in params_node.children:
                if child.type == 'identifier':
                    param_name = child.text.decode('utf-8')
                    params.append(f"{param_name}: any")
                elif child.type == 'required_parameter':
                    # TypeScript参数
                    param_info = self._extract_typescript_parameter_type(child)
                    if param_info:
                        params.append(param_info)
                elif child.type == 'optional_parameter':
                    # TypeScript可选参数
                    param_info = self._extract_typescript_parameter_type(child)
                    if param_info:
                        params.append(param_info + "?")
            
            return params
            
        except Exception as e:
            logger.error(f"解析formal_parameters时发生错误: {e}")
            return []
    
    def _extract_typescript_parameter_type(self, param_node) -> str:
        """提取TypeScript参数类型"""
        try:
            param_name = "unknown"
            param_type = "any"
            
            # 查找参数名和类型
            for child in param_node.children:
                if child.type == 'identifier':
                    param_name = child.text.decode('utf-8')
                elif child.type == 'type_annotation':
                    # 提取类型注解
                    for type_child in child.children:
                        if type_child.type != ':':
                            param_type = type_child.text.decode('utf-8')
                            break
            
            return f"{param_name}: {param_type}"
            
        except Exception as e:
            logger.error(f"提取TypeScript参数类型时发生错误: {e}")
            return "unknown: any"
    
    def _extract_return_type(self, node, lines: List[str]) -> str:
        """提取返回类型"""
        try:
            # 查找type_annotation节点
            for child in node.children:
                if child.type == 'type_annotation':
                    # 提取类型注解
                    for type_child in child.children:
                        if type_child.type != ':':
                            return type_child.text.decode('utf-8')
            
            return "any"
            
        except Exception as e:
            logger.error(f"提取返回类型时发生错误: {e}")
            return "any"
    
    def _extract_arrow_function_return_type(self, arrow_func_node, lines: List[str]) -> str:
        """提取箭头函数返回类型"""
        try:
            # 箭头函数的返回类型注解
            for child in arrow_func_node.children:
                if child.type == 'type_annotation':
                    for type_child in child.children:
                        if type_child.type != ':':
                            return type_child.text.decode('utf-8')
            
            return "any"
            
        except Exception as e:
            logger.error(f"提取箭头函数返回类型时发生错误: {e}")
            return "any"
    
    def extract_dependencies(self, tree, code_content: str) -> List['DependencyInfo']:
        """提取JavaScript/TypeScript依赖信息"""
        try:
            from ...types import DependencyInfo
            dependencies = []
            
            # 查找import语句
            import_query = "(import_statement) @import"
            captures = self.execute_query(import_query, tree.root_node)
            
            if 'import' in captures:
                for import_node in captures['import']:
                    dep_info = self._parse_import_statement(import_node, code_content)
                    if dep_info:
                        dependencies.append(dep_info)
            
            # 查找require调用
            require_query = "(call_expression) @call"
            captures = self.execute_query(require_query, tree.root_node)
            
            if 'call' in captures:
                for call_node in captures['call']:
                    dep_info = self._parse_require_call(call_node, code_content)
                    if dep_info:
                        dependencies.append(dep_info)
            
            return dependencies
            
        except Exception as e:
            logger.error(f"提取JavaScript依赖时发生错误: {e}")
            return []
    
    def _parse_import_statement(self, import_node, code_content: str) -> 'DependencyInfo':
        """解析import语句"""
        try:
            from ...types import DependencyInfo
            
            # 提取import语句的文本
            import_text = import_node.text.decode('utf-8')
            
            # 简单解析import语句
            if 'from' in import_text:
                parts = import_text.split('from')
                if len(parts) >= 2:
                    module_name = parts[-1].strip().strip('\'"').strip(';')
                    if module_name:
                        return DependencyInfo(
                            import_name=module_name,
                            import_type='import'
                        )
            
            return None
            
        except Exception as e:
            logger.error(f"解析import语句时发生错误: {e}")
            return None
    
    def _parse_require_call(self, call_node, code_content: str) -> 'DependencyInfo':
        """解析require调用"""
        try:
            from ...types import DependencyInfo
            
            # 检查是否是require调用
            call_text = call_node.text.decode('utf-8')
            
            if call_text.startswith('require('):
                # 提取require的参数
                for child in call_node.children:
                    if child.type == 'arguments':
                        for arg_child in child.children:
                            if arg_child.type == 'string':
                                module_name = arg_child.text.decode('utf-8').strip('\'"')
                                if module_name:
                                    return DependencyInfo(
                                        import_name=module_name,
                                        import_type='require'
                                    )
            
            return None
            
        except Exception as e:
            logger.error(f"解析require调用时发生错误: {e}")
            return None