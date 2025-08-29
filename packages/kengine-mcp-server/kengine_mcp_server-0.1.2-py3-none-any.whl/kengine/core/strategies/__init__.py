"""
策略模块

包含所有文档生成策略的实现
"""

from .base_strategy import DocumentGenerationStrategy
from .prompt_strategy import PromptBasedStrategy  
from .agent_strategy import AgentBasedStrategy
from .hybrid_strategy import HybridStrategy

__all__ = [
    'DocumentGenerationStrategy',
    'PromptBasedStrategy',
    'AgentBasedStrategy',
    'HybridStrategy'
]