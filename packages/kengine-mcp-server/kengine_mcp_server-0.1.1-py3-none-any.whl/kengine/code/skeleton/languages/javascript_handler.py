"""
JavaScript/TypeScript语言代码骨架处理器
重构版本：添加字段提取功能
"""

import logging
from typing import List, Dict, Any
from .base_language import BaseLanguageHandler

logger = logging.getLogger(__name__)


class JavaScriptHandler(BaseLanguageHandler):
    """JavaScript/TypeScript代码骨架处理器"""
    
    def generate_skeleton(self, tree, code_content: str) -> str:
        """生成JavaScript/TypeScript代码骨架"""
        lines = code_content.split('\n')
        skeleton_lines = []
        
        # 提取导入语句
        self._extract_imports(tree.root_node, lines, skeleton_lines)
        
        # 提取导出语句 (修复关键问题3)
        self._extract_exports(tree.root_node, lines, skeleton_lines)
        
        # 提取接口 (修复关键问题1)
        self._extract_interfaces(tree.root_node, lines, skeleton_lines)
        
        # 提取枚举 (修复关键问题2)
        self._extract_enums(tree.root_node, lines, skeleton_lines)
        
        # 提取类
        self._extract_classes(tree.root_node, lines, skeleton_lines)
        
        # 提取函数
        self._extract_functions(tree.root_node, lines, skeleton_lines)
        
        return '\n'.join(skeleton_lines)
    
    def extract_class_name(self, node, lines: List[str]) -> str:
        """提取JavaScript类名"""
        try:
            # JavaScript AST: class_declaration -> identifier
            for child in node.children:
                if child.type == 'identifier':
                    return child.text.decode('utf-8')
            return "UnknownClass"
        except Exception as e:
            logger.error(f"提取JavaScript类名时发生错误: {e}")
            return "UnknownClass"
    
    def extract_function_signature(self, node, lines: List[str]) -> str:
        """提取JavaScript函数签名"""
        return self._extract_js_function_signature(node, lines)
    
    def extract_method_signature(self, node, lines: List[str]) -> str:
        """提取JavaScript方法签名"""
        return self._extract_js_method_signature(node, lines)
    
    def extract_field_info(self, node, lines: List[str]) -> Dict[str, Any]:
        """
        提取JavaScript/TypeScript字段信息
        
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
                
                # 解析JavaScript/TypeScript字段声明
                # 支持多种格式：
                # 1. public name: type = value;
                # 2. private static name = value;
                # 3. @decorator name: type;
                # 4. name = value;
                
                # 提取注释
                if '//' in line:
                    line_parts = line.split('//', 1)
                    line = line_parts[0].strip()
                    field_info['comment'] = line_parts[1].strip()
                
                # 移除分号
                line = line.rstrip(';')
                
                # 提取装饰器
                decorators = []
                if line.strip().startswith('@'):
                    # 处理装饰器
                    parts = line.split()
                    for part in parts:
                        if part.startswith('@'):
                            decorators.append(part)
                        else:
                            line = ' '.join(parts[parts.index(part):])
                            break
                
                # 解析修饰符
                modifiers = []
                parts = line.split()
                i = 0
                
                # 检查访问修饰符和其他修饰符
                while i < len(parts) and parts[i] in ['public', 'private', 'protected', 'static', 'readonly', 'abstract']:
                    modifiers.append(parts[i])
                    if parts[i] == 'static':
                        field_info['is_static'] = True
                    i += 1
                
                # 获取字段名和类型 (修复关键问题4 - 字段名解析错误)
                if i < len(parts):
                    remaining = ' '.join(parts[i:])
                    
                    # 处理类型注解
                    if ':' in remaining and '=' in remaining and '=>' not in remaining:
                        # name: type = value 或 name?: type = value (排除箭头函数类型)
                        name_type_part, value_part = remaining.split('=', 1)
                        if ':' in name_type_part:
                            # 需要正确处理包含冒号的复杂类型（如函数类型）
                            colon_pos = name_type_part.find(':')
                            name_part = name_type_part[:colon_pos]
                            type_part = name_type_part[colon_pos + 1:]
                            # 修复可选字段名称解析 (移除 ? 符号)
                            field_name = name_part.strip().rstrip('?')
                            field_info['name'] = field_name
                            field_info['type'] = type_part.strip()
                            # 如果是可选字段，添加到修饰符中
                            if name_part.strip().endswith('?'):
                                field_info['modifiers'].append('optional')
                        else:
                            field_info['name'] = name_type_part.strip().rstrip('?')
                            field_info['type'] = 'any'
                    elif ':' in remaining:
                        # name: type 或 name?: type
                        # 需要正确处理包含冒号的复杂类型（如函数类型）
                        
                        # 找到字段名后的第一个冒号位置
                        colon_pos = remaining.find(':')
                        name_part = remaining[:colon_pos]
                        type_part = remaining[colon_pos + 1:]
                        
                        # 修复可选字段名称解析 (移除 ? 符号)
                        field_name = name_part.strip().rstrip('?')
                        field_info['name'] = field_name
                        field_info['type'] = type_part.strip()
                        # 如果是可选字段，添加到修饰符中
                        if name_part.strip().endswith('?'):
                            field_info['modifiers'].append('optional')
                    elif '=' in remaining:
                        # name = value
                        name_part, value_part = remaining.split('=', 1)
                        field_info['name'] = name_part.strip().rstrip('?')
                        # 尝试从值推断类型
                        value_part = value_part.strip()
                        if value_part.startswith('"') or value_part.startswith("'") or value_part.startswith('`'):
                            field_info['type'] = 'string'
                        elif value_part.replace('.', '').replace('-', '').isdigit():
                            field_info['type'] = 'number'
                        elif value_part in ['true', 'false']:
                            field_info['type'] = 'boolean'
                        elif value_part.startswith('['):
                            field_info['type'] = 'array'
                        elif value_part.startswith('{'):
                            field_info['type'] = 'object'
                        elif value_part == 'null' or value_part == 'undefined':
                            field_info['type'] = 'any'
                        else:
                            field_info['type'] = 'any'
                    else:
                        # 只有名称
                        field_name = remaining.strip().rstrip('?')
                        field_info['name'] = field_name
                        field_info['type'] = 'any'
                        # 如果是可选字段，添加到修饰符中
                        if remaining.strip().endswith('?'):
                            field_info['modifiers'].append('optional')
                
                # 添加修饰符和装饰器
                field_info['modifiers'] = modifiers + decorators
                
                # 提取前一行的注释
                if start_line > 0:
                    prev_line = lines[start_line - 1].strip()
                    if prev_line.startswith('//'):
                        field_info['comment'] = prev_line[2:].strip()
                    elif prev_line.startswith('/*') and prev_line.endswith('*/'):
                        field_info['comment'] = prev_line[2:-2].strip()
            
            return field_info
            
        except Exception as e:
            logger.error(f"提取JavaScript字段信息时发生错误: {e}")
            return self.create_field_info_template()
    
    def _extract_imports(self, root_node, lines: List[str], skeleton_lines: List[str]):
        """提取导入语句"""
        import_captures = self.execute_query("(import_statement) @import", root_node)
        
        import_nodes = []
        for nodes in import_captures.values():
            import_nodes.extend(nodes)
            
        if import_nodes:
            skeleton_lines.append("// 导入语句")
            for node in import_nodes[:10]:
                import_line = lines[node.start_point[0]]
                skeleton_lines.append(import_line)
            if len(import_nodes) > 10:
                skeleton_lines.append(f"// ... 还有 {len(import_nodes) - 10} 个导入语句")
            skeleton_lines.append("")
    
    def _extract_exports(self, root_node, lines: List[str], skeleton_lines: List[str]):
        """提取导出语句 (修复关键问题3)"""
        export_queries = [
            "(export_statement) @export",
            "(export_statement (function_declaration)) @export_func",
            "(export_statement (class_declaration)) @export_class",
            "(export_statement (variable_declaration)) @export_var"
        ]
        
        export_nodes = []
        processed_positions = set()
        
        for query in export_queries:
            export_captures = self.execute_query(query, root_node)
            for nodes in export_captures.values():
                for node in nodes:
                    pos_key = (node.start_point[0], node.start_point[1])
                    if pos_key not in processed_positions:
                        export_nodes.append(node)
                        processed_positions.add(pos_key)
        
        if export_nodes:
            skeleton_lines.append("// 导出语句")
            for node in export_nodes[:10]:
                export_line = lines[node.start_point[0]]
                # 只显示导出声明，不显示完整实现
                if '{' in export_line:
                    export_line = export_line[:export_line.find('{')] + '{ ... }'
                elif '=>' in export_line:
                    export_line = export_line[:export_line.find('=>')] + '=> { ... }'
                skeleton_lines.append(export_line.strip())
            if len(export_nodes) > 10:
                skeleton_lines.append(f"// ... 还有 {len(export_nodes) - 10} 个导出语句")
            skeleton_lines.append("")
    
    def _extract_classes(self, root_node, lines: List[str], skeleton_lines: List[str]):
        """提取类 - 支持多种类声明模式"""
        class_queries = [
            "(class_declaration) @class",
            "(export_statement (class_declaration)) @export_class"
        ]
        
        all_class_nodes = []
        processed_positions = set()  # 防止重复提取同一个类
        
        for query in class_queries:
            class_captures = self.execute_query(query, root_node)
            for nodes in class_captures.values():
                for node in nodes:
                    # 对于export_statement，需要找到其中的class_declaration
                    if node.type == 'export_statement':
                        for child in node.children:
                            if child.type == 'class_declaration':
                                node = child
                                break
                    
                    # 使用位置信息去重
                    pos_key = (node.start_point[0], node.start_point[1])
                    if pos_key not in processed_positions:
                        all_class_nodes.append(node)
                        processed_positions.add(pos_key)
        
        # 总是尝试手动解析作为补充，以找到可能遗漏的类（如泛型类）
        manual_nodes = self._find_js_classes_manually(root_node, lines)
        for node in manual_nodes:
            pos_key = (node.start_point[0], node.start_point[1])
            if pos_key not in processed_positions:
                all_class_nodes.append(node)
                processed_positions.add(pos_key)
                    
        for node in all_class_nodes:
            class_signature = self._extract_js_class_signature(node, lines)
            if class_signature and class_signature.strip():
                skeleton_lines.append(class_signature)
                skeleton_lines.append("")
                
                # 提取字段
                self._extract_fields(node, lines, skeleton_lines)
                
                # 提取方法
                self._extract_methods(node, lines, skeleton_lines)
                skeleton_lines.append("}")
                skeleton_lines.append("")
    
    def _find_js_classes_manually(self, root_node, lines: List[str]):
        """手动查找JavaScript/TypeScript类声明，处理泛型等复杂情况"""
        class_nodes = []
        
        def traverse_node(node):
            # 检查是否是类声明的关键字
            if hasattr(node, 'type') and hasattr(node, 'text'):
                node_text = node.text.decode('utf-8') if hasattr(node.text, 'decode') else str(node.text)
                
                # 查找包含 'class' 关键字的节点
                if 'class ' in node_text and node.start_point[0] < len(lines):
                    line_text = lines[node.start_point[0]].strip()
                    # 检查是否是类声明行
                    if (line_text.startswith('class ') or
                        line_text.startswith('export class ') or
                        line_text.startswith('abstract class ') or
                        'class ' in line_text):
                        class_nodes.append(node)
                        # 继续遍历子节点，不要提前返回
            
            # 递归遍历子节点
            if hasattr(node, 'children'):
                for child in node.children:
                    traverse_node(child)
        
        traverse_node(root_node)
        return class_nodes
    
    def _extract_js_class_signature(self, node, lines: List[str]) -> str:
        """提取JavaScript类签名 (增强泛型类处理能力)"""
        try:
            start_line = node.start_point[0]
            line = lines[start_line].strip()
            
            # 处理多行类声明（泛型约束可能跨行）
            full_signature = line
            
            # 如果行以逗号结尾或包含未闭合的泛型，检查下一行
            if (line.count('<') > line.count('>') or
                line.endswith(',') or
                'extends' in line and '{' not in line):
                
                current_line = start_line + 1
                while current_line < len(lines) and current_line < start_line + 5:  # 最多检查5行
                    next_line = lines[current_line].strip()
                    full_signature += " " + next_line
                    if '{' in next_line:
                        break
                    current_line += 1
            
            # 提取类声明部分（到第一个大括号）
            brace_pos = full_signature.find('{')
            if brace_pos != -1:
                signature = full_signature[:brace_pos].strip()
            else:
                signature = full_signature.strip()
            
            # 确保以 " {" 结尾
            if not signature.endswith('{'):
                signature += " {"
            
            return signature
            
        except Exception as e:
            logger.error(f"提取类签名失败: {e}")
            return "class UnknownClass {"
    
    def _extract_methods(self, class_node, lines: List[str], skeleton_lines: List[str]):
        """提取JavaScript/TypeScript方法签名"""
        method_captures = self.execute_query("(method_definition) @method", class_node)
        
        method_nodes = []
        for nodes in method_captures.values():
            method_nodes.extend(nodes)
            
        for node in method_nodes:
            method_signature = self.extract_method_signature(node, lines)
            skeleton_lines.append(f"    {method_signature}")
            skeleton_lines.append("")
    
    def _extract_js_method_signature(self, node, lines: List[str]) -> str:
        """提取JavaScript方法签名"""
        try:
            start_line = node.start_point[0]
            line = lines[start_line]
            brace_pos = line.find('{')
            if brace_pos != -1:
                return line[:brace_pos].strip() + " { ... }"
            return line.strip() + " { ... }"
        except:
            return "unknown() { ... }"
    
    def _extract_functions(self, root_node, lines: List[str], skeleton_lines: List[str]):
        """提取函数"""
        function_captures = self.execute_query("(function_declaration) @func", root_node)
        
        function_nodes = []
        for nodes in function_captures.values():
            function_nodes.extend(nodes)
            
        for node in function_nodes:
            func_signature = self.extract_function_signature(node, lines)
            skeleton_lines.append(func_signature)
            skeleton_lines.append("")
    
    def _extract_js_function_signature(self, node, lines: List[str]) -> str:
        """提取JavaScript函数签名"""
        try:
            start_line = node.start_point[0]
            line = lines[start_line]
            brace_pos = line.find('{')
            if brace_pos != -1:
                return line[:brace_pos].strip() + " { ... }"
            return line.strip() + " { ... }"
        except:
            return "function unknown() { ... }"
    
    def _extract_fields(self, class_node, lines: List[str], skeleton_lines: List[str]):
        """提取JavaScript/TypeScript类字段 (修复AST查询中的无效节点类型错误)"""
        # 修正的字段查询 - 使用正确的AST节点类型
        field_queries = [
            "(field_definition) @field",
            "(public_field_definition) @field",
            "(private_field_definition) @field",
            "(property_signature) @field",
            "(class_body (property_identifier)) @field",
            "(method_definition) @method"  # 包含getter/setter
        ]
        
        field_nodes = []
        processed_positions = set()
        
        for query in field_queries:
            try:
                field_captures = self.execute_query(query, class_node)
                for nodes in field_captures.values():
                    for node in nodes:
                        # 过滤掉方法节点，只保留字段
                        if node.type == 'method_definition':
                            # 检查是否是getter/setter
                            start_line = node.start_point[0]
                            if start_line < len(lines):
                                line = lines[start_line].strip()
                                if not (line.startswith('get ') or line.startswith('set ')):
                                    continue  # 跳过普通方法
                        
                        pos_key = (node.start_point[0], node.start_point[1])
                        if pos_key not in processed_positions:
                            field_nodes.append(node)
                            processed_positions.add(pos_key)
            except Exception as e:
                logger.error(f"字段查询失败: {query}, 错误: {e}")
        
        # 如果没有找到字段，尝试手动解析
        if not field_nodes:
            field_nodes = self._find_fields_manually(class_node, lines)
        
        if field_nodes:
            skeleton_lines.append("    // 字段")
            for node in field_nodes:
                field_info = self.extract_field_info(node, lines)
                if field_info['comment']:
                    skeleton_lines.append(f"    // {field_info['comment']}")
                skeleton_lines.append(f"    {field_info['declaration']}")
            skeleton_lines.append("")
    
    def _find_fields_manually(self, class_node, lines: List[str]):
        """手动查找类字段"""
        field_nodes = []
        
        try:
            start_line = class_node.start_point[0]
            end_line = class_node.end_point[0]
            
            # 查找类体内的字段声明
            for line_num in range(start_line + 1, min(end_line, len(lines))):
                line = lines[line_num].strip()
                
                # 跳过注释和空行
                if not line or line.startswith('//') or line.startswith('/*'):
                    continue
                
                # 跳过方法定义（但保留getter/setter）
                if ('(' in line and ')' in line and '{' in line and
                    not line.startswith('get ') and not line.startswith('set ')):
                    continue
                
                # 检查是否是字段声明
                if ((':' in line or '=' in line) and
                    not line.strip().startswith('constructor') and
                    not line.strip().startswith('function')):
                    
                    # 创建模拟节点
                    mock_node = type('MockNode', (), {
                        'start_point': (line_num, 0),
                        'end_point': (line_num, len(line)),
                        'type': 'field_definition'
                    })()
                    field_nodes.append(mock_node)
        except:
            pass
        
        return field_nodes
    
    def _extract_interfaces(self, root_node, lines: List[str], skeleton_lines: List[str]):
        """
        提取TypeScript接口 (修复关键问题1 - 接口提取功能完全缺失)
        支持基础接口、泛型接口、继承接口、函数类型接口等
        """
        interface_queries = [
            "(interface_declaration) @interface",
            "(export_statement (interface_declaration)) @export_interface"
        ]
        
        all_interface_nodes = []
        processed_positions = set()
        
        for query in interface_queries:
            try:
                interface_captures = self.execute_query(query, root_node)
                for nodes in interface_captures.values():
                    for node in nodes:
                        # 对于export_statement，需要找到其中的interface_declaration
                        if node.type == 'export_statement':
                            for child in node.children:
                                if child.type == 'interface_declaration':
                                    node = child
                                    break
                        
                        # 使用位置信息去重
                        pos_key = (node.start_point[0], node.start_point[1])
                        if pos_key not in processed_positions:
                            all_interface_nodes.append(node)
                            processed_positions.add(pos_key)
            except Exception as e:
                logger.error(f"接口查询失败: {query}, 错误: {e}")
        
        # 如果标准查询没有找到接口，尝试手动解析
        if not all_interface_nodes:
            manual_nodes = self._find_interfaces_manually(root_node, lines)
            for node in manual_nodes:
                pos_key = (node.start_point[0], node.start_point[1])
                if pos_key not in processed_positions:
                    all_interface_nodes.append(node)
                    processed_positions.add(pos_key)
        
        if all_interface_nodes:
            skeleton_lines.append("// TypeScript接口")
            for node in all_interface_nodes:
                interface_signature = self._extract_interface_signature(node, lines)
                if interface_signature and interface_signature.strip():
                    skeleton_lines.append(interface_signature)
                    
                    # 提取接口成员
                    self._extract_interface_members(node, lines, skeleton_lines)
                    skeleton_lines.append("}")
                    skeleton_lines.append("")
    
    def _find_interfaces_manually(self, root_node, lines: List[str]):
        """手动查找TypeScript接口声明"""
        interface_nodes = []
        
        def traverse_node(node):
            if hasattr(node, 'type') and hasattr(node, 'text'):
                node_text = node.text.decode('utf-8') if hasattr(node.text, 'decode') else str(node.text)
                
                # 查找包含 'interface' 关键字的节点
                if 'interface ' in node_text and node.start_point[0] < len(lines):
                    line_text = lines[node.start_point[0]].strip()
                    # 检查是否是接口声明行
                    if (line_text.startswith('interface ') or
                        line_text.startswith('export interface ') or
                        'interface ' in line_text):
                        interface_nodes.append(node)
                        return
            
            # 递归遍历子节点
            if hasattr(node, 'children'):
                for child in node.children:
                    traverse_node(child)
        
        traverse_node(root_node)
        return interface_nodes
    
    def _extract_interface_signature(self, node, lines: List[str]) -> str:
        """提取接口签名"""
        try:
            start_line = node.start_point[0]
            line = lines[start_line]
            brace_pos = line.find('{')
            if brace_pos != -1:
                return line[:brace_pos].strip() + " {"
            return line.strip() + " {"
        except:
            return "interface UnknownInterface {"
    
    def _extract_interface_members(self, interface_node, lines: List[str], skeleton_lines: List[str]):
        """提取接口成员（属性和方法签名）"""
        # 查询接口成员
        member_queries = [
            "(property_signature) @property",
            "(method_signature) @method",
            "(call_signature) @call",
            "(construct_signature) @construct",
            "(index_signature) @index"
        ]
        
        member_nodes = []
        processed_positions = set()
        
        for query in member_queries:
            try:
                member_captures = self.execute_query(query, interface_node)
                for nodes in member_captures.values():
                    for node in nodes:
                        pos_key = (node.start_point[0], node.start_point[1])
                        if pos_key not in processed_positions:
                            member_nodes.append(node)
                            processed_positions.add(pos_key)
            except Exception as e:
                logger.error(f"接口成员查询失败: {query}, 错误: {e}")
        
        if member_nodes:
            skeleton_lines.append("    // 接口成员")
            for node in member_nodes:
                try:
                    start_line = node.start_point[0]
                    if start_line < len(lines):
                        member_line = lines[start_line].strip()
                        skeleton_lines.append(f"    {member_line}")
                except:
                    skeleton_lines.append("    // 未知成员")
            skeleton_lines.append("")
    
    def _extract_enums(self, root_node, lines: List[str], skeleton_lines: List[str]):
        """
        提取TypeScript枚举 (修复关键问题2 - 枚举提取功能完全缺失)
        支持数字枚举、字符串枚举、常量枚举、外部枚举等
        """
        enum_queries = [
            "(enum_declaration) @enum",
            "(export_statement (enum_declaration)) @export_enum",
            "(ambient_declaration (enum_declaration)) @declare_enum"
        ]
        
        all_enum_nodes = []
        processed_positions = set()
        
        for query in enum_queries:
            try:
                enum_captures = self.execute_query(query, root_node)
                for nodes in enum_captures.values():
                    for node in nodes:
                        # 对于export_statement或ambient_declaration，需要找到其中的enum_declaration
                        if node.type in ['export_statement', 'ambient_declaration']:
                            for child in node.children:
                                if child.type == 'enum_declaration':
                                    node = child
                                    break
                        
                        # 使用位置信息去重
                        pos_key = (node.start_point[0], node.start_point[1])
                        if pos_key not in processed_positions:
                            all_enum_nodes.append(node)
                            processed_positions.add(pos_key)
            except Exception as e:
                logger.error(f"枚举查询失败: {query}, 错误: {e}")
        
        # 如果标准查询没有找到枚举，尝试手动解析
        if not all_enum_nodes:
            manual_nodes = self._find_enums_manually(root_node, lines)
            for node in manual_nodes:
                pos_key = (node.start_point[0], node.start_point[1])
                if pos_key not in processed_positions:
                    all_enum_nodes.append(node)
                    processed_positions.add(pos_key)
        
        if all_enum_nodes:
            skeleton_lines.append("// TypeScript枚举")
            for node in all_enum_nodes:
                enum_signature = self._extract_enum_signature(node, lines)
                if enum_signature and enum_signature.strip():
                    skeleton_lines.append(enum_signature)
                    
                    # 提取枚举成员
                    self._extract_enum_members(node, lines, skeleton_lines)
                    skeleton_lines.append("}")
                    skeleton_lines.append("")
    
    def _find_enums_manually(self, root_node, lines: List[str]):
        """手动查找TypeScript枚举声明"""
        enum_nodes = []
        
        def traverse_node(node):
            if hasattr(node, 'type') and hasattr(node, 'text'):
                node_text = node.text.decode('utf-8') if hasattr(node.text, 'decode') else str(node.text)
                
                # 查找包含 'enum' 关键字的节点
                if 'enum ' in node_text and node.start_point[0] < len(lines):
                    line_text = lines[node.start_point[0]].strip()
                    # 检查是否是枚举声明行
                    if (line_text.startswith('enum ') or
                        line_text.startswith('export enum ') or
                        line_text.startswith('const enum ') or
                        line_text.startswith('declare enum ') or
                        'enum ' in line_text):
                        enum_nodes.append(node)
                        return
            
            # 递归遍历子节点
            if hasattr(node, 'children'):
                for child in node.children:
                    traverse_node(child)
        
        traverse_node(root_node)
        return enum_nodes
    
    def _extract_enum_signature(self, node, lines: List[str]) -> str:
        """提取枚举签名"""
        try:
            start_line = node.start_point[0]
            line = lines[start_line]
            brace_pos = line.find('{')
            if brace_pos != -1:
                return line[:brace_pos].strip() + " {"
            return line.strip() + " {"
        except:
            return "enum UnknownEnum {"
    
    def _extract_enum_members(self, enum_node, lines: List[str], skeleton_lines: List[str]):
        """提取枚举成员"""
        # 查询枚举成员
        member_queries = [
            "(enum_member) @member",
            "(property_identifier) @property"
        ]
        
        member_nodes = []
        processed_positions = set()
        
        for query in member_queries:
            try:
                member_captures = self.execute_query(query, enum_node)
                for nodes in member_captures.values():
                    for node in nodes:
                        pos_key = (node.start_point[0], node.start_point[1])
                        if pos_key not in processed_positions:
                            member_nodes.append(node)
                            processed_positions.add(pos_key)
            except Exception as e:
                logger.error(f"枚举成员查询失败: {query}, 错误: {e}")
        
        # 如果没有找到成员，尝试手动解析枚举体
        if not member_nodes:
            member_nodes = self._find_enum_members_manually(enum_node, lines)
        
        if member_nodes:
            skeleton_lines.append("    // 枚举成员")
            for node in member_nodes:
                try:
                    start_line = node.start_point[0]
                    if start_line < len(lines):
                        member_line = lines[start_line].strip()
                        # 移除末尾的逗号
                        if member_line.endswith(','):
                            member_line = member_line[:-1]
                        skeleton_lines.append(f"    {member_line},")
                except:
                    skeleton_lines.append("    // 未知成员,")
            skeleton_lines.append("")
    
    def _find_enum_members_manually(self, enum_node, lines: List[str]):
        """手动查找枚举成员"""
        member_nodes = []
        
        try:
            start_line = enum_node.start_point[0]
            end_line = enum_node.end_point[0]
            
            # 查找枚举体内的成员
            for line_num in range(start_line + 1, min(end_line, len(lines))):
                line = lines[line_num].strip()
                if line and not line.startswith('//') and not line.startswith('/*') and line != '{' and line != '}':
                    # 创建一个简单的模拟节点
                    mock_node = type('MockNode', (), {
                        'start_point': (line_num, 0),
                        'end_point': (line_num, len(line))
                    })()
                    member_nodes.append(mock_node)
        except:
            pass
        
        return member_nodes