"""
基于 tree-sitter 的代码依赖分析器包

提供精确的代码分析功能，支持多种编程语言的 AST 解析和方法引用查找。
当前支持的语言：
- Java: 基于 tree-sitter-java 的精确方法引用分析

主要组件：
- TreeSitterJavaMethodAnalyzer: Java 方法引用分析器
- JavaASTParser: Java AST 解析器
- MethodReferenceResult: 方法引用结果数据结构
"""

from .java_method_analyzer import TreeSitterJavaMethodAnalyzer
from .ast_parser import JavaASTParser
from .models import MethodReferenceResult, VariableInfo, MethodCallInfo

__all__ = [
    'TreeSitterJavaMethodAnalyzer',
    'JavaASTParser', 
    'MethodReferenceResult',
    'VariableInfo',
    'MethodCallInfo'
]