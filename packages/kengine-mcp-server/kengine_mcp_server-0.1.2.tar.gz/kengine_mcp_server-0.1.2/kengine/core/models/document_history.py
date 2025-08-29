"""
文档变更历史模型

定义文档变更历史的数据结构和相关操作
"""

from typing import Dict, Any
from sqlalchemy import Column, String, Integer, ForeignKey, Index, BigInteger
from sqlalchemy.orm import relationship
from .base import BaseModel


class DocumentHistory(BaseModel):
    """文档变更历史模型"""
    __tablename__ = "document_history"
    
    # 外键
    document_id = Column(BigInteger, ForeignKey('document.id'), nullable=False, comment='文档ID')
    
    # 业务字段
    source_storage_path = Column(String(1000), nullable=False, comment='原存储路径')
    change_type = Column(Integer, nullable=False, default=1, comment='变更类型')
    diff_content = Column(String(2000), nullable=True, default='', comment='差异内容')
    
    # 关系
    document = relationship("Document", back_populates="histories")
    
    # 索引
    __table_args__ = (
        Index('idx_document_id', 'document_id'),
    )
    
    def __repr__(self):
        return f"<DocumentHistory(id={self.id}, document_id={self.document_id}, change_type='{self.change_type}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        base_dict = super().to_dict()
        base_dict.update({
            'document_id': self.document_id,
            'source_storage_path': self.source_storage_path,
            'change_type': self.change_type,
            'diff_content': self.diff_content,
        })
        return base_dict
    
    @property
    def has_diff_content(self) -> bool:
        """判断是否有差异内容"""
        return bool(self.diff_content is not None and self.diff_content.strip())
    
    @property
    def diff_content_preview(self) -> str:
        """获取差异内容预览（前200个字符）"""
        if not self.diff_content:
            return ""
        return self.diff_content[:200] + "..." if len(self.diff_content) > 200 else self.diff_content
    
    def set_diff_content(self, diff_content: str = None, user: str = None):
        """设置差异内容"""
        if diff_content is not None:
            self.diff_content = diff_content
        if user:
            self.update_user = user
        self.update_by_user(user or self.update_user)
    
    @classmethod
    def create_history(cls, document_id: int, source_storage_path: str, change_type: int = 1, 
                      diff_content: str = '', create_user: str = ''):
        """创建历史记录"""
        return cls(
            document_id=document_id,
            source_storage_path=source_storage_path,
            change_type=change_type,
            diff_content=diff_content,
            create_user=create_user,
            update_user=create_user
        )