"""
C#语言代码骨架处理器
重构版本：修复关键错误并添加字段提取功能和结构体支持
"""

import logging
from typing import List, Dict, Any, Optional
from .base_language import BaseLanguageHandler

logger = logging.getLogger(__name__)


class CSharpHandler(BaseLanguageHandler):
    """C#语言代码骨架处理器"""
    
    def generate_skeleton(self, tree, code_content: str) -> str:
        """生成C#代码骨架"""
        lines = code_content.split('\n')
        skeleton_lines = []
        
        # 提取using语句
        self._extract_usings(tree.root_node, lines, skeleton_lines)
        
        # 提取命名空间
        self._extract_namespaces(tree.root_node, lines, skeleton_lines)
        
        return '\n'.join(skeleton_lines)
    
    def extract_class_name(self, node, lines: List[str]) -> str:
        """提取C#类名"""
        try:
            # C# AST可能包含修饰符，需要跳过它们找到类名
            # 结构: class_declaration -> [modifiers] -> identifier
            for child in node.children:
                if child.type == 'identifier':
                    return child.text.decode('utf-8')
                elif child.type == 'type_identifier':
                    return child.text.decode('utf-8')
            return "UnknownClass"
        except Exception as e:
            logger.error(f"提取C#类名时发生错误: {e}")
            return "UnknownClass"
    
    def extract_function_signature(self, node, lines: List[str]) -> str:
        """提取C#方法签名"""
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
        """提取C#方法签名"""
        return self.extract_function_signature(node, lines)
    
    def extract_field_info(self, node, lines: List[str]) -> Dict[str, Any]:
        """
        提取C#字段信息
        
        Args:
            node: AST节点
            lines: 源代码行列表
            
        Returns:
            字段信息字典，包含name, type, modifiers, is_static, comment, declaration
        """
        try:
            field_info = {
                'name': 'unknown',
                'type': 'unknown',
                'modifiers': [],
                'is_static': False,
                'comment': '',
                'declaration': ''
            }
            
            start_line = node.start_point[0]
            if start_line < len(lines):
                line = lines[start_line].strip()
                field_info['declaration'] = line
                
                # 解析C#字段声明
                # 格式: [modifiers] type fieldName [= value];
                line_without_semicolon = line.replace(';', '')
                
                # 提取修饰符和类型
                modifiers = []
                type_name = 'unknown'
                field_name = 'unknown'
                
                # 使用更智能的解析方式处理泛型类型
                parts = line_without_semicolon.split()
                i = 0
                
                # 跳过修饰符
                while i < len(parts) and parts[i] in ['public', 'private', 'protected', 'internal', 'static', 'readonly', 'const', 'volatile']:
                    modifiers.append(parts[i])
                    if parts[i] == 'static':
                        field_info['is_static'] = True
                    i += 1
                
                # 获取类型（处理泛型类型）
                if i < len(parts):
                    type_start = i
                    # 如果类型包含 '<'，需要找到匹配的 '>'
                    if '<' in parts[i]:
                        bracket_count = 0
                        type_parts = []
                        while i < len(parts):
                            part = parts[i]
                            type_parts.append(part)
                            bracket_count += part.count('<') - part.count('>')
                            i += 1
                            if bracket_count == 0:
                                break
                        # 重新组合泛型类型，保持正确的空格
                        type_name = ' '.join(type_parts)
                        # 移除多余的空格，但保持泛型参数间的逗号后空格
                        import re
                        type_name = re.sub(r'<\s+', '<', type_name)
                        type_name = re.sub(r'\s+>', '>', type_name)
                        type_name = re.sub(r',\s*', ', ', type_name)
                    else:
                        type_name = parts[i]
                        i += 1
                
                # 获取字段名
                if i < len(parts):
                    field_name = parts[i].split('=')[0].strip()
                
                field_info['modifiers'] = modifiers
                field_info['type'] = type_name
                field_info['name'] = field_name
                
                # 提取注释（查找前一行的注释）
                if start_line > 0:
                    prev_line = lines[start_line - 1].strip()
                    if prev_line.startswith('//'):
                        field_info['comment'] = prev_line[2:].strip()
            
            return field_info
            
        except Exception as e:
            logger.error(f"提取C#字段信息时发生错误: {e}")
            return {
                'name': 'unknown',
                'type': 'unknown', 
                'modifiers': [],
                'is_static': False,
                'comment': '',
                'declaration': ''
            }
    
    def _extract_usings(self, root_node, lines: List[str], skeleton_lines: List[str]):
        """提取using语句"""
        using_captures = self.execute_query("(using_directive) @using", root_node)
        
        using_nodes = []
        for nodes in using_captures.values():
            using_nodes.extend(nodes)
            
        if using_nodes:
            skeleton_lines.append("// Using语句")
            for node in using_nodes[:10]:
                using_line = lines[node.start_point[0]]
                skeleton_lines.append(using_line)
            if len(using_nodes) > 10:
                skeleton_lines.append(f"// ... 还有 {len(using_nodes) - 10} 个using语句")
            skeleton_lines.append("")
    
    def _extract_namespaces(self, root_node, lines: List[str], skeleton_lines: List[str]):
        """提取命名空间"""
        # 修复：使用self.execute_query而不是execute_query
        namespace_captures = self.execute_query("(namespace_declaration) @namespace", root_node)
        
        namespace_nodes = []
        for nodes in namespace_captures.values():
            namespace_nodes.extend(nodes)
            
        for namespace_node in namespace_nodes:
            namespace_signature = self._extract_csharp_namespace_signature(namespace_node, lines)
            skeleton_lines.append(namespace_signature)
            skeleton_lines.append("")
            
            # 提取命名空间中的所有类型
            self._extract_interfaces(namespace_node, lines, skeleton_lines)
            self._extract_enums(namespace_node, lines, skeleton_lines)
            self._extract_structs(namespace_node, lines, skeleton_lines)
            self._extract_classes(namespace_node, lines, skeleton_lines)
            
            skeleton_lines.append("}")
            skeleton_lines.append("")
    
    def _extract_csharp_namespace_signature(self, node, lines: List[str]) -> str:
        """提取C#命名空间签名"""
        try:
            start_line = node.start_point[0]
            line = lines[start_line]
            brace_pos = line.find('{')
            return line[:brace_pos].strip() + " {" if brace_pos != -1 else line.strip() + " {"
        except:
            return "namespace Unknown {"
    
    def _extract_structs(self, namespace_node, lines: List[str], skeleton_lines: List[str]):
        """提取结构体定义"""
        struct_captures = self.execute_query("(struct_declaration) @struct", namespace_node)
        
        struct_nodes = []
        for nodes in struct_captures.values():
            struct_nodes.extend(nodes)
            
        for struct_node in struct_nodes:
            struct_signature = self._extract_csharp_struct_signature(struct_node, lines)
            skeleton_lines.append(f"    {struct_signature}")
            skeleton_lines.append("")
            
            # 提取结构体内部接口
            self._extract_inner_interfaces(struct_node, lines, skeleton_lines)
            
            # 提取结构体内部枚举
            self._extract_inner_enums(struct_node, lines, skeleton_lines)
            
            # 提取结构体内部结构体
            self._extract_inner_structs(struct_node, lines, skeleton_lines)
            
            # 提取结构体字段
            self._extract_fields(struct_node, lines, skeleton_lines)
            
            # 提取结构体属性
            self._extract_properties(struct_node, lines, skeleton_lines)
            
            # 提取结构体方法
            self._extract_methods(struct_node, lines, skeleton_lines)
            skeleton_lines.append("    }")
            skeleton_lines.append("")
    
    def _extract_csharp_struct_signature(self, node, lines: List[str]) -> str:
        """提取C#结构体签名"""
        try:
            start_line = node.start_point[0]
            line = lines[start_line]
            brace_pos = line.find('{')
            return line[:brace_pos].strip() + " {" if brace_pos != -1 else line.strip() + " {"
        except Exception as e:
            logger.error(f"提取C#结构体签名时发生错误: {e}")
            return "struct Unknown {"
    
    def _extract_interfaces(self, namespace_node, lines: List[str], skeleton_lines: List[str]):
        """提取接口定义"""
        interface_captures = self.execute_query("(interface_declaration) @interface", namespace_node)
        
        interface_nodes = []
        for nodes in interface_captures.values():
            interface_nodes.extend(nodes)
            
        for interface_node in interface_nodes:
            interface_signature = self._extract_csharp_interface_signature(interface_node, lines)
            skeleton_lines.append(f"    {interface_signature}")
            skeleton_lines.append("")
            
            # 提取接口方法
            self._extract_interface_methods(interface_node, lines, skeleton_lines)
            skeleton_lines.append("    }")
            skeleton_lines.append("")
    
    def _extract_csharp_interface_signature(self, node, lines: List[str]) -> str:
        """提取C#接口签名"""
        try:
            start_line = node.start_point[0]
            line = lines[start_line]
            brace_pos = line.find('{')
            return line[:brace_pos].strip() + " {" if brace_pos != -1 else line.strip() + " {"
        except:
            return "interface Unknown {"
    
    def _extract_interface_methods(self, interface_node, lines: List[str], skeleton_lines: List[str]):
        """提取接口方法"""
        method_captures = self.execute_query("(method_declaration) @method", interface_node)
        
        method_nodes = []
        for nodes in method_captures.values():
            method_nodes.extend(nodes)
            
        for node in method_nodes:
            method_signature = self._extract_csharp_interface_method_signature(node, lines)
            skeleton_lines.append(f"        {method_signature}")
            skeleton_lines.append("")
    
    def _extract_csharp_interface_method_signature(self, node, lines: List[str]) -> str:
        """提取C#接口方法签名"""
        try:
            start_line = node.start_point[0]
            line = lines[start_line].strip()
            # 接口方法通常以分号结尾
            if line.endswith(';'):
                return line
            else:
                return line + ";"
        except:
            return "unknown();"
    
    def _extract_enums(self, namespace_node, lines: List[str], skeleton_lines: List[str]):
        """提取枚举定义"""
        enum_captures = self.execute_query("(enum_declaration) @enum", namespace_node)
        
        enum_nodes = []
        for nodes in enum_captures.values():
            enum_nodes.extend(nodes)
            
        for enum_node in enum_nodes:
            enum_signature = self._extract_csharp_enum_signature(enum_node, lines)
            skeleton_lines.append(f"    {enum_signature}")
            skeleton_lines.append("")
            
            # 提取枚举值
            self._extract_enum_values(enum_node, lines, skeleton_lines)
            skeleton_lines.append("    }")
            skeleton_lines.append("")
    
    def _extract_csharp_enum_signature(self, node, lines: List[str]) -> str:
        """提取C#枚举签名"""
        try:
            start_line = node.start_point[0]
            end_line = node.end_point[0]
            
            # 收集所有相关行（特性和枚举声明）
            signature_parts = []
            enum_declaration_found = False
            
            for line_idx in range(start_line, min(end_line + 1, len(lines))):
                line = lines[line_idx].strip()
                if not line:
                    continue
                    
                # 检查是否是特性行
                if line.startswith('[') and line.endswith(']'):
                    signature_parts.append(line)
                # 检查是否是枚举声明行
                elif 'enum' in line and not enum_declaration_found:
                    brace_pos = line.find('{')
                    if brace_pos != -1:
                        signature_parts.append(line[:brace_pos].strip())
                        enum_declaration_found = True
                        break
                    else:
                        signature_parts.append(line)
                        enum_declaration_found = True
                        break
            
            # 组合签名
            if signature_parts:
                result = ' '.join(signature_parts) + " {"
                return result
            else:
                return "enum Unknown {"
                
        except Exception as e:
            logger.error(f"提取C#枚举签名时发生错误: {e}")
            return "enum Unknown {"
    
    def _extract_enum_values(self, enum_node, lines: List[str], skeleton_lines: List[str]):
        """提取枚举值"""
        enum_member_captures = self.execute_query("(enum_member_declaration) @member", enum_node)
        
        member_nodes = []
        for nodes in enum_member_captures.values():
            member_nodes.extend(nodes)
            
        if member_nodes:
            skeleton_lines.append("        // 枚举值")
            for node in member_nodes:
                member_line = lines[node.start_point[0]].strip()
                skeleton_lines.append(f"        {member_line}")
            skeleton_lines.append("")
    
    def _extract_classes(self, namespace_node, lines: List[str], skeleton_lines: List[str]):
        """提取类定义"""
        # 修复：使用self.execute_query而不是execute_query
        class_captures = self.execute_query("(class_declaration) @class", namespace_node)
        
        class_nodes = []
        for nodes in class_captures.values():
            class_nodes.extend(nodes)
            
        for class_node in class_nodes:
            class_signature = self._extract_csharp_class_signature(class_node, lines)
            skeleton_lines.append(f"    {class_signature}")
            skeleton_lines.append("")
            
            # 提取内部接口
            self._extract_inner_interfaces(class_node, lines, skeleton_lines)
            
            # 提取内部枚举
            self._extract_inner_enums(class_node, lines, skeleton_lines)
            
            # 提取内部结构体
            self._extract_inner_structs(class_node, lines, skeleton_lines)
            
            # 提取字段
            self._extract_fields(class_node, lines, skeleton_lines)
            
            # 提取属性
            self._extract_properties(class_node, lines, skeleton_lines)
            
            # 提取方法
            self._extract_methods(class_node, lines, skeleton_lines)
            skeleton_lines.append("    }")
            skeleton_lines.append("")
    
    def _extract_csharp_class_signature(self, node, lines: List[str]) -> str:
        """提取C#类签名"""
        try:
            start_line = node.start_point[0]
            line = lines[start_line]
            brace_pos = line.find('{')
            return line[:brace_pos].strip() + " {" if brace_pos != -1 else line.strip() + " {"
        except:
            return "class Unknown {"
    
    def _extract_inner_interfaces(self, parent_node, lines: List[str], skeleton_lines: List[str]):
        """提取内部接口"""
        interface_captures = self.execute_query("(interface_declaration) @interface", parent_node)
        
        interface_nodes = []
        for nodes in interface_captures.values():
            interface_nodes.extend(nodes)
            
        for interface_node in interface_nodes:
            interface_signature = self._extract_csharp_interface_signature(interface_node, lines)
            skeleton_lines.append(f"        {interface_signature}")
            skeleton_lines.append("")
            
            # 提取接口方法
            self._extract_inner_interface_methods(interface_node, lines, skeleton_lines)
            skeleton_lines.append("        }")
            skeleton_lines.append("")
    
    def _extract_inner_interface_methods(self, interface_node, lines: List[str], skeleton_lines: List[str]):
        """提取内部接口方法"""
        method_captures = self.execute_query("(method_declaration) @method", interface_node)
        
        method_nodes = []
        for nodes in method_captures.values():
            method_nodes.extend(nodes)
            
        for node in method_nodes:
            method_signature = self._extract_csharp_interface_method_signature(node, lines)
            skeleton_lines.append(f"            {method_signature}")
            skeleton_lines.append("")
    
    def _extract_inner_enums(self, parent_node, lines: List[str], skeleton_lines: List[str]):
        """提取内部枚举"""
        enum_captures = self.execute_query("(enum_declaration) @enum", parent_node)
        
        enum_nodes = []
        for nodes in enum_captures.values():
            enum_nodes.extend(nodes)
            
        for enum_node in enum_nodes:
            enum_signature = self._extract_csharp_enum_signature(enum_node, lines)
            skeleton_lines.append(f"        {enum_signature}")
            skeleton_lines.append("")
            
            # 提取枚举值
            self._extract_inner_enum_values(enum_node, lines, skeleton_lines)
            skeleton_lines.append("        }")
            skeleton_lines.append("")
    
    def _extract_inner_enum_values(self, enum_node, lines: List[str], skeleton_lines: List[str]):
        """提取内部枚举值"""
        enum_member_captures = self.execute_query("(enum_member_declaration) @member", enum_node)
        
        member_nodes = []
        for nodes in enum_member_captures.values():
            member_nodes.extend(nodes)
            
        if member_nodes:
            skeleton_lines.append("            // 枚举值")
            for node in member_nodes:
                member_line = lines[node.start_point[0]].strip()
                skeleton_lines.append(f"            {member_line}")
            skeleton_lines.append("")
    
    def _extract_inner_structs(self, parent_node, lines: List[str], skeleton_lines: List[str]):
        """提取内部结构体"""
        struct_captures = self.execute_query("(struct_declaration) @struct", parent_node)
        
        struct_nodes = []
        for nodes in struct_captures.values():
            struct_nodes.extend(nodes)
            
        for struct_node in struct_nodes:
            struct_signature = self._extract_csharp_struct_signature(struct_node, lines)
            skeleton_lines.append(f"        {struct_signature}")
            skeleton_lines.append("")
            
            # 提取内部结构体的内容
            self._extract_inner_struct_fields(struct_node, lines, skeleton_lines)
            self._extract_inner_struct_properties(struct_node, lines, skeleton_lines)
            self._extract_inner_struct_methods(struct_node, lines, skeleton_lines)
            skeleton_lines.append("        }")
            skeleton_lines.append("")
    
    def _extract_inner_struct_fields(self, struct_node, lines: List[str], skeleton_lines: List[str]):
        """提取内部结构体字段"""
        field_captures = self.execute_query("(field_declaration) @field", struct_node)
        
        field_nodes = []
        for nodes in field_captures.values():
            field_nodes.extend(nodes)
            
        if field_nodes:
            skeleton_lines.append("            // 字段")
            for node in field_nodes:
                field_info = self.extract_field_info(node, lines)
                if field_info['comment']:
                    skeleton_lines.append(f"            // {field_info['comment']}")
                skeleton_lines.append(f"            {field_info['declaration']}")
            skeleton_lines.append("")
    
    def _extract_inner_struct_properties(self, struct_node, lines: List[str], skeleton_lines: List[str]):
        """提取内部结构体属性"""
        property_captures = self.execute_query("(property_declaration) @property", struct_node)
        
        property_nodes = []
        for nodes in property_captures.values():
            property_nodes.extend(nodes)
            
        if property_nodes:
            skeleton_lines.append("            // 属性")
            for node in property_nodes:
                property_signature = self._extract_csharp_property_signature(node, lines)
                skeleton_lines.append(f"            {property_signature}")
            skeleton_lines.append("")
    
    def _extract_inner_struct_methods(self, struct_node, lines: List[str], skeleton_lines: List[str]):
        """提取内部结构体方法"""
        method_captures = self.execute_query("(method_declaration) @method", struct_node)
        
        method_nodes = []
        for nodes in method_captures.values():
            method_nodes.extend(nodes)
            
        for node in method_nodes:
            method_signature = self._extract_csharp_method_signature(node, lines)
            skeleton_lines.append(f"            {method_signature}")
            skeleton_lines.append("")
    
    def _extract_fields(self, class_node, lines: List[str], skeleton_lines: List[str]):
        """提取C#字段"""
        # 查询字段声明
        field_captures = self.execute_query("(field_declaration) @field", class_node)
        
        field_nodes = []
        for nodes in field_captures.values():
            field_nodes.extend(nodes)
            
        if field_nodes:
            skeleton_lines.append("        // 字段")
            for node in field_nodes:
                field_info = self.extract_field_info(node, lines)
                if field_info['comment']:
                    skeleton_lines.append(f"        // {field_info['comment']}")
                skeleton_lines.append(f"        {field_info['declaration']}")
            skeleton_lines.append("")
    
    def _extract_properties(self, parent_node, lines: List[str], skeleton_lines: List[str]):
        """提取C#属性"""
        property_captures = self.execute_query("(property_declaration) @property", parent_node)
        
        property_nodes = []
        for nodes in property_captures.values():
            property_nodes.extend(nodes)
            
        if property_nodes:
            skeleton_lines.append("        // 属性")
            for node in property_nodes:
                property_signature = self._extract_csharp_property_signature(node, lines)
                skeleton_lines.append(f"        {property_signature}")
            skeleton_lines.append("")
    
    def _extract_csharp_property_signature(self, node, lines: List[str]) -> str:
        """提取C#属性签名"""
        try:
            start_line = node.start_point[0]
            line = lines[start_line].strip()
            # 属性通常包含 { get; set; } 或类似结构
            return line
        except:
            return "unknown Property { get; set; }"
    
    def _extract_methods(self, class_node, lines: List[str], skeleton_lines: List[str]):
        """提取C#方法"""
        # 修复：使用self.execute_query而不是execute_query
        method_captures = self.execute_query("(method_declaration) @method", class_node)
        
        method_nodes = []
        for nodes in method_captures.values():
            method_nodes.extend(nodes)
            
        for node in method_nodes:
            method_signature = self._extract_csharp_method_signature(node, lines)
            skeleton_lines.append(f"        {method_signature}")
            skeleton_lines.append("")
    
    def _extract_csharp_method_signature(self, node, lines: List[str]) -> str:
        """提取C#方法签名"""
        try:
            start_line = node.start_point[0]
            line = lines[start_line]
            brace_pos = line.find('{')
            return line[:brace_pos].strip() + " { ... }" if brace_pos != -1 else line.strip() + " { ... }"
        except:
            return "unknown() { ... }"