"""
RAG工具函数模块

该模块包含RAG系统的便捷函数和工具方法。
"""

from typing import Any, Dict, List
from .interface import RAGService, DocumentInfo
from .factory import RAGServiceFactory

def build_rag_service(group_name: str, repo_name: str) -> RAGService:
    """
    从代码库构建知识库的便捷函数
    
    Args:
        group_name: repo group name
        repo_name: repo name
        
    Returns:
        已构建知识库的RAG服务实例
    """
    factory = RAGServiceFactory()
    rag_service = factory.create_rag_service()
    rag_service.build_knowledge_base(group_name, repo_name)
    return rag_service


def similarity_search(group_name: str, repo_name: str, kw: str, count: int=5) -> List[DocumentInfo]:
    """
    执行相似度搜索的便捷函数
    
    基于指定的仓库构建知识库，然后执行相似度搜索，返回与查询关键词最相似的文档片段。
    
    Args:
        group_name (str): 仓库组名
        repo_name (str): 仓库名称
        kw (str): 搜索关键词
        count (int): 返回结果数量，默认为5
        
    Returns:
        List[DocumentInfo]: 包含content、metadata、source、filename的相似文档列表
        
    Raises:
        ValueError: 当指定目录中未找到有效文档时抛出
        Exception: 知识库构建或搜索过程中的其他异常
    """
    service = build_rag_service(group_name, repo_name)
    return service.similarity_search(kw, count)


def do_rag(group_name: str, repo_name: str, user_question: str) -> str:
    """
    执行RAG查询的便捷函数
    
    基于指定的仓库构建知识库，然后执行检索增强生成查询，返回基于知识库内容的答案。
    
    Args:
        group_name (str): 仓库组名
        repo_name (str): 仓库名称
        user_question (str): 用户问题
        
    Returns:
        str: 基于知识库内容生成的答案
        
    Raises:
        ValueError: 当指定目录中未找到有效文档时抛出
        Exception: 知识库构建或查询执行过程中的其他异常
    """
    service = build_rag_service(group_name, repo_name)
    rag_result = service.rag(user_question)
    return rag_result['answer']