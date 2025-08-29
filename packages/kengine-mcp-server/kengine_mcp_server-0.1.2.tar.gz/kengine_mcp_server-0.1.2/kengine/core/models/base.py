"""
基础模型类

定义所有业务模型的公用字段和基础功能
"""

from datetime import datetime
from typing import Dict, Any
from sqlalchemy import Column, String, DateTime, Boolean, BigInteger
from ...db import Base


class BaseModel(Base):
    """基础模型类，包含所有业务模型的公用字段"""
    __abstract__ = True
    
    # 主键
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    
    # 公用字段
    create_user = Column(String(100), nullable=False, comment='创建人')
    create_time = Column(DateTime, nullable=False, default=datetime.utcnow, comment='创建时间')
    update_user = Column(String(100), nullable=True, default='', comment='更新人')
    update_time = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    is_delete = Column(Boolean, nullable=False, default=False, comment='是否删除，0:否;1:是')
    
    def __repr__(self):
        """基础字符串表示"""
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，子类可以重写此方法添加更多字段"""
        return {
            'id': self.id,
            'create_user': self.create_user,
            'create_time': self.create_time.isoformat() if self.create_time else None,
            'update_user': self.update_user,
            'update_time': self.update_time.isoformat() if self.update_time else None,
            'is_delete': self.is_delete,
        }
    
    def soft_delete(self, user: str = None):
        """软删除记录"""
        self.is_delete = True
        if user:
            self.update_user = user
        self.update_time = datetime.utcnow()
    
    def restore(self, user: str = None):
        """恢复已删除的记录"""
        self.is_delete = False
        if user:
            self.update_user = user
        self.update_time = datetime.utcnow()
    
    def update_by_user(self, user: str):
        """更新记录的修改人和修改时间"""
        self.update_user = user
        self.update_time = datetime.utcnow()