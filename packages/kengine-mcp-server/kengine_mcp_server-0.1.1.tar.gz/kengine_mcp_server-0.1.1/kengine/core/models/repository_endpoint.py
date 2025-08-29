"""
仓库端点信息模型

定义仓库端点的数据结构和相关操作
"""

from typing import Dict, Any
from sqlalchemy import Column, String, Integer, ForeignKey, Index, BigInteger
from sqlalchemy.orm import relationship
from .base import BaseModel


class RepositoryEndpoint(BaseModel):
    """仓库端点信息模型"""
    __tablename__ = "repository_endpoint"
    
    # 外键
    repo_id = Column(BigInteger, ForeignKey('repository.id'), nullable=False, comment='项目ID')
    
    # 业务字段
    endpoint_type = Column(Integer, nullable=False, comment='端点类型')
    endpoint_url = Column(String(500), nullable=False, comment='端点URL')
    doc_url = Column(String(500), nullable=True, default='', comment='文档地址')
    desc = Column(String(500), nullable=True, default='', comment='接口描述')
    
    # 关系
    repository = relationship("Repository", back_populates="endpoints")
    dependencies = relationship("RepositoryDependency", back_populates="target_endpoint")
    
    # 索引
    __table_args__ = (
        Index('idx_repo_id', 'repo_id'),
        Index('idx_endpoint_url', 'endpoint_url'),
    )
    
    def __repr__(self):
        return f"<RepositoryEndpoint(id={self.id}, endpoint_url='{self.endpoint_url}', type={self.endpoint_type})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        base_dict = super().to_dict()
        base_dict.update({
            'repo_id': self.repo_id,
            'endpoint_type': self.endpoint_type,
            'endpoint_url': self.endpoint_url,
            'doc_url': self.doc_url,
            'desc': self.desc,
        })
        return base_dict
    
    @property
    def has_documentation(self) -> bool:
        """判断是否有文档"""
        return bool(self.doc_url and self.doc_url.strip())
    
    @property
    def has_description(self) -> bool:
        """判断是否有描述"""
        return bool(self.desc and self.desc.strip())
    
    def update_documentation(self, doc_url: str, user: str = None):
        """更新文档地址"""
        self.doc_url = doc_url
        if user:
            self.update_user = user
        self.update_by_user(user or self.update_user)
    
    def update_description(self, description: str, user: str = None):
        """更新描述"""
        self.desc = description
        if user:
            self.update_user = user
        self.update_by_user(user or self.update_user)