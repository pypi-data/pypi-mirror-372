"""
方法依赖分析工具模块

包含 MethodDependencyAnalyzer 类，提供代码库中方法依赖关系分析功能。
分析给定方法在代码库中的使用情况，找出哪些类依赖了该方法。
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import sys
from pydantic import BaseModel, Field
from kengine.agent.shared.decorators import prevent_duplicate_calls
from kengine.agent.shared.tools.error_handler import handle_tool_errors

sys.path.append('.')

from kengine.agent.shared.tools.base import BasePathTool
from kengine.agent.shared.tools.exceptions import SearchError, FileOperationError, PathValidationError

# 导入 tree-sitter 分析器
from kengine.code.reader.dependency_analyzer import TreeSitterJavaMethodAnalyzer
from kengine.code.reader.dependency_analyzer.ast_parser import JavaASTParser


class MethodDependencyAnalyzer(BasePathTool):
    """方法依赖分析工具
    
    分析代码库中的方法依赖关系，找出哪些类依赖了给定的方法。
    
    功能特性：
    - 支持Java方法全名格式解析（如：com.jdl.abc.PickingService#lookupTask）
    - 使用grep命令进行高效搜索
    - 返回依赖文件路径和上下文代码
    - 支持markdown格式输出
    - 提供详细的错误处理和异常信息
    """
    
    def __init__(self, base_dir: str):
        """
        初始化方法依赖分析工具
        
        Args:
            base_dir: 基础目录路径，用于搜索的项目根目录
            
        Raises:
            PathValidationError: 基础目录无效
        """
        super().__init__(base_dir)
        self.context_lines = 3  # 前后3行上下文
        
        self.tree_sitter_analyzer = TreeSitterJavaMethodAnalyzer()
        self.ast_parser = JavaASTParser()
        
    def analyze_method_dependencies(self, method_full_name: str) -> Dict[str, Any]:
        """
        分析方法依赖关系
        
        Args:
            method_full_name: 方法全名，格式如 "com.jdl.abc.PickingService#lookupTask"
            
        Returns:
            包含分析结果的字典，格式：
            {
                "success": bool,
                "method_full_name": str,
                "target_class": str,
                "target_method": str,
                "dependencies": List[Dict],
                "markdown_result": str,
                "error": str (如果失败)
            }
        """
        try:
            # 验证输入参数
            if not method_full_name or not method_full_name.strip():
                raise SearchError(
                    "方法全名不能为空",
                    pattern=method_full_name,
                    tool_name=self.__class__.__name__
                )
            
            method_full_name = method_full_name.strip()
            
            # 解析方法全名
            target_class, target_method = self._parse_method_full_name(method_full_name)
            
            # 执行依赖分析
            dependencies = self._find_method_dependencies(target_class, target_method)
            
            # 生成markdown格式结果
            markdown_result = self._format_markdown_result(dependencies)
            
            return {
                "success": True,
                "method_full_name": method_full_name,
                "target_class": target_class,
                "target_method": target_method,
                "dependencies": dependencies,
                "markdown_result": markdown_result
            }
            
        except Exception as e:
            return {
                "success": False,
                "method_full_name": method_full_name,
                "error": str(e),
                "markdown_result": f"# 方法依赖分析失败\n\n错误信息：{str(e)}"
            }
    
    def _parse_method_full_name(self, method_full_name: str) -> Tuple[str, str]:
        """
        解析方法全名，提取类名和方法名
        
        Args:
            method_full_name: 方法全名，如 "com.jdl.abc.PickingService#lookupTask"
            
        Returns:
            (target_class, target_method) 元组
            
        Raises:
            SearchError: 方法全名格式不正确
        """
        if '#' not in method_full_name:
            raise SearchError(
                f"方法全名格式不正确，应包含'#'分隔符: {method_full_name}",
                pattern=method_full_name,
                tool_name=self.__class__.__name__
            )
        
        parts = method_full_name.split('#')
        if len(parts) != 2:
            raise SearchError(
                f"方法全名格式不正确，'#'分隔符应该只有一个: {method_full_name}",
                pattern=method_full_name,
                tool_name=self.__class__.__name__
            )
        
        full_class_name = parts[0].strip()
        method_name = parts[1].strip()
        
        if not full_class_name or not method_name:
            raise SearchError(
                f"类名或方法名不能为空: {method_full_name}",
                pattern=method_full_name,
                tool_name=self.__class__.__name__
            )
        
        # 提取简单类名（最后一个点后面的部分）
        if '.' in full_class_name:
            target_class = full_class_name.split('.')[-1]
        else:
            target_class = full_class_name
        
        return target_class, method_name
    
    def _find_method_dependencies(self, target_class: str, target_method: str) -> List[Dict[str, Any]]:
        """
        查找方法依赖关系
        
        Args:
            target_class: 目标类名
            target_method: 目标方法名
            
        Returns:
            依赖信息列表
            
        Raises:
            SearchError: 搜索过程中出现错误
        """
        try:
            # 第一阶段：查找引用目标类的文件
            class_files = self._find_files_referencing_class(target_class)
            
            if not class_files:
                return []
            
            # 第二阶段：在引用类的文件中搜索方法调用
            dependencies = []
            for file_path in class_files:
                method_usages = self._find_method_usages_in_file(file_path, target_method)
                dependencies.extend(method_usages)
            
            return dependencies
            
        except subprocess.CalledProcessError as e:
            raise SearchError(
                f"执行grep命令失败: {str(e)}",
                pattern=f"{target_class}#{target_method}",
                search_root=str(self.base_dir),
                tool_name=self.__class__.__name__
            )
        except Exception as e:
            raise SearchError(
                f"查找方法依赖时出错: {str(e)}",
                pattern=f"{target_class}#{target_method}",
                search_root=str(self.base_dir),
                tool_name=self.__class__.__name__
            )
    
    def _find_files_referencing_class(self, target_class: str) -> List[str]:
        """
        查找引用目标类的文件（混合策略：grep + AST验证）
        
        Args:
            target_class: 目标类名（可以是简单类名或完整类名）
            
        Returns:
            文件路径列表
        """
        try:
            # 阶段1：使用grep快速筛选候选文件（高效但可能有误报）
            grep_files = self._grep_files_referencing_class(target_class)
            
            if not grep_files:
                return []
            
            # 阶段2：使用AST分析进行精确验证（准确但较慢）
            verified_files = []
            
            for file_path in grep_files:
                if self._verify_class_reference(file_path, target_class):
                    verified_files.append(file_path)
                else:
                    # 记录被过滤掉的误报文件
                    print(f"[DEBUG] 过滤误报文件: {file_path} (不包含真正的 {target_class} 引用)")
            
            return verified_files
                
        except Exception as e:
            raise SearchError(
                f"查找引用类'{target_class}'的文件时出错: {str(e)}",
                pattern=target_class,
                search_root=str(self.base_dir),
                tool_name=self.__class__.__name__
            )
    
    def _grep_files_referencing_class(self, target_class: str) -> List[str]:
        """
        使用grep查找引用目标类的文件（传统方法，作为回退方案）
        
        Args:
            target_class: 目标类名
            
        Returns:
            文件路径列表
        """
        try:
            # 构建grep命令：查找引用目标类的Java文件
            cmd = [
                'grep', '-rl', '--include=*.java',
                target_class, str(self.base_dir)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.base_dir),
                timeout=30  # 30秒超时
            )
            
            if result.returncode == 0:
                # 过滤和清理文件路径
                files = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
                # 转换为绝对路径并验证文件存在
                absolute_files = []
                for f in files:
                    if f:
                        # 如果是相对路径，转换为绝对路径
                        if not os.path.isabs(f):
                            abs_path = os.path.join(str(self.base_dir), f)
                        else:
                            abs_path = f
                        
                        if os.path.exists(abs_path):
                            absolute_files.append(abs_path)
                
                return absolute_files
            else:
                # grep返回1表示没有找到匹配，这是正常情况
                return []
                
        except subprocess.TimeoutExpired:
            raise SearchError(
                f"搜索引用类'{target_class}'的文件时超时",
                pattern=target_class,
                search_root=str(self.base_dir),
                tool_name=self.__class__.__name__
            )
        except Exception as e:
            raise SearchError(
                f"搜索引用类'{target_class}'的文件时出错: {str(e)}",
                pattern=target_class,
                search_root=str(self.base_dir),
                tool_name=self.__class__.__name__
            )
    
    def _verify_class_reference(self, file_path: str, target_class: str) -> bool:
        """
        验证文件中是否真正引用了目标类（通过导入语句分析）
        
        Args:
            file_path: Java文件路径
            target_class: 目标类名（可以是简单类名或完整类名）
            
        Returns:
            bool: 是否真正引用了目标类
        """
        try:
            # 确定目标类的简单类名
            simple_class_name = target_class.split('.')[-1] if '.' in target_class else target_class
            
            # 检查是否是类定义文件本身
            file_name = os.path.basename(file_path)
            if file_name == f"{simple_class_name}.java":
                return False  # 排除类定义文件本身
            
            # 解析文件的AST
            tree = self.ast_parser.parse_file(file_path)
            if not tree:
                # 如果AST解析失败，回退到传统方法（认为引用有效）
                return True
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            # 提取导入信息
            import_mapping = self.ast_parser.extract_imports(tree, code_content)
            
            # 解析通配符导入
            enhanced_mapping = self.ast_parser.resolve_wildcard_imports(
                str(self.base_dir), import_mapping
            )
            
            # 确定目标类的简单类名和完整类名
            if '.' in target_class:
                # target_class是完整类名
                full_class_name = target_class
                simple_class_name = target_class.split('.')[-1]
            else:
                # target_class是简单类名
                simple_class_name = target_class
                full_class_name = enhanced_mapping.get(target_class, target_class)
            
            # 检查是否是Java内置类型（不需要导入）
            java_builtin_types = {
                'String', 'Integer', 'Long', 'Double', 'Float', 'Boolean', 'Character',
                'Byte', 'Short', 'Object', 'Class', 'System', 'Math', 'Thread'
            }
            
            if simple_class_name in java_builtin_types:
                # 对于内置类型，我们不关心这种依赖关系，返回False过滤掉
                return False
            
            # 检查是否有对应的导入
            if simple_class_name in enhanced_mapping:
                imported_full_name = enhanced_mapping[simple_class_name]
                # 检查导入的完整类名是否匹配
                if imported_full_name == full_class_name:
                    return True
            
            # 检查是否在代码中直接使用完整类名
            if full_class_name in code_content:
                return True
            
            # 检查是否在同一个包中（无需导入）
            if self._is_same_package(file_path, full_class_name):
                return True
            
            # 如果都不匹配，可能是误报
            return False
            
        except Exception as e:
            # 如果验证过程出错，回退到传统方法（认为引用有效）
            return True
    
    def _is_same_package(self, file_path1: str, file_path2_or_class: str) -> bool:
        """
        检查文件和目标类/文件是否在同一个包中
        
        Args:
            file_path1: Java文件路径
            file_path2_or_class: 另一个Java文件路径或目标类的完整类名
            
        Returns:
            bool: 是否在同一个包中
        """
        try:
            # 从第一个文件中读取包声明
            with open(file_path1, 'r', encoding='utf-8') as f:
                content1 = f.read()
            
            import re
            package_match1 = re.search(r'^\s*package\s+([\w.]+)\s*;', content1, re.MULTILINE)
            package1 = package_match1.group(1) if package_match1 else ''
            
            # 判断第二个参数是文件路径还是类名
            if os.path.exists(file_path2_or_class) and file_path2_or_class.endswith('.java'):
                # 是文件路径，读取包声明
                with open(file_path2_or_class, 'r', encoding='utf-8') as f:
                    content2 = f.read()
                
                package_match2 = re.search(r'^\s*package\s+([\w.]+)\s*;', content2, re.MULTILINE)
                package2 = package_match2.group(1) if package_match2 else ''
            else:
                # 是类名，从类名提取包名
                if '.' in file_path2_or_class:
                    package2 = '.'.join(file_path2_or_class.split('.')[:-1])
                else:
                    package2 = ''
            
            return package1 == package2
            
        except Exception:
            return False
    
    def _find_method_usages_in_file(self, file_path: str, target_method: str) -> List[Dict[str, Any]]:
        """
        在指定文件中查找方法使用情况
        
        Args:
            file_path: 文件路径
            target_method: 目标方法名
            
        Returns:
            方法使用情况列表
        """
        usages = []
        
        # 对于 Java 文件，使用 tree-sitter 分析器
        if file_path.endswith('.java'):
            try:
                # 使用简化的 tree-sitter 分析器查找方法调用
                result = self.tree_sitter_analyzer.find_all_method_calls(file_path, target_method)
                
                if result.success and result.method_calls:
                    for call in result.method_calls:
                        usage_info = {
                            "file_path": os.path.relpath(file_path, self.base_dir),
                            "line_number": call.call_line,
                            "context_code": call.context_code,
                            "target_method": target_method
                        }
                        usages.append(usage_info)
                
                return usages
                
            except Exception:
                # tree-sitter 分析失败，回退到 grep 方式
                pass
        else:
            raise RuntimeError(f'目前只支持Java')
    
    def _parse_grep_output(self, grep_output: str, file_path: str, target_method: str) -> List[Dict[str, Any]]:
        """
        解析grep命令输出
        
        Args:
            grep_output: grep命令的输出
            file_path: 文件路径
            target_method: 目标方法名
            
        Returns:
            解析后的使用情况列表
        """
        usages = []
        
        if not grep_output.strip():
            return usages
        
        lines = grep_output.strip().split('\n')
        current_block = []
        current_line_num = None
        
        for line in lines:
            if line.startswith('--'):
                # 分隔符，处理当前块
                if current_block and current_line_num:
                    usage = self._create_usage_info(
                        file_path, current_line_num, current_block, target_method
                    )
                    if usage:
                        usages.append(usage)
                current_block = []
                current_line_num = None
            else:
                # 解析行号和内容
                match = re.match(r'^(\d+)[-:](.*)$', line)
                if match:
                    line_num = int(match.group(1))
                    content = match.group(2)
                    
                    # 检查是否包含目标方法
                    if target_method in content and current_line_num is None:
                        current_line_num = line_num
                    
                    current_block.append(f"{line_num} | {content}")
        
        # 处理最后一个块
        if current_block and current_line_num:
            usage = self._create_usage_info(
                file_path, current_line_num, current_block, target_method
            )
            if usage:
                usages.append(usage)
        
        return usages
    
    def _create_usage_info(self, file_path: str, line_num: int, context_lines: List[str], target_method: str) -> Optional[Dict[str, Any]]:
        """
        创建使用情况信息
        
        Args:
            file_path: 文件路径
            line_num: 行号
            context_lines: 上下文行
            target_method: 目标方法名
            
        Returns:
            使用情况信息字典
        """
        if not context_lines:
            return None
        
        # 获取相对路径
        try:
            relative_path = os.path.relpath(file_path, self.base_dir)
        except ValueError:
            relative_path = file_path
        
        # 格式化上下文代码
        context_code = '\n'.join(context_lines)
        
        return {
            "file_path": relative_path,
            "line_number": line_num,
            "context_code": context_code,
            "target_method": target_method
        }
    
    def _format_markdown_result(self, dependencies: List[Dict[str, Any]]) -> str:
        """
        格式化为markdown结果
        
        Args:
            dependencies: 依赖信息列表
            
        Returns:
            markdown格式的结果字符串
        """
        if not dependencies:
            return "# 方法依赖分析结果\n\n未找到任何依赖关系。"
        
        markdown_lines = ["# 方法依赖分析结果\n"]
        
        for dep in dependencies:
            file_path = dep.get("file_path", "未知文件")
            line_num = dep.get("line_number", "未知行号")
            context_code = dep.get("context_code", "")
            
            markdown_lines.append(f"- {file_path} Line {line_num}")
            if context_code:
                # 添加代码块
                markdown_lines.append(f"\t{context_code.replace(chr(10), chr(10) + chr(9))}")
            markdown_lines.append("")  # 空行分隔
        
        return '\n'.join(markdown_lines)
    
    @handle_tool_errors(tool_name="MethodDependencyAnalyzer", operation="analyzer", return_format="json", rethrow_exceptions=True)
    @BasePathTool.json_compatible_input({'method_full_name': 'method_full_name'})
    @prevent_duplicate_calls(ttl=300)
    def run(self, method_full_name: str) -> str:
        """
        运行方法依赖分析（兼容性接口）
        
        Args:
            method_full_name: 方法全名
            
        Returns:
            markdown格式的分析结果
        """
        result = self.analyze_method_dependencies(method_full_name)
        return result.get("markdown_result", "分析失败")

class MethodDependencyAnalyzerInput(BaseModel):
    """
    方法依赖分析输入模型
    """
    method_full_name: str = Field(
        description="分析依赖的方法全名， 格式： com.jdl.wms.XXX@methodName",
        examples=["com.jd.wms.pick.PickingTaskService@dispachTask", ]
    )