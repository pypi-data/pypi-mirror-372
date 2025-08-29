"""
Agent工具包初始化模块

提供完全向后兼容的导入接口，确保现有代码无需修改即可使用重构后的工具。

重构说明：
- 原 tools.py 文件已拆分为多个模块
- 所有类和功能保持完全兼容
- 新增了更强的错误处理和配置选项
- 支持多种输出格式以优化token使用
"""

# 导入所有工具类，保持向后兼容
from .base import BasePathTool
from .file_search import FileSearchTool
from .file_read import FileReadTool
from .directory_structure import DirectoryStructureTool
from .rag_search import RAGSearchTool
from .text_grep_tool import TextGrepTool
from .db_extractor_tool import DBExtractorTool
from .factory import AgentToolFactory
from .exceptions import (
    ToolError,
    PathValidationError,
    SecurityError,
    FileOperationError,
    SearchError,
    ConfigurationError,
    ServiceUnavailableError
)
__all__ = [
    # 核心工具类
    'BasePathTool',
    'FileSearchTool', 
    'FileReadTool',
    'DirectoryStructureTool',
    'RAGSearchTool',
    'TextGrepTool',
    'DBExtractorTool',
    
    # 工厂类
    'AgentToolFactory',
    
    # 异常类
    'ToolError',
    'PathValidationError',
    'SecurityError',
    'FileOperationError',
    'SearchError',
    'ConfigurationError',
    'ServiceUnavailableError'
]
