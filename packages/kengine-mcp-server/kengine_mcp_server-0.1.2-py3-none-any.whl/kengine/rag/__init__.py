"""
RAG (Retrieval-Augmented Generation) 模块

该模块提供完整的RAG功能，包括：
- 配置管理
- 文档处理
- 向量存储管理
- 检索服务
- 便捷工具函数

重构后的模块化设计，提供更好的可维护性和扩展性。
"""

from .interface import RAGService

# 提供默认工厂实例
from .utils import build_rag_service, similarity_search, do_rag

__all__ = [
    'RAGService',
    'build_rag_service',
    'similarity_search', 
    'do_rag'
]