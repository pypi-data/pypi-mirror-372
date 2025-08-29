"""
仓库依赖关系模型

定义仓库间依赖关系的数据结构和相关操作
"""

from typing import Dict, Any, Optional
from sqlalchemy import Column, String, BigInteger, ForeignKey, Index
from sqlalchemy.orm import relationship
from .base import BaseModel


class RepositoryDependency(BaseModel):
    """仓库依赖关系模型"""
    __tablename__ = "repository_dependency"
    
    # 外键
    source_repo_id = Column(BigInteger, ForeignKey('repository.id'), nullable=False, comment='源项目ID')
    target_repo_id = Column(BigInteger, ForeignKey('repository.id'), nullable=True, comment='依赖目标项目ID')
    target_endpoint_id = Column(BigInteger, ForeignKey('repository_endpoint.id'), nullable=True, comment='依赖目标接口ID')
    
    # 业务字段
    target_endpoint_url = Column(String(500), nullable=False, comment='依赖目标接口URL')
    
    # 关系
    source_repository = relationship("Repository", 
                                   foreign_keys=[source_repo_id], 
                                   back_populates="source_dependencies")
    target_repository = relationship("Repository", 
                                   foreign_keys=[target_repo_id], 
                                   back_populates="target_dependencies")
    target_endpoint = relationship("RepositoryEndpoint", back_populates="dependencies")
    
    # 索引
    __table_args__ = (
        Index('idx_source_target_repo', 'source_repo_id', 'target_repo_id'),
        Index('idx_target_endpoint_id', 'target_endpoint_id'),
    )
    
    def __repr__(self):
        return f"<RepositoryDependency(id={self.id}, source_repo_id={self.source_repo_id}, target_endpoint_url='{self.target_endpoint_url}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        base_dict = super().to_dict()
        base_dict.update({
            'source_repo_id': self.source_repo_id,
            'target_repo_id': self.target_repo_id,
            'target_endpoint_id': self.target_endpoint_id,
            'target_endpoint_url': self.target_endpoint_url,
        })
        return base_dict
    
    @property
    def has_target_repository(self) -> bool:
        """判断是否有目标仓库"""
        return self.target_repo_id is not None
    
    @property
    def has_target_endpoint(self) -> bool:
        """判断是否有目标端点"""
        return self.target_endpoint_id is not None
    
    @property
    def is_internal_dependency(self) -> bool:
        """判断是否为内部依赖（有目标仓库）"""
        return self.has_target_repository
    
    @property
    def is_external_dependency(self) -> bool:
        """判断是否为外部依赖（无目标仓库）"""
        return not self.has_target_repository
    
    def get_dependency_type(self) -> str:
        """获取依赖类型"""
        if self.is_internal_dependency:
            return "internal"
        else:
            return "external"
    
    def update_target_endpoint(self, endpoint_url: str, endpoint_id: int = None, user: str = None):
        """更新目标端点"""
        self.target_endpoint_url = endpoint_url
        if endpoint_id:
            self.target_endpoint_id = endpoint_id
        if user:
            self.update_user = user
        self.update_by_user(user or self.update_user)