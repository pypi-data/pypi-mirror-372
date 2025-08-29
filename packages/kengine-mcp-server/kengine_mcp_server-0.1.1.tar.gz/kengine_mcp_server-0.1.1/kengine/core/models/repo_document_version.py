"""
仓库文档版本模型

定义仓库文档版本的数据结构和相关操作
"""

from typing import Dict, Any, Optional
from sqlalchemy import Column, String, Integer, JSON, ForeignKey, Index, BigInteger
from sqlalchemy.orm import relationship
from .base import BaseModel


class RepoDocumentVersion(BaseModel):
    """仓库文档版本模型"""
    __tablename__ = "repo_document_version"
    
    # 外键
    repo_id = Column(BigInteger, ForeignKey('repository.id'), nullable=False, comment='仓库ID')
    
    # 业务字段
    version = Column(String(50), nullable=False, comment='版本号')
    git_commit = Column(String(100), nullable=True, default='', comment='Git提交号')
    analysis_config = Column(JSON, nullable=True, comment='分析配置（大模型版本，提示词版本等信息）')
    type = Column(Integer, nullable=False, default=1, comment='领域类型')
    status = Column(Integer, nullable=False, default=1, comment='状态')
    
    # 关系
    repository = relationship("Repository", back_populates="document_versions")
    documents = relationship("Document", back_populates="repo_document_version", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_repo_id_version_type', 'repo_id', 'version', 'type'),
    )
    
    def __repr__(self):
        return f"<RepoDocumentVersion(id={self.id}, repo_id={self.repo_id}, version='{self.version}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        base_dict = super().to_dict()
        base_dict.update({
            'repo_id': self.repo_id,
            'version': self.version,
            'git_commit': self.git_commit,
            'analysis_config': self.analysis_config,
            'type': self.type,
            'status': self.status,
        })
        return base_dict
    
    @property
    def has_git_commit(self) -> bool:
        """判断是否有Git提交号"""
        return bool(self.git_commit and self.git_commit.strip())
    
    @property
    def has_analysis_config(self) -> bool:
        """判断是否有分析配置"""
        return self.analysis_config is not None
    
    @property
    def document_count(self) -> int:
        """获取文档数量"""
        return len(self.documents) if self.documents else 0
    
    def get_analysis_config_value(self, key: str, default: Any = None) -> Any:
        """获取分析配置中的值"""
        if not self.has_analysis_config:
            return default
        return self.analysis_config.get(key, default)
    
    def set_analysis_config_value(self, key: str, value: Any, user: str = None):
        """设置分析配置中的值"""
        if self.analysis_config is None:
            self.analysis_config = {}
        self.analysis_config[key] = value
        if user:
            self.update_user = user
        self.update_by_user(user or self.update_user)
    
    def update_git_commit(self, git_commit: str, user: str = None):
        """更新Git提交号"""
        self.git_commit = git_commit
        if user:
            self.update_user = user
        self.update_by_user(user or self.update_user)
    
    def update_status(self, status: int, user: str = None):
        """更新状态"""
        self.status = status
        if user:
            self.update_user = user
        self.update_by_user(user or self.update_user)
    
    def get_version_info(self) -> Dict[str, Any]:
        """获取版本信息摘要"""
        return {
            'version': self.version,
            'git_commit': self.git_commit,
            'type': self.type,
            'status': self.status,
            'document_count': self.document_count,
            'has_analysis_config': self.has_analysis_config,
        }