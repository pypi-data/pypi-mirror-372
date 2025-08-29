"""
语言处理器模块
包含各种编程语言的代码骨架提取处理器
"""

from .python_handler import PythonHandler
from .java_handler import JavaHandler
from .javascript_handler import JavaScriptHandler
from .go_handler import GoHandler
from .csharp_handler import CSharpHandler
from .cpp_handler import CppHandler
from .kotlin_handler import KotlinHandler

__all__ = [
    'PythonHandler',
    'JavaHandler', 
    'JavaScriptHandler',
    'GoHandler',
    'CSharpHandler',
    'CppHandler',
    'KotlinHandler'
]