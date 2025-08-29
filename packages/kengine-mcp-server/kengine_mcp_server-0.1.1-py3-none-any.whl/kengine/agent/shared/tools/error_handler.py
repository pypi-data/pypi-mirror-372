"""
统一异常处理机制模块

提供统一的错误处理装饰器和错误格式化功能。
"""

import logging
import traceback
from functools import wraps
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from kengine.config.logging_config import setup_logging

from .exceptions import (
    ToolError, PathValidationError, SecurityError, 
    FileOperationError, SearchError, ConfigurationError, 
    ServiceUnavailableError
)

setup_logging()

logger = logging.getLogger(__name__)

class ErrorCode(Enum):
    """标准错误码枚举"""
    # 通用错误
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    
    # 路径相关错误
    PATH_NOT_FOUND = "PATH_NOT_FOUND"
    PATH_INVALID = "PATH_INVALID"
    PATH_SECURITY_VIOLATION = "PATH_SECURITY_VIOLATION"
    
    # 文件操作错误
    FILE_READ_ERROR = "FILE_READ_ERROR"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    ENCODING_ERROR = "ENCODING_ERROR"
    
    # 搜索错误
    SEARCH_PATTERN_INVALID = "SEARCH_PATTERN_INVALID"
    SEARCH_EXECUTION_FAILED = "SEARCH_EXECUTION_FAILED"
    
    # 配置错误
    CONFIG_INVALID = "CONFIG_INVALID"
    CONFIG_MISSING = "CONFIG_MISSING"
    
    # 服务错误
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    SERVICE_TIMEOUT = "SERVICE_TIMEOUT"


class ErrorHandler:
    """统一错误处理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def format_error_response(
        self, 
        error: Exception, 
        tool_name: str,
        operation: str = None,
        suggestions: List[str] = None
    ) -> Dict[str, Any]:
        """
        格式化错误响应
        
        Args:
            error: 异常对象
            tool_name: 工具名称
            operation: 操作类型
            suggestions: 建议列表
            
        Returns:
            统一格式的错误响应字典
        """
        error_code, error_message, default_suggestions = self._analyze_error(error)
        
        # 合并建议
        all_suggestions = (suggestions or []) + default_suggestions
        
        response = {
            "success": False,
            "error": error_code.value,
            "message": error_message,
            "tool_name": tool_name,
            "suggestions": all_suggestions
        }
        
        # 添加操作信息
        if operation:
            response["operation"] = operation
        
        # 添加具体错误信息
        # if hasattr(error, 'path'):
        #     response["path"] = error.path
        # if hasattr(error, 'file_path'):
        #     response["file_path"] = error.file_path
        # if hasattr(error, 'pattern'):
        #     response["pattern"] = error.pattern
        # if hasattr(error, 'config_key'):
        #     response["config_key"] = error.config_key
        
        # 使用专门的工具错误日志记录器
        tool_error_logger = logging.getLogger(f"kengine.tools.{tool_name}")
        tool_error_logger.error(
            f"工具错误: {error_message}",
            exc_info=True,
            extra={
                "tool_name": tool_name,
                "error_code": error_code.value,
                "operation": operation,
                "error_type": type(error).__name__
            }
        )
        
        return response
    
    def _analyze_error(self, error: Exception) -> tuple[ErrorCode, str, List[str]]:
        """
        分析异常并返回错误码、消息和建议
        
        Args:
            error: 异常对象
            
        Returns:
            (错误码, 错误消息, 建议列表)
        """
        if isinstance(error, PathValidationError):
            if "不存在" in str(error):
                path = getattr(error, 'path', '未知路径')
                return (
                    ErrorCode.PATH_NOT_FOUND,
                    f"路径不存在: {path}",
                    [
                        "检查路径拼写是否正确",
                        "确认文件或目录是否存在",
                        "使用文件搜索工具查找相似的文件名",
                        "检查项目的实际目录结构",
                        "尝试使用相对路径而不是绝对路径",
                        "如果查找Java文件，确认包名和目录结构是否匹配"
                    ]
                )
            else:
                return (
                    ErrorCode.PATH_INVALID,
                    str(error),
                    [
                        "检查路径格式是否正确",
                        "确认路径指向的是正确的文件类型"
                    ]
                )
        
        elif isinstance(error, SecurityError):
            return (
                ErrorCode.PATH_SECURITY_VIOLATION,
                "路径访问被安全策略阻止",
                [
                    "确保访问的路径在允许的目录范围内",
                    "避免使用包含'..'的路径"
                ]
            )
        
        elif isinstance(error, FileOperationError):
            # 使用异常中的建议，如果有的话
            if hasattr(error, 'suggestions') and error.suggestions:
                suggestions = error.suggestions
            else:
                suggestions = []
            
            if "编码" in str(error) or "decode" in str(error).lower():
                return (
                    ErrorCode.ENCODING_ERROR,
                    "文件编码解析失败",
                    suggestions + [
                        "文件可能包含特殊字符或使用了不支持的编码",
                        "尝试使用文本编辑器检查文件内容",
                        "确认文件不是二进制文件"
                    ]
                )
            elif "大小超过限制" in str(error):
                return (
                    ErrorCode.FILE_TOO_LARGE,
                    str(error),
                    suggestions + [
                        "尝试读取文件的部分内容",
                        "使用文件搜索工具查找特定内容",
                        "联系管理员调整文件大小限制"
                    ]
                )
            elif "不存在" in str(error):
                return (
                    ErrorCode.PATH_NOT_FOUND,
                    str(error),
                    suggestions + [
                        "使用文件搜索工具查找相似的文件名",
                        "检查项目的实际目录结构",
                        "确认包名和目录结构是否匹配",
                        "尝试使用相对路径而不是绝对路径"
                    ]
                )
            else:
                return (
                    ErrorCode.FILE_READ_ERROR,
                    f"文件操作失败: {str(error)}",
                    suggestions + [
                        "尝试其他工具"
                    ]
                )
        
        elif isinstance(error, SearchError):
            if "模式" in str(error) and "空" in str(error):
                return (
                    ErrorCode.SEARCH_PATTERN_INVALID,
                    "搜索模式不能为空",
                    [
                        "提供有效的搜索模式",
                        "使用通配符如 *.py 搜索特定类型文件",
                        "使用 **/*.java 进行递归搜索"
                    ]
                )
            else:
                return (
                    ErrorCode.SEARCH_EXECUTION_FAILED,
                    f"搜索执行失败: {str(error)}",
                    [
                        "检查搜索模式语法是否正确",
                        "确认搜索目录存在且可访问",
                        "尝试简化搜索模式"
                    ]
                )
        
        elif isinstance(error, ConfigurationError):
            return (
                ErrorCode.CONFIG_INVALID,
                f"配置错误: {str(error)}",
                [
                    "检查配置参数是否正确",
                    "参考文档了解支持的配置选项",
                    "使用默认配置重试"
                ]
            )
        
        elif isinstance(error, ServiceUnavailableError):
            return (
                ErrorCode.SERVICE_UNAVAILABLE,
                f"服务不可用: {str(error)}",
                [
                    "检查服务是否正常运行",
                    "尝试使用其他可用的工具",
                    "联系管理员检查服务状态"
                ]
            )
        
        else:
            return (
                ErrorCode.UNKNOWN_ERROR,
                f"未知错误: {str(error)}",
                [
                    "重试操作",
                    "检查输入参数是否正确",
                    "尝试其他工具/方法"
                ]
            )
    
    def format_success_response(
        self, 
        data: Any, 
        message: str = "操作成功",
        tool_name: str = None,
        operation: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        格式化成功响应
        
        Args:
            data: 返回的数据
            message: 成功消息
            tool_name: 工具名称
            operation: 操作类型
            metadata: 额外的元数据
            
        Returns:
            统一格式的成功响应字典
        """
        response = {
            "success": True,
            "data": data,
            "message": message
        }
        
        if tool_name:
            response["tool_name"] = tool_name
        if operation:
            response["operation"] = operation
        if metadata:
            response["metadata"] = metadata
        
        return response


def handle_tool_errors(
    tool_name: str = None,
    operation: str = None,
    return_format: str = "dict",
    rethrow_exceptions: bool = False
):
    """
    工具错误处理装饰器
    
    Args:
        tool_name: 工具名称
        operation: 操作类型
        return_format: 返回格式，"dict" 或 "json"
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            error_handler = ErrorHandler()
            
            try:
                result = func(*args, **kwargs)
                
                # 如果结果已经是字典格式且包含success字段，直接返回
                if isinstance(result, dict) and "success" in result:
                    return result
                
                # 否则包装为成功响应
                if return_format == "dict":
                    return error_handler.format_success_response(
                        data=result,
                        tool_name=tool_name or func.__name__,
                        operation=operation
                    )
                else:
                    return result
                    
            except Exception as e:
                # 使用配置文件中的日志设置记录工具错误
                tool_error_logger = logging.getLogger(f"kengine.tools.{tool_name or func.__name__}")
                tool_error_logger.error(
                    f"工具执行失败: {str(e)}",
                    exc_info=True,
                    extra={
                        "tool_name": tool_name or func.__name__,
                        "operation": operation,
                        "error_type": type(e).__name__,
                        "error_message": str(e)
                    }
                )
                
                # 如果需要重新抛出异常，直接抛出
                if rethrow_exceptions:
                    raise
                
                error_response = error_handler.format_error_response(
                    error=e,
                    tool_name=tool_name or func.__name__,
                    operation=operation
                )
                
                if return_format == "json":
                    import json
                    return json.dumps(error_response, ensure_ascii=False, indent=2)
                elif return_format == "str":
                    return error_response.get("message", str(e))
                else:
                    return error_response
        
        return wrapper
    return decorator


def safe_execute(
    func: Callable,
    tool_name: str,
    operation: str = None,
    *args,
    **kwargs
) -> Dict[str, Any]:
    """
    安全执行函数，捕获异常并返回统一格式
    
    Args:
        func: 要执行的函数
        tool_name: 工具名称
        operation: 操作类型
        *args: 函数参数
        **kwargs: 函数关键字参数
        
    Returns:
        统一格式的响应字典
    """
    error_handler = ErrorHandler()
    
    try:
        result = func(*args, **kwargs)
        return error_handler.format_success_response(
            data=result,
            tool_name=tool_name,
            operation=operation
        )
    except Exception as e:
        return error_handler.format_error_response(
            error=e,
            tool_name=tool_name,
            operation=operation
        )