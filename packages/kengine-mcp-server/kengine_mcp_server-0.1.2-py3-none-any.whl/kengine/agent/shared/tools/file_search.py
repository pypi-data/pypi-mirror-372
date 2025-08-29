"""
文件搜索工具模块 - 重构版本

包含 FileSearchTool 类，支持多种输出格式的文件搜索功能，使用统一的错误处理机制。
"""
import glob
import os
from pathlib import Path
from typing import Optional, List, Dict, Any, Union

from .base import BasePathTool
from .exceptions import SearchError, ConfigurationError, PathValidationError, SecurityError
from .error_handler import ErrorHandler, handle_tool_errors, safe_execute
from ..decorators import prevent_duplicate_calls


class FileSearchTool(BasePathTool):
    """文件搜索工具 - 重构版本
    
    支持多种输出格式的文件搜索工具，参考 DirectoryStructureTool 的设计思想：
    - plain: 简单格式（默认，保持向后兼容）
    - simple: 使用连接符和图标的优化格式
    - compact: 使用 "- " 前缀的紧凑格式
    
    使用统一的错误处理机制，返回结构化的响应。
    """
    
    def __init__(self, base_dir: str, output_format: str = "plain"):
        """
        初始化文件搜索工具
        
        Args:
            base_dir: 基础目录路径
            output_format: 输出格式，可选值：
                - "plain": 简单格式（默认，保持向后兼容）
                - "simple": 使用连接符和图标的优化格式
                - "compact": 使用 "- " 前缀的紧凑格式
                
        Raises:
            ConfigurationError: 输出格式不支持
        """
        super().__init__(base_dir)
        self.max_results = 500
        self.output_format = output_format
        self.error_handler = ErrorHandler()
        
        # 验证输出格式
        valid_formats = ["plain", "simple", "compact"]
        if output_format not in valid_formats:
            raise ConfigurationError(
                f"不支持的输出格式: {output_format}，支持的格式: {valid_formats}",
                config_key="output_format",
                config_value=output_format,
                tool_name=self.__class__.__name__
            )
    
    def search(self, pattern: str, file_types: Optional[List[str]] = None,
              exclude_patterns: Optional[List[str]] = None, output_format: Optional[str] = None) -> Dict[str, Any]:
        """
        搜索文件并返回格式化结果（新的推荐接口）- 返回结构化响应
        
        Args:
            pattern: 搜索模式
            file_types: 文件类型列表（暂未实现，保留接口）
            exclude_patterns: 排除模式列表（暂未实现，保留接口）
            output_format: 输出格式，如果为None则使用实例的默认格式
            
        Returns:
            包含搜索结果或错误信息的字典
        """
        return safe_execute(
            self._search_internal,
            tool_name="FileSearchTool",
            operation="search",
            pattern=pattern,
            file_types=file_types,
            exclude_patterns=exclude_patterns,
            output_format=output_format
        )
    
    def _search_internal(self, pattern: str, file_types: Optional[List[str]] = None,
                        exclude_patterns: Optional[List[str]] = None, output_format: Optional[str] = None) -> str:
        """
        内部搜索方法
        
        Args:
            pattern: 搜索模式
            file_types: 文件类型列表
            exclude_patterns: 排除模式列表
            output_format: 输出格式
            
        Returns:
            格式化的搜索结果字符串
            
        Raises:
            SearchError: 搜索失败
        """
        if not pattern.strip():
            raise SearchError("搜索模式不能为空", tool_name=self.__class__.__name__)
        
        # 使用指定格式或默认格式
        format_to_use = output_format if output_format is not None else self.output_format
        
        # 构建搜索模式
        search_pattern = str(self.base_dir / pattern)
        paths = glob.glob(search_pattern, recursive=True)
        
        files = []
        for path in paths:
            if os.path.isfile(path):
                rel_path = self._get_relative_path(Path(path))
                files.append(rel_path)
                if len(files) >= self.max_results:
                    break
        
        if not files:
            return ""
        
        # 使用新的格式化方法
        result = self._format_file_list(files, format_to_use)
        
        if len(files) >= self.max_results:
            result += f"\n# 注意: 结果已限制为前{self.max_results}个文件"
        
        return result
    

    @handle_tool_errors(tool_name="FileSearchTool", operation="search", return_format="json", rethrow_exceptions=True)
    @BasePathTool.json_compatible_input({'pattern': 'pattern', 'root': 'root'})
    @prevent_duplicate_calls(ttl=300)
    def run(self, pattern: str, root: str = ".") -> Union[str, Dict[str, Any]]:
        """
        搜索文件（保持向后兼容的接口）- 可返回JSON格式错误
        
        Args:
            pattern: 搜索模式，支持JSON格式参数
            root: 搜索根目录
            
        Returns:
            搜索结果字符串或JSON格式的错误信息
        """
        if not pattern.strip():
            raise SearchError("搜索模式不能为空", tool_name=self.__class__.__name__)
        
        pattern = pattern.strip()
        
        root = root.strip()
        # 验证搜索根目录
        try:
            search_root = self._validate_directory_path(root)
        except (PathValidationError, SecurityError) as e:
            raise SearchError(f"文件搜索失败: {str(e)}", tool_name=self.__class__.__name__) from e
        
        # 构建搜索模式 - 修复：智能处理通配符模式
        old_cwd = os.getcwd()
        try:
            os.chdir(str(search_root))
            
            # 检测通配符模式并自动使用递归搜索
            if '*' in pattern or '?' in pattern:
                # 如果是简单通配符模式（如 *.java），转换为递归模式
                if not pattern.startswith('**/') and '**' not in pattern:
                    recursive_pattern = f"**/{pattern}"
                    paths = glob.glob(recursive_pattern, recursive=True)
                    # 如果递归搜索找到结果，使用递归结果；否则使用原始模式
                    if not paths:
                        paths = glob.glob(pattern, recursive=True)
                else:
                    paths = glob.glob(pattern, recursive=True)
            else:
                # 修复：对于具体文件名，也尝试递归搜索
                # 首先尝试直接匹配
                paths = glob.glob(pattern, recursive=True)
                # 如果没有找到，尝试递归搜索
                if not paths:
                    recursive_pattern = f"**/{pattern}"
                    paths = glob.glob(recursive_pattern, recursive=True)
                
            # 转换为绝对路径
            paths = [os.path.join(str(search_root), p) for p in paths]
        except (OSError, PermissionError) as e:
            raise SearchError(f"文件搜索失败: {str(e)}", tool_name=self.__class__.__name__) from e
        finally:
            os.chdir(old_cwd)
        
        files = []
        for path in paths:
            if os.path.isfile(path):
                rel_path = self._get_relative_path(Path(path))
                files.append(rel_path)
                if len(files) >= self.max_results:
                    break
        
        if not files:
            # 修复：改进错误信息处理逻辑
            # 对于具体文件名，提供更详细的搜索建议
            if '*' in pattern or '?' in pattern or '**' in pattern:
                return ""  # 通配符搜索没有匹配，返回空结果
            else:
                # 具体文件搜索没有找到，提供更详细的错误信息
                error_msg = f"错误： 文件'{pattern}'不存在"
                
                # 尝试提供搜索建议
                try:
                    # 检查是否在项目根目录下
                    root_search = self._search_in_project_root(pattern)
                    if root_search:
                        error_msg += f"\n\n搜索建议：\n- 文件可能位于：{root_search}"
                    
                    # 检查是否有类似的文件名
                    similar_files = self._find_similar_files(pattern)
                    if similar_files:
                        error_msg += f"\n- 可能的相似文件：\n" + "\n".join([f"  - {f}" for f in similar_files[:5]])
                        
                except Exception:
                    # 如果搜索建议失败，不影响主要功能
                    pass
                
                return error_msg
        
        # 使用新的格式化方法
        result = self._format_file_list(files, self.output_format)
        if len(files) >= self.max_results:
            result += f"\n# 注意: 结果已限制为前{self.max_results}个文件"
        
        return result
    
    def _search_in_project_root(self, filename: str) -> Optional[str]:
        """
        在项目根目录下搜索文件
        
        Args:
            filename: 文件名
            
        Returns:
            找到的文件路径，如果没找到返回None
        """
        try:
            # 在项目根目录下递归搜索
            root_pattern = f"**/{filename}"
            root_paths = glob.glob(str(self.base_dir / root_pattern), recursive=True)
            
            if root_paths:
                # 返回第一个找到的文件
                found_path = Path(root_paths[0])
                return str(found_path.relative_to(self.base_dir))
        except Exception:
            pass
        
        return None
    
    def _find_similar_files(self, filename: str) -> List[str]:
        """
        查找相似的文件名
        
        Args:
            filename: 原始文件名
            
        Returns:
            相似文件列表
        """
        try:
            # 提取文件名和扩展名
            name_parts = filename.split('.')
            if len(name_parts) >= 2:
                base_name = name_parts[0]
                extension = '.' + '.'.join(name_parts[1:])
            else:
                base_name = filename
                extension = ''
            
            # 搜索包含相同基础名称的文件
            pattern = f"**/*{base_name}*{extension}"
            similar_paths = glob.glob(str(self.base_dir / pattern), recursive=True)
            
            # 转换为相对路径并限制数量
            similar_files = []
            for path in similar_paths[:10]:  # 限制最多10个
                rel_path = Path(path).relative_to(self.base_dir)
                similar_files.append(str(rel_path))
            
            return similar_files
        except Exception:
            return []
    
    def _format_file_list(self, files: List[str], output_format: str = "plain") -> str:
        """
        格式化文件列表输出
        
        Args:
            files: 文件路径列表
            output_format: 输出格式
            
        Returns:
            格式化后的文件列表字符串
        """
        if not files:
            return ""
        
        # 去重并排序
        unique_files = sorted(set(files))
        
        if output_format == "simple":
            return self._generate_simple_list(unique_files)
        elif output_format == "compact":
            return self._generate_compact_list(unique_files)
        else:  # plain
            return "\n".join(unique_files)
    
    def _generate_simple_list(self, files: List[str]) -> str:
        """
        生成simple格式的文件列表
        
        使用树状连接符和文件图标，提高可读性
        
        Args:
            files: 排序后的文件列表
            
        Returns:
            simple格式的文件列表字符串
        """
        if not files:
            return ""
        
        lines = []
        for i, file_path in enumerate(files):
            is_last = (i == len(files) - 1)
            connector = "└── " if is_last else "├── "
            lines.append(f"{connector}📄 {file_path}")
        
        return "\n".join(lines)
    
    def _generate_compact_list(self, files: List[str]) -> str:
        """
        生成compact格式的文件列表
        
        使用简洁的 "- " 前缀，最大化节省token
        
        Args:
            files: 排序后的文件列表
            
        Returns:
            compact格式的文件列表字符串
        """
        if not files:
            return ""
        
        lines = [f"- {file_path}" for file_path in files]
        return "\n".join(lines)
    
    def get_format_info(self) -> Dict[str, Any]:
        """
        获取当前输出格式的信息
        
        Returns:
            包含格式信息的字典
        """
        format_info = {
            "plain": {
                "name": "简单格式",
                "description": "原始换行符分隔格式，保持向后兼容",
                "token_efficiency": "基准（100%）",
                "use_case": "向后兼容和简单文件列表展示"
            },
            "simple": {
                "name": "树状格式",
                "description": "使用连接符和图标的优化格式",
                "token_efficiency": "可读性优化",
                "use_case": "提高可读性的文件列表展示"
            },
            "compact": {
                "name": "紧凑格式",
                "description": "使用 '- ' 前缀的紧凑格式",
                "token_efficiency": "节省10-20%",
                "use_case": "Token受限场景的文件列表展示"
            }
        }
        
        return {
            "success": True,
            "data": {
                "current_format": self.output_format,
                "format_details": format_info[self.output_format],
                "all_formats": format_info
            },
            "message": "格式信息获取成功",
            "tool_name": "FileSearchTool",
            "operation": "get_format_info"
        }
    
    def set_output_format(self, output_format: str) -> Dict[str, Any]:
        """
        设置输出格式 - 返回结构化响应
        
        Args:
            output_format: 新的输出格式
            
        Returns:
            操作结果字典
        """
        try:
            valid_formats = ["plain", "simple", "compact"]
            if output_format not in valid_formats:
                return self.error_handler.format_error_response(
                    ConfigurationError(
                        f"不支持的输出格式: {output_format}，支持的格式: {valid_formats}",
                        config_key="output_format",
                        config_value=output_format,
                        tool_name=self.__class__.__name__
                    ),
                    tool_name="FileSearchTool",
                    operation="set_output_format"
                )
            
            old_format = self.output_format
            self.output_format = output_format
            
            return self.error_handler.format_success_response(
                data={
                    "old_format": old_format,
                    "new_format": output_format
                },
                message=f"输出格式已更新为: {output_format}",
                tool_name="FileSearchTool",
                operation="set_output_format"
            )
        except Exception as e:
            return self.error_handler.format_error_response(
                e,
                tool_name="FileSearchTool",
                operation="set_output_format"
            )
    
    def set_max_results(self, max_results: int) -> Dict[str, Any]:
        """
        设置最大结果数量限制 - 返回结构化响应
        
        Args:
            max_results: 最大结果数量
            
        Returns:
            操作结果字典
        """
        try:
            if max_results <= 0:
                return self.error_handler.format_error_response(
                    ValueError("最大结果数量必须大于0"),
                    tool_name="FileSearchTool",
                    operation="set_max_results"
                )
            
            old_max = self.max_results
            self.max_results = max_results
            
            return self.error_handler.format_success_response(
                data={
                    "old_max_results": old_max,
                    "new_max_results": max_results
                },
                message=f"最大结果数量已更新为: {max_results}",
                tool_name="FileSearchTool",
                operation="set_max_results"
            )
        except Exception as e:
            return self.error_handler.format_error_response(
                e,
                tool_name="FileSearchTool",
                operation="set_max_results"
            )
    
    def get_search_statistics(self, pattern: str, root: str = ".") -> Dict[str, Any]:
        """
        获取搜索统计信息（不返回具体文件列表）- 返回结构化响应
        
        Args:
            pattern: 搜索模式
            root: 搜索根目录
            
        Returns:
            包含搜索统计信息或错误信息的字典
        """
        return safe_execute(
            self._get_search_statistics_internal,
            tool_name="FileSearchTool",
            operation="get_statistics",
            pattern=pattern,
            root=root
        )
    
    def _get_search_statistics_internal(self, pattern: str, root: str = ".") -> Dict[str, Any]:
        """
        内部获取搜索统计信息方法
        
        Args:
            pattern: 搜索模式
            root: 搜索根目录
            
        Returns:
            包含搜索统计信息的字典
        """
        if not pattern.strip():
            raise SearchError("搜索模式不能为空", tool_name=self.__class__.__name__)
        
        # 验证搜索根目录
        search_root = self._validate_directory_path(root.strip())
        
        # 执行搜索统计
        old_cwd = os.getcwd()
        os.chdir(str(search_root))
        try:
            paths = glob.glob(pattern, recursive=True)
            # 转换为绝对路径
            paths = [os.path.join(str(search_root), p) for p in paths]
        finally:
            os.chdir(old_cwd)
        
        # 统计信息
        total_matches = len(paths)
        file_matches = sum(1 for path in paths if os.path.isfile(path))
        dir_matches = sum(1 for path in paths if os.path.isdir(path))
        
        # 文件类型统计
        file_extensions = {}
        for path in paths:
            if os.path.isfile(path):
                ext = Path(path).suffix.lower()
                if not ext:
                    ext = "(无扩展名)"
                file_extensions[ext] = file_extensions.get(ext, 0) + 1
        
        return {
            "pattern": pattern,
            "search_root": str(search_root),
            "total_matches": total_matches,
            "file_matches": file_matches,
            "directory_matches": dir_matches,
            "file_extensions": file_extensions,
            "max_results_limit": self.max_results,
            "would_be_truncated": file_matches > self.max_results
        }
    