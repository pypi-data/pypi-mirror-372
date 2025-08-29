"""
文档信息模型

定义文档的数据结构和相关操作
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import Column, String, Integer, JSON, ForeignKey, Index, Text, BigInteger
from sqlalchemy.orm import relationship
from .base import BaseModel


class Document(BaseModel):
    """文档信息模型"""
    __tablename__ = "document"
    
    # 外键
    repo_doc_version_id = Column(BigInteger, ForeignKey('repo_document_version.id'), nullable=False, comment='仓库文档版本ID')
    parent_id = Column(BigInteger, nullable=True, default=0, comment='父文档ID')
    
    # 业务字段
    doc_title = Column(String(500), nullable=False, comment='文档标题')
    file_path = Column(String(1000), nullable=True, default='', comment='文件路径')
    storage_path = Column(String(1000), nullable=True, default='', comment='存储路径（oss路径）')
    summary = Column(String(2000), nullable=True, default='', comment='文档摘要')
    level = Column(Integer, nullable=True, default=1, comment='文档层级')
    sort_order = Column(Integer, nullable=True, default=0, comment='排序序号')
    related_file_paths = Column(JSON, nullable=True, comment='关联文件路径')
    
    # 关系
    repo_document_version = relationship("RepoDocumentVersion", back_populates="documents")
    comments = relationship("DocumentComment", back_populates="document", cascade="all, delete-orphan")
    histories = relationship("DocumentHistory", back_populates="document", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_repo_doc_version_id', 'repo_doc_version_id'),
        Index('idx_parent_id', 'parent_id'),
    )
    
    def __repr__(self):
        return f"<Document(id={self.id}, doc_title='{self.doc_title}', level={self.level})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        base_dict = super().to_dict()
        base_dict.update({
            'repo_doc_version_id': self.repo_doc_version_id,
            'parent_id': self.parent_id,
            'doc_title': self.doc_title,
            'file_path': self.file_path,
            'storage_path': self.storage_path,
            'summary': self.summary,
            'level': self.level,
            'sort_order': self.sort_order,
            'related_file_paths': self.related_file_paths,
        })
        return base_dict
    
    @property
    def is_root_document(self) -> bool:
        """判断是否为根文档"""
        return self.parent_id == 0 or self.parent_id is None
    
    @property
    def has_file_path(self) -> bool:
        """判断是否有文件路径"""
        return bool(self.file_path and self.file_path.strip())
    
    @property
    def has_storage_path(self) -> bool:
        """判断是否有存储路径"""
        return bool(self.storage_path and self.storage_path.strip())
    
    @property
    def has_summary(self) -> bool:
        """判断是否有摘要"""
        return bool(self.summary and self.summary.strip())
    
    @property
    def has_related_files(self) -> bool:
        """判断是否有关联文件"""
        return self.related_file_paths is not None and len(self.related_file_paths) > 0
    
    @property
    def comment_count(self) -> int:
        """获取评论数量"""
        return len(self.comments) if self.comments else 0
    
    @property
    def history_count(self) -> int:
        """获取历史记录数量"""
        return len(self.histories) if self.histories else 0
    
    def get_related_file_paths(self) -> List[str]:
        """获取关联文件路径列表"""
        if not self.has_related_files:
            return []
        return self.related_file_paths if isinstance(self.related_file_paths, list) else []
    
    def add_related_file_path(self, file_path: str, user: str = None):
        """添加关联文件路径"""
        if self.related_file_paths is None:
            self.related_file_paths = []
        if file_path not in self.related_file_paths:
            self.related_file_paths.append(file_path)
            if user:
                self.update_user = user
            self.update_by_user(user or self.update_user)
    
    def remove_related_file_path(self, file_path: str, user: str = None):
        """移除关联文件路径"""
        if self.has_related_files and file_path in self.related_file_paths:
            self.related_file_paths.remove(file_path)
            if user:
                self.update_user = user
            self.update_by_user(user or self.update_user)
    
    def update_storage_path(self, storage_path: str, user: str = None):
        """更新存储路径"""
        self.storage_path = storage_path
        if user:
            self.update_user = user
        self.update_by_user(user or self.update_user)
    
    def update_summary(self, summary: str, user: str = None):
        """更新摘要"""
        self.summary = summary
        if user:
            self.update_user = user
        self.update_by_user(user or self.update_user)
    
    def update_sort_order(self, sort_order: int, user: str = None):
        """更新排序序号"""
        self.sort_order = sort_order
        if user:
            self.update_user = user
        self.update_by_user(user or self.update_user)