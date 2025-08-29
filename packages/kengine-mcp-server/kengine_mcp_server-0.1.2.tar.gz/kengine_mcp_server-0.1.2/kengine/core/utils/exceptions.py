"""
文档生成相关的异常定义
"""

from typing import Dict, Any, Optional


class DocumentGenerationError(Exception):
    """文档生成基础异常类"""
    
    def __init__(self, message: str, error_code: str = None, context: Dict[str, Any] = None):
        super().__init__(message)
        self.error_code = error_code
        self.context = context or {}


class StrategyNotFoundError(DocumentGenerationError):
    """策略未找到异常"""
    pass


class ValidationError(DocumentGenerationError):
    """验证失败异常"""
    pass


class GenerationTimeoutError(DocumentGenerationError):
    """生成超时异常"""
    pass


class ConfigurationError(DocumentGenerationError):
    """配置错误异常"""
    pass


class SummarizeError(Exception):
    """文本总结相关异常"""
    
    def __init__(self, message: str, error_code: str = None, context: Dict[str, Any] = None):
        super().__init__(message)
        self.error_code = error_code
        self.context = context or {}