"""
Kotlin语言代码骨架处理器
"""

import logging
from typing import List, Dict, Any
from .base_language import BaseLanguageHandler

logger = logging.getLogger(__name__)


class KotlinHandler(BaseLanguageHandler):
    """Kotlin代码骨架处理器"""
    
    def __init__(self, lang_lib):
        super().__init__(lang_lib)
        self.language_name = "Kotlin"
        self.file_extensions = [".kt", ".kts"]
        self.comment_styles = {
            "line": ["//"],
            "block": [("/*", "*/")]
        }
        
    def can_handle(self, file_extension: str) -> bool:
        """Check if this handler can handle the given file extension."""
        return file_extension.lower() in self.file_extensions
        
    def generate_skeleton(self, tree, code_content: str) -> str:
        """生成Kotlin代码骨架"""
        lines = code_content.split('\n')
        skeleton_lines = []
        
        # 提取包声明
        self._extract_package(tree.root_node, lines, skeleton_lines)
        
        # 提取类
        self._extract_classes(tree.root_node, lines, skeleton_lines)
        
        return '\n'.join(skeleton_lines)
        
    def extract_class_name(self, node, lines: List[str]) -> str:
        """提取Kotlin类名或接口名"""
        try:
            # Kotlin AST可能包含修饰符，需要跳过它们找到类名/接口名
            # 结构: class_declaration/interface_declaration -> [modifiers] -> identifier
            for child in node.children:
                if child.type == 'identifier':
                    # 获取完整的类名，包括泛型参数
                    class_name = child.text.decode('utf-8')
                    
                    # 检查是否有泛型参数
                    next_sibling_index = node.children.index(child) + 1
                    if next_sibling_index < len(node.children):
                        next_sibling = node.children[next_sibling_index]
                        if next_sibling.type == 'type_parameters':
                            generic_params = next_sibling.text.decode('utf-8')
                            class_name += generic_params
                    
                    return class_name
                elif child.type == 'type_identifier':  # 有些情况下类名是type_identifier
                    return child.text.decode('utf-8')
            return "UnknownClass"
        except Exception as e:
            logger.error(f"提取Kotlin类名时发生错误: {e}")
            return "UnknownClass"
            
    def extract_function_signature(self, node, lines: List[str]) -> str:
        """提取Kotlin函数签名"""
        return self._extract_kotlin_function_signature(node, lines)
        
    def extract_method_signature(self, node, lines: List[str]) -> str:
        """提取Kotlin方法签名"""
        return self._extract_kotlin_function_signature(node, lines)
        
    def extract_field_info(self, node, lines: List[str]) -> Dict[str, Any]:
        """
        提取字段信息，返回统一格式
        
        Args:
            node: AST节点
            lines: 源代码行列表
            
        Returns:
            字段信息字典，包含统一格式的字段信息
        """
        try:
            # 使用基类的统一模板
            template = self.create_field_info_template()
            
            # 获取原有的字段解析结果
            field_data = self._parse_field_info(node, lines)
            
            # 转换为统一格式
            if field_data.get('names') and len(field_data['names']) > 0:
                template['name'] = field_data['names'][0]
            else:
                template['name'] = 'unknown'
            
            template['type'] = field_data.get('type', 'unknown')
            template['is_static'] = field_data.get('is_static', False)
            
            # 转换修饰符格式
            if field_data.get('modifiers'):
                template['modifiers'] = field_data['modifiers'].copy()
            
            # 添加访问修饰符到modifiers列表
            access_modifier = field_data.get('access_modifier', 'package')
            if access_modifier != 'package':
                if access_modifier not in template['modifiers']:
                    template['modifiers'].append(access_modifier)
            
            # 保留原有的声明提取逻辑
            template['declaration'] = self._extract_field_declaration(node, lines)
            
            # 提取字段注释
            template['comment'] = self.extract_docstring(node, lines)
            
            return template
            
        except Exception as e:
            logger.error(f"提取字段完整信息时发生错误: {e}")
            # 返回统一格式的错误模板
            error_template = self.create_field_info_template()
            error_template['declaration'] = '// 字段信息提取失败'
            return error_template
            
    def extract_functions(self, content: str) -> list:
        """Extract function definitions from Kotlin code."""
        functions = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Match function declarations
            if "fun " in line and "(" in line:
                func_name = self._extract_function_name(line)
                if func_name:
                    function_info = {
                        "name": func_name,
                        "line_number": i + 1,
                        "signature": line.strip(),
                        "language": self.language_name
                    }
                    functions.append(function_info)
                    
        return functions
        
    def extract_classes(self, content: str) -> list:
        """Extract class definitions from Kotlin code."""
        classes = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Match class declarations
            if "class " in line and not line.strip().startswith("//"):
                class_name = self._extract_class_name(line)
                if class_name:
                    class_info = {
                        "name": class_name,
                        "line_number": i + 1,
                        "signature": line.strip(),
                        "language": self.language_name
                    }
                    classes.append(class_info)
                    
        return classes
        
    def _extract_function_name(self, line: str) -> str:
        """Extract function name from a function declaration line."""
        # Handle "fun functionName(...)"
        if "fun " in line:
            start = line.find("fun ") + 4
            end = line.find("(")
            if end == -1:
                end = len(line)
                # Handle functions without parentheses
                while end > start and line[end-1] in [' ', '\t']:
                    end -= 1
                    
            func_name = line[start:end].strip()
            if func_name:
                return func_name
                
        return ""
        
    def _extract_class_name(self, line: str) -> str:
        """Extract class name from a class declaration line."""
        # Handle "class ClassName ..."
        if "class " in line:
            start = line.find("class ") + 6
            # Find end of class name (before colon, parentheses, or end of line)
            end_chars = [':', '(', '{', ' ', '\t']
            end = len(line)
            
            for char in end_chars:
                pos = line.find(char, start)
                if pos != -1 and pos < end:
                    end = pos
                    
            class_name = line[start:end].strip()
            if class_name:
                return class_name
                
        return ""
        
    def extract_imports(self, content: str) -> list:
        """Extract import statements from Kotlin code."""
        imports = []
        lines = content.split('\n')
        
        for line in lines:
            if line.strip().startswith("import "):
                import_stmt = line.strip()[7:].strip()  # Remove "import " prefix
                if import_stmt:
                    imports.append(import_stmt)
                    
        return imports
        
    def extract_package_info(self, content: str) -> dict:
        """Extract package information from Kotlin code."""
        lines = content.split('\n')
        
        for line in lines:
            if line.strip().startswith("package "):
                package_name = line.strip()[8:].strip()  # Remove "package " prefix
                return {"name": package_name}
                
        return {}

    def _extract_kotlin_function_signature(self, node, lines: List[str]) -> str:
        """使用tree-sitter提取Kotlin函数签名"""
        signature_parts = []
        
        # 1. 提取函数的注解
        # 查找函数节点的注解子节点
        for child in node.children:
            if child.type == 'modifiers':
                # modifiers节点包含注解和访问修饰符
                for modifier_child in child.children:
                    if modifier_child.type == 'annotation':
                        # 提取完整的注解文本
                        annotation_text = modifier_child.text.decode('utf-8')
                        signature_parts.append(annotation_text)
        
        # 2. 提取函数声明部分（不包括函数体）
        # 查找函数头部分
        function_header_parts = []
        for child in node.children:
            if child.type in ['modifiers', 'type_identifier', 'generic_type', 'void_type', 'identifier', 'formal_parameters', 'integral_type', 'floating_point_type', 'boolean_type']:
                if child.type == 'modifiers':
                    # 只提取访问修饰符，跳过注解（已经处理过了）
                    for modifier_child in child.children:
                        if modifier_child.type != 'annotation':
                            function_header_parts.append(modifier_child.text.decode('utf-8'))
                else:
                    function_header_parts.append(child.text.decode('utf-8'))
            elif child.type == 'block':
                # 遇到函数体就停止
                break
        
        # 3. 组合完整签名
        if function_header_parts:
            # 清理和格式化函数签名部分
            cleaned_parts = []
            for i, part in enumerate(function_header_parts):
                part = part.strip()
                if part:
                    # 特殊处理参数列表，确保括号紧贴函数名
                    if part.startswith('(') and i > 0:
                        # 将参数列表直接附加到前一个部分（函数名）
                        if cleaned_parts:
                            cleaned_parts[-1] = cleaned_parts[-1] + part
                        else:
                            cleaned_parts.append(part)
                    else:
                        cleaned_parts.append(part)
            
            function_signature = ' '.join(cleaned_parts)
            if signature_parts:
                # 有注解的情况
                full_signature = ' '.join(signature_parts) + ' ' + function_signature
            else:
                # 没有注解的情况
                full_signature = function_signature
            return full_signature + " { /*函数体已忽略，若需要请用工具读取*/ }"
        
        # 4. 如果tree-sitter解析失败，回退到简单的文本提取
        start_line = node.start_point[0]
        return lines[start_line].strip() + " { /*函数体已忽略，若需要请用工具读取*/ }" if start_line < len(lines) else "unknown() { /*函数体已忽略，若需要请用工具读取*/ }"
        
    def _extract_package(self, root_node, lines: List[str], skeleton_lines: List[str]):
        """提取包声明"""
        package_captures = self.execute_query("(package_declaration) @package", root_node)
        for nodes in package_captures.values():
            for node in nodes:
                package_line = lines[node.start_point[0]]
                skeleton_lines.append(package_line)
                skeleton_lines.append("")
                break
                
    def _extract_classes(self, root_node, lines: List[str], skeleton_lines: List[str]):
        """提取类、接口和枚举定义"""
        # 查找类声明、接口声明和枚举声明
        class_captures = self.execute_query("(class_declaration) @class", root_node)
        interface_captures = self.execute_query("(interface_declaration) @interface", root_node)
        
        # 收集所有节点并按位置排序
        all_nodes = []
        
        # 添加类节点
        for nodes in class_captures.values():
            for node in nodes:
                all_nodes.append(('class', node))
        
        # 添加接口节点
        for nodes in interface_captures.values():
            for node in nodes:
                all_nodes.append(('interface', node))
        
        # 按源代码中的位置排序
        all_nodes.sort(key=lambda x: x[1].start_point)
            
        for node_type, node in all_nodes:
            self._extract_class_or_interface(node, lines, skeleton_lines)
            
    def _extract_class_or_interface(self, node, lines: List[str], skeleton_lines: List[str]):
        """提取类或接口定义"""
        # 提取类的注释
        class_docstring = self.extract_docstring(node, lines)
        if class_docstring:
            skeleton_lines.append(f"/**")
            skeleton_lines.append(f" * {class_docstring}")
            skeleton_lines.append(f" */")
        
        class_signature = self._extract_kotlin_class_signature(node, lines)
        skeleton_lines.append(class_signature)
        skeleton_lines.append("")
        
        # 提取类字段
        self._extract_fields(node, lines, skeleton_lines)
        
        # 提取方法
        self._extract_methods(node, lines, skeleton_lines)
        
        # 递归提取内部类
        self._extract_inner_classes(node, lines, skeleton_lines, indent="    ")
        
        skeleton_lines.append("}")
        skeleton_lines.append("")
        
    def _extract_kotlin_class_signature(self, node, lines: List[str]) -> str:
        """提取Kotlin类或接口签名"""
        # 使用我们改进的类名提取方法
        class_name = self.extract_class_name(node, lines)
        
        # 构建类/接口签名
        signature_parts = []
        
        # 提取修饰符和注解
        for child in node.children:
            if child.type == 'modifiers':
                # 提取修饰符文本
                modifiers_text = child.text.decode('utf-8').strip()
                if modifiers_text:
                    signature_parts.append(modifiers_text)
                break
        
        # 根据节点类型添加关键字和名称
        if node.type == 'interface_declaration':
            signature_parts.append(f"interface {class_name}")
        else:
            signature_parts.append(f"class {class_name}")
        
        # 组合完整签名
        full_signature = ' '.join(signature_parts) + " {"
        
        return full_signature
        
    def _extract_methods(self, class_node, lines: List[str], skeleton_lines: List[str]):
        """提取Kotlin方法"""
        method_captures = self.execute_query("(function_declaration) @method", class_node)
        
        method_nodes = []
        for nodes in method_captures.values():
            method_nodes.extend(nodes)
            
        for node in method_nodes:
            # 提取方法的注释
            method_docstring = self.extract_docstring(node, lines)
            if method_docstring:
                skeleton_lines.append(f"    /**")
                skeleton_lines.append(f"     * {method_docstring}")
                skeleton_lines.append(f"     */")
                
            method_signature = self.extract_method_signature(node, lines)
            skeleton_lines.append(f"    {method_signature}")
            skeleton_lines.append("")
            
    def _extract_fields(self, class_node, lines: List[str], skeleton_lines: List[str]):
        """
        通用字段提取方法 - 子类可以重写以实现特定语言的字段提取逻辑
        
        Args:
            class_node: 类AST节点
            lines: 源代码行列表
            skeleton_lines: 骨架代码行列表（用于输出）
        """
        try:
            field_captures = self.execute_query("(property_declaration) @field", class_node)
            
            field_nodes = []
            for nodes in field_captures.values():
                field_nodes.extend(nodes)
            
            if field_nodes:
                skeleton_lines.append("    // 类字段")
                
                for node in field_nodes:
                    # 提取字段的注释
                    field_docstring = self.extract_docstring(node, lines)
                    if field_docstring:
                        skeleton_lines.append(f"    /**")
                        skeleton_lines.append(f"     * {field_docstring}")
                        skeleton_lines.append(f"     */")
                    
                    # 提取字段声明
                    field_declaration = self._extract_field_declaration(node, lines)
                    skeleton_lines.append(f"    {field_declaration}")
                
                skeleton_lines.append("")
                
        except Exception as e:
            logger.error(f"提取Kotlin字段时发生错误: {e}")
            skeleton_lines.append("    // 字段提取失败")
            skeleton_lines.append("")
            
    def _extract_field_declaration(self, node, lines: List[str]) -> str:
        """提取Kotlin字段声明"""
        try:
            field_info = self._parse_field_info(node, lines)
            
            # 构建字段声明
            declaration_parts = []
            
            # 添加修饰符
            if field_info['modifiers']:
                declaration_parts.extend(field_info['modifiers'])
            
            # 添加字段名和类型
            if field_info['names']:
                # 处理多个字段声明的情况
                field_names = ', '.join(field_info['names'])
                if field_info['type']:
                    declaration_parts.append(f"{field_names}: {field_info['type']}")
                else:
                    declaration_parts.append(field_names)
            
            return ' '.join(declaration_parts) + ";"
            
        except Exception as e:
            logger.error(f"提取字段声明时发生错误: {e}")
            # 回退到简单的文本提取
            start_line = node.start_point[0]
            if start_line < len(lines):
                return lines[start_line].strip()
            return "// 字段声明提取失败"
            
    def _parse_field_info(self, node, lines: List[str]) -> Dict[str, Any]:
        """解析字段信息"""
        field_info = {
            'modifiers': [],
            'type': '',
            'names': [],
            'is_static': False,
            'access_modifier': 'package'  # 默认包级访问
        }
        
        try:
            # 遍历字段声明的子节点
            for child in node.children:
                if child.type == 'modifiers':
                    # 提取修饰符
                    modifiers_text = child.text.decode('utf-8').strip()
                    if modifiers_text:
                        modifiers = modifiers_text.split()
                        field_info['modifiers'] = modifiers
                        
                        # 确定访问修饰符
                        if 'private' in modifiers:
                            field_info['access_modifier'] = 'private'
                        elif 'protected' in modifiers:
                            field_info['access_modifier'] = 'protected'
                        elif 'public' in modifiers:
                            field_info['access_modifier'] = 'public'
                
                elif child.type in ['type_identifier', 'generic_type']:
                    # 提取字段类型
                    field_info['type'] = child.text.decode('utf-8').strip()
                
                elif child.type == 'variable_declarator':
                    # 提取变量声明器中的字段名
                    field_name = self._extract_field_name_from_declarator(child)
                    if field_name:
                        field_info['names'].append(field_name)
                        
                elif child.type == 'identifier':
                    # 直接的标识符（简单的属性声明）
                    field_name = child.text.decode('utf-8').strip()
                    if field_name and field_name not in field_info['names']:
                        field_info['names'].append(field_name)
            
            return field_info
            
        except Exception as e:
            logger.error(f"解析字段信息时发生错误: {e}")
            return field_info
            
    def _extract_field_name_from_declarator(self, declarator_node) -> str:
        """从变量声明器中提取字段名"""
        try:
            # 查找标识符节点
            for child in declarator_node.children:
                if child.type == 'identifier':
                    return child.text.decode('utf-8').strip()
            return ""
        except Exception as e:
            logger.error(f"提取字段名时发生错误: {e}")
            return ""
            
    def _extract_inner_classes(self, parent_node, lines: List[str], skeleton_lines: List[str], indent: str = "    "):
        """递归提取内部类"""
        try:
            # 在父节点内查找内部类、接口
            inner_class_captures = self.execute_query("(class_declaration) @inner_class", parent_node)
            inner_interface_captures = self.execute_query("(interface_declaration) @inner_interface", parent_node)
            
            # 收集所有内部节点
            inner_nodes = []
            
            for nodes in inner_class_captures.values():
                for node in nodes:
                    # 确保这是直接的内部类，不是更深层的嵌套
                    if self._is_direct_child_class(node, parent_node):
                        inner_nodes.append(('class', node))
            
            for nodes in inner_interface_captures.values():
                for node in nodes:
                    if self._is_direct_child_class(node, parent_node):
                        inner_nodes.append(('interface', node))
            
            # 按位置排序
            inner_nodes.sort(key=lambda x: x[1].start_point)
            
            # 处理每个内部类/接口
            for node_type, node in inner_nodes:
                skeleton_lines.append("")
                
                # 提取注释
                docstring = self.extract_docstring(node, lines)
                if docstring:
                    skeleton_lines.append(f"{indent}/**")
                    skeleton_lines.append(f"{indent} * {docstring}")
                    skeleton_lines.append(f"{indent} */")
                
                # 处理内部类/接口
                class_signature = self._extract_kotlin_class_signature(node, lines)
                skeleton_lines.append(f"{indent}{class_signature}")
                skeleton_lines.append("")
                
                # 提取字段和方法（增加缩进）
                temp_lines = []
                self._extract_fields(node, lines, temp_lines)
                self._extract_methods(node, lines, temp_lines)
                for line in temp_lines:
                    if line.strip():
                        skeleton_lines.append(f"{indent}{line}")
                
                # 递归处理更深层的内部类
                self._extract_inner_classes(node, lines, skeleton_lines, indent + "    ")
                
                skeleton_lines.append(f"{indent}}}")
                
        except Exception as e:
            logger.error(f"提取内部类时发生错误: {e}")
            
    def _is_direct_child_class(self, child_node, parent_node) -> bool:
        """检查子节点是否是父节点的直接子类（不是更深层的嵌套）"""
        try:
            # 简单的启发式方法：检查嵌套深度
            child_start = child_node.start_point[0]
            parent_start = parent_node.start_point[0]
            parent_end = parent_node.end_point[0]
            
            # 子节点必须在父节点范围内
            if not (parent_start < child_start < parent_end):
                return False
            
            # 查找中间是否有其他类节点
            # 这是一个简化的检查，实际情况可能更复杂
            return True
            
        except Exception as e:
            logger.error(f"检查直接子类关系时发生错误: {e}")
            return False