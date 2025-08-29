"""
文档生成工厂

负责策略管理、实例创建和项目类型映射
"""

from typing import Dict, Any, Optional, List, Type
import threading
import logging

from .enums import GenerationStrategy
from .strategies import DocumentGenerationStrategy
from kengine.config.application_config import get_application_config
from .utils.exceptions import StrategyNotFoundError


class StrategyFactory:
    """文档生成工厂 - 专注于策略管理和实例创建"""
    
    def __init__(self):
        """
        初始化工厂
        """
        self._strategies: Dict[GenerationStrategy, Type[DocumentGenerationStrategy]] = {}
        self._project_strategy_mapping: Dict[str, GenerationStrategy] = {}
        self._lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        
        # 使用全局配置
        self._config_manager = get_application_config()
        
        # 初始化配置
        self._initialize_configuration()
        
        # 注册默认策略
        self._register_default_strategies_class()
    
    def _initialize_configuration(self):
        """初始化配置"""
        # 如果有配置管理器，加载外部配置
        if not self._config_manager:
            raise RuntimeError(f'application config missing strategy config')
    
        # 初始化空的配置字典，完全依赖外部配置
        self._project_strategy_mapping = {}
        
        # 直接使用 ApplicationConfig 的方法，无需类型转换
        raw_mapping = self._config_manager.get_project_strategy_mapping()
        
        # 转换为 GenerationStrategy 枚举
        for project_type, strategy_str in raw_mapping.items():
            self._project_strategy_mapping[project_type] = GenerationStrategy(strategy_str)
        
    
    def _register_default_strategies_class(self):
        """注册默认策略"""
        # 延迟导入避免循环依赖
        from .strategies import PromptBasedStrategy, AgentBasedStrategy, HybridStrategy
        
        self._strategies[GenerationStrategy.PROMPT]= PromptBasedStrategy
        self._strategies[GenerationStrategy.AGENT] = AgentBasedStrategy
        self._strategies[GenerationStrategy.HYBRID] = HybridStrategy
        
    
    def create_generator(self, 
                        strategy: GenerationStrategy,
                        config: Optional[Dict[str, Any]] = None) -> DocumentGenerationStrategy:
        """
        创建文档生成器实例
        
        Args:
            strategy: 生成策略
            config: 覆盖默认配置的自定义配置
            
        Returns:
            策略实例
            
        Raises:
            StrategyNotFoundError: 策略未注册
        """
        if strategy not in self._strategies:
            raise StrategyNotFoundError(
                f"Strategy '{strategy.value}' not registered",
                error_code="STRATEGY_NOT_FOUND",
                context={"available_strategies": [s.value for s in self._strategies.keys()]}
            )
        
        # 获取策略配置
        strategy_config =  self._config_manager.get_strategy_config(strategy.value)
        if config:
            strategy_config.update(config)
        
        # 如果没有配置且没有提供自定义配置，记录警告
        if not strategy_config and not config:
            self.logger.warning(f"策略 '{strategy.value}' 没有配置信息，将使用策略类的默认配置")
        
        # 创建实例
        strategy_class = self._strategies[strategy]
        return strategy_class(strategy_config)
    
    def get_strategy_for_project_type(self, project_type: str) -> GenerationStrategy:
        """
        根据项目类型获取推荐的生成策略
        
        Args:
            project_type: 项目类型
            
        Returns:
            生成策略
            
        Raises:
            ValueError: 当项目类型未在配置中定义时
        """
        if project_type not in self._project_strategy_mapping:
            raise ValueError(f"项目类型 '{project_type}' 未在配置中定义")
        
        return self._project_strategy_mapping[project_type]
    
    def get_available_strategies(self) -> List[GenerationStrategy]:
        """获取可用的生成策略列表"""
        return list(self._strategies.keys())
    
    
    def get_project_type_mappings(self) -> Dict[str, str]:
        """获取项目类型到策略的映射信息（用于显示）"""
        return {
            project_type: strategy.value 
            for project_type, strategy in self._project_strategy_mapping.items()
        }
   