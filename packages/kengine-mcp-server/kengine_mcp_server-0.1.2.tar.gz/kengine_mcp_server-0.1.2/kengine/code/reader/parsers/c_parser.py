"""
C语言方法解析器
专门处理C代码的函数提取
"""

import logging
from typing import List, Tuple
from .base_parser import BaseMethodParser, MethodInfo
from ...language_loader import get_language_for_extension

logger = logging.getLogger(__name__)


class CMethodParser(BaseMethodParser):
    """C语言方法解析器"""
    
    def __init__(self):
        super().__init__()
        self.lang_lib, _ = get_language_for_extension('.c')
        if not self.lang_lib:
            logger.error("无法加载C语言库")
    
    def find_all_methods(self, tree, code_content: str) -> List[MethodInfo]:
        """查找所有C函数"""
        methods = []
        lines = code_content.split('\n')
        
        try:
            function_query = "(function_definition) @function"
            captures = self.execute_query(function_query, tree.root_node)
            
            if 'function' in captures:
                for func_node in captures['function']:
                    method_info = self._parse_function_node(func_node, lines, code_content)
                    if method_info:
                        methods.append(method_info)
            
            return methods
        except Exception as e:
            logger.error(f"查找C函数时发生错误: {e}")
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
            logger.error(f"解析C函数节点时发生错误: {e}")
            return None
    
    def extract_method_signature(self, node, lines: List[str]) -> Tuple[str, List[str], str]:
        """提取C函数签名信息"""
        try:
            method_name = "unknown"
            param_types = []
            return_type = "void"
            
            # 查找函数声明器
            for child in node.children:
                if child.type == 'function_declarator':
                    method_name, param_types = self._extract_from_declarator(child)
                elif child.type in ['primitive_type', 'type_identifier']:
                    return_type = child.text.decode('utf-8')
            
            return method_name, param_types, return_type
        except Exception as e:
            logger.error(f"提取C函数签名时发生错误: {e}")
            return "unknown", [], "void"
    
    def _extract_from_declarator(self, declarator_node) -> Tuple[str, List[str]]:
        """从函数声明器提取信息"""
        method_name = "unknown"
        param_types = []
        
        try:
            for child in declarator_node.children:
                if child.type == 'identifier':
                    method_name = child.text.decode('utf-8')
                elif child.type == 'parameter_list':
                    param_types = self._extract_parameters_from_list(child)
            
            return method_name, param_types
        except Exception:
            return "unknown", []
    
    def _extract_parameters_from_list(self, params_node) -> List[str]:
        """从参数列表提取参数类型"""
        param_types = []
        try:
            for child in params_node.children:
                if child.type == 'parameter_declaration':
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
                if child.type in ['primitive_type', 'type_identifier']:
                    return child.text.decode('utf-8')
            return "void"
        except Exception:
            return "void"
    
    def extract_dependencies(self, tree, code_content: str) -> List['DependencyInfo']:
        """
        提取C文件中的依赖关系
        
        Returns:
            List[DependencyInfo]: 依赖信息列表
        """
        from ..dependency_extractor import DependencyInfo
        
        dependencies = []
        
        try:
            # 查找#include预处理指令
            preproc_query = "(preproc_include) @include"
            captures = self.execute_query(preproc_query, tree.root_node)
            
            if 'include' in captures:
                for include_node in captures['include']:
                    dep = self._parse_include_directive(include_node, code_content)
                    if dep:
                        dependencies.append(dep)
            
            return dependencies
            
        except Exception as e:
            logger.error(f"提取C依赖时发生错误: {e}")
            return []
    
    def _parse_include_directive(self, include_node, code_content: str) -> 'DependencyInfo':
        """解析C #include指令"""
        from ..dependency_extractor import DependencyInfo
        
        try:
            # 获取include语句的文本
            include_text = self.get_node_text(include_node, code_content)
            
            # 解析include语句：#include <stdio.h> 或 #include "header.h"
            include_text = include_text.strip()
            
            # 提取头文件名
            if '<' in include_text and '>' in include_text:
                # 系统头文件：#include <stdio.h>
                start = include_text.find('<') + 1
                end = include_text.find('>')
                header_name = include_text[start:end]
                import_type = 'system_include'
            elif '"' in include_text:
                # 用户头文件：#include "header.h"
                start = include_text.find('"') + 1
                end = include_text.rfind('"')
                header_name = include_text[start:end]
                import_type = 'user_include'
            else:
                return None
            
            if header_name:
                return DependencyInfo(
                    import_name=header_name,
                    import_type=import_type
                )
            
            return None
            
        except Exception as e:
            logger.error(f"解析C include指令时发生错误: {e}")
            return None