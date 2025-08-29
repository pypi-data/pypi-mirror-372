"""
Python方法解析器
专门处理Python代码的方法提取
"""

import re
import logging
from typing import List, Tuple
from .base_parser import BaseMethodParser, MethodInfo
from ...language_loader import get_language_for_extension

logger = logging.getLogger(__name__)


class PythonMethodParser(BaseMethodParser):
    """Python方法解析器"""
    
    def __init__(self):
        super().__init__()
        # 获取Python语言库
        self.lang_lib, _ = get_language_for_extension('.py')
        if not self.lang_lib:
            logger.error("无法加载Python语言库")
    
    def find_all_methods(self, tree, code_content: str) -> List[MethodInfo]:
        """查找所有Python方法和函数"""
        logger.info("开始查找Python方法")
        methods = []
        lines = code_content.split('\n')
        
        try:
            # 查找所有函数定义
            function_query = "(function_definition) @function"
            logger.info(f"执行查询: {function_query}")
            captures = self.execute_query(function_query, tree.root_node)
            logger.info(f"查询返回的captures: {captures}")
            
            if 'function' in captures:
                for func_node in captures['function']:
                    method_info = self._parse_function_node(func_node, lines, code_content)
                    if method_info:
                        methods.append(method_info)
            
            return methods
            
        except Exception as e:
            logger.error(f"查找Python方法时发生错误: {e}")
            return []
    
    def _parse_function_node(self, func_node, lines: List[str], code_content: str) -> MethodInfo:
        """解析函数节点"""
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
            logger.error(f"解析Python函数节点时发生错误: {e}")
            return None
    
    def extract_method_signature(self, node, lines: List[str]) -> Tuple[str, List[str], str]:
        """
        提取Python方法签名信息
        
        Returns:
            Tuple[str, List[str], str]: (方法名, 参数类型列表, 返回类型)
        """
        try:
            method_name = "unknown"
            param_types = []
            return_type = ""
            
            # 提取方法名
            for child in node.children:
                if child.type == 'identifier':
                    method_name = child.text.decode('utf-8')
                    break
            
            # 提取参数信息
            param_types = self._extract_parameters(node, lines)
            
            # 提取返回类型
            return_type = self._extract_return_type(node, lines)
            
            return method_name, param_types, return_type
            
        except Exception as e:
            logger.error(f"提取Python方法签名时发生错误: {e}")
            return "unknown", [], ""
    
    def _extract_parameters(self, func_node, lines: List[str]) -> List[str]:
        """提取参数类型列表"""
        param_types = []
        
        try:
            # 查找参数列表
            for child in func_node.children:
                if child.type == 'parameters':
                    param_types = self._parse_parameters_node(child, lines)
                    break
            
            return param_types
            
        except Exception as e:
            logger.error(f"提取Python参数时发生错误: {e}")
            return []
    
    def _parse_parameters_node(self, params_node, lines: List[str]) -> List[str]:
        """解析参数节点"""
        param_types = []
        
        try:
            for child in params_node.children:
                if child.type == 'identifier':
                    # 简单参数，没有类型注解
                    param_name = child.text.decode('utf-8')
                    if param_name != 'self':  # 跳过self参数
                        param_types.append('Any')
                
                elif child.type == 'typed_parameter':
                    # 带类型注解的参数
                    param_type = self._extract_typed_parameter(child, lines)
                    if param_type:
                        param_types.append(param_type)
                
                elif child.type == 'default_parameter':
                    # 带默认值的参数
                    param_type = self._extract_default_parameter(child, lines)
                    if param_type:
                        param_types.append(param_type)
            
            return param_types
            
        except Exception as e:
            logger.error(f"解析Python参数节点时发生错误: {e}")
            return []
    
    def _extract_typed_parameter(self, typed_param_node, lines: List[str]) -> str:
        """提取带类型注解的参数"""
        try:
            param_name = ""
            param_type = "Any"
            
            for child in typed_param_node.children:
                if child.type == 'identifier':
                    param_name = child.text.decode('utf-8')
                elif child.type == 'type':
                    param_type = child.text.decode('utf-8')
            
            # 跳过self参数
            if param_name == 'self':
                return None
            
            return param_type
            
        except Exception as e:
            logger.error(f"提取带类型注解的参数时发生错误: {e}")
            return "Any"
    
    def _extract_default_parameter(self, default_param_node, lines: List[str]) -> str:
        """提取带默认值的参数"""
        try:
            param_name = ""
            param_type = "Any"
            
            for child in default_param_node.children:
                if child.type == 'identifier':
                    param_name = child.text.decode('utf-8')
                elif child.type == 'type':
                    param_type = child.text.decode('utf-8')
            
            # 跳过self参数
            if param_name == 'self':
                return None
            
            # 如果没有类型注解，尝试从默认值推断
            if param_type == "Any":
                param_type = self._infer_type_from_default(default_param_node)
            
            return param_type
            
        except Exception as e:
            logger.error(f"提取带默认值的参数时发生错误: {e}")
            return "Any"
    
    def _infer_type_from_default(self, default_param_node) -> str:
        """从默认值推断参数类型"""
        try:
            # 查找默认值
            for child in default_param_node.children:
                if child.type in ['integer', 'float', 'string', 'true', 'false', 'none']:
                    if child.type == 'integer':
                        return 'int'
                    elif child.type == 'float':
                        return 'float'
                    elif child.type == 'string':
                        return 'str'
                    elif child.type in ['true', 'false']:
                        return 'bool'
                    elif child.type == 'none':
                        return 'Optional[Any]'
            
            return "Any"
            
        except Exception:
            return "Any"
    
    def _extract_return_type(self, func_node, lines: List[str]) -> str:
        """提取返回类型"""
        try:
            # 查找返回类型注解
            start_line = func_node.start_point[0]
            end_line = min(func_node.start_point[0] + 5, len(lines))  # 只检查前几行
            
            for i in range(start_line, end_line):
                line = lines[i].strip()
                # 查找 -> 返回类型注解
                if '->' in line:
                    # 提取返回类型
                    parts = line.split('->')
                    if len(parts) > 1:
                        return_part = parts[1].split(':')[0].strip()
                        return return_part
            
            return ""
            
        except Exception as e:
            logger.error(f"提取Python返回类型时发生错误: {e}")
            return ""
    
    def extract_dependencies(self, tree, code_content: str) -> List['DependencyInfo']:
        """
        提取Python文件中的依赖关系
        
        Returns:
            List[DependencyInfo]: 依赖信息列表
        """
        from ..dependency_extractor import DependencyInfo
        
        dependencies = []
        
        try:
            # 查找import语句
            import_query = "(import_statement) @import"
            captures = self.execute_query(import_query, tree.root_node)
            
            if 'import' in captures:
                for import_node in captures['import']:
                    deps = self._parse_import_statement(import_node, code_content)
                    dependencies.extend(deps)
            
            # 查找from import语句
            from_import_query = "(import_from_statement) @from_import"
            captures = self.execute_query(from_import_query, tree.root_node)
            
            if 'from_import' in captures:
                for from_import_node in captures['from_import']:
                    deps = self._parse_from_import_statement(from_import_node, code_content)
                    dependencies.extend(deps)
            
            return dependencies
            
        except Exception as e:
            logger.error(f"提取Python依赖时发生错误: {e}")
            return []
    
    def _parse_import_statement(self, import_node, code_content: str) -> List['DependencyInfo']:
        """解析import语句"""
        from ..dependency_extractor import DependencyInfo
        
        dependencies = []
        
        try:
            # 获取import语句的文本
            import_text = self.get_node_text(import_node, code_content)
            
            # 解析import语句：import module1, module2, module3
            import_text = import_text.replace('import ', '').strip()
            modules = [m.strip() for m in import_text.split(',')]
            
            for module in modules:
                if module:
                    # 处理 as 别名
                    if ' as ' in module:
                        module = module.split(' as ')[0].strip()
                    
                    dependencies.append(DependencyInfo(
                        import_name=module,
                        import_type='import'
                    ))
            
            return dependencies
            
        except Exception as e:
            logger.error(f"解析Python import语句时发生错误: {e}")
            return []
    
    def _parse_from_import_statement(self, from_import_node, code_content: str) -> List['DependencyInfo']:
        """解析from import语句"""
        from ..dependency_extractor import DependencyInfo
        
        dependencies = []
        
        try:
            # 获取from import语句的文本
            from_import_text = self.get_node_text(from_import_node, code_content)
            
            # 解析from import语句：from module import item1, item2
            if ' from ' in from_import_text and ' import ' in from_import_text:
                parts = from_import_text.split(' import ')
                if len(parts) == 2:
                    module_part = parts[0].replace('from ', '').strip()
                    
                    # 只记录模块依赖，不记录具体导入的项
                    if module_part:
                        dependencies.append(DependencyInfo(
                            import_name=module_part,
                            import_type='from_import'
                        ))
            
            return dependencies
            
        except Exception as e:
            logger.error(f"解析Python from import语句时发生错误: {e}")
            return []