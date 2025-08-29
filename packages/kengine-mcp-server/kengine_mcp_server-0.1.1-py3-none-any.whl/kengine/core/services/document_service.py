"""
文档信息服务

提供文档信息相关的业务逻辑处理
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ...db.database_manager import db_manager
from ..models.document import Document


class DocumentService:
    """文档信息服务类"""
    
    def __init__(self):
        """初始化文档信息服务"""
        pass
    
    def create_document(self, repo_doc_version_id: int, doc_title: str, 
                       parent_id: int = 0, file_path: str = "", storage_path: str = "",
                       summary: str = "", level: int = 1, sort_order: int = 0,
                       related_file_paths: List[str] = None, **kwargs) -> Document:
        """创建文档"""
        with db_manager.transaction() as session:
            document = Document(
                repo_doc_version_id=repo_doc_version_id,
                parent_id=parent_id,
                doc_title=doc_title,
                file_path=file_path,
                storage_path=storage_path,
                summary=summary,
                level=level,
                sort_order=sort_order,
                related_file_paths=related_file_paths,
                **kwargs
            )
            session.add(document)
            session.flush()  # 获取 ID
            session.expunge(document)  # 从会话中分离
            return document
    
    def get_document_by_id(self, document_id: int) -> Optional[Document]:
        """根据ID获取文档"""
        with db_manager.session() as session:
            document = session.query(Document).filter(
                Document.id == document_id
            ).first()
            if document:
                session.expunge(document)
            return document
    
    def get_documents_by_version(self, repo_doc_version_id: int) -> List[Document]:
        """根据仓库文档版本ID获取所有文档"""
        with db_manager.session() as session:
            documents = session.query(Document).filter(
                Document.repo_doc_version_id == repo_doc_version_id
            ).order_by(Document.sort_order.asc(), Document.created_at.asc()).all()
            for document in documents:
                session.expunge(document)
            return documents
    
    def get_documents_by_parent(self, parent_id: int) -> List[Document]:
        """根据父文档ID获取子文档列表"""
        with db_manager.session() as session:
            documents = session.query(Document).filter(
                Document.parent_id == parent_id
            ).order_by(Document.sort_order.asc(), Document.created_at.asc()).all()
            for document in documents:
                session.expunge(document)
            return documents
    
    def get_root_documents(self, repo_doc_version_id: int) -> List[Document]:
        """获取根文档列表"""
        with db_manager.session() as session:
            documents = session.query(Document).filter(
                Document.repo_doc_version_id == repo_doc_version_id,
                (Document.parent_id == 0) | (Document.parent_id.is_(None))
            ).order_by(Document.sort_order.asc(), Document.created_at.asc()).all()
            for document in documents:
                session.expunge(document)
            return documents
    
    def get_documents_by_level(self, repo_doc_version_id: int, level: int) -> List[Document]:
        """根据层级获取文档列表"""
        with db_manager.session() as session:
            documents = session.query(Document).filter(
                Document.repo_doc_version_id == repo_doc_version_id,
                Document.level == level
            ).order_by(Document.sort_order.asc(), Document.created_at.asc()).all()
            for document in documents:
                session.expunge(document)
            return documents
    
    def get_document_by_file_path(self, repo_doc_version_id: int, file_path: str) -> Optional[Document]:
        """根据文件路径获取文档"""
        with db_manager.session() as session:
            document = session.query(Document).filter(
                Document.repo_doc_version_id == repo_doc_version_id,
                Document.file_path == file_path
            ).first()
            if document:
                session.expunge(document)
            return document
    
    def search_documents(self, keyword: str, repo_doc_version_id: int = None) -> List[Document]:
        """搜索文档（根据标题、摘要、文件路径）"""
        with db_manager.session() as session:
            query = session.query(Document).filter(
                (Document.doc_title.contains(keyword)) |
                (Document.summary.contains(keyword)) |
                (Document.file_path.contains(keyword))
            )
            if repo_doc_version_id:
                query = query.filter(Document.repo_doc_version_id == repo_doc_version_id)
            documents = query.order_by(Document.created_at.desc()).all()
            for document in documents:
                session.expunge(document)
            return documents
    
    def get_all_documents(self, limit: Optional[int] = None,
                         order_by: str = 'created_at', desc_order: bool = True) -> List[Document]:
        """获取所有文档"""
        with db_manager.session() as session:
            query = session.query(Document)
            if hasattr(Document, order_by):
                order_field = getattr(Document, order_by)
                if desc_order:
                    query = query.order_by(order_field.desc())
                else:
                    query = query.order_by(order_field.asc())
            if limit:
                query = query.limit(limit)
            documents = query.all()
            for document in documents:
                session.expunge(document)
            return documents
    
    def get_documents_with_summary(self, repo_doc_version_id: int = None) -> List[Document]:
        """获取有摘要的文档"""
        with db_manager.session() as session:
            query = session.query(Document).filter(
                Document.summary.isnot(None),
                Document.summary != ''
            )
            if repo_doc_version_id:
                query = query.filter(Document.repo_doc_version_id == repo_doc_version_id)
            documents = query.order_by(Document.created_at.desc()).all()
            for document in documents:
                session.expunge(document)
            return documents
    
    def get_documents_without_summary(self, repo_doc_version_id: int = None) -> List[Document]:
        """获取无摘要的文档"""
        with db_manager.session() as session:
            query = session.query(Document).filter(
                (Document.summary.is_(None)) |
                (Document.summary == '')
            )
            if repo_doc_version_id:
                query = query.filter(Document.repo_doc_version_id == repo_doc_version_id)
            documents = query.order_by(Document.created_at.desc()).all()
            for document in documents:
                session.expunge(document)
            return documents
    
    def get_documents_with_file_path(self, repo_doc_version_id: int = None) -> List[Document]:
        """获取有文件路径的文档"""
        with db_manager.session() as session:
            query = session.query(Document).filter(
                Document.file_path.isnot(None),
                Document.file_path != ''
            )
            if repo_doc_version_id:
                query = query.filter(Document.repo_doc_version_id == repo_doc_version_id)
            documents = query.order_by(Document.created_at.desc()).all()
            for document in documents:
                session.expunge(document)
            return documents
    
    def get_documents_with_storage_path(self, repo_doc_version_id: int = None) -> List[Document]:
        """获取有存储路径的文档"""
        with db_manager.session() as session:
            query = session.query(Document).filter(
                Document.storage_path.isnot(None),
                Document.storage_path != ''
            )
            if repo_doc_version_id:
                query = query.filter(Document.repo_doc_version_id == repo_doc_version_id)
            documents = query.order_by(Document.created_at.desc()).all()
            for document in documents:
                session.expunge(document)
            return documents
    
    def update_document(self, document_id: int, **kwargs) -> Optional[Document]:
        """更新文档信息"""
        with db_manager.transaction() as session:
            document = session.query(Document).filter(
                Document.id == document_id
            ).first()
            if document:
                for key, value in kwargs.items():
                    if hasattr(document, key):
                        setattr(document, key, value)
                document.updated_at = datetime.utcnow()
                session.flush()
                session.expunge(document)
                return document
            return None
    
    def update_document_title(self, document_id: int, doc_title: str, user: str = None) -> Optional[Document]:
        """更新文档标题"""
        update_data = {'doc_title': doc_title}
        if user:
            update_data['update_user'] = user
        return self.update_document(document_id, **update_data)
    
    def update_document_summary(self, document_id: int, summary: str, user: str = None) -> Optional[Document]:
        """更新文档摘要"""
        update_data = {'summary': summary}
        if user:
            update_data['update_user'] = user
        return self.update_document(document_id, **update_data)
    
    def update_storage_path(self, document_id: int, storage_path: str, user: str = None) -> Optional[Document]:
        """更新存储路径"""
        update_data = {'storage_path': storage_path}
        if user:
            update_data['update_user'] = user
        return self.update_document(document_id, **update_data)
    
    def update_sort_order(self, document_id: int, sort_order: int, user: str = None) -> Optional[Document]:
        """更新排序序号"""
        update_data = {'sort_order': sort_order}
        if user:
            update_data['update_user'] = user
        return self.update_document(document_id, **update_data)
    
    def update_level(self, document_id: int, level: int, user: str = None) -> Optional[Document]:
        """更新文档层级"""
        update_data = {'level': level}
        if user:
            update_data['update_user'] = user
        return self.update_document(document_id, **update_data)
    
    def add_related_file_path(self, document_id: int, file_path: str, user: str = None) -> Optional[Document]:
        """添加关联文件路径"""
        document = self.get_document_by_id(document_id)
        if not document:
            return None
        
        with db_manager.transaction() as session:
            doc_obj = session.query(Document).filter(
                Document.id == document_id
            ).first()
            if doc_obj:
                if doc_obj.related_file_paths is None:
                    doc_obj.related_file_paths = []
                if file_path not in doc_obj.related_file_paths:
                    doc_obj.related_file_paths.append(file_path)
                    doc_obj.updated_at = datetime.utcnow()
                    if user:
                        doc_obj.update_user = user
                    session.flush()
                    session.expunge(doc_obj)
                    return doc_obj
            return None
    
    def remove_related_file_path(self, document_id: int, file_path: str, user: str = None) -> Optional[Document]:
        """移除关联文件路径"""
        document = self.get_document_by_id(document_id)
        if not document:
            return None
        
        with db_manager.transaction() as session:
            doc_obj = session.query(Document).filter(
                Document.id == document_id
            ).first()
            if doc_obj and doc_obj.related_file_paths and file_path in doc_obj.related_file_paths:
                doc_obj.related_file_paths.remove(file_path)
                doc_obj.updated_at = datetime.utcnow()
                if user:
                    doc_obj.update_user = user
                session.flush()
                session.expunge(doc_obj)
                return doc_obj
            return None
    
    def delete_document(self, document_id: int) -> bool:
        """删除文档"""
        with db_manager.transaction() as session:
            document = session.query(Document).filter(
                Document.id == document_id
            ).first()
            if document:
                session.delete(document)
                return True
            return False
    
    def delete_documents_by_version(self, repo_doc_version_id: int) -> int:
        """删除指定版本的所有文档"""
        with db_manager.transaction() as session:
            count = session.query(Document).filter(
                Document.repo_doc_version_id == repo_doc_version_id
            ).delete()
            return count
    
    def delete_documents_by_parent(self, parent_id: int) -> int:
        """删除指定父文档的所有子文档"""
        with db_manager.transaction() as session:
            count = session.query(Document).filter(
                Document.parent_id == parent_id
            ).delete()
            return count
    
    def get_document_statistics(self) -> Dict[str, Any]:
        """获取文档统计信息"""
        with db_manager.session() as session:
            total_count = session.query(Document).count()
            
            # 按层级统计
            level_stats = {}
            level_results = session.query(
                Document.level,
                session.func.count(Document.id)
            ).group_by(Document.level).all()
            
            for level, count in level_results:
                level_stats[level] = count
            
            # 根文档统计
            root_count = session.query(Document).filter(
                (Document.parent_id == 0) | (Document.parent_id.is_(None))
            ).count()
            
            # 摘要统计
            with_summary_count = session.query(Document).filter(
                Document.summary.isnot(None),
                Document.summary != ''
            ).count()
            
            # 文件路径统计
            with_file_path_count = session.query(Document).filter(
                Document.file_path.isnot(None),
                Document.file_path != ''
            ).count()
            
            # 存储路径统计
            with_storage_path_count = session.query(Document).filter(
                Document.storage_path.isnot(None),
                Document.storage_path != ''
            ).count()
            
            return {
                'total_documents': total_count,
                'level_distribution': level_stats,
                'root_documents': root_count,
                'with_summary': with_summary_count,
                'with_file_path': with_file_path_count,
                'with_storage_path': with_storage_path_count,
                'summary_percentage': round(with_summary_count / total_count * 100, 2) if total_count > 0 else 0,
                'file_path_percentage': round(with_file_path_count / total_count * 100, 2) if total_count > 0 else 0
            }
    
    def get_documents_with_relations(self, document_ids: List[int] = None) -> List[Document]:
        """获取文档及其关联数据"""
        with db_manager.session() as session:
            query = session.query(Document)
            if document_ids:
                query = query.filter(Document.id.in_(document_ids))
            
            # 预加载关联数据
            documents = query.options(
                session.joinedload(Document.repo_document_version),
                session.joinedload(Document.comments),
                session.joinedload(Document.histories)
            ).all()
            
            for document in documents:
                session.expunge(document)
            return documents
    
    def get_document_tree(self, repo_doc_version_id: int) -> List[Dict[str, Any]]:
        """获取文档树结构"""
        def build_tree(parent_id: int = 0) -> List[Dict[str, Any]]:
            children = self.get_documents_by_parent(parent_id)
            result = []
            for child in children:
                child_dict = child.to_dict()
                child_dict['children'] = build_tree(child.id)
                result.append(child_dict)
            return result
        
        # 获取根文档并构建树
        root_documents = self.get_root_documents(repo_doc_version_id)
        tree = []
        for root in root_documents:
            root_dict = root.to_dict()
            root_dict['children'] = build_tree(root.id)
            tree.append(root_dict)
        
        return tree
    
    def get_document_path(self, document_id: int) -> List[Document]:
        """获取文档路径（从根到当前文档）"""
        path = []
        current_doc = self.get_document_by_id(document_id)
        
        while current_doc:
            path.insert(0, current_doc)
            if current_doc.is_root_document:
                break
            current_doc = self.get_document_by_id(current_doc.parent_id)
        
        return path
    
    def batch_update_level(self, document_ids: List[int], level: int, user: str = None) -> int:
        """批量更新文档层级"""
        with db_manager.transaction() as session:
            update_data = {'level': level, 'updated_at': datetime.utcnow()}
            if user:
                update_data['update_user'] = user
            
            count = session.query(Document).filter(
                Document.id.in_(document_ids)
            ).update(update_data, synchronize_session=False)
            return count
    
    def batch_update_sort_order(self, document_updates: List[Dict[str, Any]], user: str = None) -> int:
        """批量更新文档排序"""
        count = 0
        with db_manager.transaction() as session:
            for update_info in document_updates:
                document_id = update_info.get('document_id')
                sort_order = update_info.get('sort_order')
                if document_id and sort_order is not None:
                    update_data = {'sort_order': sort_order, 'updated_at': datetime.utcnow()}
                    if user:
                        update_data['update_user'] = user
                    
                    updated = session.query(Document).filter(
                        Document.id == document_id
                    ).update(update_data, synchronize_session=False)
                    count += updated
            return count
    
    def get_document_summary(self, document_id: int) -> Optional[Dict[str, Any]]:
        """获取文档摘要信息"""
        document = self.get_document_by_id(document_id)
        if not document:
            return None
        
        # 获取子文档数量
        children_count = len(self.get_documents_by_parent(document_id))
        
        # 获取评论和历史数量
        with db_manager.session() as session:
            comment_count = session.query(session.func.count()).select_from(
                session.query().filter().subquery()
            ).scalar() if hasattr(document, 'comments') else 0
            
            history_count = session.query(session.func.count()).select_from(
                session.query().filter().subquery()
            ).scalar() if hasattr(document, 'histories') else 0
        
        return {
            'document': document.to_dict(),
            'children_count': children_count,
            'comment_count': document.comment_count,
            'history_count': document.history_count,
            'has_summary': document.has_summary,
            'has_file_path': document.has_file_path,
            'has_storage_path': document.has_storage_path,
            'has_related_files': document.has_related_files,
            'is_root_document': document.is_root_document
        }
    
    def find_duplicate_titles(self, repo_doc_version_id: int = None) -> List[Dict[str, Any]]:
        """查找重复的文档标题"""
        with db_manager.session() as session:
            query = session.query(
                Document.doc_title,
                session.func.count(Document.id).label('count')
            ).group_by(Document.doc_title).having(
                session.func.count(Document.id) > 1
            )
            
            if repo_doc_version_id:
                query = query.filter(Document.repo_doc_version_id == repo_doc_version_id)
            
            duplicates = query.all()
            
            result = []
            for title, count in duplicates:
                # 获取具体的重复文档
                docs_query = session.query(Document).filter(
                    Document.doc_title == title
                )
                if repo_doc_version_id:
                    docs_query = docs_query.filter(Document.repo_doc_version_id == repo_doc_version_id)
                
                documents = docs_query.all()
                
                result.append({
                    'doc_title': title,
                    'duplicate_count': count,
                    'documents': [{'id': doc.id, 'repo_doc_version_id': doc.repo_doc_version_id} for doc in documents]
                })
            
            return result
    
    def move_document(self, document_id: int, new_parent_id: int, user: str = None) -> Optional[Document]:
        """移动文档到新的父文档下"""
        # 检查是否会形成循环引用
        if self._would_create_cycle(document_id, new_parent_id):
            return None
        
        update_data = {'parent_id': new_parent_id}
        if user:
            update_data['update_user'] = user
        return self.update_document(document_id, **update_data)
    
    def _would_create_cycle(self, document_id: int, new_parent_id: int) -> bool:
        """检查移动文档是否会创建循环引用"""
        if new_parent_id == 0 or new_parent_id is None:
            return False
        
        current_id = new_parent_id
        while current_id and current_id != 0:
            if current_id == document_id:
                return True
            parent_doc = self.get_document_by_id(current_id)
            if not parent_doc:
                break
            current_id = parent_doc.parent_id
        
        return False


# 全局文档信息服务实例
document_service = DocumentService()