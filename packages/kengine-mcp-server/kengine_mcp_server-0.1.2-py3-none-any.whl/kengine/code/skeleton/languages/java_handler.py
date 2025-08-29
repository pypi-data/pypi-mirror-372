"""
Java语言代码骨架处理器
"""

import logging
from typing import List, Dict, Any
from .base_language import BaseLanguageHandler

logger = logging.getLogger(__name__)


class JavaHandler(BaseLanguageHandler):
    """Java代码骨架处理器"""
    
    def generate_skeleton(self, tree, code_content: str) -> str:
        """生成Java代码骨架"""
        lines = code_content.split('\n')
        skeleton_lines = []
        
        # 提取包声明
        self._extract_package(tree.root_node, lines, skeleton_lines)
        
        # 提取导入语句
        self._extract_imports(tree.root_node, lines, skeleton_lines)
        
        # 提取类
        self._extract_classes(tree.root_node, lines, skeleton_lines)
        
        return '\n'.join(skeleton_lines)
    
    def extract_class_name(self, node, lines: List[str]) -> str:
        """提取Java类名或接口名"""
        try:
            # Java AST可能包含修饰符，需要跳过它们找到类名/接口名
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
            logger.error(f"提取Java类名时发生错误: {e}")
            return "UnknownClass"
    
    def extract_function_signature(self, node, lines: List[str]) -> str:
        """提取Java方法签名"""
        return self._extract_java_method_signature(node, lines)
    
    def extract_method_signature(self, node, lines: List[str]) -> str:
        """提取Java方法签名"""
        return self._extract_java_method_signature(node, lines)
    
    def extract_docstring(self, node, lines: List[str]) -> str:
        """提取Java文档注释 (修复关键问题2)"""
        try:
            # 查找方法或类前面的JavaDoc注释
            start_line = node.start_point[0]
            
            # 向上查找JavaDoc注释
            for i in range(start_line - 1, max(start_line - 10, -1), -1):
                if i < 0 or i >= len(lines):
                    continue
                    
                line = lines[i].strip()
                
                # 找到JavaDoc注释的结束
                if line.endswith('*/'):
                    # 收集整个JavaDoc注释块
                    javadoc_lines = []
                    
                    # 向上收集注释行直到找到开始
                    for j in range(i, max(i - 20, -1), -1):
                        if j < 0 or j >= len(lines):
                            continue
                        comment_line = lines[j].strip()
                        javadoc_lines.insert(0, comment_line)
                        
                        if comment_line.startswith('/**'):
                            # 找到JavaDoc开始，处理注释内容
                            return self._clean_javadoc(javadoc_lines)
                    break
                elif line and not line.startswith('*') and not line.startswith('//'):
                    # 遇到非注释行，停止查找
                    break
            
            return ""
        except Exception as e:
            logger.error(f"提取Java文档注释时发生错误: {e}")
            return ""
    
    def _clean_javadoc(self, javadoc_lines: List[str]) -> str:
        """清理JavaDoc注释格式，去除作者、日期等标签，只保留文本说明"""
        try:
            cleaned_lines = []
            for line in javadoc_lines:
                # 移除注释标记
                line = line.strip()
                if line.startswith('/**'):
                    line = line[3:].strip()
                elif line.startswith('*/'):
                    line = line[:-2].strip()
                elif line.startswith('*'):
                    line = line[1:].strip()
                
                # 跳过空行
                if not line:
                    continue
                
                # 过滤掉常见的JavaDoc标签和元信息
                # 跳过@author, @date, @version, @since等标签
                if line.startswith('@'):
                    continue
                
                # 跳过常见的作者和日期模式
                lower_line = line.lower()
                if any(keyword in lower_line for keyword in [
                    'author:', 'created by', 'created on', 'date:', 'version:',
                    'since:', 'modified by', 'last modified', 'copyright',
                    '作者:', '创建者:', '创建时间:', '日期:', '版本:', '修改者:'
                ]):
                    continue
                
                # 跳过看起来像日期的行 (简单的日期模式匹配)
                import re
                if re.match(r'.*\d{4}[-/]\d{1,2}[-/]\d{1,2}.*', line) or \
                   re.match(r'.*\d{1,2}[-/]\d{1,2}[-/]\d{4}.*', line):
                    continue
                
                # 保留有意义的描述文本
                cleaned_lines.append(line)
            
            # 合并所有有效行，并限制长度以保持简洁
            result = ' '.join(cleaned_lines) if cleaned_lines else ""
            return result
        except:
            return ""
    
    def _extract_package(self, root_node, lines: List[str], skeleton_lines: List[str]):
        """提取包声明"""
        package_captures = self.execute_query("(package_declaration) @package", root_node)
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
            for node in import_nodes[:10]:  # 只显示前10个导入
                import_line = lines[node.start_point[0]]
                skeleton_lines.append(import_line)
            if len(import_nodes) > 10:
                skeleton_lines.append(f"// ... 还有 {len(import_nodes) - 10} 个导入语句")
            skeleton_lines.append("")
    
    def _extract_classes(self, root_node, lines: List[str], skeleton_lines: List[str]):
        """提取类、接口和枚举定义"""
        # 查找类声明、接口声明和枚举声明
        class_captures = self.execute_query("(class_declaration) @class", root_node)
        interface_captures = self.execute_query("(interface_declaration) @interface", root_node)
        enum_captures = self.execute_query("(enum_declaration) @enum", root_node)
        
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
                
        # 添加枚举节点
        for nodes in enum_captures.values():
            for node in nodes:
                all_nodes.append(('enum', node))
        
        # 按源代码中的位置排序
        all_nodes.sort(key=lambda x: x[1].start_point)
            
        for node_type, node in all_nodes:
            if node_type == 'enum':
                self._extract_enum(node, lines, skeleton_lines)
            else:
                self._extract_class_or_interface(node, lines, skeleton_lines)
    
    def _extract_java_class_signature(self, node, lines: List[str]) -> str:
        """提取Java类或接口签名 - 改进版本，使用AST信息"""
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
        
        # 提取extends和implements部分
        for child in node.children:
            if child.type == 'superclass':
                extends_text = child.text.decode('utf-8').strip()
                signature_parts.append(extends_text)
            elif child.type == 'super_interfaces':
                implements_text = child.text.decode('utf-8').strip()
                signature_parts.append(implements_text)
            elif child.type == 'extends_interfaces':  # 接口的extends
                extends_text = child.text.decode('utf-8').strip()
                signature_parts.append(extends_text)
        
        # 组合完整签名
        full_signature = ' '.join(signature_parts) + " {"
        
        return full_signature
    
    def _extract_methods(self, class_node, lines: List[str], skeleton_lines: List[str]):
        """提取Java方法（排除私有方法）"""
        method_captures = self.execute_query("(method_declaration) @method", class_node)
        
        method_nodes = []
        for nodes in method_captures.values():
            method_nodes.extend(nodes)
            
        for node in method_nodes:
            # 检查是否为私有方法，如果是则跳过
            if self._is_private_java_method(node):
                continue
            
            # 提取方法的JavaDoc注释
            method_javadoc = self.extract_docstring(node, lines)
            if method_javadoc:
                skeleton_lines.append(f"    // {method_javadoc}")
                
            method_signature = self.extract_method_signature(node, lines)
            skeleton_lines.append(f"    {method_signature}")
            skeleton_lines.append("")
    
    def _is_private_java_method(self, node) -> bool:
        """检查Java方法是否为私有方法"""
        # 查找方法节点的修饰符
        for child in node.children:
            if child.type == 'modifiers':
                # 检查修饰符中是否包含private
                for modifier_child in child.children:
                    if modifier_child.type == 'private':
                        return True
        return False
    
    def _extract_java_method_signature(self, node, lines: List[str]) -> str:
        """使用tree-sitter提取Java方法签名"""
        signature_parts = []
        has_method_body = False
        
        # 1. 提取方法的注解
        # 查找方法节点的注解子节点
        for child in node.children:
            if child.type == 'modifiers':
                # modifiers节点包含注解和访问修饰符
                for modifier_child in child.children:
                    if modifier_child.type == 'annotation':
                        # 提取完整的注解文本
                        annotation_text = modifier_child.text.decode('utf-8')
                        signature_parts.append(annotation_text)
        
        # 2. 提取方法声明部分（不包括方法体）并检测是否有方法体
        # 查找方法头部分
        method_header_parts = []
        for child in node.children:
            if child.type in ['modifiers', 'type_identifier', 'generic_type', 'void_type', 'identifier', 'formal_parameters', 'integral_type', 'floating_point_type', 'boolean_type']:
                if child.type == 'modifiers':
                    # 只提取访问修饰符，跳过注解（已经处理过了）
                    for modifier_child in child.children:
                        if modifier_child.type != 'annotation':
                            method_header_parts.append(modifier_child.text.decode('utf-8'))
                else:
                    method_header_parts.append(child.text.decode('utf-8'))
            elif child.type == 'block':
                # 检测到方法体
                has_method_body = True
                break
        
        # 3. 组合完整签名
        if method_header_parts:
            # 清理和格式化方法签名部分
            cleaned_parts = []
            for i, part in enumerate(method_header_parts):
                part = part.strip()
                if part:
                    # 特殊处理参数列表，确保括号紧贴方法名
                    if part.startswith('(') and i > 0:
                        # 将参数列表直接附加到前一个部分（方法名）
                        if cleaned_parts:
                            cleaned_parts[-1] = cleaned_parts[-1] + part
                        else:
                            cleaned_parts.append(part)
                    else:
                        cleaned_parts.append(part)
            
            method_signature = ' '.join(cleaned_parts)
            if signature_parts:
                # 有注解的情况
                full_signature = ' '.join(signature_parts) + ' ' + method_signature
            else:
                # 没有注解的情况
                full_signature = method_signature
            
            # 4. 根据是否有方法体决定输出格式
            if has_method_body:
                # 有方法体的方法（类方法）：添加方法体标记
                return full_signature + " { /*方法体已忽略，若需要请用工具读取*/ }\n\n"
            else:
                # 没有方法体的方法（接口方法）：以分号结尾
                return full_signature + ";\n\n"
        
        # 5. 如果tree-sitter解析失败，回退到简单的文本提取
        start_line = node.start_point[0]
        return lines[start_line].strip() + ";\n\n" if start_line < len(lines) else ""
    
    def _extract_fields(self, class_node, lines: List[str], skeleton_lines: List[str]):
        """提取Java类字段（成员变量）"""
        try:
            field_captures = self.execute_query("(field_declaration) @field", class_node)
            
            field_nodes = []
            for nodes in field_captures.values():
                field_nodes.extend(nodes)
            
            if field_nodes:
                skeleton_lines.append("    // 类字段")
                
                for node in field_nodes:
                    # 提取字段的JavaDoc注释
                    field_javadoc = self.extract_docstring(node, lines)
                    if field_javadoc:
                        skeleton_lines.append(f"    // {field_javadoc}")
                    
                    # 提取字段声明
                    field_declaration = self._extract_field_declaration(node, lines)
                    skeleton_lines.append(f"    {field_declaration}")
                
                skeleton_lines.append("")
                
        except Exception as e:
            logger.error(f"提取Java字段时发生错误: {e}")
            skeleton_lines.append("    // 字段提取失败")
            skeleton_lines.append("")
    
    def _extract_field_declaration(self, node, lines: List[str]) -> str:
        """提取Java字段声明"""
        try:
            field_info = self._parse_field_info(node, lines)
            
            # 构建字段声明
            declaration_parts = []
            
            # 添加修饰符
            if field_info['modifiers']:
                declaration_parts.extend(field_info['modifiers'])
            
            # 添加类型
            if field_info['type']:
                declaration_parts.append(field_info['type'])
            
            # 添加字段名
            if field_info['names']:
                # 处理多个字段声明的情况
                field_names = ', '.join(field_info['names'])
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
            'is_final': False,
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
                        
                        # 检查特殊修饰符
                        if 'static' in modifiers:
                            field_info['is_static'] = True
                        if 'final' in modifiers:
                            field_info['is_final'] = True
                        
                        # 确定访问修饰符
                        if 'private' in modifiers:
                            field_info['access_modifier'] = 'private'
                        elif 'protected' in modifiers:
                            field_info['access_modifier'] = 'protected'
                        elif 'public' in modifiers:
                            field_info['access_modifier'] = 'public'
                
                elif child.type in ['type_identifier', 'generic_type', 'array_type', 'integral_type', 'floating_point_type', 'boolean_type']:
                    # 提取字段类型
                    field_info['type'] = child.text.decode('utf-8').strip()
                
                elif child.type == 'variable_declarator':
                    # 提取变量声明器中的字段名
                    field_name = self._extract_field_name_from_declarator(child)
                    if field_name:
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
    
    def _extract_class_or_interface(self, node, lines: List[str], skeleton_lines: List[str]):
        """提取类或接口定义（重构后的方法）"""
        # 提取类的JavaDoc注释
        class_javadoc = self.extract_docstring(node, lines)
        if class_javadoc:
            skeleton_lines.append(f"// {class_javadoc}")
        
        class_signature = self._extract_java_class_signature(node, lines)
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
    
    def _extract_enum(self, node, lines: List[str], skeleton_lines: List[str]):
        """提取枚举定义"""
        try:
            # 提取枚举的JavaDoc注释
            enum_javadoc = self.extract_docstring(node, lines)
            if enum_javadoc:
                skeleton_lines.append(f"// {enum_javadoc}")
            
            # 提取枚举签名
            enum_signature = self._extract_enum_signature(node, lines)
            skeleton_lines.append(enum_signature)
            skeleton_lines.append("")
            
            # 提取枚举常量
            self._extract_enum_constants(node, lines, skeleton_lines)
            
            # 提取枚举字段
            self._extract_fields(node, lines, skeleton_lines)
            
            # 提取枚举方法（包括构造函数）
            self._extract_methods(node, lines, skeleton_lines)
            
            skeleton_lines.append("}")
            skeleton_lines.append("")
            
        except Exception as e:
            logger.error(f"提取枚举时发生错误: {e}")
            skeleton_lines.append("// 枚举提取失败")
            skeleton_lines.append("")
    
    def _extract_enum_signature(self, node, lines: List[str]) -> str:
        """提取枚举签名"""
        try:
            signature_parts = []
            
            # 提取修饰符
            for child in node.children:
                if child.type == 'modifiers':
                    modifiers_text = child.text.decode('utf-8').strip()
                    if modifiers_text:
                        signature_parts.append(modifiers_text)
                    break
            
            # 提取枚举名称
            enum_name = self.extract_class_name(node, lines)
            signature_parts.append(f"enum {enum_name}")
            
            # 提取implements部分
            for child in node.children:
                if child.type == 'super_interfaces':
                    implements_text = child.text.decode('utf-8').strip()
                    signature_parts.append(implements_text)
            
            return ' '.join(signature_parts) + " {"
            
        except Exception as e:
            logger.error(f"提取枚举签名时发生错误: {e}")
            return "enum UnknownEnum {"
    
    def _extract_enum_constants(self, node, lines: List[str], skeleton_lines: List[str]):
        """提取枚举常量"""
        try:
            # 查找枚举常量
            constant_captures = self.execute_query("(enum_constant) @constant", node)
            
            constants = []
            for nodes in constant_captures.values():
                for constant_node in nodes:
                    constant_text = constant_node.text.decode('utf-8').strip()
                    constants.append(constant_text)
            
            if constants:
                skeleton_lines.append("    // 枚举常量")
                # 将常量按行显示，每行最多3个
                for i in range(0, len(constants), 3):
                    batch = constants[i:i+3]
                    skeleton_lines.append(f"    {', '.join(batch)}")
                skeleton_lines.append("")
                
        except Exception as e:
            logger.error(f"提取枚举常量时发生错误: {e}")
            skeleton_lines.append("    // 枚举常量提取失败")
            skeleton_lines.append("")
    
    def _extract_inner_classes(self, parent_node, lines: List[str], skeleton_lines: List[str], indent: str = "    "):
        """递归提取内部类"""
        try:
            # 在父节点内查找内部类、接口和枚举
            inner_class_captures = self.execute_query("(class_declaration) @inner_class", parent_node)
            inner_interface_captures = self.execute_query("(interface_declaration) @inner_interface", parent_node)
            inner_enum_captures = self.execute_query("(enum_declaration) @inner_enum", parent_node)
            
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
                        
            for nodes in inner_enum_captures.values():
                for node in nodes:
                    if self._is_direct_child_class(node, parent_node):
                        inner_nodes.append(('enum', node))
            
            # 按位置排序
            inner_nodes.sort(key=lambda x: x[1].start_point)
            
            # 处理每个内部类/接口/枚举
            for node_type, node in inner_nodes:
                skeleton_lines.append("")
                
                # 提取注释
                docstring = self.extract_docstring(node, lines)
                if docstring:
                    skeleton_lines.append(f"{indent}// {docstring}")
                
                if node_type == 'enum':
                    # 处理内部枚举
                    enum_signature = self._extract_enum_signature(node, lines)
                    skeleton_lines.append(f"{indent}{enum_signature}")
                    skeleton_lines.append("")
                    
                    # 提取枚举常量（增加缩进）
                    temp_lines = []
                    self._extract_enum_constants(node, lines, temp_lines)
                    for line in temp_lines:
                        if line.strip():
                            skeleton_lines.append(f"{indent}{line}")
                    
                    # 提取枚举字段和方法
                    temp_lines = []
                    self._extract_fields(node, lines, temp_lines)
                    self._extract_methods(node, lines, temp_lines)
                    for line in temp_lines:
                        if line.strip():
                            skeleton_lines.append(f"{indent}{line}")
                else:
                    # 处理内部类/接口
                    class_signature = self._extract_java_class_signature(node, lines)
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