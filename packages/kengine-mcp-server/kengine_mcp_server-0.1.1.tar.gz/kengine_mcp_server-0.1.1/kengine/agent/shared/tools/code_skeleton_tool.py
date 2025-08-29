"""
代码骨架提取工具模块

包含 CodeSkeletonTool 类，提供安全的代码骨架提取功能，使用统一的错误处理机制。
"""

import json
from pathlib import Path
from typing import Dict, Any, Union

from .base import BasePathTool
from .exceptions import FileOperationError, PathValidationError
from .error_handler import ErrorHandler, handle_tool_errors, safe_execute
from ..decorators import prevent_duplicate_calls

from kengine.code.skeleton import extract_skeleton, validate_file_for_skeleton_extraction
from kengine.code import support_file


class CodeSkeletonTool(BasePathTool):
    """代码骨架提取工具
    
    提供安全的代码骨架提取功能，支持多种编程语言的代码结构分析。
    使用统一的错误处理机制，返回结构化的响应。
    """
    
    def __init__(self, base_dir: str):
        """
        初始化代码骨架提取工具
        
        Args:
            base_dir: 基础目录路径
        """
        super().__init__(base_dir)
        self.error_handler = ErrorHandler()
    
    def extract_skeleton(self, file_path: str) -> Dict[str, Any]:
        """
        提取代码骨架（新的推荐接口）- 返回结构化响应
        
        Args:
            file_path: 代码文件路径
            
        Returns:
            包含代码骨架或错误信息的字典
        """
        return safe_execute(
            self._extract_skeleton_internal,
            tool_name="CodeSkeletonTool",
            operation="extract",
            file_path=file_path
        )
    
    def _extract_skeleton_internal(self, file_path: str) -> str:
        """
        内部代码骨架提取方法
        
        Args:
            file_path: 代码文件路径
            
        Returns:
            代码骨架字符串
            
        Raises:
            FileOperationError: 文件操作失败
            PathValidationError: 路径验证失败
        """
        # 验证文件路径
        validated_path = self._validate_file_path(file_path)
        
        # 检查文件是否支持骨架提取
        if not support_file(str(validated_path)):
            raise FileOperationError(
                f"不支持的文件类型，无法提取代码骨架: {validated_path.suffix}",
                file_path=str(validated_path),
                operation="extract",
                tool_name=self.__class__.__name__
            )
        
        # 验证文件是否可以进行骨架提取
        is_valid, validation_message = validate_file_for_skeleton_extraction(str(validated_path))
        if not is_valid:
            raise FileOperationError(
                f"文件验证失败: {validation_message}",
                file_path=str(validated_path),
                operation="extract",
                tool_name=self.__class__.__name__
            )
        
        try:
            # 提取代码骨架
            skeleton_code = extract_skeleton(str(validated_path))
            
            if not skeleton_code or skeleton_code.strip() == "":
                raise FileOperationError(
                    "提取的代码骨架为空，可能文件不包含可提取的代码结构",
                    file_path=str(validated_path),
                    operation="extract",
                    tool_name=self.__class__.__name__
                )
            
            return skeleton_code
            
        except Exception as e:
            if isinstance(e, FileOperationError):
                raise
            else:
                raise FileOperationError(
                    f"代码骨架提取失败: {str(e)}",
                    file_path=str(validated_path),
                    operation="extract",
                    tool_name=self.__class__.__name__
                ) from e
    
    @BasePathTool.json_compatible_input({'file_path': 'file_path'})
    @prevent_duplicate_calls(ttl=300)
    @handle_tool_errors(tool_name="CodeSkeletonTool", operation="extract", return_format="json")
    def run(self, file_path: str) -> Union[str, Dict[str, Any]]:
        """
        提取代码骨架（保持向后兼容的接口）- 可返回JSON格式错误
        
        Args:
            file_path: 代码文件路径，支持JSON格式参数
            
        Returns:
            代码骨架字符串或JSON格式的错误信息
        """
        file_path = self._to_abs(file_path)
        return self._extract_skeleton_internal(file_path)
    
    def get_supported_file_types(self) -> Dict[str, Any]:
        """
        获取支持的文件类型信息 - 返回结构化响应
        
        Returns:
            包含支持的文件类型信息的字典
        """
        return safe_execute(
            self._get_supported_file_types_internal,
            tool_name="CodeSkeletonTool",
            operation="get_supported_types"
        )
    
    def _get_supported_file_types_internal(self) -> Dict[str, Any]:
        """
        内部获取支持的文件类型方法
        
        Returns:
            包含支持的文件类型信息的字典
        """
        from kengine.code.language_loader import get_supported_file_types, get_supported_languages
        
        supported_types = get_supported_file_types()  # 这是一个列表
        supported_languages = get_supported_languages()  # 这是一个字典
        
        return {
            "supported_extensions": supported_types,
            "total_count": len(supported_types),
            "language_mapping": supported_languages
        }
    
    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """
        验证文件是否可以进行骨架提取 - 返回结构化响应
        
        Args:
            file_path: 文件路径
            
        Returns:
            包含验证结果的字典
        """
        return safe_execute(
            self._validate_file_internal,
            tool_name="CodeSkeletonTool",
            operation="validate",
            file_path=file_path
        )
    
    def _validate_file_internal(self, file_path: str) -> Dict[str, Any]:
        """
        内部文件验证方法
        
        Args:
            file_path: 文件路径
            
        Returns:
            包含验证结果的字典
        """
        # 验证文件路径
        validated_path = self._validate_file_path(file_path)
        
        # 检查文件是否支持
        is_supported = support_file(str(validated_path))
        
        # 验证文件是否可以进行骨架提取
        is_valid, validation_message = validate_file_for_skeleton_extraction(str(validated_path))
        
        return {
            "path": str(validated_path),
            "relative_path": self._get_relative_path(validated_path),
            "file_extension": validated_path.suffix,
            "is_supported": is_supported,
            "is_valid_for_extraction": is_valid,
            "validation_message": validation_message,
            "can_extract_skeleton": is_supported and is_valid
        }