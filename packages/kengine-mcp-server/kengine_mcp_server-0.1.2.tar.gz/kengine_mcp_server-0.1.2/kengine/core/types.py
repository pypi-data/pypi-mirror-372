"""
文档生成相关的数据类型定义

包含枚举、数据类和接口定义
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
import logging
from pathlib import Path
import re
import json

from .enums import GenerationStrategy, ValidationLevel, ExecuteStep

@dataclass_json
@dataclass
class KnowledgeGenerationRequest:
    """知识生成请求参数 - 支持多种输入格式"""
    # 必需参数 - 支持两种格式
    repo_group: Optional[str] = None
    repo_name: Optional[str] = None
    
    # 可选参数
    model_name: str = "gpt-4.1"
    prompt_version: Optional[str] = None
    branch: str = "master"
    force_project_type: Optional[str] = None  # 强制指定项目类型
    execute_step: ExecuteStep = ExecuteStep.FULL  # 执行步骤控制，使用枚举类型
    specify_document_path: Optional[str] = None
    user_annotation: Optional[str] = None  # 用户批注，仅在execute_step为document且指定specify_document_path时使用
    
    def __post_init__(self):
        """后处理：确保execute_step是正确的枚举类型，并处理仓库信息"""
        if isinstance(self.execute_step, str):
            # 向后兼容：如果传入字符串，自动转换为枚举
            self.execute_step = ExecuteStep.from_string(self.execute_step)
        elif not isinstance(self.execute_step, ExecuteStep):
            raise TypeError(f"execute_step必须是ExecuteStep枚举或字符串类型，当前类型: {type(self.execute_step).__name__}")
        
        # 验证必需参数
        if not self.repo_group:
            raise ValueError("repo_group参数是必需的")
        if not self.repo_name:
            raise ValueError("repo_name参数是必需的")
        
        # 验证用户批注使用条件
        if self.user_annotation:
            if self.execute_step != ExecuteStep.DOCUMENT:
                raise ValueError("用户批注功能仅在execute_step为DOCUMENT时可用")
            if not self.specify_document_path:
                raise ValueError("使用用户批注功能时必须指定specify_document_path")
    

@dataclass_json
@dataclass
class KnowledgeGenerationResult:
    """知识生成结果"""
    success: bool
    project_path: str
    output_path: str
    
    # 分类结果
    classification_result: Optional[Dict[str, Any]] = None
    project_type: Optional[str] = None
    strategy_used: Optional[GenerationStrategy] = None
    
    # RAG结果
    rag_service: Optional[Any] = None
    rag_built: bool = False
    
    # 文档生成结果
    catalogue_result: Optional[Any] = None
    documents_result: Optional[Any] = None
    overview_result: Optional[Any] = None
    
    # 元数据
    metadata_saved: bool = False
    metadata_path: Optional[str] = None
    
    # 错误信息
    error: Optional[str] = None
    generate_stage: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


@dataclass_json
@dataclass
class GenerationContext:
    """生成上下文信息"""
    project_path: str
    project_type: str
    strategy: Optional[GenerationStrategy]
    llm_options: Optional[Dict[str, Any]] = None
    rag_service: Optional[Any] = None
    git_repository_url: Optional[str] = None
    branch: str = "master"
    validation_level: ValidationLevel = ValidationLevel.BASIC
    custom_config: Optional[Dict[str, Any]] = None
    prompt_version: Optional[str] = None
    doc_output_base_path: Optional[str] = None
    extra_context: Dict[str, Any] = field(default_factory=dict)
    # 项目信息缓存，避免重复调用 analyze_project
    _project_info: Optional[Any] = field(default=None, init=False)
    catalogue:  Optional[Dict[str, Any]] = None
    # 任务ID，用于大模型调用统计和进度跟踪
    task_id: Optional[str] = None
    # 进度跟踪器，用于文档生成进度回调
    tracker: Optional[Any] = None
    repo_name: str = None
    repo_group: str = None
    
    def get_project_info(self):
        """获取项目信息，使用缓存避免重复分析"""
        import logging
        logger = logging.getLogger(__name__)
        
        if self._project_info is None:
            logger.warning(f"🔍 [DEBUG] GenerationContext.get_project_info() - 缓存未命中，开始分析项目: {self.project_path}")
            from ..utils.project_utils import analyze_project
            self._project_info = analyze_project(self.project_path)
        else:
            logger.warning(f"🔍 [DEBUG] GenerationContext.get_project_info() - 缓存命中，复用项目信息: {self.project_path}")
        return self._project_info
    


@dataclass_json
@dataclass
class StepGenerationResult:
    """生成结果统一数据结构 - 使用标准的dataclasses-json实现"""
    success: bool
    data: Optional[Dict[str, Any]] = field(default_factory=dict)
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    execution_time: Optional[float] = None
    strategy_used: Optional[str] = None  # 使用字符串存储枚举值，简化序列化
    
    def set_strategy(self, strategy: Optional[GenerationStrategy]) -> None:
        """设置策略，自动转换为字符串"""
        self.strategy_used = strategy.value if strategy else None
    
    def get_strategy(self) -> Optional[GenerationStrategy]:
        """获取策略枚举对象"""
        if self.strategy_used:
            return GenerationStrategy(self.strategy_used)
        return None


@dataclass_json
@dataclass
class DocumentGenerationStats:
    """文档生成统计信息"""
    total_items: int = 0
    successful_generations: int = 0
    failed_generations: int = 0
    generated_files: List[str] = field(default_factory=list)
    failed_items: List[Dict[str, str]] = field(default_factory=list)
    execution_time: float = 0.0


@dataclass_json
@dataclass
class ValidationResult:
    """验证结果"""
    passed: bool
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    confidence_score: Optional[float] = None