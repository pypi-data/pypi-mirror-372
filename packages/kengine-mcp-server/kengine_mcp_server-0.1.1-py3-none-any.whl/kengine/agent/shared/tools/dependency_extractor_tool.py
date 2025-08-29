"""
代码依赖提取工具模块

包含 DependencyExtractorTool 类，提供安全的代码依赖提取功能，使用统一的错误处理机制。
作为资深测试开发工程师实现，确保代码质量和错误处理的完整性。
"""

import json
from pathlib import Path
from typing import Dict, Any, Union, List

from .base import BasePathTool
from .exceptions import FileOperationError, PathValidationError
from .error_handler import ErrorHandler, handle_tool_errors, safe_execute
from ..decorators import prevent_duplicate_calls

from kengine.code.reader import read_dependencies
from kengine.code import support_file


class DependencyExtractorTool(BasePathTool):
    """代码依赖提取工具
    
    提供安全的代码依赖提取功能，支持多种编程语言的依赖分析。
    使用统一的错误处理机制，返回结构化的响应。
    
    功能特性：
    - 支持多种编程语言（Python、Java、JavaScript、TypeScript、C++、C#等）
    - 自动排除语言内置依赖和第三方库依赖
    - 只返回项目内部的依赖文件列表
    - 路径安全检查，确保文件在base_dir范围内
    - 统一的错误处理和中文错误信息
    - 结构化的响应格式
    """
    
    def __init__(self, base_dir: str):
        """
        初始化代码依赖提取工具
        
        Args:
            base_dir: 基础目录路径
        """
        super().__init__(base_dir)
        self.error_handler = ErrorHandler()
    
    def extract_dependencies(self, file_path: str) -> Dict[str, Any]:
        """
        提取代码依赖（新的推荐接口）- 返回结构化响应
        
        Args:
            file_path: 代码文件路径
            
        Returns:
            包含依赖文件列表或错误信息的字典
        """
        return safe_execute(
            self._extract_dependencies_internal,
            tool_name="DependencyExtractorTool",
            operation="extract_dependencies",
            file_path=file_path
        )
    
    def _extract_dependencies_internal(self, file_path: str) -> List[str]:
        """
        内部依赖提取实现
        
        Args:
            file_path: 代码文件路径
            
        Returns:
            项目内依赖文件的相对路径列表
            
        Raises:
            FileOperationError: 文件操作失败
            PathValidationError: 路径验证失败
        """
        # 验证文件路径
        validated_path = self._validate_file_path(file_path)
        
        # 检查文件是否支持依赖提取
        if not support_file(str(validated_path)):
            raise FileOperationError(
                f"不支持的文件类型，无法提取依赖: {validated_path.suffix}",
                file_path=str(validated_path),
                operation="extract_dependencies",
                tool_name=self.__class__.__name__
            )
        
        try:
            # 使用 read_dependencies 函数提取依赖
            # 传入项目根目录（base_dir）和文件路径
            dependencies = read_dependencies(str(self.base_dir), str(validated_path))
            
            # 确保返回的是列表
            if not isinstance(dependencies, list):
                dependencies = []
            
            # 过滤和标准化依赖路径
            filtered_dependencies = []
            for dep in dependencies:
                if dep and isinstance(dep, str):
                    # 确保依赖路径是相对于base_dir的相对路径
                    dep_path = Path(dep)
                    if dep_path.is_absolute():
                        try:
                            # 尝试转换为相对于base_dir的相对路径
                            relative_dep = dep_path.relative_to(self.base_dir)
                            filtered_dependencies.append(str(relative_dep))
                        except ValueError:
                            # 如果不在base_dir内，跳过
                            continue
                    else:
                        # 已经是相对路径，直接使用
                        filtered_dependencies.append(dep)
            
            return filtered_dependencies
            
        except FileNotFoundError as e:
            raise FileOperationError(
                f"文件不存在: {str(validated_path)}",
                file_path=str(validated_path),
                operation="extract_dependencies",
                tool_name=self.__class__.__name__
            ) from e
        except ValueError as e:
            error_msg = str(e)
            if "不支持的文件类型" in error_msg:
                raise FileOperationError(
                    f"不支持的文件类型: {validated_path.suffix}",
                    file_path=str(validated_path),
                    operation="extract_dependencies",
                    tool_name=self.__class__.__name__
                ) from e
            elif "无法加载语言库" in error_msg:
                raise FileOperationError(
                    f"无法加载对应的语言解析库: {validated_path.suffix}",
                    file_path=str(validated_path),
                    operation="extract_dependencies",
                    tool_name=self.__class__.__name__
                ) from e
            else:
                raise FileOperationError(
                    f"依赖提取失败: {error_msg}",
                    file_path=str(validated_path),
                    operation="extract_dependencies",
                    tool_name=self.__class__.__name__
                ) from e
        except RuntimeError as e:
            raise FileOperationError(
                f"代码解析失败: {str(e)}",
                file_path=str(validated_path),
                operation="extract_dependencies",
                tool_name=self.__class__.__name__
            ) from e
        except Exception as e:
            raise FileOperationError(
                f"依赖提取过程中发生未知错误: {str(e)}",
                file_path=str(validated_path),
                operation="extract_dependencies",
                tool_name=self.__class__.__name__
            ) from e
    
    @BasePathTool.json_compatible_input({'file_path': 'file_path'})
    @prevent_duplicate_calls(ttl=300)
    @handle_tool_errors(tool_name="DependencyExtractorTool", operation="extract_dependencies", return_format="json")
    def run(self, file_path: str) -> Union[str, Dict[str, Any]]:
        """
        提取代码依赖（保持向后兼容的接口）- 可返回JSON格式错误
        
        Args:
            file_path: 代码文件路径，支持JSON格式参数
            
        Returns:
            依赖文件列表的JSON字符串或JSON格式的错误信息
        """
        file_path = self._to_abs(file_path)
        dependencies = self._extract_dependencies_internal(file_path)
        
        # 返回JSON格式的依赖列表
        return json.dumps(dependencies, ensure_ascii=False, indent=2)
    
    def validate_file_for_dependency_extraction(self, file_path: str) -> Dict[str, Any]:
        """
        验证文件是否可以进行依赖提取 - 返回结构化响应
        
        Args:
            file_path: 文件路径
            
        Returns:
            包含验证结果的字典
        """
        return safe_execute(
            self._validate_file_for_dependency_extraction_internal,
            tool_name="DependencyExtractorTool",
            operation="validate_file",
            file_path=file_path
        )
    
    def _validate_file_for_dependency_extraction_internal(self, file_path: str) -> Dict[str, Any]:
        """
        内部文件验证方法
        
        Args:
            file_path: 文件路径
            
        Returns:
            包含验证结果的字典
        """
        # 验证文件路径
        validated_path = self._validate_file_path(file_path)
        
        # 检查文件是否支持依赖提取
        is_supported = support_file(str(validated_path))
        
        return {
            "path": str(validated_path),
            "relative_path": self._get_relative_path(validated_path),
            "file_extension": validated_path.suffix,
            "is_supported": is_supported,
            "can_extract_dependencies": is_supported,
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
            tool_name="DependencyExtractorTool",
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
            "dependency_extraction_features": {
                "project_internal_only": "只返回项目内部依赖文件",
                "exclude_builtin": "自动排除语言内置依赖",
                "exclude_third_party": "自动排除第三方库依赖",
                "relative_paths": "返回相对于项目根目录的相对路径",
                "multiple_languages": "支持多种编程语言的依赖分析"
            }
        }
    
    def analyze_dependency_statistics(self, file_path: str) -> Dict[str, Any]:
        """
        分析依赖统计信息 - 返回结构化响应
        
        Args:
            file_path: 文件路径
            
        Returns:
            包含依赖统计信息的字典
        """
        return safe_execute(
            self._analyze_dependency_statistics_internal,
            tool_name="DependencyExtractorTool",
            operation="analyze_statistics",
            file_path=file_path
        )
    
    def _analyze_dependency_statistics_internal(self, file_path: str) -> Dict[str, Any]:
        """
        内部依赖统计分析方法
        
        Args:
            file_path: 文件路径
            
        Returns:
            包含依赖统计信息的字典
        """
        # 获取依赖列表
        dependencies = self._extract_dependencies_internal(file_path)
        
        # 分析依赖统计
        stats = {
            "total_dependencies": len(dependencies),
            "dependency_files": dependencies,
            "file_types": {},
            "directory_distribution": {}
        }
        
        # 分析文件类型分布
        for dep in dependencies:
            dep_path = Path(dep)
            file_ext = dep_path.suffix.lower()
            if file_ext:
                stats["file_types"][file_ext] = stats["file_types"].get(file_ext, 0) + 1
            
            # 分析目录分布
            parent_dir = str(dep_path.parent) if dep_path.parent != Path('.') else "根目录"
            stats["directory_distribution"][parent_dir] = stats["directory_distribution"].get(parent_dir, 0) + 1
        
        return stats