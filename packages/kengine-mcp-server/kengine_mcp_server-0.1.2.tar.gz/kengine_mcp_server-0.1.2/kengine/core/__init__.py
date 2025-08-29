"""
核心服务模块

统一的知识工程和文档生成框架，包括：
- 完整的知识生成服务（KnowledgeService）
- 多种文档生成策略支持
- Agent和基于提示词的生成方式
- RAG知识库集成
- 项目分类和元数据管理

主要组件：
- KnowledgeService: 端到端的知识生成服务
- StrategyFactory: 策略管理和实例创建
- DocumentGenerationService: 高级生成服务
- DocumentGenerationStrategy: 策略抽象基类
"""

from .types import (
    GenerationStrategy,
    ValidationLevel,
    GenerationContext,
    StepGenerationResult,
    DocumentGenerationStats,
    ValidationResult,
    KnowledgeGenerationRequest, 
    KnowledgeGenerationResult
)

from .strategy_factory import StrategyFactory
from .document_service import DocumentGenerationService
from .services.document_comment_service import DocumentCommentService
from .knowledge_service import (
    KnowledgeService
)

__all__ = [
    # Types
    'GenerationStrategy',
    'ValidationLevel',
    'GenerationContext',
    'StepGenerationResult',
    'DocumentGenerationStats',
    'ValidationResult',
    
    # Core services
    'KnowledgeService',
    'KnowledgeGenerationRequest',
    'KnowledgeGenerationResult',
    'DocumentCommentService',
    
    # Document generation components
    'StrategyFactory',
    'DocumentGenerationService'
]