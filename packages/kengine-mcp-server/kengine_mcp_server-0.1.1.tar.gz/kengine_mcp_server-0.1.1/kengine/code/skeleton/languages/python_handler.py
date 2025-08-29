"""
Python语言代码骨架处理器
重构版本：添加字段提取功能
"""

import logging
import re
from typing import List, Dict, Any
from .base_language import BaseLanguageHandler

logger = logging.getLogger(__name__)


class PythonHandler(BaseLanguageHandler):
    """Python代码骨架处理器"""
    
    def generate_skeleton(self, tree, code_content: str) -> str:
        """生成Python代码骨架"""
        lines = code_content.split('\n')
        skeleton_lines = []
        
        # 提取导入语句
        self._extract_imports(tree.root_node, lines, skeleton_lines)
        
        # 提取类
        class_nodes = self._extract_classes(tree.root_node, lines, skeleton_lines)
        
        # 提取顶级函数
        self._extract_top_level_functions(tree.root_node, lines, skeleton_lines, class_nodes)
        
        return '\n'.join(skeleton_lines)
    
    def extract_class_name(self, node, lines: List[str]) -> str:
        """提取Python类名"""
        try:
            # Python AST: class_definition -> identifier
            for child in node.children:
                if child.type == 'identifier':
                    return child.text.decode('utf-8')
            return "UnknownClass"
        except Exception as e:
            logger.error(f"提取Python类名时发生错误: {e}")
            return "UnknownClass"
    
    def extract_function_signature(self, node, lines: List[str]) -> str:
        """提取Python函数签名，修复类型注解格式问题"""
        try:
            start_line = node.start_point[0]
            start_col = node.start_point[1]
            end_line = node.end_point[0]
            end_col = node.end_point[1]
            
            # 直接从源代码行中提取完整的函数签名
            signature_lines = []
            paren_count = 0
            bracket_count = 0
            in_string = False
            string_char = None
            
            for i in range(start_line, min(end_line + 5, len(lines))):
                line = lines[i]
                
                if i == start_line:
                    # 第一行，从特定列开始
                    line_part = line[start_col:]
                else:
                    line_part = line.strip()
                
                # 逐字符分析，处理字符串和括号
                j = 0
                while j < len(line_part):
                    char = line_part[j]
                    
                    # 处理字符串
                    if char in ['"', "'"] and not in_string:
                        in_string = True
                        string_char = char
                    elif char == string_char and in_string:
                        # 检查是否是转义字符
                        if j == 0 or line_part[j-1] != '\\':
                            in_string = False
                            string_char = None
                    
                    # 如果不在字符串中，计算括号
                    if not in_string:
                        if char == '(':
                            paren_count += 1
                        elif char == ')':
                            paren_count -= 1
                        elif char == '[':
                            bracket_count += 1
                        elif char == ']':
                            bracket_count -= 1
                        elif char == ':' and paren_count == 0 and bracket_count == 0:
                            # 找到函数签名结束的冒号
                            signature_lines.append(line_part[:j + 1])
                            break
                    
                    j += 1
                else:
                    # 如果没有找到冒号，添加整行
                    signature_lines.append(line_part)
                    continue
                
                # 如果找到了冒号，跳出循环
                break
            
            if signature_lines:
                # 清理并连接签名行
                cleaned_lines = []
                for line in signature_lines:
                    cleaned_line = line.strip()
                    if cleaned_line:
                        cleaned_lines.append(cleaned_line)
                
                if cleaned_lines:
                    # 智能连接多行签名
                    result = cleaned_lines[0]
                    for line in cleaned_lines[1:]:
                        if line.startswith(')') or line.startswith(',') or line.startswith(':'):
                            result += line
                        else:
                            result += ' ' + line
                    
                    # 清理多余的空格，但保持基本结构，确保符合PEP 8规范
                    result = re.sub(r'\s+', ' ', result)
                    result = re.sub(r'\s*\(\s*', '(', result)
                    result = re.sub(r'\s*\)\s*', ')', result)
                    result = re.sub(r'\s*,\s*', ', ', result)
                    
                    # 修复Python类型注解格式：确保冒号后有空格 (修复关键问题1)
                    # 处理参数类型注解：param: type
                    result = re.sub(r':\s*([^,):\s]+)', r': \1', result)
                    # 处理返回类型注解：) -> type:
                    result = re.sub(r'\)\s*->\s*([^:]+)\s*:', r') -> \1:', result)
                    
                    return result.strip()
            
            # 如果没有找到有效签名，返回第一行
            fallback = lines[start_line].strip() if start_line < len(lines) else "def unknown():"
            return fallback
            
        except Exception as e:
            logger.error(f"提取Python函数签名时发生错误: {e}")
            return "def unknown():"
    
    def extract_method_signature(self, node, lines: List[str]) -> str:
        """提取Python方法签名"""
        # 对于Python，方法签名和函数签名的提取逻辑相同
        return self.extract_function_signature(node, lines)
    
    def extract_field_info(self, node, lines: List[str]) -> Dict[str, Any]:
        """
        提取Python字段信息
        
        Args:
            node: AST节点
            lines: 源代码行列表
            
        Returns:
            字段信息字典，包含name, type, modifiers, is_static, comment, declaration
        """
        try:
            field_info = self.create_field_info_template()
            
            start_line = node.start_point[0]
            if start_line < len(lines):
                line = lines[start_line].strip()
                field_info['declaration'] = line
                
                # 解析Python字段声明
                # 支持多种格式：
                # 1. name: type = value
                # 2. name = value
                # 3. name: type
                
                # 移除注释部分
                if '#' in line:
                    line_parts = line.split('#', 1)
                    line = line_parts[0].strip()
                    field_info['comment'] = line_parts[1].strip()
                
                # 检查是否是类变量（在类级别定义）
                if line.strip() and not line.startswith('def ') and not line.startswith('@'):
                    # 解析赋值语句
                    if '=' in line:
                        left_part, right_part = line.split('=', 1)
                        left_part = left_part.strip()
                        
                        # 检查类型注解
                        if ':' in left_part:
                            name_part, type_part = left_part.split(':', 1)
                            field_info['name'] = name_part.strip()
                            field_info['type'] = type_part.strip()
                        else:
                            field_info['name'] = left_part.strip()
                            # 尝试从值推断类型
                            right_part = right_part.strip()
                            if right_part.startswith('"') or right_part.startswith("'"):
                                field_info['type'] = 'str'
                            elif right_part.isdigit():
                                field_info['type'] = 'int'
                            elif right_part in ['True', 'False']:
                                field_info['type'] = 'bool'
                            elif right_part.startswith('['):
                                field_info['type'] = 'list'
                            elif right_part.startswith('{'):
                                field_info['type'] = 'dict'
                            else:
                                field_info['type'] = 'Any'
                    
                    elif ':' in line and '=' not in line:
                        # 只有类型注解，没有赋值
                        name_part, type_part = line.split(':', 1)
                        field_info['name'] = name_part.strip()
                        field_info['type'] = type_part.strip()
                    
                    else:
                        # 简单赋值，没有类型注解
                        field_info['name'] = line.split('=')[0].strip() if '=' in line else line.strip()
                        field_info['type'] = 'Any'
                
                # Python没有真正的静态字段概念，类变量不是静态字段
                field_info['is_static'] = False
                field_info['modifiers'] = ['class_variable']
                
                # 提取前一行的注释
                if start_line > 0:
                    prev_line = lines[start_line - 1].strip()
                    if prev_line.startswith('#'):
                        field_info['comment'] = prev_line[1:].strip()
            
            return field_info
            
        except Exception as e:
            logger.error(f"提取Python字段信息时发生错误: {e}")
            return self.create_field_info_template()
    
    def extract_docstring(self, node, lines: List[str]) -> str:
        """提取Python文档字符串"""
        try:
            # 查找函数体中的第一个字符串字面量
            for child in node.children:
                if child.type == 'block':
                    for stmt in child.children:
                        if stmt.type == 'expression_statement':
                            for expr_child in stmt.children:
                                if expr_child.type == 'string':
                                    docstring = expr_child.text.decode('utf-8')
                                    # 清理文档字符串
                                    docstring = docstring.strip('"""').strip("'''").strip('"').strip("'")
                                    return docstring.strip()
            return ""
        except:
            return ""
    
    def _extract_imports(self, root_node, lines: List[str], skeleton_lines: List[str]):
        """提取导入语句"""
        import_captures = self.execute_query("(import_statement) @import", root_node)
        import_from_captures = self.execute_query("(import_from_statement) @import_from", root_node)
        
        # 合并所有导入节点
        all_import_nodes = []
        for nodes in import_captures.values():
            all_import_nodes.extend(nodes)
        for nodes in import_from_captures.values():
            all_import_nodes.extend(nodes)
            
        if all_import_nodes:
            skeleton_lines.append("# 导入语句")
            for node in all_import_nodes[:10]:  # 只显示前10个导入
                import_line = lines[node.start_point[0]]
                skeleton_lines.append(import_line)
            if len(all_import_nodes) > 10:
                skeleton_lines.append(f"# ... 还有 {len(all_import_nodes) - 10} 个导入语句")
            skeleton_lines.append("")
    
    def _extract_classes(self, root_node, lines: List[str], skeleton_lines: List[str]) -> List:
        """提取类定义"""
        class_captures = self.execute_query("(class_definition) @class", root_node)
        
        # 获取所有类节点
        class_nodes = []
        for nodes in class_captures.values():
            class_nodes.extend(nodes)
            
        for node in class_nodes:
            # 提取类名
            class_name = self.extract_class_name(node, lines)
            skeleton_lines.append(f"class {class_name}:")
            
            # 提取类的文档字符串
            class_docstring = self.extract_docstring(node, lines)
            if class_docstring:
                skeleton_lines.extend([f'    """{class_docstring}"""', ""])
            
            # 提取类变量/字段
            self._extract_fields(node, lines, skeleton_lines)
            
            # 提取类中的方法
            self._extract_methods(node, lines, skeleton_lines)
            skeleton_lines.append("")
        
        return class_nodes
    
    def _extract_methods(self, class_node, lines: List[str], skeleton_lines: List[str]):
        """提取Python方法签名"""
        method_captures = self.execute_query("(function_definition) @method", class_node)
        
        # 获取所有方法节点
        method_nodes = []
        for nodes in method_captures.values():
            method_nodes.extend(nodes)
            
        for node in method_nodes:
            method_signature = self.extract_method_signature(node, lines)
            skeleton_lines.append(f"    {method_signature}")
            
            # 提取方法文档字符串
            method_docstring = self.extract_docstring(node, lines)
            if method_docstring:
                skeleton_lines.extend([f'        """{method_docstring}"""', ""])
            else:
                skeleton_lines.append("    pass")
                skeleton_lines.append("")
    
    def _extract_fields(self, class_node, lines: List[str], skeleton_lines: List[str]):
        """提取Python类变量和字段"""
        # 查找赋值语句（类变量）
        assignment_captures = self.execute_query("(assignment) @assignment", class_node)
        
        assignment_nodes = []
        for nodes in assignment_captures.values():
            assignment_nodes.extend(nodes)
        
        # 过滤出类级别的赋值（不在方法内的）
        class_level_assignments = []
        method_captures = self.execute_query("(function_definition) @method", class_node)
        method_nodes = []
        for nodes in method_captures.values():
            method_nodes.extend(nodes)
        
        for assignment_node in assignment_nodes:
            # 检查赋值是否在方法内
            is_in_method = False
            for method_node in method_nodes:
                if (method_node.start_point[0] <= assignment_node.start_point[0] <= method_node.end_point[0]):
                    is_in_method = True
                    break
            
            if not is_in_method:
                class_level_assignments.append(assignment_node)
        
        if class_level_assignments:
            skeleton_lines.append("    # 类变量")
            for node in class_level_assignments:
                field_info = self.extract_field_info(node, lines)
                if field_info['comment']:
                    skeleton_lines.append(f"    # {field_info['comment']}")
                skeleton_lines.append(f"    {field_info['declaration']}")
            skeleton_lines.append("")
    
    def _extract_top_level_functions(self, root_node, lines: List[str], skeleton_lines: List[str], class_nodes: List):
        """提取顶级函数"""
        function_captures = self.execute_query("(function_definition) @func", root_node)
        
        function_nodes = []
        for nodes in function_captures.values():
            function_nodes.extend(nodes)
            
        for node in function_nodes:
            # 检查是否是类中的方法（跳过）
            if self.is_method_in_class(node, class_nodes):
                continue
                
            func_signature = self.extract_function_signature(node, lines)
            skeleton_lines.append(func_signature)
            
            # 提取函数文档字符串
            func_docstring = self.extract_docstring(node, lines)
            if func_docstring:
                skeleton_lines.extend([f'    """{func_docstring}"""', ""])
            else:
                skeleton_lines.append("    pass")
                skeleton_lines.append("")