"""
文档评论模型

定义文档评论的数据结构和相关操作
"""

from typing import Dict, Any
from sqlalchemy import Column, String, BigInteger, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from .base import BaseModel


class DocumentComment(BaseModel):
    """文档评论模型"""
    __tablename__ = "document_comment"
    
    # 外键
    document_id = Column(BigInteger, ForeignKey('document.id'), nullable=False, comment='文档ID')
    
    # 业务字段
    ref_id = Column(BigInteger, nullable=False, default=0, comment='上一级文档评论ID')
    user_name = Column(String(100), nullable=False, comment='用户名')
    content = Column(String(1000), nullable=False, comment='评论内容')
    is_accepted = Column(Boolean, nullable=True, comment='是否可被采用（0：否；1: 是）')
    regenerate_flag = Column(Boolean, nullable=False, default=0, comment='重新触发文档生成标识（0：未生成；1：已生成）')
    
    # 关系
    document = relationship("Document", back_populates="comments")
    
    # 索引
    __table_args__ = (
        Index('idx_document_id', 'document_id'),
        Index('idx_ref_id', 'ref_id'),
        Index('idx_regenerate_flag', 'regenerate_flag'),
        Index('idx_is_accepted', 'is_accepted'),
        Index('idx_user_name', 'user_name'),
    )
    
    def __repr__(self):
        return f"<DocumentComment(id={self.id}, document_id={self.document_id}, user_name='{self.user_name}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        base_dict = super().to_dict()
        base_dict.update({
            'document_id': self.document_id,
            'ref_id': self.ref_id,
            'user_name': self.user_name,
            'content': self.content,
            'is_accepted': self.is_accepted,
            'regenerate_flag': self.regenerate_flag,
        })
        return base_dict
    
    @property
    def is_regenerate_request(self) -> bool:
        """判断是否为重新生成请求"""
        return self.is_accepted and not self.regenerate_flag
    
    @property
    def content_length(self) -> int:
        """获取评论内容长度"""
        return len(self.content) if self.content else 0
    
    @property
    def content_preview(self) -> str:
        """获取评论内容预览（前50个字符）"""
        if not self.content:
            return ""
        return self.content[:50] + "..." if len(self.content) > 50 else self.content

    
    def set_is_accepted(self, flag: bool = True, user: str = None):
        """设置该评论是否被采纳标识，仅一级评论"""
        self.is_accepted = flag
        if user:
            self.update_user = user
        self.update_by_user(user or self.update_user)
    

    def set_delete(self, user: str = None):
        """删除评论"""
        self.is_delete = True
        if user:
            self.update_user = user
        self.update_by_user(user or self.update_user)


    def set_regenerate_flag(self, user: str = None):
        """设置当前评论需要重新生成文档"""
        self.regenerate_flag = False
        if user:
            self.update_user = user
        self.update_by_user(user or self.update_user)
    

    def mark_as_processed(self, user: str = None):
        """
        标记当前对象为已处理状态
        """
        # 设置处理状态标志为已完成
        self.regenerate_flag = True
        
        # 更新操作用户信息（如果提供了新的用户标识）
        if user:
            self.update_user = user
        
        # 执行更新操作
        self.update_by_user(user or self.update_user)



