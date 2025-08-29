"""
RAG服务抽象接口模块

该模块定义了RAG系统的抽象接口，规范了RAG服务应该提供的核心业务功能。

设计原则：
- 接口与具体技术实现无关（如 FAISS、向量存储等）
- 只抽象核心的业务功能，不包含实现细节
- 保持接口的通用性和可扩展性
- 支持不同的RAG实现方式

核心功能：
- 知识库构建
- 检索增强生成查询
- 相似度搜索
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


# 数据类定义，用于更准确的类型注解

@dataclass
class DocumentInfo:
    """文档信息数据类"""
    content: str
    metadata: Dict[str, Any]
    source: str
    filename: str


@dataclass
class SourceDocument:
    """源文档数据类，用于RAG查询结果"""
    content: str
    source: str
    filename: str
    chunk_id: int = 0


@dataclass
class RAGQueryResult:
    """RAG查询结果数据类"""
    question: str
    answer: str
    source_documents: List[SourceDocument]
    num_sources: int


# 类型别名
SimilaritySearchResult = List[DocumentInfo]

class RAGService(ABC):
    """RAG服务抽象接口
    
    定义了RAG系统的核心业务功能接口。该接口与具体的技术实现无关，
    专注于抽象RAG系统应该提供的业务能力。
    
    设计原则：
    - 技术无关性：不依赖特定的向量存储、嵌入模型或检索技术
    - 业务导向：专注于用户需要的核心功能
    - 简洁性：只包含必要的抽象方法
    - 扩展性：支持不同的RAG实现策略
    """
    
    # ==================== 知识库管理接口 ====================
    
    @abstractmethod
    def build_knowledge_base(self, group_name: str, repo_name: Optional[str] = None) -> None:
        """
        构建知识库
        
        这是一个业务级别的抽象方法，不涉及具体的存储技术实现。
        具体实现可以选择任何合适的向量存储、文档处理和索引技术。
        
        Args:
            group_name: 仓库组名
            repo_name: 仓库名称（可选）
            
        Raises:
            ValueError: 当目录中未找到有效文档时
            Exception: 构建过程中的其他异常
        """
        pass
    
    
    @abstractmethod
    def rag(self, question: str) -> RAGQueryResult:
        """
        执行检索增强生成查询
        
        这是RAG系统的核心业务功能，通过检索相关文档来增强生成答案的质量。
        具体实现可以使用任何检索技术和生成模型。
        
        Args:
            question: 用户问题
            
        Returns:
            RAGQueryResult: 包含以下字段的结果对象：
                - question: 原始问题
                - answer: 生成的答案
                - source_documents: 相关文档列表 (List[SourceDocument])
                - num_sources: 源文档数量
                
        Raises:
            ValueError: 知识库未初始化时
            Exception: 查询执行失败时
        """
        pass
    
    @abstractmethod
    def similarity_search(self, query: str, k: int = 20) -> SimilaritySearchResult:
        """
        执行相似度搜索
        
        提供基于语义相似度的文档检索功能。具体实现可以使用任何
        相似度计算方法和检索算法。
        
        Args:
            query: 查询文本
            k: 返回结果数量，默认20
            
        Returns:
            SimilaritySearchResult: 相似文档列表 (List[DocumentInfo])，每个文档包含：
                - content: 文档内容
                - metadata: 元数据信息
                - source: 文档来源
                - filename: 文件名
                
        Raises:
            ValueError: 知识库未初始化时
            Exception: 搜索过程中的其他异常
        """
        pass
    



