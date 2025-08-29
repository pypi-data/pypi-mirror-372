"""
代码方法提取工具模块

包含 MethodExtractorTool 类，提供安全的代码方法提取功能，使用统一的错误处理机制。
作为资深测试开发工程师实现，确保代码质量和错误处理的完整性。
"""

import json
from pathlib import Path
from typing import Dict, Any, Union, List

from .base import BasePathTool
from .exceptions import FileOperationError, PathValidationError
from .error_handler import ErrorHandler, handle_tool_errors, safe_execute
from ..decorators import prevent_duplicate_calls

from kengine.code.reader import read_method
from kengine.code import support_file


class MethodExtractorTool(BasePathTool):
    """代码方法提取工具
    
    提供安全的代码方法提取功能，支持多种编程语言的方法提取。
    使用统一的错误处理机制，返回结构化的响应。
    
    功能特性：
    - 支持多种编程语言（Python、Java、JavaScript、TypeScript、C++、C#等）
    - 支持精确参数匹配和模糊方法名匹配
    - 路径安全检查，确保文件在base_dir范围内
    - 统一的错误处理和中文错误信息
    - 结构化的响应格式
    """
    
    def __init__(self, base_dir: str):
        """
        初始化代码方法提取工具
        
        Args:
            base_dir: 基础目录路径
        """
        super().__init__(base_dir)
        self.error_handler = ErrorHandler()
    
    def extract_method(self, file_path: str, method_name: str, arg_types: List[str] = None) -> Dict[str, Any]:
        """
        提取代码方法（新的推荐接口）- 返回结构化响应
        
        Args:
            file_path: 代码文件路径
            method_name: 方法名称
            arg_types: 参数类型列表，为空时取第一个匹配方法名的方法
            
        Returns:
            包含方法代码或错误信息的字典
        """
        return safe_execute(
            self._extract_method_internal,
            tool_name="MethodExtractorTool",
            operation="extract_method",
            file_path=file_path,
            method_name=method_name,
            arg_types=arg_types
        )
    
    def _extract_method_internal(self, file_path: str, method_name: str, arg_types: List[str] = None) -> str:
        """
        内部方法提取实现
        
        Args:
            file_path: 代码文件路径
            method_name: 方法名称
            arg_types: 参数类型列表
            
        Returns:
            方法的完整代码字符串
            
        Raises:
            FileOperationError: 文件操作失败
            PathValidationError: 路径验证失败
        """
        # 验证输入参数
        if not method_name or not method_name.strip():
            raise FileOperationError(
                "方法名称不能为空",
                file_path=file_path,
                operation="extract_method",
                tool_name=self.__class__.__name__
            )
        
        method_name = method_name.strip()
        
        # 验证文件路径
        validated_path = self._validate_file_path(file_path)
        
        # 检查文件是否支持方法提取
        if not support_file(str(validated_path)):
            raise FileOperationError(
                f"不支持的文件类型，无法提取方法: {validated_path.suffix}",
                file_path=str(validated_path),
                operation="extract_method",
                tool_name=self.__class__.__name__
            )
        
        try:
            # 使用 read_method 函数提取方法
            method_code = read_method(str(validated_path), method_name, arg_types)
            
            if not method_code or method_code.strip() == "":
                if arg_types:
                    raise FileOperationError(
                        f"未找到匹配的方法: {method_name}({', '.join(arg_types)})",
                        file_path=str(validated_path),
                        operation="extract_method",
                        tool_name=self.__class__.__name__
                    )
                else:
                    raise FileOperationError(
                        f"未找到方法: {method_name}",
                        file_path=str(validated_path),
                        operation="extract_method",
                        tool_name=self.__class__.__name__
                    )
            
            return method_code
            
        except FileNotFoundError as e:
            # 提供更详细的错误信息和建议
            error_msg = f"文件不存在: {str(validated_path)}"
            suggestions = [
                "使用文件搜索工具查找相似的文件名",
                "检查项目的实际目录结构",
                "确认包名和目录结构是否匹配",
                "尝试使用相对路径而不是绝对路径"
            ]
            
            # 如果是Java文件，提供额外的建议
            if str(validated_path).endswith('.java'):
                suggestions.extend([
                    "Java文件的包名应该与目录结构一致",
                    "检查是否在正确的模块目录下查找",
                    "使用 'find . -name \"*.java\" | grep -i methodname' 查找文件"
                ])
            
            raise FileOperationError(
                error_msg,
                file_path=str(validated_path),
                operation="extract_method",
                tool_name=self.__class__.__name__,
                suggestions=suggestions
            ) from e
        except ValueError as e:
            error_msg = str(e)
            if "不支持的文件类型" in error_msg:
                raise FileOperationError(
                    f"不支持的文件类型: {validated_path.suffix}",
                    file_path=str(validated_path),
                    operation="extract_method",
                    tool_name=self.__class__.__name__
                ) from e
            elif "未找到方法" in error_msg:
                raise FileOperationError(
                    error_msg,
                    file_path=str(validated_path),
                    operation="extract_method",
                    tool_name=self.__class__.__name__
                ) from e
            else:
                raise FileOperationError(
                    f"方法提取失败: {error_msg}",
                    file_path=str(validated_path),
                    operation="extract_method",
                    tool_name=self.__class__.__name__
                ) from e
        except RuntimeError as e:
            raise FileOperationError(
                f"代码解析失败: {str(e)}",
                file_path=str(validated_path),
                operation="extract_method",
                tool_name=self.__class__.__name__
            ) from e
        except Exception as e:
            raise FileOperationError(
                f"方法提取过程中发生未知错误: {str(e)}",
                file_path=str(validated_path),
                operation="extract_method",
                tool_name=self.__class__.__name__
            ) from e
    
    @BasePathTool.json_compatible_input({'file_path': 'file_path', 'method_name': 'method_name', 'arg_types': 'arg_types'})
    @prevent_duplicate_calls(ttl=300)
    @handle_tool_errors(tool_name="MethodExtractorTool", operation="extract_method", return_format="json")
    def run(self, file_path: str, method_name: str = None, arg_types: str = None) -> Union[str, Dict[str, Any]]:
        """
        提取代码方法（保持向后兼容的接口）- 可返回JSON格式错误
        
        Args:
            file_path: 代码文件路径，支持JSON格式参数
            method_name: 方法名称（可选，用于非JSON格式调用）
            arg_types: 参数类型列表的JSON字符串（可选）
            
        Returns:
            方法代码字符串或JSON格式的错误信息
        """
        # 验证必需参数
        if not method_name:
            raise FileOperationError(
                "方法名称参数不能为空",
                file_path=file_path,
                operation="extract_method",
                tool_name=self.__class__.__name__
            )
        
        # 处理参数类型列表
        parsed_arg_types = None
        if arg_types:
            if isinstance(arg_types, str):
                try:
                    # 尝试解析JSON格式的参数类型列表
                    if arg_types.strip().startswith('['):
                        parsed_arg_types = json.loads(arg_types)
                    else:
                        # 简单的逗号分隔格式
                        parsed_arg_types = [t.strip() for t in arg_types.split(',') if t.strip()]
                except json.JSONDecodeError:
                    # 如果JSON解析失败，尝试逗号分隔
                    parsed_arg_types = [t.strip() for t in arg_types.split(',') if t.strip()]
            elif isinstance(arg_types, list):
                parsed_arg_types = arg_types
        
        file_path = self._to_abs(file_path)
        return self._extract_method_internal(file_path, method_name, parsed_arg_types)
    
    def validate_file_for_method_extraction(self, file_path: str) -> Dict[str, Any]:
        """
        验证文件是否可以进行方法提取 - 返回结构化响应
        
        Args:
            file_path: 文件路径
            
        Returns:
            包含验证结果的字典
        """
        return safe_execute(
            self._validate_file_for_method_extraction_internal,
            tool_name="MethodExtractorTool",
            operation="validate_file",
            file_path=file_path
        )
    
    def _validate_file_for_method_extraction_internal(self, file_path: str) -> Dict[str, Any]:
        """
        内部文件验证方法
        
        Args:
            file_path: 文件路径
            
        Returns:
            包含验证结果的字典
        """
        # 验证文件路径
        validated_path = self._validate_file_path(file_path)
        
        # 检查文件是否支持方法提取
        is_supported = support_file(str(validated_path))
        
        return {
            "path": str(validated_path),
            "relative_path": self._get_relative_path(validated_path),
            "file_extension": validated_path.suffix,
            "is_supported": is_supported,
            "can_extract_methods": is_supported,
            "supported_languages": [
                "Python (.py)", "Java (.java)", "JavaScript (.js)", 
                "TypeScript (.ts)", "C++ (.cpp, .cc, .cxx)", 
                "C# (.cs)", "C (.c)", "Go (.go)"
            ]
        }
    
    def get_supported_languages(self) -> Dict[str, Any]:
        """
        获取支持的编程语言信息 - 返回结构化响应
        
        Returns:
            包含支持的编程语言信息的字典
        """
        return safe_execute(
            self._get_supported_languages_internal,
            tool_name="MethodExtractorTool",
            operation="get_supported_languages"
        )
    
    def _get_supported_languages_internal(self) -> Dict[str, Any]:
        """
        内部获取支持的编程语言方法
        
        Returns:
            包含支持的编程语言信息的字典
        """
        from kengine.code.language_loader import get_supported_file_types, get_supported_languages
        
        supported_types = get_supported_file_types()
        supported_languages = get_supported_languages()
        
        return {
            "supported_extensions": supported_types,
            "total_count": len(supported_types),
            "language_mapping": supported_languages,
            "method_extraction_features": {
                "parameter_matching": "支持精确参数类型匹配",
                "fuzzy_matching": "支持模糊方法名匹配",
                "multiple_overloads": "支持方法重载识别",
                "static_methods": "支持静态方法提取",
                "class_methods": "支持类方法提取"
            }
        }