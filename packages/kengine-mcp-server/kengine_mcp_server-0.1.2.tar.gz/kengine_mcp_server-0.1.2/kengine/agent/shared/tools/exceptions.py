"""
Agent工具自定义异常模块

定义工具相关的自定义异常类，提供更精确的错误处理和诊断信息。
"""


class ToolError(Exception):
    """工具基础异常类"""
    
    def __init__(self, message: str, tool_name: str = None, details: dict = None):
        """
        初始化工具异常
        
        Args:
            message: 错误消息
            tool_name: 工具名称
            details: 额外的错误详情
        """
        super().__init__(message)
        self.tool_name = tool_name
        self.details = details or {}
    
    def __str__(self):
        if self.tool_name:
            return f"[{self.tool_name}] {super().__str__()}"
        return super().__str__()


class PathValidationError(ToolError):
    """路径验证异常"""
    
    def __init__(self, message: str, path: str = None, tool_name: str = None):
        """
        初始化路径验证异常
        
        Args:
            message: 错误消息
            path: 导致错误的路径
            tool_name: 工具名称
        """
        super().__init__(message, tool_name)
        self.path = path


class SecurityError(ToolError):
    """安全性异常"""
    
    def __init__(self, message: str, path: str = None, tool_name: str = None):
        """
        初始化安全性异常
        
        Args:
            message: 错误消息
            path: 导致安全问题的路径
            tool_name: 工具名称
        """
        super().__init__(message, tool_name)
        self.path = path


class FileOperationError(ToolError):
    """文件操作异常"""
    
    def __init__(self, message: str, file_path: str = None, operation: str = None, tool_name: str = None, suggestions: list = None):
        """
        初始化文件操作异常
        
        Args:
            message: 错误消息
            file_path: 操作的文件路径
            operation: 操作类型（read, write, search等）
            tool_name: 工具名称
            suggestions: 解决建议列表
        """
        super().__init__(message, tool_name)
        self.file_path = file_path
        self.operation = operation
        self.suggestions = suggestions or []


class SearchError(ToolError):
    """搜索操作异常"""
    
    def __init__(self, message: str, pattern: str = None, search_root: str = None, tool_name: str = None):
        """
        初始化搜索异常
        
        Args:
            message: 错误消息
            pattern: 搜索模式
            search_root: 搜索根目录
            tool_name: 工具名称
        """
        super().__init__(message, tool_name)
        self.pattern = pattern
        self.search_root = search_root


class ConfigurationError(ToolError):
    """配置异常"""
    
    def __init__(self, message: str, config_key: str = None, config_value: str = None, tool_name: str = None):
        """
        初始化配置异常
        
        Args:
            message: 错误消息
            config_key: 配置键
            config_value: 配置值
            tool_name: 工具名称
        """
        super().__init__(message, tool_name)
        self.config_key = config_key
        self.config_value = config_value


class ServiceUnavailableError(ToolError):
    """服务不可用异常"""
    
    def __init__(self, message: str, service_name: str = None, tool_name: str = None):
        """
        初始化服务不可用异常
        
        Args:
            message: 错误消息
            service_name: 服务名称
            tool_name: 工具名称
        """
        super().__init__(message, tool_name)
        self.service_name = service_name