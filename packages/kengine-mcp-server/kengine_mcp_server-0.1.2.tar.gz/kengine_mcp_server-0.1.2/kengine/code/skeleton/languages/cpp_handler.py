"""
C/C++语言代码骨架处理器
重构版本：添加字段提取功能
"""

import logging
from typing import List, Dict, Any
from .base_language import BaseLanguageHandler

logger = logging.getLogger(__name__)


class CppHandler(BaseLanguageHandler):
    """C/C++语言代码骨架处理器"""
    
    def __init__(self, lang_lib, lang_name=None):
        super().__init__(lang_lib)
        self.lang_name = lang_name or 'cpp'  # 'c' 或 'cpp'
    
    def generate_skeleton(self, tree, code_content: str) -> str:
        """生成C/C++代码骨架"""
        lines = code_content.split('\n')
        skeleton_lines = []
        
        # 提取包含语句
        self._extract_includes(tree.root_node, lines, skeleton_lines)
        
        # 提取模板函数（仅C++）
        if self.lang_name == 'cpp':
            self._extract_templates(tree.root_node, lines, skeleton_lines)
        
        # 提取函数声明和定义
        self._extract_functions(tree.root_node, lines, skeleton_lines)
        
        # 对于C++，还要提取类
        if self.lang_name == 'cpp':
            self._extract_classes(tree.root_node, lines, skeleton_lines)
        
        return '\n'.join(skeleton_lines)
    
    def extract_class_name(self, node, lines: List[str]) -> str:
        """提取C++类名"""
        try:
            # C++ AST: class_specifier -> type_identifier
            for child in node.children:
                if child.type == 'type_identifier':
                    return child.text.decode('utf-8')
                elif child.type == 'identifier':
                    return child.text.decode('utf-8')
            return "UnknownClass"
        except Exception as e:
            logger.error(f"提取C++类名时发生错误: {e}")
            return "UnknownClass"
    
    def extract_function_signature(self, node, lines: List[str]) -> str:
        """提取C++函数签名"""
        try:
            start_line = node.start_point[0]
            line = lines[start_line]
            brace_pos = line.find('{')
            if brace_pos != -1:
                return line[:brace_pos].strip() + " { ... }"
            return line.strip() + " { ... }"
        except:
            return "unknown() { ... }"
    
    def extract_method_signature(self, node, lines: List[str]) -> str:
        """提取C++方法签名"""
        return self.extract_function_signature(node, lines)
    
    def extract_field_info(self, node, lines: List[str]) -> Dict[str, Any]:
        """
        提取C++字段信息
        
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
                
                # 解析C++字段声明
                # 格式: [access_specifier] [static] [const] type fieldName [= value];
                
                # 提取注释
                if '//' in line:
                    line_parts = line.split('//', 1)
                    line = line_parts[0].strip()
                    field_info['comment'] = line_parts[1].strip()
                elif '/*' in line and '*/' in line:
                    comment_start = line.find('/*')
                    comment_end = line.find('*/')
                    field_info['comment'] = line[comment_start+2:comment_end].strip()
                    line = line[:comment_start] + line[comment_end+2:]
                
                # 移除分号
                line = line.rstrip(';')
                
                # 解析修饰符和类型
                parts = line.split()
                modifiers = []
                i = 0
                
                # 检查修饰符
                while i < len(parts) and parts[i] in ['static', 'const', 'mutable', 'volatile', 'extern']:
                    modifiers.append(parts[i])
                    if parts[i] == 'static':
                        field_info['is_static'] = True
                    i += 1
                
                # 获取类型和字段名
                if i < len(parts):
                    # 处理复杂类型（如模板类型）
                    type_parts = []
                    field_name = 'unknown'
                    
                    # 查找等号位置（如果有初始化）
                    remaining_parts = parts[i:]
                    equals_index = -1
                    for j, part in enumerate(remaining_parts):
                        if '=' in part:
                            equals_index = j
                            break
                    
                    if equals_index > 0:
                        # 有初始化值
                        type_and_name_parts = remaining_parts[:equals_index]
                        if len(type_and_name_parts) >= 2:
                            type_parts = type_and_name_parts[:-1]
                            field_name = type_and_name_parts[-1]
                        elif len(type_and_name_parts) == 1:
                            # 可能是 auto 类型推导
                            if type_and_name_parts[0] == 'auto':
                                type_parts = ['auto']
                                field_name = remaining_parts[equals_index].split('=')[0]
                            else:
                                field_name = type_and_name_parts[0]
                                type_parts = ['auto']
                    else:
                        # 没有初始化值
                        if len(remaining_parts) >= 2:
                            type_parts = remaining_parts[:-1]
                            field_name = remaining_parts[-1].split('=')[0] if '=' in remaining_parts[-1] else remaining_parts[-1]
                        elif len(remaining_parts) == 1:
                            field_name = remaining_parts[0].split('=')[0] if '=' in remaining_parts[0] else remaining_parts[0]
                    
                    field_info['type'] = ' '.join(type_parts) if type_parts else 'unknown'
                    field_info['name'] = field_name
                
                field_info['modifiers'] = modifiers
                
                # 提取前一行的注释（仅当没有行内注释时）
                if not field_info['comment'] and start_line > 0:
                    prev_line = lines[start_line - 1].strip()
                    if prev_line.startswith('//'):
                        field_info['comment'] = prev_line[2:].strip()
                    elif prev_line.startswith('/*') and prev_line.endswith('*/'):
                        field_info['comment'] = prev_line[2:-2].strip()
            
            return field_info
            
        except Exception as e:
            logger.error(f"提取C++字段信息时发生错误: {e}")
            return self.create_field_info_template()
    
    def _extract_includes(self, root_node, lines: List[str], skeleton_lines: List[str]):
        """提取包含语句"""
        include_captures = self.execute_query("(preproc_include) @include", root_node)
        
        include_nodes = []
        for nodes in include_captures.values():
            include_nodes.extend(nodes)
            
        if include_nodes:
            skeleton_lines.append("// 包含语句")
            for node in include_nodes[:10]:
                include_line = lines[node.start_point[0]]
                skeleton_lines.append(include_line)
            if len(include_nodes) > 10:
                skeleton_lines.append(f"// ... 还有 {len(include_nodes) - 10} 个包含语句")
            skeleton_lines.append("")
    
    def _extract_templates(self, root_node, lines: List[str], skeleton_lines: List[str]):
        """提取模板函数（C++）"""
        template_captures = self.execute_query("(template_declaration) @template", root_node)
        template_nodes = []
        for nodes in template_captures.values():
            template_nodes.extend(nodes)
            
        for node in template_nodes:
            template_signature = self._extract_cpp_template_signature(node, lines)
            skeleton_lines.append(template_signature)
            skeleton_lines.append("")
    
    def _extract_cpp_template_signature(self, node, lines: List[str]) -> str:
        """提取C++模板签名"""
        start_line = node.start_point[0]
        end_line = node.end_point[0]
        
        # 提取模板声明
        template_lines = []
        for i in range(start_line, min(end_line + 1, len(lines))):
            line = lines[i].strip()
            if line:
                if '{' in line:
                    brace_pos = line.find('{')
                    template_lines.append(line[:brace_pos].strip() + " { ... }")
                    break
                else:
                    template_lines.append(line)
                    
        return '\n'.join(template_lines) if template_lines else ""
    
    def _extract_functions(self, root_node, lines: List[str], skeleton_lines: List[str]):
        """提取函数声明和定义"""
        function_captures = self.execute_query("(function_definition) @func", root_node)
        
        function_nodes = []
        for nodes in function_captures.values():
            function_nodes.extend(nodes)
            
        for node in function_nodes:
            func_signature = self._extract_c_function_signature(node, lines)
            skeleton_lines.append(func_signature)
            skeleton_lines.append("")
    
    def _extract_c_function_signature(self, node, lines: List[str]) -> str:
        """提取C函数签名"""
        try:
            start_line = node.start_point[0]
            line = lines[start_line]
            brace_pos = line.find('{')
            if brace_pos != -1:
                return line[:brace_pos].strip() + " { ... }"
            return line.strip() + " { ... }"
        except:
            return "unknown() { ... }"
    
    def _extract_classes(self, root_node, lines: List[str], skeleton_lines: List[str]):
        """提取类（C++）"""
        class_captures = self.execute_query("(class_specifier) @class", root_node)
        
        class_nodes = []
        for nodes in class_captures.values():
            class_nodes.extend(nodes)
            
        for node in class_nodes:
            class_signature = self._extract_cpp_class_signature(node, lines)
            skeleton_lines.append(class_signature)
            
            # 提取类中的字段
            self._extract_cpp_fields(node, lines, skeleton_lines)
            
            # 提取类中的方法
            self._extract_cpp_methods(node, lines, skeleton_lines)
            skeleton_lines.append("};")
            skeleton_lines.append("")
    
    def _extract_cpp_class_signature(self, node, lines: List[str]) -> str:
        """提取C++类签名"""
        try:
            start_line = node.start_point[0]
            line = lines[start_line]
            brace_pos = line.find('{')
            if brace_pos != -1:
                return line[:brace_pos].strip() + " {"
            return line.strip() + " {"
        except:
            return "class UnknownClass {"
    
    def _extract_cpp_fields(self, class_node, lines: List[str], skeleton_lines: List[str]):
        """提取C++类中的字段"""
        # 查询字段声明
        field_queries = [
            "(field_declaration) @field",
            "(declaration) @field"
        ]
        
        field_nodes = []
        processed_positions = set()
        
        for query in field_queries:
            field_captures = self.execute_query(query, class_node)
            for nodes in field_captures.values():
                for node in nodes:
                    pos_key = (node.start_point[0], node.start_point[1])
                    if pos_key not in processed_positions:
                        # 检查是否是字段声明（不是方法声明）
                        start_line = node.start_point[0]
                        if start_line < len(lines):
                            line = lines[start_line].strip()
                            # 排除方法声明和访问修饰符
                            if (not line.endswith(':') and 
                                '(' not in line and 
                                not line.startswith('//') and
                                not line.startswith('/*') and
                                line.endswith(';')):
                                field_nodes.append(node)
                                processed_positions.add(pos_key)
        
        if field_nodes:
            skeleton_lines.append("    // 成员变量")
            for node in field_nodes:
                field_info = self.extract_field_info(node, lines)
                if field_info['comment']:
                    skeleton_lines.append(f"    // {field_info['comment']}")
                skeleton_lines.append(f"    {field_info['declaration']}")
            skeleton_lines.append("")
    
    def _extract_cpp_methods(self, class_node, lines: List[str], skeleton_lines: List[str]):
        """提取C++类中的方法"""
        # 提取构造函数
        constructor_captures = self.execute_query("(function_definition) @constructor", class_node)
        
        constructor_nodes = []
        for nodes in constructor_captures.values():
            constructor_nodes.extend(nodes)
            
        # 提取方法声明
        method_captures = self.execute_query("(function_declarator) @method", class_node)
        
        method_nodes = []
        for nodes in method_captures.values():
            method_nodes.extend(nodes)
        
        # 处理所有找到的方法
        all_methods = constructor_nodes + method_nodes
        processed_lines = set()
        
        for node in all_methods:
            start_line = node.start_point[0]
            if start_line in processed_lines:
                continue
            processed_lines.add(start_line)
            
            method_signature = self._extract_cpp_method_signature(node, lines)
            if method_signature and method_signature.strip():
                skeleton_lines.append(f"    {method_signature}")
                skeleton_lines.append("")
    
    def _extract_cpp_method_signature(self, node, lines: List[str]) -> str:
        """提取C++方法签名"""
        start_line = node.start_point[0]
        end_line = node.end_point[0]
        
        # 查找方法签名（到分号或左大括号为止）
        for i in range(start_line, min(end_line + 1, len(lines))):
            line = lines[i].strip()
            if not line:
                continue
                
            # 跳过访问修饰符行
            if line in ['public:', 'private:', 'protected:']:
                continue
                
            if '{' in line:
                brace_pos = line.find('{')
                signature = line[:brace_pos].strip()
                if signature:
                    return signature + " { ... }"
            elif ';' in line:
                return line.rstrip(';') + ";"
            elif i == end_line:
                return line + " { ... }"
        
        return lines[start_line].strip() + " { ... }" if start_line < len(lines) else ""