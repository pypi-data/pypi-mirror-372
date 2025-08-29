"""
数据模型包

包含知识生成系统的所有数据模型
"""

from ...db import Base, get_db_session
from ..enums import TaskStatus, ProgressStage, ProgressStatus, LLMCallType

# 新增的知识库模型
from .base import BaseModel
from .domain import Domain
from .repository import Repository
from .repository_endpoint import RepositoryEndpoint
from .repository_dependency import RepositoryDependency
from .repo_document_version import RepoDocumentVersion
from .document import Document
from .document_comment import DocumentComment
from .document_history import DocumentHistory

__all__ = [
    # 数据库基础
    'Base',
    'get_db_session',
    
    # 知识库模型
    'BaseModel',
    'Domain',
    'Repository',
    'RepositoryEndpoint',
    'RepositoryDependency',
    'RepoDocumentVersion',
    'Document',
    'DocumentComment',
    'DocumentHistory',
]