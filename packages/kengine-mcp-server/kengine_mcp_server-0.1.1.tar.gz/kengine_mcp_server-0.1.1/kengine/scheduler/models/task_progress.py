"""
任务进度模型

定义任务进度跟踪的数据模型，记录任务执行过程中的各个阶段和进度信息
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey, Index, Integer, Numeric
from sqlalchemy.orm import relationship
from ...db import Base
from ...core.enums import ProgressStage, ProgressStatus


class TaskProgress(Base):
    """任务进度记录模型"""
    __tablename__ = "task_progress"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 关联任务
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False, comment="关联任务ID")
    
    # 进度信息
    stage = Column(String(50), nullable=False, comment="进度阶段")
    status = Column(String(20), nullable=False, comment="进度状态")
    progress = Column(Numeric(3,2), nullable=False, default=0.00, comment="进度百分比 (0.0-1.0)")
    message = Column(String(500), nullable=True, comment="进度消息")
    
    # 详细信息
    details = Column(String(1000), nullable=True, comment="详细信息")
    error_message = Column(String(1000), nullable=True, comment="错误信息")
    
    # 时间信息
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, comment="记录时间")
    stage_started_at = Column(DateTime, nullable=True, comment="阶段开始时间")
    stage_completed_at = Column(DateTime, nullable=True, comment="阶段完成时间")
    
    # 统计信息
    stage_duration_ms = Column(Integer, nullable=True, comment="阶段耗时(毫秒)")
    estimated_remaining_ms = Column(Integer, nullable=True, comment="预估剩余时间(毫秒)")
    
    # 大模型统计信息快照
    llm_stats_snapshot = Column(JSON, nullable=True, comment="大模型统计信息快照")
    
    # 序号（用于排序）
    sequence = Column(Integer, nullable=False, default=0, comment="序号")
    
    # 关系
    task = relationship("Task", back_populates="progress_records")
    
    # 索引
    __table_args__ = (
        Index('idx_progress_task_id', 'task_id'),
        Index('idx_progress_stage', 'stage'),
        Index('idx_progress_status', 'status'),
        Index('idx_progress_timestamp', 'timestamp'),
        Index('idx_progress_task_sequence', 'task_id', 'sequence'),
    )
    
    
    def __repr__(self):
        return f"<TaskProgress(id={self.id}, task_id={self.task_id}, stage='{self.stage}', status='{self.status}')>"
    
    @property
    def progress_percentage(self) -> float:
        """获取进度百分比（0-100）"""
        return self.progress * 100
    
    @property
    def is_completed(self) -> bool:
        """判断阶段是否已完成"""
        return self.status == ProgressStatus.COMPLETED.value
    
    @property
    def is_failed(self) -> bool:
        """判断阶段是否失败"""
        return self.status == ProgressStatus.FAILED.value
    
    @property
    def is_running(self) -> bool:
        """判断阶段是否正在运行"""
        return self.status == ProgressStatus.RUNNING.value
    
    @property
    def stage_duration_seconds(self) -> Optional[float]:
        """获取阶段耗时（秒）"""
        if self.stage_duration_ms is not None:
            return self.stage_duration_ms / 1000.0
        elif self.stage_started_at and self.stage_completed_at:
            return (self.stage_completed_at - self.stage_started_at).total_seconds()
        return None
    
    def start_stage(self, message: str = ""):
        """开始阶段"""
        self.status = ProgressStatus.RUNNING.value
        self.stage_started_at = datetime.utcnow()
        self.timestamp = datetime.utcnow()
        if message:
            self.message = message
    
    def update_progress(self, progress: float, message: str = "", details: Dict[str, Any] = None):
        """更新进度"""
        self.progress = max(0.0, min(1.0, progress))  # 确保在0-1范围内
        self.timestamp = datetime.utcnow()
        if message:
            self.message = message
        if details:
            self.details = details
    
    def complete_stage(self, message: str = ""):
        """完成阶段"""
        self.status = ProgressStatus.COMPLETED.value
        self.progress = 1.0
        self.stage_completed_at = datetime.utcnow()
        self.timestamp = datetime.utcnow()
        if message:
            self.message = message
        
        # 计算阶段耗时
        if self.stage_started_at:
            duration = (self.stage_completed_at - self.stage_started_at).total_seconds()
            self.stage_duration_ms = int(duration * 1000)
    
    def fail_stage(self, error_message: str):
        """阶段失败"""
        self.status = ProgressStatus.FAILED.value
        self.stage_completed_at = datetime.utcnow()
        self.timestamp = datetime.utcnow()
        self.error_message = error_message
        
        # 计算阶段耗时
        if self.stage_started_at:
            duration = (self.stage_completed_at - self.stage_started_at).total_seconds()
            self.stage_duration_ms = int(duration * 1000)
    
    def set_llm_stats_snapshot(self, llm_stats: Dict[str, Any]):
        """设置大模型统计信息快照"""
        self.llm_stats_snapshot = llm_stats
        self.timestamp = datetime.utcnow()
    
    def set_detail(self, key: str, value: Any):
        """设置详细信息"""
        if self.details is None:
            self.details = {}
        self.details[key] = value
        self.timestamp = datetime.utcnow()
    
    def get_detail(self, key: str, default: Any = None) -> Any:
        """获取详细信息"""
        if self.details is None:
            return default
        return self.details.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'stage': self.stage,
            'status': self.status,
            'progress': self.progress,
            'progress_percentage': self.progress_percentage,
            'message': self.message,
            'details': self.details,
            'error_message': self.error_message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'stage_started_at': self.stage_started_at.isoformat() if self.stage_started_at else None,
            'stage_completed_at': self.stage_completed_at.isoformat() if self.stage_completed_at else None,
            'stage_duration_ms': self.stage_duration_ms,
            'stage_duration_seconds': self.stage_duration_seconds,
            'estimated_remaining_ms': self.estimated_remaining_ms,
            'llm_stats_snapshot': self.llm_stats_snapshot,
            'sequence': self.sequence,
        }
    
    @classmethod
    def create_stage_record(cls, task_id: int, stage: str, sequence: int = 0) -> 'TaskProgress':
        """创建阶段记录"""
        return cls(
            task_id=task_id,
            stage=stage,
            status=ProgressStatus.PENDING.value,
            progress=0.0,
            sequence=sequence,
            timestamp=datetime.utcnow()
        )
    
    @classmethod
    def get_stage_display_name(cls, stage: str) -> str:
        """获取阶段显示名称"""
        stage_names = {
            ProgressStage.CLONE.value: "代码库克隆",
            ProgressStage.CLASSIFICATION.value: "项目分类",
            ProgressStage.RAG_BUILD.value: "RAG知识库构建",
            ProgressStage.CATALOGUE_GENERATION.value: "文档目录生成",
            ProgressStage.DOCUMENT_GENERATION.value: "文档内容生成",
            ProgressStage.OVERVIEW_GENERATION.value: "项目概览生成",
        }
        return stage_names.get(stage, stage)
    
    @classmethod
    def get_status_display_name(cls, status: str) -> str:
        """获取状态显示名称"""
        status_names = {
            ProgressStatus.PENDING.value: "待处理",
            ProgressStatus.RUNNING.value: "进行中",
            ProgressStatus.COMPLETED.value: "已完成",
            ProgressStatus.FAILED.value: "失败",
        }
        return status_names.get(status, status)