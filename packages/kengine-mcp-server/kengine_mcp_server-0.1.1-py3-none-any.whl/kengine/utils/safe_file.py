"""
文件操作安全包装器模块

提供统一的文件操作错误处理装饰器，用于包装文件相关操作，
提供更好的错误信息和异常处理。

重构历史:
- 从 kengine.core.types 模块重构而来，提供更好的模块组织
"""

from typing import Callable, TypeVar
import logging
import functools

# 定义类型变量
T = TypeVar('T')


def safe_file_operation(operation_name: str = "文件操作"):
    """
    文件操作安全包装器装饰器
    
    Args:
        operation_name: 操作名称，用于错误日志
    
    Returns:
        装饰器函数
        
    Example:
        @safe_file_operation("读取配置文件")
        def read_config(file_path: str):
            with open(file_path, 'r') as f:
                return f.read()
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            logger = logging.getLogger(func.__module__)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 根据异常类型提供不同的错误信息
                if isinstance(e, (OSError, IOError)):
                    error_msg = f"{operation_name}失败: {e}"
                elif isinstance(e, PermissionError):
                    error_msg = f"{operation_name}权限不足: {e}"
                elif isinstance(e, FileNotFoundError):
                    error_msg = f"{operation_name}文件未找到: {e}"
                elif isinstance(e, ValueError):
                    error_msg = f"{operation_name}参数错误: {e}"
                else:
                    # 对于其他异常，保持原始异常类型
                    error_msg = f"{operation_name}出现异常: {e}"
                
                logger.error(error_msg)
                # 保持原始异常类型，但提供更好的错误信息
                raise type(e)(error_msg) from e
        return wrapper
    return decorator