"""
混合文档生成策略

支持在overview、catalogue、document三个功能模块中自由组合使用prompt和agent策略
通过配置文件动态配置每个功能模块使用的策略类型
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .base_strategy import DocumentGenerationStrategy, GenerationMode
from .prompt_strategy import PromptBasedStrategy
from .agent_strategy import AgentBasedStrategy
from .strategy_utils import StrategyUtils
from ..types import GenerationContext, StepGenerationResult
from ..enums import GenerationStrategy


class HybridStrategy(DocumentGenerationStrategy):
    """混合策略 - 可以为不同功能模块配置不同的实现策略"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化混合策略
        
        Args:
            config: 混合策略配置，包含各功能模块的策略选择
                   格式: {
                       "overview_strategy": "prompt" | "agent",
                       "catalogue_strategy": "prompt" | "agent", 
                       "document_strategy": "prompt" | "agent",
                       "prompt_config": {...},  # prompt策略的配置
                       "agent_config": {...}    # agent策略的配置
                   }
        """
        super().__init__(config)
        
        # 解析配置
        self._parse_hybrid_config(config or {})
        
        # 初始化子策略实例
        self._init_sub_strategies()
        
        self.logger.info(f"混合策略初始化完成 - Overview: {self.overview_strategy}, "
                        f"Catalogue: {self.catalogue_strategy}, Document: {self.document_strategy}")
    
    def _parse_hybrid_config(self, config: Dict[str, Any]) -> None:
        """解析混合策略配置"""
        # 默认配置：所有功能都使用prompt策略
        self.overview_strategy = config.get("overview_strategy", "prompt")
        self.catalogue_strategy = config.get("catalogue_strategy", "prompt") 
        self.document_strategy = config.get("document_strategy", "prompt")
        
        # 验证策略配置
        valid_strategies = ["prompt", "agent"]
        for strategy_name, strategy_value in [
            ("overview_strategy", self.overview_strategy),
            ("catalogue_strategy", self.catalogue_strategy),
            ("document_strategy", self.document_strategy)
        ]:
            if strategy_value not in valid_strategies:
                raise ValueError(f"无效的策略配置 {strategy_name}: {strategy_value}, "
                               f"有效值: {valid_strategies}")
        
        # 提取子策略配置
        self.prompt_config = config.get("prompt_config", {})
        self.agent_config = config.get("agent_config", {})
    
    def _init_sub_strategies(self) -> None:
        """初始化子策略实例"""
        # 根据需要初始化prompt和agent策略
        strategies_needed = {self.overview_strategy, self.catalogue_strategy, self.document_strategy}
        
        self._prompt_strategy = None
        self._agent_strategy = None
        
        if "prompt" in strategies_needed:
            self._prompt_strategy = PromptBasedStrategy(self.prompt_config)
            self.logger.debug("初始化Prompt策略实例")
        
        if "agent" in strategies_needed:
            self._agent_strategy = AgentBasedStrategy(self.agent_config)
            self.logger.debug("初始化Agent策略实例")
    
    def get_strategy_name(self) -> str:
        """返回策略名称"""
        return f"Hybrid(overview:{self.overview_strategy},catalogue:{self.catalogue_strategy},document:{self.document_strategy})"
    
    def generate_overview(self, context: GenerationContext) -> StepGenerationResult:
        """
        生成项目概览文档
        
        Args:
            context: 生成上下文信息
            
        Returns:
            包含概览内容的生成结果
        """
        try:
            self.logger.info(f"使用{self.overview_strategy}策略生成项目概览")
            
            if self.overview_strategy == "prompt":
                if not self._prompt_strategy:
                    raise RuntimeError("Prompt策略未初始化")
                result = self._prompt_strategy.generate_overview(context)
            elif self.overview_strategy == "agent":
                if not self._agent_strategy:
                    raise RuntimeError("Agent策略未初始化")
                result = self._agent_strategy.generate_overview(context)
            else:
                raise ValueError(f"不支持的概览策略: {self.overview_strategy}")
            
            # 更新策略标识为混合策略
            if result.success:
                result.strategy_used = GenerationStrategy.AGENT  # 使用AGENT标识混合策略
                result.metadata = result.metadata or {}
                result.metadata["hybrid_strategy"] = True
                result.metadata["overview_strategy"] = self.overview_strategy
            
            return result
            
        except Exception as e:
            error_msg = f"混合策略生成概览失败 (使用{self.overview_strategy}策略): {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return StepGenerationResult(
                success=False,
                error=error_msg,
                strategy_used=GenerationStrategy.AGENT,
                metadata={"hybrid_strategy": True, "overview_strategy": self.overview_strategy}
            )
    
    def generate_catalogue(self, context: GenerationContext) -> StepGenerationResult:
        """
        生成文档目录结构
        
        Args:
            context: 生成上下文信息
            
        Returns:
            包含目录结构的生成结果
        """
        try:
            self.logger.info(f"使用{self.catalogue_strategy}策略生成文档目录")
            
            if self.catalogue_strategy == "prompt":
                if not self._prompt_strategy:
                    raise RuntimeError("Prompt策略未初始化")
                result = self._prompt_strategy.generate_catalogue(context)
            elif self.catalogue_strategy == "agent":
                if not self._agent_strategy:
                    raise RuntimeError("Agent策略未初始化")
                result = self._agent_strategy.generate_catalogue(context)
            else:
                raise ValueError(f"不支持的目录策略: {self.catalogue_strategy}")
            
            # 更新策略标识为混合策略
            if result.success:
                result.strategy_used = GenerationStrategy.AGENT  # 使用AGENT标识混合策略
                result.metadata = result.metadata or {}
                result.metadata["hybrid_strategy"] = True
                result.metadata["catalogue_strategy"] = self.catalogue_strategy
            
            return result
            
        except Exception as e:
            error_msg = f"混合策略生成目录失败 (使用{self.catalogue_strategy}策略): {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return StepGenerationResult(
                success=False,
                error=error_msg,
                strategy_used=GenerationStrategy.AGENT,
                metadata={"hybrid_strategy": True, "catalogue_strategy": self.catalogue_strategy}
            )
    
    def generate_documents(self,
                          catalogue_data: Dict[str, Any],
                          context: GenerationContext,
                          mode: GenerationMode = GenerationMode.SERIAL,
                          max_workers: Optional[int] = None) -> StepGenerationResult:
        """
        生成文档内容，支持串行和并行模式
        
        Args:
            catalogue_data: 文档目录结构数据
            context: 生成上下文信息
            mode: 生成模式（串行或并行）
            max_workers: 并行模式下的最大工作线程数，None表示使用默认值
            
        Returns:
            包含生成统计信息的生成结果
        """
        try:
            self.logger.info(f"使用{self.document_strategy}策略生成文档内容，模式: {mode.value}")
            
            if self.document_strategy == "prompt":
                if not self._prompt_strategy:
                    raise RuntimeError("Prompt策略未初始化")
                result = self._prompt_strategy.generate_documents(catalogue_data, context, mode, max_workers)
            elif self.document_strategy == "agent":
                if not self._agent_strategy:
                    raise RuntimeError("Agent策略未初始化")
                result = self._agent_strategy.generate_documents(catalogue_data, context, mode, max_workers)
            else:
                raise ValueError(f"不支持的文档策略: {self.document_strategy}")
            
            # 更新策略标识为混合策略
            if result.success:
                result.strategy_used = GenerationStrategy.AGENT  # 使用AGENT标识混合策略
                result.metadata = result.metadata or {}
                result.metadata["hybrid_strategy"] = True
                result.metadata["document_strategy"] = self.document_strategy
            
            return result
            
        except Exception as e:
            error_msg = f"混合策略生成文档失败 (使用{self.document_strategy}策略): {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return StepGenerationResult(
                success=False,
                error=error_msg,
                strategy_used=GenerationStrategy.AGENT,
                metadata={"hybrid_strategy": True, "document_strategy": self.document_strategy}
            )
    
    def _generate_document(self,
                          document_path: str,
                          catalogue_data: Dict[str, Any],
                          context: GenerationContext) -> Optional[str]:
        """
        生成单个文档的内容
        
        Args:
            document_path: 文档在目录结构中的路径（用于定位文档项）
            catalogue_data: 文档目录结构数据
            context: 生成上下文信息
            
        Returns:
            生成的文档内容，如果生成失败则返回None
        """
        self.logger.debug(f"使用{self.document_strategy}策略生成单个文档: {document_path}")
        
        if self.document_strategy == "prompt":
            if not self._prompt_strategy:
                raise RuntimeError("Prompt策略未初始化")
            return self._prompt_strategy._generate_document(document_path, catalogue_data, context)
        elif self.document_strategy == "agent":
            if not self._agent_strategy:
                raise RuntimeError("Agent策略未初始化")
            return self._agent_strategy._generate_document(document_path, catalogue_data, context)
        else:
            raise ValueError(f"不支持的文档策略: {self.document_strategy}")
                
    
    def estimate_cost(self, context: GenerationContext) -> Dict[str, Any]:
        """
        估算生成成本（聚合各子策略的成本估算）
        
        Args:
            context: 生成上下文
            
        Returns:
            成本估算信息
        """
        try:
            cost_estimates = {}
            
            # 估算概览成本
            if self.overview_strategy == "prompt" and self._prompt_strategy:
                cost_estimates["overview"] = self._prompt_strategy.estimate_cost(context)
            elif self.overview_strategy == "agent" and self._agent_strategy:
                cost_estimates["overview"] = self._agent_strategy.estimate_cost(context)
            
            # 估算目录成本
            if self.catalogue_strategy == "prompt" and self._prompt_strategy:
                cost_estimates["catalogue"] = self._prompt_strategy.estimate_cost(context)
            elif self.catalogue_strategy == "agent" and self._agent_strategy:
                cost_estimates["catalogue"] = self._agent_strategy.estimate_cost(context)
            
            # 估算文档成本
            if self.document_strategy == "prompt" and self._prompt_strategy:
                cost_estimates["document"] = self._prompt_strategy.estimate_cost(context)
            elif self.document_strategy == "agent" and self._agent_strategy:
                cost_estimates["document"] = self._agent_strategy.estimate_cost(context)
            
            return {
                "estimated": True,
                "strategy": "hybrid",
                "breakdown": cost_estimates,
                "overview_strategy": self.overview_strategy,
                "catalogue_strategy": self.catalogue_strategy,
                "document_strategy": self.document_strategy
            }
            
        except Exception as e:
            self.logger.warning(f"混合策略成本估算失败: {e}")
            return {
                "estimated": False,
                "reason": f"混合策略成本估算失败: {str(e)}"
            }
    
    def cleanup(self, context: GenerationContext) -> None:
        """
        清理策略相关资源
        
        Args:
            context: 生成上下文
        """
        try:
            if self._prompt_strategy:
                self._prompt_strategy.cleanup(context)
            if self._agent_strategy:
                self._agent_strategy.cleanup(context)
            self.logger.info("混合策略资源清理完成")
        except Exception as e:
            self.logger.warning(f"混合策略资源清理失败: {e}")