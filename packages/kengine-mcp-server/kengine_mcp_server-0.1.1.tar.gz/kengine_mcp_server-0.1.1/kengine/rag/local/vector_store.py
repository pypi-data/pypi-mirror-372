"""
向量存储管理器模块

该模块提供向量存储的管理功能，包括：
1. 构建向量存储（支持批量处理和错误重试）
2. 保存和加载向量存储
3. 向量存储质量验证
4. 检索器获取
"""

import logging
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Tuple

from langchain_community.vectorstores.faiss import FAISS
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_openai import OpenAIEmbeddings

from ..config import RAGConfigManager
from ...config.network_config import network_config

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """向量存储管理器"""
    
    def __init__(self):
        self.config = RAGConfigManager()
        
        # 记录网络配置信息
        network_config.log_config()
        
        model_options = self.config.embeddings_model_options()
        self.embeddings = OpenAIEmbeddings(**model_options)
        # 修复配置键名拼写错误
        self.concurrent = self.config.get_embeddings_concurrent()
        self.batch_size = self.config.get_embedding_batch_size()
        self.vector_store: Optional[FAISS] = None
        # 添加线程锁保护向量存储合并操作
        self._merge_lock = threading.Lock()

    def build_vector_store(self, documents: List[Document]) -> FAISS:
        """
        构建向量存储（优化版本，支持批量处理和错误重试）
        
        Args:
            documents: 文档列表
            
        Returns:
            FAISS向量存储实例
        """
        if not documents:
            raise ValueError("文档列表不能为空")
        
        logger.info(f"开始构建向量存储，文档数量: {len(documents)}")
        # 设置批量处理大小，避免一次性处理过多文档
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                if len(documents) <= self.batch_size:
                    # 文档较少，直接处理
                    self.vector_store = FAISS.from_documents(
                        documents=documents,
                        embedding=self.embeddings
                    )
                else:
                    # 文档较多，分批处理
                    logger.info(f"文档数量较多({len(documents)})，将分批处理，每批 {self.batch_size} 个文档")
                    
                    # 处理第一批创建向量存储
                    first_batch = documents[:self.batch_size]
                    self.vector_store = FAISS.from_documents(
                        documents=first_batch,
                        embedding=self.embeddings
                    )
                    logger.info(f"已处理第 1 批，共 {len(first_batch)} 个文档")
                    
                    # 处理剩余批次 - 支持并发执行
                    remaining_batches = []
                    for i in range(self.batch_size, len(documents), self.batch_size):
                        batch = documents[i:i + self.batch_size]
                        batch_num = (i // self.batch_size) + 1
                        remaining_batches.append((batch, batch_num))
                    
                    # 根据配置决定是否使用并发处理
                    if self.concurrent > 1 and len(remaining_batches) > self.concurrent:
                        logger.info(f"启用并发处理，并发数: {self.concurrent}")
                        self._process_batches_concurrently(remaining_batches)
                    else:
                        logger.info("使用串行处理")
                        self._process_batches_serially(remaining_batches)
                
                # 新增：在向量存储构建完成后进行验证
                if self.vector_store:
                    self._validate_vector_store_quality()
                logger.info("向量存储构建完成")
                return self.vector_store
                
            except Exception as e:
                logger.warning(f"构建向量存储失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    # 指数退避重试
                    wait_time = (2 ** attempt) * 5  # 5, 10, 20 秒
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"构建向量存储最终失败: {e}")
                    raise
        
        # 如果代码执行到这里，说明发生了意外情况
        raise RuntimeError("向量存储构建失败：未知错误")

    def _validate_vector_store_quality(self) -> None:
        """
        验证向量存储的质量（在构建完成后调用）
        """
        if not self.vector_store:
            logger.warning("向量存储为空，无法验证")
            return

        try:
            # 检查向量存储的基本信息
            if hasattr(self.vector_store, 'index'):
                vector_count = self.vector_store.index.ntotal
                dimension = self.vector_store.index.d
                logger.info(f"向量存储验证: {vector_count} 个向量，维度: {dimension}")

                if vector_count == 0:
                    logger.error("向量存储中没有向量")
                    raise ValueError("向量存储构建失败：没有生成向量")

                # 可选：进行简单的相似度搜索测试
                if len(self.vector_store.docstore._dict) > 0:
                    # 获取第一个文档进行测试搜索
                    test_docs = list(self.vector_store.docstore._dict.values())
                    if test_docs:
                        test_content = test_docs[0].page_content[:100]  # 取前100字符
                        similar_docs = self.vector_store.similarity_search(test_content, k=1)
                        if similar_docs:
                            logger.info("向量存储功能验证通过")
                        else:
                            logger.warning("向量存储搜索功能异常")
            else:
                logger.warning("无法获取向量存储详细信息")

        except ValueError as e:
            # 对于关键的验证失败（如空向量存储），重新抛出异常
            logger.error(f"向量存储质量验证失败: {e}")
            raise
        except Exception as e:
            logger.error(f"向量存储质量验证失败: {e}")
            # 对于其他异常，不抛出异常，因为向量存储可能仍然可用
            raise

    def save_vector_store(self, save_path: str) -> None:
        """
        保存向量存储到本地
        
        Args:
            save_path: 保存路径
        """
        if not self.vector_store:
            raise ValueError("向量存储未初始化")
        
        try:
            self.vector_store.save_local(save_path)
            logger.info(f"向量存储已保存到: {save_path}")
        except Exception as e:
            logger.error(f"保存向量存储失败，保存路径='{save_path}', 错误: {e}")
            raise
    
    def load_vector_store(self, load_path: str) -> FAISS:
        """
        从本地加载向量存储
        
        Args:
            load_path: 加载路径
            
        Returns:
            FAISS向量存储实例
        """
        try:
            self.vector_store = FAISS.load_local(
                load_path, 
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            logger.info(f"向量存储已从 {load_path} 加载")
            return self.vector_store
        except Exception as e:
            logger.error(f"加载向量存储失败，加载路径='{load_path}', 错误: {e}")
            raise
    
    def get_retriever(self) -> BaseRetriever:
        """
        获取检索器
        
        Returns:
            检索器实例
        """
        if not self.vector_store:
            raise ValueError("向量存储未初始化")
        
        return self.vector_store.as_retriever(
            search_kwargs={"k": self.config.default_retrieval_k()}
        )
            
            
    def _process_batch(self, batch_data: Tuple[List[Document], int]) -> FAISS:
        """
        处理单个批次的文档，支持重试机制
        
        Args:
            batch_data: 包含文档列表和批次号的元组
            
        Returns:
            FAISS向量存储实例
            
        Raises:
            Exception: 重试3次后仍然失败时抛出异常
        """
        batch, batch_num = batch_data
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # 创建临时向量存储
                temp_store = FAISS.from_documents(
                    documents=batch,
                    embedding=self.embeddings
                )
                logger.info(f"已处理第 {batch_num + 1} 批，共 {len(batch)} 个文档")
                return temp_store
                
            except Exception as batch_error:
                last_error = batch_error
                if attempt < max_retries - 1:
                    logger.warning(f"处理第 {batch_num + 1} 批时出错（第 {attempt + 1} 次尝试）: {batch_error}，正在重试...")
                else:
                    logger.error(f"处理第 {batch_num + 1} 批时出错（已重试 {max_retries} 次）: {batch_error}")
        
        # 重试失败后抛出异常给上层处理
        raise Exception(f"批次 {batch_num + 1} 处理失败，已重试 {max_retries} 次") from last_error

    def _process_batches_serially(self, batches: List[Tuple[List[Document], int]]) -> None:
        """
        串行处理批次列表
        
        Args:
            batches: 批次列表，每个元素为(文档列表, 批次号)的元组
        """
        for batch_data in batches:
            try:
                temp_store = self._process_batch(batch_data)
                # 使用锁保护合并操作
                with self._merge_lock:
                    self.vector_store.merge_from(temp_store)
            except Exception as e:
                # 记录失败但继续处理其他批次
                batch, batch_num = batch_data
                logger.error(f"跳过失败的批次 {batch_num + 1}: {e}")
                continue

    def _process_batches_concurrently(self, batches: List[Tuple[List[Document], int]]) -> None:
        """
        并发处理批次列表
        
        Args:
            batches: 批次列表，每个元素为(文档列表, 批次号)的元组
            
        Raises:
            Exception: 如果有批次处理失败，会抛出异常给上层处理
        """
        successful_batches = 0
        failed_batches = 0
        failed_exceptions = []
        
        # 使用ThreadPoolExecutor进行并发处理，设置线程池名称
        with ThreadPoolExecutor(
            max_workers=self.concurrent, 
            thread_name_prefix="VectorStore-Worker"
        ) as executor:
            # 提交所有批次任务
            future_to_batch = {
                executor.submit(self._process_batch, batch_data): batch_data 
                for batch_data in batches
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_batch):
                batch_data = future_to_batch[future]
                batch, batch_num = batch_data
                
                try:
                    temp_store = future.result()
                    # 使用锁保护合并操作，确保线程安全
                    with self._merge_lock:
                        self.vector_store.merge_from(temp_store)
                    successful_batches += 1
                        
                except Exception as exc:
                    logger.error(f"批次 {batch_num + 1} 处理异常: {exc}")
                    failed_batches += 1
                    failed_exceptions.append(exc)
        
        # 记录并发处理结果
        total_batches = len(batches)
        logger.info(f"并发处理完成: 成功 {successful_batches}/{total_batches} 批次")
        
        # 如果有失败的批次，抛出异常给上层处理
        if failed_batches > 0:
            logger.error(f"并发处理失败: {failed_batches}/{total_batches} 批次失败")
            # 抛出第一个异常，包含失败统计信息
            raise Exception(f"并发处理失败: {failed_batches}/{total_batches} 批次失败") from failed_exceptions[0]