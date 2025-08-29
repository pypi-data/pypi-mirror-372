"""
Vearch RAG服务模块

该模块包含基于Vearch向量数据库的RAG系统核心服务类，提供完整的RAG功能：
- 知识库构建和加载
- 检索链构建
- 查询和相似度搜索
- 统计信息获取
"""

import os
import logging
import threading
from typing import List, Optional, Dict, Any

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from ...tasks.llm import init_llm
from ...utils.prompt_loader import load_custom_prompt
from ..config import RAGConfigManager
from kengine.rag.shared.document_processor import DocumentProcessor
from .vector_store import VearchVectorStoreManager
from ..interface import RAGService, RAGQueryResult, SimilaritySearchResult, SourceDocument, DocumentInfo

logger = logging.getLogger(__name__)


class VearchRAGService(RAGService):
    """基于Vearch的RAG检索服务类"""
    
    # 类级别的缓存，跨实例共享
    _knowledge_base_cache = {}  # 缓存已构建的知识库状态
    _cache_lock = threading.RLock()  # 线程安全锁
    
    def __init__(self):
        self.config = RAGConfigManager()
        self.document_processor = DocumentProcessor()
        self.vector_store_manager = VearchVectorStoreManager()
        self.llm = init_llm(self.config.search_model_options())
        
        # 创建提示模板 - 从模板文件加载
        template_text = load_custom_prompt('rag', 'default')
        
        self.prompt_template = ChatPromptTemplate.from_template(template_text)
        
        self.output_parser = StrOutputParser()
        self._chain = None
        self._current_cache_key = None  # 当前实例加载的知识库缓存键
        
        logger.info("VearchRAGService初始化完成")
        logger.info(f"Vearch配置 - Router: {self.vector_store_manager.router_server}")
        logger.info(f"数据库: {self.vector_store_manager.db_name}, 空间: {self.vector_store_manager.space_name}")
    
    def build_knowledge_base(self, group_name: str, repo_name: Optional[str] = None) -> None:
        """
        构建基于Vearch的知识库（支持内存缓存）
        
        Args:
            group_name: 仓库组名
            repo_name: 仓库名称（可选）
        """
        
        directory_path = f".cloned-repo/{group_name}/{repo_name}"
        save_path = f".kb-vearch/{group_name}/{repo_name}"
        
        # 生成缓存键
        cache_key = f"vearch:{group_name}:{repo_name}" if repo_name else f"vearch:{group_name}"
        
        logger.info(f"开始构建Vearch知识库，目录: {directory_path}, 缓存键: {cache_key}")
        
        # 检查内存缓存
        with VearchRAGService._cache_lock:
            if cache_key in VearchRAGService._knowledge_base_cache:
                cached_data = VearchRAGService._knowledge_base_cache[cache_key]
                logger.info(f"从内存缓存加载Vearch知识库: {cache_key}")
                
                # 从缓存恢复向量存储管理器状态
                self.vector_store_manager = cached_data['vector_store_manager']
                
                # 构建检索链
                self._build_retrieval_chain()
                self._current_cache_key = cache_key
                
                logger.info("从内存缓存加载Vearch知识库完成")
                return
        
        # 检查磁盘缓存（Vearch元数据）
        if save_path and os.path.exists(save_path):
            logger.info(f"从磁盘加载Vearch知识库元数据: {save_path}")
            self._load_knowledge_base(save_path)
            
            # 将磁盘加载的数据缓存到内存
            with VearchRAGService._cache_lock:
                VearchRAGService._knowledge_base_cache[cache_key] = {
                    'vector_store_manager': self.vector_store_manager,
                    'save_path': save_path
                }
                self._current_cache_key = cache_key
                logger.info(f"已将Vearch磁盘数据缓存到内存: {cache_key}")
            return

        # 构建新的知识库
        logger.info("构建新的Vearch知识库")
        
        # 加载文档
        documents = self.document_processor.load_documents_from_directory(directory_path)
        if not documents:
            raise ValueError(f"在目录 {directory_path} 中未找到有效文档")
        
        # 分割文档
        split_documents = self.document_processor.split_documents(documents)
        
        # 构建Vearch向量存储
        logger.info(f"开始构建Vearch向量存储，文档数量: {len(split_documents)}")
        self.vector_store_manager.build_vector_store(split_documents)
        
        # 保存向量存储元数据（如果指定了路径）
        if save_path:
            self.vector_store_manager.save_vector_store(save_path)
        
        # 构建检索链
        self._build_retrieval_chain()
        
        # 缓存到内存
        with VearchRAGService._cache_lock:
            VearchRAGService._knowledge_base_cache[cache_key] = {
                'vector_store_manager': self.vector_store_manager,
                'save_path': save_path
            }
            self._current_cache_key = cache_key
            logger.info(f"已将新构建的Vearch知识库缓存到内存: {cache_key}")
        
        logger.info("Vearch知识库构建完成")
    
    def _load_knowledge_base(self, load_path: str) -> None:
        """
        加载已保存的Vearch知识库
        
        Args:
            load_path: 向量存储加载路径
        """
        logger.info(f"加载Vearch知识库: {load_path}")
        
        # 加载Vearch向量存储
        self.vector_store_manager.load_vector_store(load_path)
        
        # 构建检索链
        self._build_retrieval_chain()
        
        logger.info("Vearch知识库加载完成")
    
    def _build_retrieval_chain(self) -> None:
        """构建基于Vearch的检索链"""
        logger.info("开始构建Vearch RAG检索链...")
        
        retriever = self.vector_store_manager.get_retriever()
        logger.info(f"获取Vearch检索器成功，检索参数: k={self.vector_store_manager.search_limit}")
        
        # 创建检索链
        logger.debug("构建Vearch检索链组件:")
        logger.debug("  - context: vearch_retriever | _format_docs (检索文档并格式化)")
        logger.debug("  - question: RunnablePassthrough() (传递用户问题)")
        logger.debug("  - prompt_template: 组合上下文和问题")
        logger.debug("  - llm: 大语言模型生成答案")
        logger.debug("  - output_parser: 解析输出结果")
        
        self._chain = (
            {
                "context": retriever | self._format_docs,
                "question": RunnablePassthrough()
            }
            | self.prompt_template
            | self.llm
            | self.output_parser
        )
        
        logger.info("Vearch RAG检索链构建完成")
        logger.info("链的工作流程: 用户问题 -> Vearch检索相关文档 -> 格式化上下文 -> 生成答案")
    
    def _format_docs(self, docs: List[Document]) -> str:
        """格式化检索到的文档"""
        logger.info(f"开始格式化 {len(docs)} 个从Vearch检索到的文档")
        
        formatted_docs = []
        total_content_length = 0
        
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('source', 'unknown')
            filename = doc.metadata.get('filename', 'unknown')
            content = doc.page_content.strip()
            total_content_length += len(content)
            
            formatted_doc = f"""
文档 {i} (来源: {filename}):
{content}
---
"""
            formatted_docs.append(formatted_doc)
            logger.debug(f"格式化Vearch文档 {i}: {filename}, 内容长度: {len(content)} 字符")
        
        formatted_context = "\n".join(formatted_docs)
        logger.info(f"Vearch文档格式化完成，总上下文长度: {len(formatted_context)} 字符，原始内容长度: {total_content_length} 字符")
        
        # 记录上下文的前200字符用于调试
        preview = formatted_context[:200].replace('\n', '\\n')
        logger.debug(f"格式化后的Vearch上下文预览: {preview}...")
        
        return formatted_context

    def rag(self, question: str) -> RAGQueryResult:
        """
        执行基于Vearch的检索增强生成查询

        Args:
            question (str): 用户问题

        Returns:
            RAGQueryResult: 包含答案、相关文档、来源信息的结果

        Raises:
            ValueError: 知识库未初始化
            Exception: 查询执行失败
        """
        if not self._chain:
            raise ValueError("Vearch知识库未初始化，请先构建或加载知识库")
        
        logger.info(f"开始执行Vearch RAG查询: {question}")
        
        try:
            # 执行RAG查询 - 链会自动处理检索、格式化和生成
            logger.info("调用Vearch RAG链进行检索和生成...")
            logger.debug("Vearch RAG链工作流程: 检索文档 -> 格式化上下文 -> 生成答案")
            
            answer = self._chain.invoke(question)
            
            logger.info(f"Vearch RAG链执行完成，生成答案长度: {len(answer)} 字符")
            logger.debug(f"生成的答案预览: {answer[:100]}...")
            
            # 为了API兼容性，单独执行一次检索获取源文档信息
            logger.debug("执行额外的Vearch检索以获取源文档信息（用于API返回）")
            retriever = self.vector_store_manager.get_retriever()
            relevant_docs = retriever.invoke(question)
            
            logger.info(f"从Vearch检索到 {len(relevant_docs)} 个相关文档用于API返回")
            
            # 记录检索到的文档信息
            for i, doc in enumerate(relevant_docs, 1):
                filename = doc.metadata.get('filename', 'unknown')
                content_length = len(doc.page_content)
                logger.debug(f"Vearch源文档 {i}: {filename}, 长度: {content_length} 字符")
            
            # 整理返回结果
            source_documents = [
                SourceDocument(
                    content=doc.page_content,
                    source=doc.metadata.get('source', 'unknown'),
                    filename=doc.metadata.get('filename', 'unknown'),
                    chunk_id=doc.metadata.get('chunk_id', 0)
                )
                for doc in relevant_docs
            ]
            
            result = RAGQueryResult(
                question=question,
                answer=answer,
                source_documents=source_documents,
                num_sources=len(relevant_docs)
            )
            
            logger.info(f"Vearch RAG查询完成，返回结果包含 {len(relevant_docs)} 个源文档")
            return result
            
        except Exception as e:
            logger.error(f"Vearch RAG查询执行失败，问题='{question}', 错误: {e}")
            raise
    
    def similarity_search(self, query: str, k: int = 20) -> SimilaritySearchResult:
        """
        执行基于Vearch的相似度搜索

        Args:
            query (str): 查询文本
            k (int): 返回结果数量，默认20

        Returns:
            SimilaritySearchResult: 包含content、metadata、source、filename的相似文档列表

        Raises:
            ValueError: 向量存储未初始化时抛出
            Exception: 搜索过程中的其他异常
        """
        if not self.vector_store_manager.vector_store:
            raise ValueError("Vearch向量存储未初始化")
        
        try:
            logger.info(f"开始执行Vearch相似度搜索，查询: {query[:50]}..., k={k}")
            
            # 执行Vearch相似度搜索
            docs = self.vector_store_manager.similarity_search(query, k=k)
            
            logger.info(f"Vearch相似度搜索完成，返回 {len(docs)} 个结果")
            
            # 格式化结果
            results = []
            for i, doc in enumerate(docs, 1):
                results.append(DocumentInfo(
                    content=doc.page_content,
                    metadata=doc.metadata,
                    source=doc.metadata.get('source', 'unknown'),
                    filename=doc.metadata.get('filename', 'unknown')
                ))
                logger.debug(f"Vearch搜索结果 {i}: {doc.metadata.get('filename', 'unknown')}")
            
            return results
            
        except Exception as e:
            logger.error(f"Vearch相似度搜索失败，查询='{query}', k={k}, 错误: {e}")
            raise

    @classmethod
    def clear_cache(cls, cache_key: Optional[str] = None) -> None:
        """
        清理Vearch内存缓存
        
        Args:
            cache_key: 指定要清理的缓存键，如果为None则清理所有缓存
        """
        with cls._cache_lock:
            if cache_key is None:
                # 清理所有缓存
                cleared_count = len(cls._knowledge_base_cache)
                cls._knowledge_base_cache.clear()
                logger.info(f"已清理所有Vearch内存缓存，共清理 {cleared_count} 个缓存项")
            else:
                # 清理指定缓存
                if cache_key in cls._knowledge_base_cache:
                    del cls._knowledge_base_cache[cache_key]
                    logger.info(f"已清理指定Vearch内存缓存: {cache_key}")
                else:
                    logger.warning(f"指定的Vearch缓存键不存在: {cache_key}")
    
    @classmethod
    def get_cache_info(cls) -> Dict[str, Any]:
        """
        获取Vearch缓存信息
        
        Returns:
            Dict[str, Any]: 包含缓存统计信息的字典
        """
        with cls._cache_lock:
            cache_keys = list(cls._knowledge_base_cache.keys())
            cache_info = {
                "vector_store_type": "vearch",
                "cache_count": len(cache_keys),
                "cache_keys": cache_keys,
                "cache_details": {}
            }
            
            for key, data in cls._knowledge_base_cache.items():
                cache_info["cache_details"][key] = {
                    "save_path": data.get("save_path", "N/A"),
                    "has_vector_store": data.get("vector_store_manager") is not None
                }
            
            return cache_info
    
    @classmethod
    def is_cached(cls, group_name: str, repo_name: Optional[str] = None) -> bool:
        """
        检查指定的Vearch知识库是否已缓存
        
        Args:
            group_name: 仓库组名
            repo_name: 仓库名称（可选）
            
        Returns:
            bool: 如果已缓存返回True，否则返回False
        """
        cache_key = f"vearch:{group_name}:{repo_name}" if repo_name else f"vearch:{group_name}"
        with cls._cache_lock:
            return cache_key in cls._knowledge_base_cache
    
    def get_current_cache_key(self) -> Optional[str]:
        """
        获取当前实例加载的Vearch缓存键
        
        Returns:
            Optional[str]: 当前缓存键，如果未加载任何缓存则返回None
        """
        return self._current_cache_key

    def get_stats(self) -> Dict[str, Any]:
        """
        获取Vearch RAG服务统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        vector_store_stats = self.vector_store_manager.get_stats()
        
        return {
            "service_type": "vearch_rag",
            "current_cache_key": self._current_cache_key,
            "chain_initialized": self._chain is not None,
            "vector_store_stats": vector_store_stats,
            "cache_info": self.get_cache_info()
        }