"""
文档历史服务

提供文档变更历史的业务逻辑操作
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func

from ..models.document_history import DocumentHistory
from ..models.document import Document
from ..database.db_manager import db_manager


class DocumentHistoryService:
    """文档历史服务类"""
    
    def __init__(self):
        """初始化服务"""
        pass
    
    def create_history(self, document_id: int, source_storage_path: str, 
                      change_type: int = 1, diff_content: str = '', 
                      create_user: str = '') -> DocumentHistory:
        """
        创建文档历史记录
        
        Args:
            document_id: 文档ID
            source_storage_path: 原存储路径
            change_type: 变更类型
            diff_content: 差异内容
            create_user: 创建用户
            
        Returns:
            DocumentHistory: 创建的历史记录
        """
        with db_manager.transaction() as session:
            history = DocumentHistory.create_history(
                document_id=document_id,
                source_storage_path=source_storage_path,
                change_type=change_type,
                diff_content=diff_content,
                create_user=create_user
            )
            session.add(history)
            session.flush()
            session.expunge(history)
            return history
    
    def get_history_by_id(self, history_id: int) -> Optional[DocumentHistory]:
        """
        根据ID获取历史记录
        
        Args:
            history_id: 历史记录ID
            
        Returns:
            Optional[DocumentHistory]: 历史记录对象，不存在时返回None
        """
        with db_manager.session() as session:
            history = session.query(DocumentHistory).filter(
                DocumentHistory.id == history_id
            ).first()
            if history:
                session.expunge(history)
            return history
    
    def get_histories_by_document_id(self, document_id: int, 
                                   limit: int = None, 
                                   offset: int = None) -> List[DocumentHistory]:
        """
        根据文档ID获取历史记录列表
        
        Args:
            document_id: 文档ID
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            List[DocumentHistory]: 历史记录列表
        """
        with db_manager.session() as session:
            query = session.query(DocumentHistory).filter(
                DocumentHistory.document_id == document_id
            ).order_by(desc(DocumentHistory.create_time))
            
            if offset is not None:
                query = query.offset(offset)
            if limit is not None:
                query = query.limit(limit)
                
            histories = query.all()
            for history in histories:
                session.expunge(history)
            return histories
    
    def get_histories_by_change_type(self, change_type: int, 
                                   limit: int = None, 
                                   offset: int = None) -> List[DocumentHistory]:
        """
        根据变更类型获取历史记录列表
        
        Args:
            change_type: 变更类型
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            List[DocumentHistory]: 历史记录列表
        """
        with db_manager.session() as session:
            query = session.query(DocumentHistory).filter(
                DocumentHistory.change_type == change_type
            ).order_by(desc(DocumentHistory.create_time))
            
            if offset is not None:
                query = query.offset(offset)
            if limit is not None:
                query = query.limit(limit)
                
            histories = query.all()
            for history in histories:
                session.expunge(history)
            return histories
    
    def update_history(self, history_id: int, **kwargs) -> Optional[DocumentHistory]:
        """
        更新历史记录
        
        Args:
            history_id: 历史记录ID
            **kwargs: 更新字段
            
        Returns:
            Optional[DocumentHistory]: 更新后的历史记录
        """
        with db_manager.transaction() as session:
            history = session.query(DocumentHistory).filter(
                DocumentHistory.id == history_id
            ).first()
            
            if not history:
                return None
            
            # 更新字段
            for key, value in kwargs.items():
                if hasattr(history, key):
                    setattr(history, key, value)
            
            session.flush()
            session.expunge(history)
            return history
    
    def update_diff_content(self, history_id: int, diff_content: str, 
                          user: str = None) -> Optional[DocumentHistory]:
        """
        更新差异内容
        
        Args:
            history_id: 历史记录ID
            diff_content: 差异内容
            user: 更新用户
            
        Returns:
            Optional[DocumentHistory]: 更新后的历史记录
        """
        with db_manager.transaction() as session:
            history = session.query(DocumentHistory).filter(
                DocumentHistory.id == history_id
            ).first()
            
            if not history:
                return None
            
            history.set_diff_content(diff_content, user)
            session.flush()
            session.expunge(history)
            return history
    
    def delete_history(self, history_id: int) -> bool:
        """
        删除历史记录
        
        Args:
            history_id: 历史记录ID
            
        Returns:
            bool: 删除是否成功
        """
        with db_manager.transaction() as session:
            history = session.query(DocumentHistory).filter(
                DocumentHistory.id == history_id
            ).first()
            
            if not history:
                return False
            
            session.delete(history)
            return True
    
    def delete_histories_by_document_id(self, document_id: int) -> int:
        """
        删除指定文档的所有历史记录
        
        Args:
            document_id: 文档ID
            
        Returns:
            int: 删除的记录数量
        """
        with db_manager.transaction() as session:
            count = session.query(DocumentHistory).filter(
                DocumentHistory.document_id == document_id
            ).count()
            
            session.query(DocumentHistory).filter(
                DocumentHistory.document_id == document_id
            ).delete()
            
            return count
    
    def get_all_histories(self, limit: int = None, offset: int = None) -> List[DocumentHistory]:
        """
        获取所有历史记录
        
        Args:
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            List[DocumentHistory]: 历史记录列表
        """
        with db_manager.session() as session:
            query = session.query(DocumentHistory).order_by(desc(DocumentHistory.create_time))
            
            if offset is not None:
                query = query.offset(offset)
            if limit is not None:
                query = query.limit(limit)
                
            histories = query.all()
            for history in histories:
                session.expunge(history)
            return histories
    
    def count_histories(self) -> int:
        """
        获取历史记录总数
        
        Returns:
            int: 历史记录总数
        """
        with db_manager.session() as session:
            return session.query(DocumentHistory).count()
    
    def count_histories_by_document_id(self, document_id: int) -> int:
        """
        获取指定文档的历史记录数量
        
        Args:
            document_id: 文档ID
            
        Returns:
            int: 历史记录数量
        """
        with db_manager.session() as session:
            return session.query(DocumentHistory).filter(
                DocumentHistory.document_id == document_id
            ).count()
    
    def count_histories_by_change_type(self, change_type: int) -> int:
        """
        获取指定变更类型的历史记录数量
        
        Args:
            change_type: 变更类型
            
        Returns:
            int: 历史记录数量
        """
        with db_manager.session() as session:
            return session.query(DocumentHistory).filter(
                DocumentHistory.change_type == change_type
            ).count()
    
    def get_histories_with_diff_content(self, limit: int = None, 
                                      offset: int = None) -> List[DocumentHistory]:
        """
        获取包含差异内容的历史记录
        
        Args:
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            List[DocumentHistory]: 历史记录列表
        """
        with db_manager.session() as session:
            query = session.query(DocumentHistory).filter(
                and_(
                    DocumentHistory.diff_content.isnot(None),
                    DocumentHistory.diff_content != ''
                )
            ).order_by(desc(DocumentHistory.create_time))
            
            if offset is not None:
                query = query.offset(offset)
            if limit is not None:
                query = query.limit(limit)
                
            histories = query.all()
            for history in histories:
                session.expunge(history)
            return histories
    
    def get_recent_histories(self, days: int = 7, limit: int = None) -> List[DocumentHistory]:
        """
        获取最近几天的历史记录
        
        Args:
            days: 天数
            limit: 限制数量
            
        Returns:
            List[DocumentHistory]: 历史记录列表
        """
        from datetime import datetime, timedelta
        
        with db_manager.session() as session:
            cutoff_date = datetime.now() - timedelta(days=days)
            query = session.query(DocumentHistory).filter(
                DocumentHistory.create_time >= cutoff_date
            ).order_by(desc(DocumentHistory.create_time))
            
            if limit is not None:
                query = query.limit(limit)
                
            histories = query.all()
            for history in histories:
                session.expunge(history)
            return histories
    
    def get_histories_by_storage_path(self, storage_path: str, 
                                    exact_match: bool = True) -> List[DocumentHistory]:
        """
        根据存储路径获取历史记录
        
        Args:
            storage_path: 存储路径
            exact_match: 是否精确匹配
            
        Returns:
            List[DocumentHistory]: 历史记录列表
        """
        with db_manager.session() as session:
            if exact_match:
                query = session.query(DocumentHistory).filter(
                    DocumentHistory.source_storage_path == storage_path
                )
            else:
                query = session.query(DocumentHistory).filter(
                    DocumentHistory.source_storage_path.like(f'%{storage_path}%')
                )
            
            query = query.order_by(desc(DocumentHistory.create_time))
            histories = query.all()
            for history in histories:
                session.expunge(history)
            return histories
    
    def get_change_type_statistics(self) -> Dict[int, int]:
        """
        获取变更类型统计信息
        
        Returns:
            Dict[int, int]: 变更类型统计 {change_type: count}
        """
        with db_manager.session() as session:
            results = session.query(
                DocumentHistory.change_type,
                func.count(DocumentHistory.id).label('count')
            ).group_by(DocumentHistory.change_type).all()
            
            return {result.change_type: result.count for result in results}
    
    def get_document_history_statistics(self) -> Dict[str, Any]:
        """
        获取文档历史统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        with db_manager.session() as session:
            total_histories = session.query(DocumentHistory).count()
            
            histories_with_diff = session.query(DocumentHistory).filter(
                and_(
                    DocumentHistory.diff_content.isnot(None),
                    DocumentHistory.diff_content != ''
                )
            ).count()
            
            unique_documents = session.query(DocumentHistory.document_id).distinct().count()
            
            change_type_stats = self.get_change_type_statistics()
            
            return {
                'total_histories': total_histories,
                'histories_with_diff': histories_with_diff,
                'histories_without_diff': total_histories - histories_with_diff,
                'unique_documents': unique_documents,
                'change_type_statistics': change_type_stats
            }
    
    def batch_create_histories(self, histories_data: List[Dict[str, Any]]) -> List[DocumentHistory]:
        """
        批量创建历史记录
        
        Args:
            histories_data: 历史记录数据列表
            
        Returns:
            List[DocumentHistory]: 创建的历史记录列表
        """
        with db_manager.transaction() as session:
            histories = []
            for data in histories_data:
                history = DocumentHistory.create_history(**data)
                session.add(history)
                histories.append(history)
            
            session.flush()
            for history in histories:
                session.expunge(history)
            return histories
    
    def search_histories(self, keyword: str = None, document_id: int = None,
                        change_type: int = None, limit: int = None, 
                        offset: int = None) -> List[DocumentHistory]:
        """
        搜索历史记录
        
        Args:
            keyword: 关键词（搜索差异内容和存储路径）
            document_id: 文档ID
            change_type: 变更类型
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            List[DocumentHistory]: 历史记录列表
        """
        with db_manager.session() as session:
            query = session.query(DocumentHistory)
            
            # 构建查询条件
            conditions = []
            
            if document_id is not None:
                conditions.append(DocumentHistory.document_id == document_id)
            
            if change_type is not None:
                conditions.append(DocumentHistory.change_type == change_type)
            
            if keyword:
                keyword_condition = or_(
                    DocumentHistory.diff_content.like(f'%{keyword}%'),
                    DocumentHistory.source_storage_path.like(f'%{keyword}%')
                )
                conditions.append(keyword_condition)
            
            if conditions:
                query = query.filter(and_(*conditions))
            
            query = query.order_by(desc(DocumentHistory.create_time))
            
            if offset is not None:
                query = query.offset(offset)
            if limit is not None:
                query = query.limit(limit)
                
            histories = query.all()
            for history in histories:
                session.expunge(history)
            return histories


# 创建全局服务实例
document_history_service = DocumentHistoryService()