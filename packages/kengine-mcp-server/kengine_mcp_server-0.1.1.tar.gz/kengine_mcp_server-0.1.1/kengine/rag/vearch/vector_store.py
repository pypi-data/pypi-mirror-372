"""
Vearch向量存储管理器模块

该模块提供基于Vearch的向量存储管理功能，包括：
1. 构建向量存储（支持批量处理和错误重试）
2. 保存和加载向量存储
3. 向量存储质量验证
4. 检索器获取
"""

import logging
import time
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Tuple, Dict, Any

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_openai import OpenAIEmbeddings

from ..config import RAGConfigManager
from ...config.network_config import network_config
from .vearch_core import VearchDb

logger = logging.getLogger(__name__)


class VearchVectorStoreManager:
    """Vearch向量存储管理器"""
    
    def __init__(self):
        self.config = RAGConfigManager()
        
        # 记录网络配置信息
        network_config.log_config()
        
        # 初始化嵌入模型
        model_options = self.config.embeddings_model_options()
        self.embeddings = OpenAIEmbeddings(**model_options)
        
        # 获取并发配置
        self.concurrent = self.config.get_embeddings_concurrent()
        
        # Vearch相关配置
        self.router_server = self.config.vearch_router_server()
        self.db_name = self.config.vearch_default_db_name()
        self.space_name = self.config.vearch_default_space_name()
        self.search_limit = self.config.vearch_search_limit()
        
        # 向量存储实例
        self.vector_store: Optional[VearchDb] = None
        
        # 添加线程锁保护向量存储合并操作
        self._merge_lock = threading.Lock()

    def build_vector_store(self, documents: List[Document]) -> VearchDb:
        """
        构建Vearch向量存储（优化版本，支持批量处理和错误重试）
        
        Args:
            documents: 文档列表
            
        Returns:
            VearchDb向量存储实例
        """
        if not documents:
            raise ValueError("文档列表不能为空")
        
        logger.info(f"开始构建Vearch向量存储，文档数量: {len(documents)}")
        logger.info(f"Vearch配置 - Router: {self.router_server}, DB: {self.db_name}, Space: {self.space_name}")
        
        # 设置批量处理大小，避免一次性处理过多文档
        batch_size = 100
        max_retries = self.config.vearch_retry_attempts()
        
        for attempt in range(max_retries):
            try:
                if len(documents) <= batch_size:
                    # 文档较少，直接处理
                    logger.info("文档数量较少，直接创建向量存储")
                    self.vector_store = VearchDb.from_documents(
                        documents=documents,
                        embedding=self.embeddings,
                        path_or_url=self.router_server,
                        db_name=self.db_name,
                        table_name=self.space_name
                    )
                else:
                    # 文档较多，分批处理
                    logger.info(f"文档数量较多({len(documents)})，将分批处理，每批 {batch_size} 个文档")
                    
                    # 处理第一批创建向量存储
                    first_batch = documents[:batch_size]
                    self.vector_store = VearchDb.from_documents(
                        documents=first_batch,
                        embedding=self.embeddings,
                        path_or_url=self.router_server,
                        db_name=self.db_name,
                        table_name=self.space_name
                    )
                    logger.info(f"已处理第 1 批，共 {len(first_batch)} 个文档")
                    
                    # 处理剩余批次
                    remaining_batches = []
                    for i in range(batch_size, len(documents), batch_size):
                        batch = documents[i:i + batch_size]
                        batch_num = (i // batch_size) + 1
                        remaining_batches.append((batch, batch_num))
                    
                    # 根据配置决定是否使用并发处理
                    if self.concurrent > 1 and len(remaining_batches) > self.concurrent:
                        logger.info(f"启用并发处理，并发数: {self.concurrent}")
                        self._process_batches_concurrently(remaining_batches)
                    else:
                        logger.info("使用串行处理")
                        self._process_batches_serially(remaining_batches)
                
                # 验证向量存储质量
                if self.vector_store:
                    self._validate_vector_store_quality()
                
                logger.info("Vearch向量存储构建成功")
                return self.vector_store
                
            except Exception as e:
                logger.error(f"构建向量存储失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # 指数退避
        
        raise RuntimeError("构建向量存储失败，已达到最大重试次数")

    def _process_batches_serially(self, batches: List[Tuple[List[Document], int]]) -> None:
        """串行处理批次"""
        for batch, batch_num in batches:
            try:
                logger.info(f"开始处理第 {batch_num + 1} 批，共 {len(batch)} 个文档")
                
                # 为每个批次添加文档到现有向量存储
                texts = [doc.page_content for doc in batch]
                metadatas = [doc.metadata for doc in batch]
                
                with self._merge_lock:
                    self.vector_store.add_texts(texts=texts, metadatas=metadatas)
                
                logger.info(f"第 {batch_num + 1} 批处理完成")
                
            except Exception as e:
                logger.error(f"处理第 {batch_num + 1} 批时出错: {str(e)}")
                raise

    def _process_batches_concurrently(self, batches: List[Tuple[List[Document], int]]) -> None:
        """并发处理批次"""
        with ThreadPoolExecutor(max_workers=self.concurrent) as executor:
            # 提交所有批次任务
            future_to_batch = {}
            for batch, batch_num in batches:
                future = executor.submit(self._process_single_batch, batch, batch_num)
                future_to_batch[future] = (batch, batch_num)
            
            # 收集结果并合并
            for future in as_completed(future_to_batch):
                batch, batch_num = future_to_batch[future]
                try:
                    texts, metadatas = future.result()
                    
                    # 线程安全地合并到主向量存储
                    with self._merge_lock:
                        self.vector_store.add_texts(texts=texts, metadatas=metadatas)
                    
                    logger.info(f"第 {batch_num + 1} 批处理完成并合并")
                    
                except Exception as e:
                    logger.error(f"处理第 {batch_num + 1} 批时出错: {str(e)}")
                    raise

    def _process_single_batch(self, batch: List[Document], batch_num: int) -> Tuple[List[str], List[Dict]]:
        """处理单个批次"""
        logger.info(f"开始处理第 {batch_num + 1} 批，共 {len(batch)} 个文档")
        
        texts = [doc.page_content for doc in batch]
        metadatas = [doc.metadata for doc in batch]
        
        return texts, metadatas

    def _validate_vector_store_quality(self) -> None:
        """验证向量存储质量"""
        try:
            logger.info("开始验证向量存储质量...")
            
            # 执行一个简单的相似度搜索来验证向量存储是否正常工作
            test_query = "test query for validation"
            results = self.vector_store.similarity_search(test_query, k=1)
            
            if results:
                logger.info(f"向量存储验证成功，返回 {len(results)} 个结果")
            else:
                logger.warning("向量存储验证：未返回任何结果，可能存在问题")
                
        except Exception as e:
            logger.error(f"向量存储质量验证失败: {str(e)}")
            # 不抛出异常，因为这只是验证步骤

    def save_vector_store(self, save_path: str) -> None:
        """
        保存向量存储到指定路径
        
        注意：Vearch是分布式向量数据库，数据已经持久化到服务器
        这个方法主要用于保存配置信息和元数据
        
        Args:
            save_path: 保存路径
        """
        if not self.vector_store:
            raise ValueError("向量存储未初始化，无法保存")
        
        logger.info(f"Vearch向量存储配置信息已保存到服务器")
        logger.info(f"数据库: {self.db_name}, 空间: {self.space_name}")
        
        # 可以在这里保存一些元数据信息到本地文件
        import os
        import json
        
        os.makedirs(save_path, exist_ok=True)
        
        metadata = {
            "vector_store_type": "vearch",
            "router_server": self.router_server,
            "db_name": self.db_name,
            "space_name": self.space_name,
            "created_at": time.time()
        }
        
        metadata_path = os.path.join(save_path, "vearch_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Vearch元数据已保存到: {metadata_path}")

    def load_vector_store(self, load_path: str) -> None:
        """
        加载向量存储
        
        对于Vearch，主要是重新连接到现有的数据库和空间
        
        Args:
            load_path: 加载路径
        """
        logger.info(f"开始加载Vearch向量存储: {load_path}")
        
        # 读取元数据
        import os
        import json
        
        metadata_path = os.path.join(load_path, "vearch_metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # 使用保存的配置重新连接
            self.db_name = metadata.get("db_name", self.db_name)
            self.space_name = metadata.get("space_name", self.space_name)
            logger.info(f"从元数据加载配置 - DB: {self.db_name}, Space: {self.space_name}")
        
        # 重新初始化向量存储连接
        self.vector_store = VearchDb(
            embedding_function=self.embeddings,
            path_or_url=self.router_server,
            db_name=self.db_name,
            table_name=self.space_name
        )
        
        logger.info("Vearch向量存储加载完成")

    def get_retriever(self, k: Optional[int] = None) -> BaseRetriever:
        """
        获取检索器
        
        Args:
            k: 检索结果数量，默认使用配置中的值
            
        Returns:
            BaseRetriever: 检索器实例
        """
        if not self.vector_store:
            raise ValueError("向量存储未初始化，无法创建检索器")
        
        search_k = k if k is not None else self.search_limit
        logger.info(f"创建Vearch检索器，检索数量: {search_k}")
        
        return self.vector_store.as_retriever(search_kwargs={"k": search_k})

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """
        执行相似度搜索
        
        Args:
            query: 查询文本
            k: 返回结果数量
            
        Returns:
            List[Document]: 相似文档列表
        """
        if not self.vector_store:
            raise ValueError("向量存储未初始化，无法执行搜索")
        
        logger.info(f"执行Vearch相似度搜索，查询: {query[:50]}..., k={k}")
        
        results = self.vector_store.similarity_search(query, k=k)
        logger.info(f"搜索完成，返回 {len(results)} 个结果")
        
        return results

    def get_stats(self) -> Dict[str, Any]:
        """
        获取向量存储统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        if not self.vector_store:
            return {"status": "not_initialized"}
        
        return {
            "status": "initialized",
            "vector_store_type": "vearch",
            "router_server": self.router_server,
            "db_name": self.db_name,
            "space_name": self.space_name,
            "search_limit": self.search_limit
        }