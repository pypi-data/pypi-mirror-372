"""
Go语言代码骨架处理器
重构版本：添加字段提取功能
"""

import logging
from typing import List, Dict, Any
from .base_language import BaseLanguageHandler

logger = logging.getLogger(__name__)


class GoHandler(BaseLanguageHandler):
    """Go语言代码骨架处理器"""
    
    def generate_skeleton(self, tree, code_content: str) -> str:
        """生成Go代码骨架"""
        lines = code_content.split('\n')
        skeleton_lines = []
        
        # 提取包声明
        self._extract_package(tree.root_node, lines, skeleton_lines)
        
        # 提取导入语句
        self._extract_imports(tree.root_node, lines, skeleton_lines)
        
        # 提取类型声明
        self._extract_types(tree.root_node, lines, skeleton_lines)
        
        # 提取方法和函数
        self._extract_methods_and_functions(tree.root_node, lines, skeleton_lines)
        
        return '\n'.join(skeleton_lines)
    
    def extract_class_name(self, node, lines: List[str]) -> str:
        """提取Go结构体名称"""
        try:
            # Go AST: type_declaration -> type_spec -> type_identifier
            for child in node.children:
                if child.type == 'type_spec':
                    for spec_child in child.children:
                        if spec_child.type == 'type_identifier':
                            return spec_child.text.decode('utf-8')
                elif child.type == 'type_identifier':
                    return child.text.decode('utf-8')
            return "UnknownType"
        except Exception as e:
            logger.error(f"提取Go结构体名称时发生错误: {e}")
            return "UnknownType"
    
    def extract_function_signature(self, node, lines: List[str]) -> str:
        """提取Go函数签名"""
        try:
            start_line = node.start_point[0]
            line = lines[start_line]
            brace_pos = line.find('{')
            if brace_pos != -1:
                return line[:brace_pos].strip() + " { ... }"
            return line.strip() + " { ... }"
        except:
            return "func unknown() { ... }"
    
    def extract_method_signature(self, node, lines: List[str]) -> str:
        """提取Go方法签名"""
        return self.extract_function_signature(node, lines)
    
    def extract_field_info(self, node, lines: List[str]) -> Dict[str, Any]:
        """
        提取Go结构体字段信息
        
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
                
                # 解析Go字段声明
                # 格式: FieldName Type `json:"tag"` // comment
                # 或者: FieldName, FieldName2 Type `json:"tag"`
                
                # 提取注释
                if '//' in line:
                    line_parts = line.split('//', 1)
                    line = line_parts[0].strip()
                    field_info['comment'] = line_parts[1].strip()
                
                # 提取标签
                tag_match = None
                if '`' in line:
                    # 提取反引号中的标签
                    import re
                    tag_pattern = r'`([^`]*)`'
                    tag_match = re.search(tag_pattern, line)
                    if tag_match:
                        tag_content = tag_match.group(1)
                        field_info['modifiers'].append(f'tag:{tag_content}')
                        # 移除标签部分
                        line = re.sub(tag_pattern, '', line).strip()
                
                # 解析字段名和类型
                parts = line.split()
                if len(parts) >= 2:
                    # 处理多个字段名的情况: field1, field2 Type
                    if ',' in line:
                        # 找到类型部分（最后一个非逗号的部分）
                        type_part = parts[-1]  # 类型通常是最后一个部分
                        # 提取第一个字段名
                        field_names_part = ' '.join(parts[:-1])  # 除了最后一个类型部分
                        first_field = field_names_part.split(',')[0].strip()
                        field_info['name'] = first_field
                        field_info['type'] = type_part
                    else:
                        field_info['name'] = parts[0]
                        field_info['type'] = parts[1]
                elif len(parts) == 1:
                    # 可能是嵌入字段
                    field_info['name'] = parts[0]
                    field_info['type'] = parts[0]
                    field_info['modifiers'].append('embedded')
                
                # Go中结构体字段默认不是静态的
                field_info['is_static'] = False
                
                # 检查字段是否是导出的（首字母大写）
                if field_info['name'] and field_info['name'][0].isupper():
                    field_info['modifiers'].append('exported')
                else:
                    field_info['modifiers'].append('unexported')
                
                # 提取前一行的注释
                if start_line > 0:
                    prev_line = lines[start_line - 1].strip()
                    if prev_line.startswith('//'):
                        field_info['comment'] = prev_line[2:].strip()
            
            return field_info
            
        except Exception as e:
            logger.error(f"提取Go字段信息时发生错误: {e}")
            return self.create_field_info_template()
    
    def _extract_package(self, root_node, lines: List[str], skeleton_lines: List[str]):
        """提取包声明"""
        package_captures = self.execute_query("(package_clause) @package", root_node)
        for nodes in package_captures.values():
            for node in nodes:
                package_line = lines[node.start_point[0]]
                skeleton_lines.append(package_line)
                skeleton_lines.append("")
                break
    
    def _extract_imports(self, root_node, lines: List[str], skeleton_lines: List[str]):
        """提取导入语句"""
        import_captures = self.execute_query("(import_declaration) @import", root_node)
        
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
    
    def _extract_types(self, root_node, lines: List[str], skeleton_lines: List[str]):
        """提取类型声明"""
        type_captures = self.execute_query("(type_declaration) @type", root_node)
        
        type_nodes = []
        for nodes in type_captures.values():
            type_nodes.extend(nodes)
            
        for node in type_nodes:
            type_signature = self._extract_go_type_signature(node, lines)
            skeleton_lines.append(type_signature)
            
            # 如果是结构体类型，提取字段
            if 'struct' in type_signature.lower():
                self._extract_struct_fields(node, lines, skeleton_lines)
            
            skeleton_lines.append("")
    
    def _extract_go_type_signature(self, node, lines: List[str]) -> str:
        """提取Go类型签名"""
        try:
            start_line = node.start_point[0]
            return lines[start_line].strip()
        except:
            return "type Unknown struct {}"
    
    def _extract_methods_and_functions(self, root_node, lines: List[str], skeleton_lines: List[str]):
        """提取方法和函数"""
        # 提取方法
        method_captures = self.execute_query("(method_declaration) @method", root_node)
        method_nodes = []
        for nodes in method_captures.values():
            method_nodes.extend(nodes)
            
        for node in method_nodes:
            method_signature = self.extract_method_signature(node, lines)
            skeleton_lines.append(method_signature)
            skeleton_lines.append("")
        
        # 提取函数
        function_captures = self.execute_query("(function_declaration) @func", root_node)
        function_nodes = []
        for nodes in function_captures.values():
            function_nodes.extend(nodes)
            
        for node in function_nodes:
            func_signature = self.extract_function_signature(node, lines)
            skeleton_lines.append(func_signature)
            skeleton_lines.append("")
    
    def _extract_struct_fields(self, type_node, lines: List[str], skeleton_lines: List[str]):
        """提取Go结构体字段"""
        # 查询结构体字段
        field_captures = self.execute_query("(field_declaration) @field", type_node)
        
        field_nodes = []
        for nodes in field_captures.values():
            field_nodes.extend(nodes)
        
        if field_nodes:
            skeleton_lines.append("    // 字段")
            for node in field_nodes:
                field_info = self.extract_field_info(node, lines)
                if field_info['comment']:
                    skeleton_lines.append(f"    // {field_info['comment']}")
                skeleton_lines.append(f"    {field_info['declaration']}")
            skeleton_lines.append("")