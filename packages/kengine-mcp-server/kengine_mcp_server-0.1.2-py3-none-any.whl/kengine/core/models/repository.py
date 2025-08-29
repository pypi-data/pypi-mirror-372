"""
仓库信息模型

定义代码仓库的数据结构和相关操作
"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, String, BigInteger, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from .base import BaseModel


class Repository(BaseModel):
    """仓库信息模型"""
    __tablename__ = "repository"
    
    # 外键
    domain_id = Column(BigInteger, ForeignKey('domain.id'), nullable=False, comment='业务领域ID')
    
    # 业务字段
    repo_code = Column(String(100), nullable=False, unique=True, comment='仓库编码')
    repo_name = Column(String(200), nullable=False, comment='仓库名称')
    repo_related_group = Column(String(200), nullable=False, comment='仓库关联git群组')
    description = Column(String(500), nullable=True, default='', comment='项目描述')
    repo_type = Column(String(100), nullable=False, comment='仓库类型')
    main_language = Column(String(100), nullable=False, comment='主要编程语言')
    repo_url = Column(String(500), nullable=False, comment='代码仓库地址')
    repo_default_branch = Column(String(100), nullable=False, comment='代码分支')
    last_analyzed_time = Column(DateTime, nullable=True, comment='最后分析时间')
    current_version = Column(String(50), nullable=True, default='', comment='当前版本')
    disable_flag = Column(Boolean, nullable=False, default=False, comment='禁用标识：0：否；1：是')
    
    # 关系
    domain = relationship("Domain", back_populates="repositories")
    endpoints = relationship("RepositoryEndpoint", back_populates="repository", cascade="all, delete-orphan")
    source_dependencies = relationship("RepositoryDependency", 
                                     foreign_keys="RepositoryDependency.source_repo_id",
                                     back_populates="source_repository", 
                                     cascade="all, delete-orphan")
    target_dependencies = relationship("RepositoryDependency", 
                                     foreign_keys="RepositoryDependency.target_repo_id",
                                     back_populates="target_repository")
    document_versions = relationship("RepoDocumentVersion", back_populates="repository", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('uni_idx_repo_code', 'repo_code'),
        Index('idx_domain_id', 'domain_id'),
    )
    
    def __repr__(self):
        return f"<Repository(id={self.id}, repo_code='{self.repo_code}', repo_name='{self.repo_name}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        base_dict = super().to_dict()
        base_dict.update({
            'domain_id': self.domain_id,
            'repo_code': self.repo_code,
            'repo_name': self.repo_name,
            'repo_related_group': self.repo_related_group,
            'description': self.description,
            'repo_type': self.repo_type,
            'main_language': self.main_language,
            'repo_url': self.repo_url,
            'repo_default_branch': self.repo_default_branch,
            'last_analyzed_time': self.last_analyzed_time.isoformat() if self.last_analyzed_time else None,
            'current_version': self.current_version,
            'disable_flag': self.disable_flag,
        })
        return base_dict
    
    @property
    def is_enabled(self) -> bool:
        """判断仓库是否启用"""
        return not self.disable_flag
    
    @property
    def full_repo_name(self) -> str:
        """获取完整仓库名称"""
        return f"{self.repo_related_group}/{self.repo_name}"
    
    @property
    def endpoint_count(self) -> int:
        """获取端点数量"""
        return len(self.endpoints) if self.endpoints else 0
    
    @property
    def dependency_count(self) -> int:
        """获取依赖数量"""
        return len(self.source_dependencies) if self.source_dependencies else 0
    
    def update_analyzed_time(self, analyzed_time: datetime = None):
        """更新最后分析时间"""
        self.last_analyzed_time = analyzed_time or datetime.utcnow()
        self.update_time = datetime.utcnow()
    
    def enable(self, user: str = None):
        """启用仓库"""
        self.disable_flag = False
        if user:
            self.update_user = user
        self.update_time = datetime.utcnow()
    
    def disable(self, user: str = None):
        """禁用仓库"""
        self.disable_flag = True
        if user:
            self.update_user = user
        self.update_time = datetime.utcnow()