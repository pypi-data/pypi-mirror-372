"""
进度跟踪器

包含ProgressTracker类，负责单个任务的进度跟踪和阶段管理
"""

import logging
import time
from typing import Dict, List, Optional, Any

# 导入枚举定义
from ..enums import ProgressStage, ProgressStatus

# 导入数据模型
from .models import ProgressInfo, StageConfig
from .callbacks import ProgressCallback


# 默认阶段配置
DEFAULT_STAGE_CONFIGS = {
    ProgressStage.CLONE: StageConfig(
        stage=ProgressStage.CLONE,
        description="从远程仓库克隆代码到本地",
        weight=15,
        name="代码克隆",
        estimated_duration=30
    ),
    ProgressStage.CLASSIFICATION: StageConfig(
        stage=ProgressStage.CLASSIFICATION,
        description="分析项目类型和技术栈",
        weight=10,
        name="项目分类",
        estimated_duration=60
    ),
    ProgressStage.RAG_BUILD: StageConfig(
        stage=ProgressStage.RAG_BUILD,
        description="构建检索增强生成知识库",
        weight=25,
        name="RAG知识库构建",
        estimated_duration=360
    ),
    ProgressStage.CATALOGUE_GENERATION: StageConfig(
        stage=ProgressStage.CATALOGUE_GENERATION,
        description="生成文档目录结构",
        weight=10,
        name="文档目录生成",
        estimated_duration=120
    ),
    ProgressStage.DOCUMENT_GENERATION: StageConfig(
        stage=ProgressStage.DOCUMENT_GENERATION,
        description="生成详细文档内容",
        weight=30,
        name="文档内容生成",
        estimated_duration=2100
    ),
    ProgressStage.OVERVIEW_GENERATION: StageConfig(
        stage=ProgressStage.OVERVIEW_GENERATION,
        description="生成项目概览文档",
        weight=10,
        name="项目概览生成",
        estimated_duration=180
    ),
    ProgressStage.UNKNOWN: StageConfig(
        stage=ProgressStage.UNKNOWN,
        description="未知阶段，用于错误处理",
        weight=1,
        name="未知阶段",
        estimated_duration=0
    )
}


class ProgressTracker:
    """进度跟踪器 - 跟踪单个任务的进度"""
    
    def __init__(self, task_id: int, callbacks: Optional[List[ProgressCallback]] = None, stage_configs: Optional[Dict[ProgressStage, StageConfig]] = None):
        self.task_id = task_id
        self.callbacks = callbacks or []
        self.stage_configs = stage_configs or DEFAULT_STAGE_CONFIGS.copy()
        self.current_stage: ProgressStage = ProgressStage.CLONE
        self.current_progress = 0
        self.stage_progress: Dict[ProgressStage, float] = {}
        self.stage_status: Dict[ProgressStage, ProgressStatus] = {}
        self.start_time = time.time()
        self.logger = logging.getLogger(__name__)
        
        # 文档处理相关属性
        self.total_documents = 0
        self.completed_documents = 0
        
        # 初始化所有阶段为待处理状态
        for stage in self.stage_configs.keys():
            self.stage_progress[stage] = 0.0
            self.stage_status[stage] = ProgressStatus.PENDING
    
    def add_callback(self, callback: ProgressCallback):
        """添加进度回调"""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: ProgressCallback):
        """移除进度回调"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    def set_document_count(self, total_documents: int):
        """设置总文档数"""
        self.total_documents = total_documents
        self.logger.info(f"设置总文档数: {total_documents}")
    
    def update_document_progress(self, completed_documents: int):
        """更新文档生成进度
        
        Args:
            completed_documents: 已完成的文档数量
        """
        self.completed_documents = completed_documents
        self.logger.info(f"文档进度更新: {completed_documents}/{self.total_documents}")
        
        # 如果当前处于文档生成阶段，更新阶段进度
        if self.current_stage == ProgressStage.DOCUMENT_GENERATION and self.total_documents > 0:
            # 计算文档生成阶段的进度百分比
            stage_progress = min(100.0, (completed_documents / self.total_documents) * 100.0)
            self.stage_progress[ProgressStage.DOCUMENT_GENERATION] = stage_progress
            
            # 创建进度信息并触发回调
            progress_info = ProgressInfo(
                task_id=self.task_id,
                stage=ProgressStage.DOCUMENT_GENERATION,
                status=ProgressStatus.RUNNING,
                progress=stage_progress,
                message=f"已生成文档: {completed_documents}/{self.total_documents}",
                details={
                    "completed_documents": completed_documents,
                    "total_documents": self.total_documents,
                    "completion_rate": f"{stage_progress:.1f}%"
                }
            )
            
            # 调用所有回调
            for callback in self.callbacks:
                try:
                    if hasattr(callback, 'on_progress'):
                        callback.on_progress(progress_info)
                except Exception as e:
                    self.logger.error(f"回调错误: {e}")
    
    async def update_progress(self, stage: ProgressStage, status: ProgressStatus, progress: float, message: str, details: Optional[Dict[str, Any]] = None):
        """更新进度"""
        self.current_stage = stage
        self.current_progress = progress
        self.stage_progress[stage] = progress
        self.stage_status[stage] = status
        
        progress_info = ProgressInfo(
            task_id=self.task_id,
            stage=stage,
            status=status,
            progress=progress,
            message=message,
            details=details
        )
        
        # 调用所有回调
        for callback in self.callbacks:
            try:
                if hasattr(callback, 'on_progress'):
                    callback.on_progress(progress_info)
            except Exception as e:
                self.logger.error(f"回调错误: {e}")
    
    async def start_stage(self, stage: ProgressStage, message: str = ""):
        """开始新阶段"""
        self.current_stage = stage
        self.stage_status[stage] = ProgressStatus.RUNNING
        self.stage_progress[stage] = 0.0
        
        if not message:
            message = f"开始{self.stage_configs[stage].name}"
        
        progress_info = ProgressInfo(
            task_id=self.task_id,
            stage=stage,
            status=ProgressStatus.RUNNING,
            progress=0,
            message=message
        )
        
        # 调用所有回调
        for callback in self.callbacks:
            try:
                callback.on_progress(progress_info)
            except Exception as e:
                self.logger.error(f"回调错误: {e}")
    
    async def complete_stage(self, stage: ProgressStage,  message: str = ""):
        """完成当前阶段"""
        self.current_stage = stage
        self.stage_progress[self.current_stage] = 100
        self.stage_status[self.current_stage] = ProgressStatus.COMPLETED
        
        if not message:
            message = f"{self.stage_configs[self.current_stage].name}已完成"
        
        progress_info = ProgressInfo(
            task_id=self.task_id,
            stage=self.current_stage,
            status=ProgressStatus.COMPLETED,
            progress=100,
            message=message
        )
        
        # 调用所有回调
        for callback in self.callbacks:
            try:
                if hasattr(callback, 'on_progress'):
                    callback.on_progress(progress_info)
            except Exception as e:
                self.logger.error(f"回调错误: {e}")
    
    async def fail_stage(self, stage: ProgressStage, message: str = ""):
        """阶段失败"""
        self.current_stage = stage
        
        self.stage_status[self.current_stage] = ProgressStatus.FAILED
        self.stage_progress[self.current_stage] = 0
        
        if not message:
            message = f"{self.stage_configs[self.current_stage].name}失败"
        
        progress_info = ProgressInfo(
            task_id=self.task_id,
            stage=self.current_stage,
            status=ProgressStatus.FAILED,
            progress=0,
            message=message
        )
        
        # 调用所有回调
        for callback in self.callbacks:
            try:
                if hasattr(callback, 'on_progress'):
                    callback.on_progress(progress_info)
            except Exception as e:
                self.logger.error(f"回调错误: {e}")
    
    async def report_error(self,  error_message: str):
        """报告错误并标记当前阶段失败"""
        if self.current_stage is None:
            self.current_stage = ProgressStage.UNKNOWN
        # 标记当前阶段失败
        self.stage_status[self.current_stage] = ProgressStatus.FAILED
        self.stage_progress[self.current_stage] = 0
        
        progress_info = ProgressInfo(
            task_id=self.task_id,
            stage=self.current_stage,
            status=ProgressStatus.FAILED,
            progress=0,
            message=error_message,
            error=error_message
        )
        
        # 调用所有回调
        for callback in self.callbacks:
            try:
                if hasattr(callback, 'on_progress'):
                    callback.on_progress(progress_info)
            except Exception as e:
                self.logger.error(f"回调错误: {e}")
    
    def get_overall_progress(self) -> float:
        """获取总体进度"""
        total_progress = 0.0
        total_weight = sum(config.weight for config in self.stage_configs.values())
        
        for stage, config in self.stage_configs.items():
            stage_progress = self.stage_progress.get(stage, 0.0)
            if self.stage_status.get(stage) == ProgressStatus.COMPLETED:
                stage_progress = 100.0
            total_progress += (stage_progress / 100.0) * config.weight
        
        return total_progress
    
    def get_stage_info(self, stage: ProgressStage) -> Optional[StageConfig]:
        """获取阶段信息"""
        return self.stage_configs.get(stage)
    
    def is_completed(self) -> bool:
        """检查是否完成"""
        for stage in self.stage_configs.keys():
            if self.stage_status.get(stage) != ProgressStatus.COMPLETED:
                return False
        return True
    
    def is_failed(self) -> bool:
        """检查是否失败"""
        for stage in self.stage_configs.keys():
            if self.stage_status.get(stage) == ProgressStatus.FAILED:
                return True
        return False