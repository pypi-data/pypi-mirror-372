"""
RAG服务工厂模块

该模块提供RAG服务的工厂模式实现，支持：
- 基于配置自动选择向量存储类型
- 支持Local FAISS和Vearch向量存储
- 可扩展的工厂模式设计
"""

import logging
from typing import Any, Dict, Optional

from kengine.rag.interface import RAGService
from kengine.rag.config import RAGConfigManager
from kengine.rag.local.service import LocalRAGService

logger = logging.getLogger(__name__)


class RAGServiceFactory:
    """RAG服务工厂类
    
    根据向量存储类型创建对应的RAG服务实例。
    支持的类型：
    - local: 使用LocalRAGService (FAISS向量存储)
    - vearch: 使用VearchRAGService (Vearch向量存储)
    
    这是一个具体的工厂类，通过 vector_store_type 参数来判断应该返回哪个具体的实现类。
    """
    
    def __init__(self, vector_store_type: Optional[str] = None):
        """
        初始化RAG服务工厂
        
        Args:
            vector_store_type: 指定向量存储类型，如果为None则从配置文件读取
        """
        self.config = RAGConfigManager()
        self.vector_store_type = vector_store_type or self.config.get_vector_store_type()
        
    def create_rag_service(self) -> RAGService:
        """
        根据向量存储类型创建RAG服务实例
        
        Returns:
            RAGService: 根据类型选择的RAG服务实例
            
        Raises:
            ValueError: 当指定的向量存储类型不支持时
            ImportError: 当Vearch相关依赖不可用时
        """
        logger.info(f"创建RAG服务，向量存储类型: {self.vector_store_type}")
        
        if self.vector_store_type == "local":
            logger.info("使用LocalRAGService (FAISS向量存储)")
            return LocalRAGService()
            
        elif self.vector_store_type == "vearch":
            logger.info("使用VearchRAGService (Vearch向量存储)")
            try:
                # 动态导入VearchRAGService以避免循环导入
                from kengine.rag.vearch.service import VearchRAGService
                return VearchRAGService()
            except ImportError as e:
                logger.error(f"无法导入VearchRAGService: {e}")
                logger.error("请确保Vearch相关依赖已正确安装")
                raise ImportError(f"Vearch RAG服务不可用: {e}")
                
        else:
            error_msg = f"不支持的向量存储类型: {self.vector_store_type}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def get_vector_store_type(self) -> str:
        """
        获取当前配置的向量存储类型
        
        Returns:
            str: 向量存储类型
        """
        return self.vector_store_type


# 便捷函数
def create_rag_service(vector_store_type: Optional[str] = None) -> RAGService:
    """
    便捷函数：创建RAG服务实例
    
    Args:
        vector_store_type: 指定向量存储类型，如果为None则从配置文件读取
        
    Returns:
        RAGService: RAG服务实例
        
    Raises:
        ValueError: 当指定的向量存储类型不支持时
    """
    factory = RAGServiceFactory(vector_store_type)
    return factory.create_rag_service()


def get_available_vector_store_types() -> list[str]:
    """
    获取可用的向量存储类型列表
    
    Returns:
        list[str]: 可用的向量存储类型列表
    """
    available_types = ["local"]  # FAISS总是可用的
    
    # 检查Vearch是否可用
    try:
        from kengine.rag.vearch.service import VearchRAGService
        available_types.append("vearch")
        logger.debug("Vearch向量存储可用")
    except ImportError:
        logger.debug("Vearch向量存储不可用")
    
    return available_types


def validate_vector_store_config(vector_store_type: str) -> bool:
    """
    验证指定的向量存储类型配置是否有效
    
    Args:
        vector_store_type: 向量存储类型
        
    Returns:
        bool: 配置是否有效
    """
    if vector_store_type not in get_available_vector_store_types():
        return False
    
    try:
        config = RAGConfigManager()
        
        if vector_store_type == "local":
            # 验证local配置
            config.embeddings_model_options()
            config.get_embeddings_concurrent()
            return True
            
        elif vector_store_type == "vearch":
            # 验证vearch配置
            config.vearch_router_server()
            config.vearch_default_db_name()
            config.vearch_default_space_name()
            return True
            
    except Exception as e:
        logger.error(f"验证{vector_store_type}配置失败: {e}")
        return False
    
    return False