"""
任务模型

定义知识生成任务的数据模型，包含任务的基本信息、状态和执行参数
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, Text, JSON, Integer, Index, Boolean
from sqlalchemy.orm import relationship
from ...db import Base
from ...core.enums import TaskStatus


class Task(Base):
    """知识生成任务模型"""
    __tablename__ = "tasks"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 基本信息
    name = Column(String(255), nullable=False, comment="任务名称")
    description = Column(Text, nullable=True, comment="任务描述")
    
    # 仓库信息
    repo_group = Column(String(255), nullable=False, comment="仓库组织/用户名")
    repo_name = Column(String(255), nullable=False, comment="仓库名称")
    branch = Column(String(255), nullable=False, default="master", comment="分支名称")
    
    # 执行参数
    model_name = Column(String(100), nullable=False, default="gpt-4.1", comment="使用的大模型名称")
    execute_step = Column(String(50), nullable=False, default="full", comment="执行步骤")
    prompt_version = Column(String(50), nullable=True, comment="提示词版本")
    force_project_type = Column(String(100), nullable=True, comment="强制指定的项目类型")
    specify_document_path = Column(String(500), nullable=True, comment="指定文档路径")
    output_dir = Column(String(500), nullable=True, comment="输出目录")
    
    # 任务状态
    status = Column(String(20), nullable=False, default=TaskStatus.PENDING.value, comment="任务状态")
    
    # 时间信息
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="创建时间")
    started_at = Column(DateTime, nullable=True, comment="开始时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 结果信息
    project_path = Column(String(500), nullable=True, comment="项目路径")
    output_path = Column(String(500), nullable=True, comment="输出路径")
    project_type = Column(String(100), nullable=True, comment="项目类型")
    strategy_used = Column(String(100), nullable=True, comment="使用的策略")
    
    # 统计信息
    total_documents = Column(Integer, nullable=True, default=0, comment="总文档数")
    completed_documents = Column(Integer, nullable=True, default=0, comment="已完成文档数")
    
    # 错误信息
    error_message = Column(String(500), nullable=True, comment="错误信息")
    error_stage = Column(String(100), nullable=True, comment="出错阶段")
    
    # 元数据和配置
    task_metadata = Column(String(500), nullable=True, comment="任务元数据")
    config = Column(String(500), nullable=True, comment="任务配置")
    
    # 标记字段
    is_deleted = Column(Boolean, nullable=False, default=False, comment="是否已删除")
    
    # 关系
    progress_records = relationship("TaskProgress", back_populates="task", cascade="all, delete-orphan")
    llm_stats = relationship("LLMStats", back_populates="task", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_task_created_at', 'created_at'),
        Index('idx_task_repo', 'repo_group', 'repo_name')
    )
    
    
    def __repr__(self):
        return f"<Task(id={self.id}, name='{self.name}', status='{self.status}')>"
    
    @property
    def duration_seconds(self) -> Optional[int]:
        """获取任务执行时长（秒）"""
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds())
        elif self.started_at:
            return int((datetime.utcnow() - self.started_at).total_seconds())
        return None
    
    @property
    def progress_percentage(self) -> float:
        """获取任务进度百分比"""
        if self.total_documents and self.total_documents > 0:
            return min(100.0, (self.completed_documents or 0) / self.total_documents * 100)
        return 0.0
    
    @property
    def is_running(self) -> bool:
        """判断任务是否正在运行"""
        return self.status == TaskStatus.RUNNING.value
    
    @property
    def is_completed(self) -> bool:
        """判断任务是否已完成"""
        return self.status == TaskStatus.COMPLETED.value
    
    @property
    def is_failed(self) -> bool:
        """判断任务是否失败"""
        return self.status == TaskStatus.FAILED.value
    
    @property
    def repo_full_name(self) -> str:
        """获取完整仓库名称"""
        return f"{self.repo_group}/{self.repo_name}"
    
    def start_task(self):
        """开始任务"""
        self.status = TaskStatus.RUNNING.value
        self.started_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def complete_task(self, project_path: str = None, output_path: str = None):
        """完成任务"""
        self.status = TaskStatus.COMPLETED.value
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        if project_path:
            self.project_path = project_path
        if output_path:
            self.output_path = output_path
    
    def fail_task(self, error_message: str, error_stage: str = None):
        """任务失败"""
        self.status = TaskStatus.FAILED.value
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.error_message = error_message
        if error_stage:
            self.error_stage = error_stage
    
    def cancel_task(self):
        """取消任务"""
        self.status = TaskStatus.CANCELLED.value
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def update_progress(self, completed_documents: int, total_documents: int = None):
        """更新任务进度"""
        self.completed_documents = completed_documents
        if total_documents is not None:
            self.total_documents = total_documents
        self.updated_at = datetime.utcnow()
    
    def set_metadata(self, key: str, value: Any):
        """设置元数据"""
        if self.task_metadata is None:
            self.task_metadata = {}
        self.task_metadata[key] = value
        self.updated_at = datetime.utcnow()
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """获取元数据"""
        if self.task_metadata is None:
            return default
        return self.task_metadata.get(key, default)
    
    def set_config(self, key: str, value: Any):
        """设置配置"""
        if self.config is None:
            self.config = {}
        self.config[key] = value
        self.updated_at = datetime.utcnow()
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置"""
        if self.config is None:
            return default
        return self.config.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'repo_group': self.repo_group,
            'repo_name': self.repo_name,
            'repo_full_name': self.repo_full_name,
            'branch': self.branch,
            'model_name': self.model_name,
            'execute_step': self.execute_step,
            'prompt_version': self.prompt_version,
            'force_project_type': self.force_project_type,
            'specify_document_path': self.specify_document_path,
            'output_dir': self.output_dir,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'project_path': self.project_path,
            'output_path': self.output_path,
            'project_type': self.project_type,
            'strategy_used': self.strategy_used,
            'total_documents': self.total_documents,
            'completed_documents': self.completed_documents,
            'progress_percentage': self.progress_percentage,
            'duration_seconds': self.duration_seconds,
            'error_message': self.error_message,
            'error_stage': self.error_stage,
            'metadata': self.task_metadata,
            'config': self.config,
            'is_deleted': self.is_deleted,
        }