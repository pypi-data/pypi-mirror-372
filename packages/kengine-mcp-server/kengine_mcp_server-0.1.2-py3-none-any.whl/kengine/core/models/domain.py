"""
业务领域模型

定义业务领域的数据结构和相关操作
"""

from typing import Dict, Any, List
from sqlalchemy import Column, String, Integer, Index, BigInteger
from sqlalchemy.orm import relationship
from .base import BaseModel


class Domain(BaseModel):
    """业务领域模型"""
    __tablename__ = "domain"
    
    # 业务字段
    domain_code = Column(String(100), nullable=False, unique=True, comment='业务领域编码')
    domain_name = Column(String(200), nullable=False, comment='业务领域名称')
    parent_id = Column(BigInteger, nullable=True, default=0, comment='父业务领域id')
    level = Column(Integer, nullable=True, default=0, comment='层级')
    department = Column(String(100), nullable=True, default='', comment='所属部门')
    
    # 关系
    repositories = relationship("Repository", back_populates="domain", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('uni_idx_domain_code', 'domain_code'),
        Index('uni_idx_parent_id', 'parent_id'),
    )
    
    def __repr__(self):
        return f"<Domain(id={self.id}, domain_code='{self.domain_code}', domain_name='{self.domain_name}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        base_dict = super().to_dict()
        base_dict.update({
            'domain_code': self.domain_code,
            'domain_name': self.domain_name,
            'parent_id': self.parent_id,
            'level': self.level,
            'department': self.department,
        })
        return base_dict
    
    @property
    def is_root_domain(self) -> bool:
        """判断是否为根域"""
        return self.parent_id == 0 or self.parent_id is None
    
    @property
    def repository_count(self) -> int:
        """获取该领域下的仓库数量"""
        return len(self.repositories) if self.repositories else 0
    
    def get_full_path(self) -> str:
        """获取完整路径（需要递归查询父级）"""
        # 这里只返回当前名称，完整路径需要在服务层实现
        return self.domain_name