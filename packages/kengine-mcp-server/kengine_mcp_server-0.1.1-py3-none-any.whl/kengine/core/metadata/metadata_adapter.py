"""
元数据适配器抽象基类

定义统一的元数据操作接口，支持文件存储和数据库存储两种模式
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from ..types import KnowledgeGenerationRequest, KnowledgeGenerationResult, GenerationContext, StepGenerationResult

class MetadataAdapter(ABC):
    """元数据适配器抽象基类"""
    
    @abstractmethod
    def on_start_generate(self, 
                          request: KnowledgeGenerationRequest,
                          context: GenerationContext) -> str:
        """
        开始生成文档， 保存元数据
        
        Args:
            request: 生成文档的请求信息
            context: 生成文档的上下文信息
            
        Returns:
            
            
        Raises:
            Exception: 保存失败时抛出异常
        """
        pass
    
    @abstractmethod
    def on_cloned_repository(self, 
                          context: GenerationContext,
                          generate_result: KnowledgeGenerationResult
                          ) -> Optional[Dict[str, Any]]:
        """
        加载单个项目元数据
        
        Args:
            identifier: 项目标识符
            **kwargs: 适配器特定的参数
            
        Returns:
            项目元数据字典，如果不存在则返回None
        """
        pass
    
    @abstractmethod
    def on_classified(self, 
                          context: GenerationContext,
                          generate_result: KnowledgeGenerationResult
                          ) -> Optional[Dict[str, Any]]:
        """
        加载单个项目元数据
        
        Args:
            identifier: 项目标识符
            **kwargs: 适配器特定的参数
            
        Returns:
            项目元数据字典，如果不存在则返回None
        """
        pass
    
    
    @abstractmethod
    def on_completed(self, 
                          context: GenerationContext,
                          generate_result: KnowledgeGenerationResult
                          ) -> Optional[Dict[str, Any]]:
        """
        加载单个项目元数据
        
        Args:
            identifier: 项目标识符
            **kwargs: 适配器特定的参数
            
        Returns:
            项目元数据字典，如果不存在则返回None
        """
        pass
    
    @abstractmethod
    def on_error(self, 
        context: GenerationContext,
        generate_result: KnowledgeGenerationResult,
        error: Exception
        ) -> Optional[Dict[str, Any]]:
        """
        加载单个项目元数据
        
        Args:
            identifier: 项目标识符
            **kwargs: 适配器特定的参数
            
        Returns:
            项目元数据字典，如果不存在则返回None
        """
        pass
    
    
    
    def sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        清理元数据中的敏感信息
        
        Args:
            metadata: 原始元数据
            
        Returns:
            清理后的元数据
        """
        # 创建副本避免修改原数据
        sanitized = metadata.copy()
        
        # 清理document_generate_info中的敏感信息
        if 'document_generate_info' in sanitized:
            doc_info = sanitized['document_generate_info'].copy()
            if 'model_options' in doc_info:
                model_options = doc_info['model_options'].copy()
                sensitive_patterns = ['key', 'secret', 'token', 'password', 'pwd']
                
                for key, value in model_options.items():
                    for pattern in sensitive_patterns:
                        if pattern in key.lower():
                            model_options[key] = '*****'
                            break
                
                doc_info['model_options'] = model_options
            sanitized['document_generate_info'] = doc_info
        
        return sanitized