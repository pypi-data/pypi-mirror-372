"""
基于 tree-sitter 的 Java AST 解析器（简化版）

只提供方法调用查找的核心功能，删除冗余代码。
"""

import logging
import os
import glob
from typing import List, Optional, Dict
from pathlib import Path

from .models import MethodCallInfo, ImportInfo
from kengine.code.language_loader import get_language_for_extension

logger = logging.getLogger(__name__)

try:
    from tree_sitter import Node
except ImportError:
    Node = None


class JavaASTParser:
    """Java AST 解析器（简化版）"""
    
    def __init__(self):
        """初始化解析器"""
        self.language = None
        self.language_name = None
        self._init_language()
    
    def _init_language(self):
        """初始化 tree-sitter Java 语言库"""
        try:
            self.language, self.language_name = get_language_for_extension('.java')
            if not self.language:
                logger.error("无法加载 Java 语言库")
        except Exception as e:
            logger.error(f"初始化 Java 语言库失败: {e}")
    
    def parse_file(self, file_path: str) -> Optional['Tree']:
        """解析 Java 文件"""
        try:
            if not self.language:
                logger.error("Java 语言库未初始化")
                return None
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            # 创建解析器并解析
            import tree_sitter
            parser = tree_sitter.Parser(self.language)
            tree = parser.parse(bytes(code_content, 'utf8'))
            
            return tree
            
        except Exception as e:
            logger.error(f"解析文件失败: {e}")
            return None
    
    def find_all_method_calls_by_name(self, tree: 'Tree', code_content: str, target_method: str) -> List[MethodCallInfo]:
        """
        查找文件中所有指定方法名的调用
        
        Args:
            tree: 解析树
            code_content: 源代码内容
            target_method: 目标方法名
            
        Returns:
            List[MethodCallInfo]: 方法调用信息列表
        """
        method_calls = []
        
        try:
            def traverse_node(node: 'Node', current_method: Optional[str] = None):
                # 检查是否进入新的方法
                if node.type in ['method_declaration', 'constructor_declaration']:
                    current_method = self._extract_method_name(node, code_content) or "unknown"
                
                # 查找方法调用
                elif node.type == 'method_invocation':
                    call_info = self._parse_method_invocation(
                        node, code_content, target_method, current_method
                    )
                    if call_info:
                        method_calls.append(call_info)
                
                # 递归遍历子节点
                for child in node.children:
                    traverse_node(child, current_method)
            
            traverse_node(tree.root_node)
            return method_calls
            
        except Exception as e:
            logger.error(f"查找方法调用时发生错误: {e}")
            return []
    
    def _extract_method_name(self, method_node: 'Node', code_content: str) -> Optional[str]:
        """提取方法名"""
        try:
            for child in method_node.children:
                if child.type == 'identifier':
                    return self._get_node_text(child, code_content).strip()
            return None
        except Exception:
            return None
    
    def _parse_method_invocation(self, invocation_node: 'Node', code_content: str,
                               target_method: str, caller_method: Optional[str]) -> Optional[MethodCallInfo]:
        """解析方法调用"""
        try:
            # 查找方法名 - 根据调试结果，方法名是第三个子节点（第二个identifier）
            method_name = None
            identifier_count = 0
            
            for child in invocation_node.children:
                if child.type == 'identifier':
                    identifier_count += 1
                    if identifier_count == 2:  # 第二个identifier是方法名
                        method_name = self._get_node_text(child, code_content).strip()
                        break
                    elif identifier_count == 1 and len([c for c in invocation_node.children if c.type == 'identifier']) == 1:
                        # 如果只有一个identifier，那就是直接方法调用（如 method()）
                        method_name = self._get_node_text(child, code_content).strip()
                        break
            
            # 检查方法名是否匹配
            if method_name != target_method:
                return None
            
            # 获取调用位置
            call_line, call_column = self._get_position(invocation_node)
            
            # 获取上下文代码（前后3行）
            context_code = self._get_context_code(code_content, call_line, 3)
            
            return MethodCallInfo(
                caller_method_name=caller_method or "unknown",
                caller_method_line=0,
                call_line=call_line,
                call_column=call_column,
                variable_name="",  # 简化版本不追踪变量名
                method_name=method_name,
                arguments=[],  # 简化版本不解析参数
                context_code=context_code
            )
            
        except Exception as e:
            logger.error(f"解析方法调用失败: {e}")
            return None
    
    def _get_node_text(self, node: 'Node', code_content: str) -> str:
        """获取节点文本"""
        try:
            # 将字符串转换为UTF-8字节，然后使用字节偏移获取文本
            code_bytes = code_content.encode('utf-8')
            node_bytes = code_bytes[node.start_byte:node.end_byte]
            return node_bytes.decode('utf-8')
        except Exception as e:
            # 如果字节偏移失败，尝试使用字符偏移作为备选方案
            try:
                # 计算字符偏移位置
                start_char = len(code_content.encode('utf-8')[:node.start_byte].decode('utf-8', errors='ignore'))
                end_char = len(code_content.encode('utf-8')[:node.end_byte].decode('utf-8', errors='ignore'))
                return code_content[start_char:end_char]
            except Exception:
                return ""
    
    def _get_position(self, node: 'Node') -> tuple:
        """获取节点位置（行号，列号）"""
        try:
            return node.start_point[0] + 1, node.start_point[1] + 1
        except Exception:
            return 0, 0
    
    def _get_context_code(self, code_content: str, target_line: int, context_lines: int = 3) -> str:
        """获取指定行的上下文代码"""
        try:
            lines = code_content.split('\n')
            start_line = max(0, target_line - context_lines - 1)
            end_line = min(len(lines), target_line + context_lines)
            
            context_lines_list = []
            for i in range(start_line, end_line):
                line_num = i + 1
                marker = ">>> " if line_num == target_line else "    "
                context_lines_list.append(f"{marker}{line_num:4d}: {lines[i]}")
            
            return '\n'.join(context_lines_list)
        except Exception:
            return f"Line {target_line}: (无法获取上下文)"
    
    def extract_imports(self, tree: 'Tree', code_content: str) -> Dict[str, str]:
        """
        提取Java文件中的导入语句，返回简单类名到完整类名的映射
        
        Args:
            tree: 解析树
            code_content: 源代码内容
            
        Returns:
            Dict[str, str]: 简单类名到完整类名的映射字典
        """
        import_mapping = {}
        import_infos = []
        
        try:
            def traverse_node(node: 'Node'):
                # 查找导入声明
                if node.type == 'import_declaration':
                    import_info = self._parse_import_declaration(node, code_content)
                    if import_info:
                        import_infos.append(import_info)
                        
                        if import_info.is_wildcard:
                            # 通配符导入暂时不添加到映射中，需要后续解析
                            pass
                        else:
                            # 具体导入，添加到映射中
                            class_name = import_info.get_class_name()
                            import_mapping[class_name] = import_info.import_name
                
                # 递归遍历子节点
                for child in node.children:
                    traverse_node(child)
            
            traverse_node(tree.root_node)
            
            # 存储导入信息供后续使用
            self._import_infos = import_infos
            
            return import_mapping
            
        except Exception as e:
            logger.error(f"提取导入语句时发生错误: {e}")
            return {}
    
    def _parse_import_declaration(self, import_node: 'Node', code_content: str) -> Optional[ImportInfo]:
        """解析导入声明节点"""
        try:
            is_static = False
            import_name = ""
            is_wildcard = False
            
            # 获取导入语句的行号
            line_number = import_node.start_point[0] + 1
            
            # 遍历导入声明的子节点
            for child in import_node.children:
                if child.type == 'static':
                    is_static = True
                elif child.type == 'scoped_identifier' or child.type == 'identifier':
                    import_name = self._get_node_text(child, code_content).strip()
                elif child.type == 'asterisk':
                    is_wildcard = True
            
            # 处理通配符导入
            if is_wildcard and import_name:
                import_name = import_name + ".*"
            
            if import_name:
                return ImportInfo(
                    import_name=import_name,
                    alias=None,  # Java不支持导入别名
                    is_static=is_static,
                    is_wildcard=is_wildcard,
                    line_number=line_number
                )
            
            return None
            
        except Exception as e:
            logger.error(f"解析导入声明失败: {e}")
            return None
    
    def get_import_infos(self) -> List[ImportInfo]:
        """获取解析到的导入信息列表"""
        return getattr(self, '_import_infos', [])
    
    def resolve_wildcard_imports(self, base_dir: str, import_mapping: Dict[str, str]) -> Dict[str, str]:
        """
        解析通配符导入，扫描对应包目录下的所有Java文件
        
        Args:
            base_dir: 项目根目录
            import_mapping: 现有的导入映射
            
        Returns:
            Dict[str, str]: 更新后的简单类名到完整类名的映射字典
        """
        enhanced_mapping = import_mapping.copy()
        
        try:
            import_infos = self.get_import_infos()
            
            for import_info in import_infos:
                if import_info.is_wildcard:
                    package_name = import_info.get_package_name()
                    package_classes = self._scan_package_classes(base_dir, package_name)
                    
                    # 将包中的类添加到映射中
                    for class_name in package_classes:
                        full_class_name = f"{package_name}.{class_name}"
                        # 只有当类名不存在冲突时才添加
                        if class_name not in enhanced_mapping:
                            enhanced_mapping[class_name] = full_class_name
                        else:
                            # 如果存在冲突，记录警告
                            logger.warning(f"类名冲突: {class_name} 已存在于映射中，跳过 {full_class_name}")
            
            return enhanced_mapping
            
        except Exception as e:
            logger.error(f"解析通配符导入时发生错误: {e}")
            return enhanced_mapping
    
    def _scan_package_classes(self, base_dir: str, package_name: str) -> List[str]:
        """
        扫描指定包目录下的所有Java类
        
        Args:
            base_dir: 项目根目录
            package_name: 包名（如：com.jd.abc）
            
        Returns:
            List[str]: 包中的类名列表
        """
        class_names = []
        
        try:
            # 将包名转换为目录路径
            package_path = package_name.replace('.', os.sep)
            
            # 可能的源码目录
            possible_src_dirs = [
                os.path.join(base_dir, 'src', 'main', 'java'),
                os.path.join(base_dir, 'src'),
                base_dir
            ]
            
            for src_dir in possible_src_dirs:
                full_package_path = os.path.join(src_dir, package_path)
                
                if os.path.exists(full_package_path) and os.path.isdir(full_package_path):
                    # 扫描目录中的Java文件
                    java_files = glob.glob(os.path.join(full_package_path, "*.java"))
                    
                    for java_file in java_files:
                        # 提取类名（去掉.java扩展名）
                        class_name = os.path.basename(java_file)[:-5]  # 去掉.java
                        
                        # 验证这确实是一个类文件（简单检查）
                        if self._is_valid_class_file(java_file, class_name):
                            class_names.append(class_name)
                    
                    # 找到第一个匹配的目录就停止搜索
                    if class_names:
                        break
            
            return class_names
            
        except Exception as e:
            logger.error(f"扫描包 {package_name} 时发生错误: {e}")
            return []
    
    def _is_valid_class_file(self, file_path: str, expected_class_name: str) -> bool:
        """
        简单验证Java文件是否包含预期的类定义
        
        Args:
            file_path: Java文件路径
            expected_class_name: 预期的类名
            
        Returns:
            bool: 是否为有效的类文件
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 简单的正则表达式检查类定义
            import re
            class_pattern = rf'\b(public\s+)?(abstract\s+)?(final\s+)?class\s+{re.escape(expected_class_name)}\b'
            interface_pattern = rf'\b(public\s+)?interface\s+{re.escape(expected_class_name)}\b'
            enum_pattern = rf'\b(public\s+)?enum\s+{re.escape(expected_class_name)}\b'
            
            return (re.search(class_pattern, content) is not None or
                    re.search(interface_pattern, content) is not None or
                    re.search(enum_pattern, content) is not None)
            
        except Exception as e:
            logger.error(f"验证类文件 {file_path} 时发生错误: {e}")
            return False