"""
文件读取工具模块 - 重构版本

包含 FileReadTool 类，提供安全的文件读取功能，使用统一的错误处理机制。
"""

import json
import chardet
import glob
import os
from pathlib import Path
from typing import List, Dict, Any, Union, Optional

from .base import BasePathTool
from .exceptions import FileOperationError
from .error_handler import ErrorHandler, handle_tool_errors, safe_execute
from ..decorators import prevent_duplicate_calls

from kengine.config.application_config import get_application_config
from kengine.config.file_extensions import is_document_file, is_programming_file


class FileReadTool(BasePathTool):
    """文件读取工具 - 重构版本
    
    提供安全的文件读取功能，支持自动编码检测和多种编码回退机制。
    使用统一的错误处理机制，返回结构化的响应。
    """
    
    def __init__(self, base_dir: str):
        """
        初始化文件读取工具
        
        Args:
            base_dir: 基础目录路径
        """
        super().__init__(base_dir)
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.fallback_encodings = ['utf-8', 'gbk', 'latin-1', 'cp1252']
        self.error_handler = ErrorHandler()
        config = get_application_config().get('tools').get('fileRead')
        self.compress_thrshold = config.get('compressThrshold', 100000)
        self.compress_target_size = config.get('compressTargetSize' , 1000)
    
    def _detect_encoding(self, file_path: Path) -> str:
        """
        检测文件编码
        
        Args:
            file_path: 文件路径
            
        Returns:
            检测到的编码名称
        """
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # 读取前10KB用于编码检测
                result = chardet.detect(raw_data)
                encoding = result.get('encoding', 'utf-8')
                confidence = result.get('confidence', 0)
                
                # 如果置信度太低，使用UTF-8作为默认编码
                if confidence < 0.7:
                    encoding = 'utf-8'
                    
                return encoding
        except Exception:
            return 'utf-8'
    
    def _read_file_with_encoding(self, file_path: Path, encoding: str) -> str:
        """
        使用指定编码读取文件
        
        Args:
            file_path: 文件路径
            encoding: 编码名称
            
        Returns:
            文件内容
            
        Raises:
            UnicodeDecodeError: 编码解码失败
        """
        return file_path.read_text(encoding=encoding)
    
    def _read_file_with_fallback(self, file_path: Path) -> str:
        """
        使用回退编码机制读取文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容
            
        Raises:
            FileOperationError: 所有编码都失败
        """
        # 首先尝试自动检测的编码
        detected_encoding = self._detect_encoding(file_path)
        
        try:
            return self._read_file_with_encoding(file_path, detected_encoding)
        except UnicodeDecodeError:
            pass
        
        # 尝试回退编码列表
        for fallback_encoding in self.fallback_encodings:
            if fallback_encoding != detected_encoding:
                try:
                    return self._read_file_with_encoding(file_path, fallback_encoding)
                except UnicodeDecodeError:
                    continue
        
        # 所有编码都失败
        raise FileOperationError(
            "无法解码文件内容，尝试了所有支持的编码",
            file_path=str(file_path),
            operation="read",
            tool_name=self.__class__.__name__
        )
    
    def _validate_file_size(self, file_path: Path) -> None:
        """
        验证文件大小是否在允许范围内
        
        Args:
            file_path: 文件路径
            
        Raises:
            FileOperationError: 文件大小超过限制
        """
        file_size = file_path.stat().st_size
        if file_size > self.max_file_size:
            raise FileOperationError(
                f"文件大小超过限制 ({self.max_file_size} bytes)，当前大小: {file_size} bytes",
                file_path=str(file_path),
                operation="read",
                tool_name=self.__class__.__name__
            )
    
    def read_file(self, file_path: str) -> Dict[str, Any]:
        """
        读取文件内容（新的推荐接口）- 返回结构化响应
        
        Args:
            file_path: 文件路径
            
        Returns:
            包含文件内容或错误信息的字典
        """
        return safe_execute(
            self._read_file_internal,
            tool_name="FileReadTool",
            operation="read",
            file_path=file_path
        )
    
    def _read_file_internal(self, file_path: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
        """
        内部文件读取方法
        
        Args:
            file_path: 文件路径
            start_line: 起始行号（从1开始，可选）
            end_line: 结束行号（包含该行，可选）
            
        Returns:
            文件内容字符串
            
        Raises:
            FileOperationError: 文件读取失败
        """
        # ai model 传进来的地址可能不对， 偶发现象是 传递文件路径文件名正确， 路径不全对
        # 兼容错误： 判断 file_path 对应文件是否存在， 若不存在， 从 file_path 获得文件名， 通过 glob 模块在 base_dir
        # 下搜索文件， 若存在， 且只有一个 返回 该文件地址
        # 若存在多个同名文件， 或不存在， 抛出文件不存在异常
        
        # 首先尝试验证原始文件路径
        try:
            validated_path = self._validate_file_path(file_path)
        except FileOperationError:
            # 如果原始路径验证失败，尝试兼容错误处理
            validated_path = self._handle_path_compatibility_error(file_path)
        
        # 检查文件大小限制
        self._validate_file_size(validated_path)
        
        # 使用回退编码机制读取文件
        content = self._read_file_with_fallback(validated_path)
        
        # 如果指定了行范围，则按行范围读取，不进行压缩
        if start_line is not None or end_line is not None:
            return self._extract_line_range(content, start_line, end_line)
        
        # 原有的压缩逻辑（仅在未指定行范围时执行）
        if len(content) > self.compress_thrshold:
            from kengine.core.utils.file_summerize import summerize_file
            content = summerize_file(str(validated_path),  content, self.compress_target_size)
        return content
    
    def _handle_path_compatibility_error(self, file_path: str) -> Path:
        """
        处理路径兼容性错误，通过文件名在base_dir下搜索文件
        
        Args:
            file_path: 原始文件路径
            
        Returns:
            找到的正确文件路径
            
        Raises:
            FileOperationError: 文件不存在或存在多个同名文件
        """
        # 从文件路径中提取文件名
        filename = os.path.basename(file_path)
        
        if not filename:
            raise FileOperationError(
                f"无法从路径中提取文件名: {file_path}",
                file_path=file_path,
                operation="read",
                tool_name=self.__class__.__name__
            )
        
        # 在base_dir下递归搜索同名文件
        search_pattern = os.path.join(self.base_dir, "**", filename)
        matching_files = glob.glob(search_pattern, recursive=True)
        
        if not matching_files:
            raise FileOperationError(
                f"在目录 {self.base_dir} 下未找到文件: {filename}",
                file_path=file_path,
                operation="read",
                tool_name=self.__class__.__name__
            )
        
        if len(matching_files) > 1:
            # 存在多个同名文件，列出所有找到的文件路径
            files_list = "\n".join([f"  - {f}" for f in matching_files])
            raise FileOperationError(
                f"在目录 {self.base_dir} 下找到多个同名文件 {filename}:\n{files_list}\n请指定完整路径",
                file_path=file_path,
                operation="read",
                tool_name=self.__class__.__name__
            )
        
        # 只有一个匹配文件，返回该文件路径
        found_file_path = matching_files[0]
        
        # 验证找到的文件路径是否有效
        validated_path = Path(found_file_path)
        if not validated_path.exists():
            raise FileOperationError(
                f"找到的文件路径无效: {found_file_path}",
                file_path=file_path,
                operation="read",
                tool_name=self.__class__.__name__
            )
        
        if not validated_path.is_file():
            raise FileOperationError(
                f"找到的路径不是文件: {found_file_path}",
                file_path=file_path,
                operation="read",
                tool_name=self.__class__.__name__
            )
        
        return validated_path
    
    def _extract_line_range(self, content: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
        """
        从文件内容中提取指定行范围的内容
        
        Args:
            content: 完整的文件内容
            start_line: 起始行号（从1开始，可选）
            end_line: 结束行号（包含该行，可选）
            
        Returns:
            指定行范围的内容字符串
            
        Raises:
            FileOperationError: 行号参数无效
        """
        if not content:
            return content
            
        lines = content.splitlines(keepends=True)
        total_lines = len(lines)
        
        # 参数验证和边界处理
        if start_line is not None:
            if start_line < 1:
                raise FileOperationError(
                    f"起始行号必须大于等于1，当前值: {start_line}",
                    operation="read",
                    tool_name=self.__class__.__name__
                )
            # 如果起始行号超过文件总行数，返回空字符串
            if start_line > total_lines:
                return ""
        else:
            start_line = 1
            
        if end_line is not None:
            if end_line < 1:
                raise FileOperationError(
                    f"结束行号必须大于等于1，当前值: {end_line}",
                    operation="read",
                    tool_name=self.__class__.__name__
                )
            # 如果结束行号超过文件总行数，调整为文件总行数
            if end_line > total_lines:
                end_line = total_lines
        else:
            end_line = total_lines
            
        # 验证行号范围的逻辑性
        if start_line > end_line:
            raise FileOperationError(
                f"起始行号({start_line})不能大于结束行号({end_line})",
                operation="read",
                tool_name=self.__class__.__name__
            )
        
        # 提取指定范围的行（转换为0基索引）
        start_idx = start_line - 1
        end_idx = end_line
        
        selected_lines = lines[start_idx:end_idx]
        return ''.join(selected_lines)
    
    @BasePathTool.json_compatible_input({'file_path': 'file_path', 'start_line': 'start_line', 'end_line': 'end_line'})
    @prevent_duplicate_calls(ttl=300)
    @handle_tool_errors(tool_name="FileReadTool", operation="read", return_format="dict")
    def run(self, file_path: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> Union[str, Dict[str, Any]]:
        """
        读取文件内容（保持向后兼容的接口）- 可返回JSON格式错误
        
        Args:
            file_path: 文件路径，支持JSON格式参数
            start_line: 起始行号（从1开始，可选）
            end_line: 结束行号（包含该行，可选）
            
        Returns:
            文件内容字符串或JSON格式的错误信息
        """
        # 判断文件类型， 支持 代码文件 或 文档类型， 其他类型返回错误
        file_extension = Path(file_path).suffix.lower()
        
        # 检查文件类型是否为支持的类型（代码文件或文档文件）
        if not (is_programming_file(file_extension) or is_document_file(file_extension)):
            raise FileOperationError(
                f"不支持的文件类型: '{file_extension}'仅支持代码文件和文档文件",
                file_path=file_path,
                operation="read",
                tool_name=self.__class__.__name__
            )
        
        file_path = self._to_abs(file_path)
        return self._read_file_internal(file_path, start_line, end_line)
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        获取文件信息（不读取内容）- 返回结构化响应
        
        Args:
            file_path: 文件路径
            
        Returns:
            包含文件信息或错误信息的字典
        """
        return safe_execute(
            self._get_file_info_internal,
            tool_name="FileReadTool",
            operation="info",
            file_path=file_path
        )
    
    def _get_file_info_internal(self, file_path: str) -> Dict[str, Any]:
        """
        内部获取文件信息方法
        
        Args:
            file_path: 文件路径
            
        Returns:
            包含文件信息的字典
        """
        validated_path = self._validate_file_path(file_path)
        stat_info = validated_path.stat()
        detected_encoding = self._detect_encoding(validated_path)
        
        return {
            "path": str(validated_path),
            "relative_path": self._get_relative_path(validated_path),
            "size": stat_info.st_size,
            "size_readable": self._format_file_size(stat_info.st_size),
            "detected_encoding": detected_encoding,
            "is_readable": stat_info.st_size <= self.max_file_size,
            "max_size_limit": self.max_file_size,
            "modified_time": stat_info.st_mtime
        }
    
    def _format_file_size(self, size_bytes: int) -> str:
        """
        格式化文件大小为可读格式
        
        Args:
            size_bytes: 文件大小（字节）
            
        Returns:
            格式化后的文件大小字符串
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def set_max_file_size(self, max_size: int) -> Dict[str, Any]:
        """
        设置最大文件大小限制 - 返回结构化响应
        
        Args:
            max_size: 最大文件大小（字节）
            
        Returns:
            操作结果字典
        """
        try:
            if max_size <= 0:
                return self.error_handler.format_error_response(
                    ValueError("最大文件大小必须大于0"),
                    tool_name="FileReadTool",
                    operation="set_max_file_size"
                )
            
            old_size = self.max_file_size
            self.max_file_size = max_size
            
            return self.error_handler.format_success_response(
                data={
                    "old_max_size": old_size,
                    "new_max_size": max_size,
                    "old_max_size_readable": self._format_file_size(old_size),
                    "new_max_size_readable": self._format_file_size(max_size)
                },
                message=f"最大文件大小限制已更新为 {self._format_file_size(max_size)}",
                tool_name="FileReadTool",
                operation="set_max_file_size"
            )
        except Exception as e:
            return self.error_handler.format_error_response(
                e,
                tool_name="FileReadTool",
                operation="set_max_file_size"
            )
    
    def get_supported_encodings(self) -> List[str]:
        """
        获取支持的编码列表
        
        Returns:
            支持的编码名称列表
        """
        return self.fallback_encodings.copy()
    
    def add_fallback_encoding(self, encoding: str) -> Dict[str, Any]:
        """
        添加回退编码 - 返回结构化响应
        
        Args:
            encoding: 编码名称
            
        Returns:
            操作结果字典
        """
        try:
            if encoding in self.fallback_encodings:
                return self.error_handler.format_success_response(
                    data={"encodings": self.fallback_encodings},
                    message=f"编码 '{encoding}' 已存在于回退列表中",
                    tool_name="FileReadTool",
                    operation="add_fallback_encoding"
                )
            
            self.fallback_encodings.append(encoding)
            
            return self.error_handler.format_success_response(
                data={
                    "added_encoding": encoding,
                    "all_encodings": self.fallback_encodings
                },
                message=f"已添加回退编码: {encoding}",
                tool_name="FileReadTool",
                operation="add_fallback_encoding"
            )
        except Exception as e:
            return self.error_handler.format_error_response(
                e,
                tool_name="FileReadTool",
                operation="add_fallback_encoding"
            )
    