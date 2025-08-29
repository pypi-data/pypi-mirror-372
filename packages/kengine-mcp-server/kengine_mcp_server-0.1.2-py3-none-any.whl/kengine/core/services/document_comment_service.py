"""
文档评论服务

提供文档评论相关的业务逻辑处理，包括：
1. 页面交互方法：获取全量评论（树形结构）、新增评论/回复、删除评论及其子评论
2. 核心业务流程：LLM判断、批量采纳、文档重新生成等
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc

from ...db.database_manager import db_manager
from ..models.document_comment import DocumentComment


class DocumentCommentService:
    """文档评论服务类"""
    
    def __init__(self):
        """初始化文档评论服务"""
        pass
    
    # ==================== 页面交互方法 ====================
    
    def get_all_comments_tree(self, document_id: int, include_deleted: bool = False) -> List[Dict[str, Any]]:
        """
        1. 页面获取全量的评论（包含子级评论以及子级评论的子级评论）
        返回树形结构的评论数据
        
        Args:
            document_id: 文档ID
            include_deleted: 是否包含已删除的评论
            
        Returns:
            List[Dict]: 树形结构的评论列表
        """
        with db_manager.session() as session:
            # 获取所有评论
            query = session.query(DocumentComment).filter(DocumentComment.document_id == document_id)
            if not include_deleted:
                query = query.filter(DocumentComment.is_delete == False)
            
            all_comments = query.order_by(asc(DocumentComment.create_time)).all()
            
            # 构建评论字典，便于查找
            comment_dict = {}
            for comment in all_comments:
                comment_data = comment.to_dict()
                comment_data['children'] = []  # 子评论列表
                comment_dict[comment.id] = comment_data
            
            # 构建树形结构
            root_comments = []
            for comment in all_comments:
                comment_data = comment_dict[comment.id]
                
                if comment.ref_id == 0:
                    # 一级评论（根评论）
                    root_comments.append(comment_data)
                else:
                    # 子评论，找到父评论并添加到其children中
                    if comment.ref_id in comment_dict:
                        parent_comment = comment_dict[comment.ref_id]
                        parent_comment['children'].append(comment_data)
            
            return root_comments
    
    def add_comment_or_reply(self, document_id: int, content: str, user_name: str, 
                           ref_id: int = 0, create_user: str = None, **kwargs) -> DocumentComment:
        """
        2. 针对全文(ref_id=0)或者某个评论，新增评论/回复
        
        Args:
            document_id: 文档ID
            content: 评论内容
            user_name: 用户名
            ref_id: 父级评论ID，0表示对全文的评论
            create_user: 创建用户
            **kwargs: 其他参数
            
        Returns:
            DocumentComment: 创建的评论对象
        """
        with db_manager.transaction() as session:
            # 如果是回复评论，验证父评论是否存在
            if ref_id > 0:
                parent_comment = session.query(DocumentComment).filter(
                    and_(
                        DocumentComment.id == ref_id,
                        DocumentComment.document_id == document_id,
                        DocumentComment.is_delete == False
                    )
                ).first()
                
                if not parent_comment:
                    raise ValueError(f"父评论不存在或已删除: ref_id={ref_id}")
            
            # 创建新评论
            comment = DocumentComment(
                document_id=document_id,
                ref_id=ref_id,
                user_name=user_name,
                content=content,
                create_user=create_user or user_name,
                **kwargs
            )
            
            session.add(comment)
            session.flush()  # 获取ID
            session.expunge(comment)  # 从会话中分离
            return comment
    
    def delete_comment_and_children(self, comment_id: int, user: str = None) -> bool:
        """
        3. 删除评论（删除评论及其子评论）
        递归删除评论及其所有子评论
        
        Args:
            comment_id: 要删除的评论ID
            user: 操作用户
            
        Returns:
            bool: 删除是否成功
        """
        with db_manager.transaction() as session:
            # 获取要删除的评论
            comment = session.query(DocumentComment).filter(
                and_(
                    DocumentComment.id == comment_id,
                    DocumentComment.is_delete == False
                )
            ).first()
            
            if not comment:
                return False
            
            # 递归获取所有需要删除的评论ID（包括子评论的子评论）
            comment_ids_to_delete = self._get_all_child_comment_ids(session, comment_id)
            comment_ids_to_delete.append(comment_id)  # 包含自己
            
            # 批量软删除
            deleted_count = session.query(DocumentComment).filter(
                DocumentComment.id.in_(comment_ids_to_delete)
            ).update({
                'is_delete': True,
                'update_user': user or 'system',
                'update_time': datetime.utcnow()
            }, synchronize_session=False)
            
            return deleted_count > 0
    
    def _get_all_child_comment_ids(self, session: Session, parent_id: int) -> List[int]:
        """
        递归获取所有子评论ID
        
        Args:
            session: 数据库会话
            parent_id: 父评论ID
            
        Returns:
            List[int]: 所有子评论ID列表
        """
        child_ids = []
        
        # 获取直接子评论
        direct_children = session.query(DocumentComment.id).filter(
            and_(
                DocumentComment.ref_id == parent_id,
                DocumentComment.is_delete == False
            )
        ).all()
        
        for child_id_tuple in direct_children:
            child_id = child_id_tuple[0]
            child_ids.append(child_id)
            # 递归获取子评论的子评论
            child_ids.extend(self._get_all_child_comment_ids(session, child_id))
        
        return child_ids
    
    # ==================== 核心业务流程 ====================
    
    def get_root_comments_tree(self, document_id: int) -> List[Dict[str, Any]]:
        """
        1. 获取当前文档下所有一级评论，一级评论为树形结构，包含所有子级评论
        
        Args:
            document_id: 文档ID
            
        Returns:
            List[Dict]: 一级评论树形结构
        """
        return self.get_all_comments_tree(document_id, include_deleted=False)
    
    def check_can_regenerate_document(self, document_id: int) -> Tuple[bool, str]:
        """
        2. 调用LLM接口，返回是否可重新生成文档
        
        Args:
            document_id: 文档ID
            
        Returns:
            Tuple[bool, str]: (是否可以重新生成, 原因说明)
        """
        # TODO: 这里需要集成实际的LLM接口
        # 目前返回模拟结果，实际实现时需要：
        # 1. 获取文档内容和评论内容
        # 2. 调用LLM接口进行分析
        # 3. 根据LLM返回结果判断是否可以重新生成文档
        
        with db_manager.session() as session:
            # 获取文档的评论统计
            comment_count = session.query(DocumentComment).filter(
                and_(
                    DocumentComment.document_id == document_id,
                    DocumentComment.is_delete == False
                )
            ).count()
            
            if comment_count == 0:
                return False, "没有评论，无需重新生成文档"
            
            # 获取未处理的评论数量
            unprocessed_count = session.query(DocumentComment).filter(
                and_(
                    DocumentComment.document_id == document_id,
                    DocumentComment.is_delete == False,
                    DocumentComment.is_accepted.is_(None)  # 未处理的评论
                )
            ).count()
            
            if unprocessed_count > 0:
                return True, f"有 {unprocessed_count} 条评论需要处理，建议重新生成文档"
            else:
                return False, "所有评论已处理，暂无需重新生成文档"
    
    def batch_accept_root_comments(self, document_id: int, user: str = None) -> List[DocumentComment]:
        """
        3. 如果可重新生成，则将所有一级评论的 is_accepted 设置为1，并更新文档的regenerate_flag为0
        
        Args:
            document_id: 文档ID
            user: 操作用户
            
        Returns:
            List[DocumentComment]: 被采纳的一级评论列表
        """
        with db_manager.transaction() as session:
            # 获取所有一级评论（ref_id=0）
            root_comments = session.query(DocumentComment).filter(
                and_(
                    DocumentComment.document_id == document_id,
                    DocumentComment.ref_id == 0,
                    DocumentComment.is_delete == False
                )
            ).all()
            
            accepted_comments = []
            for comment in root_comments:
                # 设置为已采纳
                comment.is_accepted = True
                comment.regenerate_flag = False  # 重置重新生成标识
                comment.update_user = user or 'system'
                comment.update_time = datetime.utcnow()
                accepted_comments.append(comment)
            
            session.flush()
            
            # 从会话中分离对象
            for comment in accepted_comments:
                session.expunge(comment)
            
            return accepted_comments
    
    def get_regenerate_data_source(self, document_id: int = None) -> List[DocumentComment]:
        """
        4. 获取所有 is_accepted==1 && regenerate_flag==0 的数据，作为当前文档的数据源
        
        Args:
            document_id: 文档ID，如果为None则获取所有文档的数据
            
        Returns:
            List[DocumentComment]: 用于重新生成的评论数据
        """
        with db_manager.session() as session:
            query = session.query(DocumentComment).filter(
                and_(
                    DocumentComment.is_accepted == True,
                    DocumentComment.regenerate_flag == False,
                    DocumentComment.is_delete == False
                )
            )
            
            if document_id:
                query = query.filter(DocumentComment.document_id == document_id)
            
            comments = query.order_by(desc(DocumentComment.create_time)).all()
            
            # 从会话中分离对象
            for comment in comments:
                session.expunge(comment)
            
            return comments
    
    def regenerate_document(self, document_id: int, user: str = None) -> Dict[str, Any]:
        """
        5. 调用接口重新生成文档
        
        Args:
            document_id: 文档ID
            user: 操作用户
            
        Returns:
            Dict[str, Any]: 重新生成结果
        """
        # 获取数据源
        data_source = self.get_regenerate_data_source(document_id)
        
        if not data_source:
            return {
                'success': False,
                'message': '没有可用于重新生成的评论数据',
                'data': None
            }
        
        # TODO: 这里需要集成实际的文档生成接口
        # 目前返回模拟结果，实际实现时需要：
        # 1. 调用文档生成服务
        # 2. 传入评论数据作为参数
        # 3. 处理生成结果
        
        try:
            # 模拟文档生成过程
            regenerate_result = {
                'document_id': document_id,
                'comment_count': len(data_source),
                'generated_at': datetime.utcnow().isoformat(),
                'status': 'success'
            }
            
            # 标记所有相关评论为已处理
            self._mark_comments_as_processed(data_source, user)
            
            return {
                'success': True,
                'message': f'文档重新生成成功，处理了 {len(data_source)} 条评论',
                'data': regenerate_result
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'文档重新生成失败: {str(e)}',
                'data': None
            }
    
    def _mark_comments_as_processed(self, comments: List[DocumentComment], user: str = None):
        """
        标记评论为已处理状态
        
        Args:
            comments: 评论列表
            user: 操作用户
        """
        if not comments:
            return
        
        comment_ids = [comment.id for comment in comments]
        
        with db_manager.transaction() as session:
            session.query(DocumentComment).filter(
                DocumentComment.id.in_(comment_ids)
            ).update({
                'regenerate_flag': True,
                'update_user': user or 'system',
                'update_time': datetime.utcnow()
            }, synchronize_session=False)
    
    # ==================== 完整业务流程 ====================
    
    def process_document_regeneration(self, document_id: int, user: str = None) -> Dict[str, Any]:
        """
        完整的文档重新生成业务流程
        
        Args:
            document_id: 文档ID
            user: 操作用户
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        try:
            # 1. 检查是否可以重新生成
            can_regenerate, reason = self.check_can_regenerate_document(document_id)
            
            if not can_regenerate:
                return {
                    'success': False,
                    'message': reason,
                    'step': 'check_regenerate',
                    'data': None
                }
            
            # 2. 批量采纳一级评论
            accepted_comments = self.batch_accept_root_comments(document_id, user)
            
            # 3. 重新生成文档
            regenerate_result = self.regenerate_document(document_id, user)
            
            if regenerate_result['success']:
                return {
                    'success': True,
                    'message': f'文档重新生成流程完成，采纳了 {len(accepted_comments)} 条一级评论',
                    'step': 'completed',
                    'data': {
                        'accepted_comments_count': len(accepted_comments),
                        'regenerate_result': regenerate_result['data']
                    }
                }
            else:
                return regenerate_result
                
        except Exception as e:
            return {
                'success': False,
                'message': f'文档重新生成流程失败: {str(e)}',
                'step': 'error',
                'data': None
            }
    
    # ==================== 辅助查询方法 ====================
    
    def get_comment_by_id(self, comment_id: int) -> Optional[DocumentComment]:
        """根据ID获取评论"""
        with db_manager.session() as session:
            comment = session.query(DocumentComment).filter(
                and_(
                    DocumentComment.id == comment_id,
                    DocumentComment.is_delete == False
                )
            ).first()
            if comment:
                session.expunge(comment)
            return comment
    
    def get_document_comment_statistics(self, document_id: int) -> Dict[str, Any]:
        """获取文档评论统计信息"""
        with db_manager.session() as session:
            base_query = session.query(DocumentComment).filter(
                and_(
                    DocumentComment.document_id == document_id,
                    DocumentComment.is_delete == False
                )
            )
            
            # 总评论数
            total_comments = base_query.count()
            
            # 一级评论数
            root_comments = base_query.filter(DocumentComment.ref_id == 0).count()
            
            # 回复评论数
            reply_comments = base_query.filter(DocumentComment.ref_id > 0).count()
            
            # 已采纳评论数
            accepted_comments = base_query.filter(DocumentComment.is_accepted == True).count()
            
            # 待处理评论数
            pending_comments = base_query.filter(DocumentComment.is_accepted.is_(None)).count()
            
            # 需要重新生成的评论数
            regenerate_needed = base_query.filter(
                and_(
                    DocumentComment.is_accepted == True,
                    DocumentComment.regenerate_flag == False
                )
            ).count()
            
            return {
                'document_id': document_id,
                'total_comments': total_comments,
                'root_comments': root_comments,
                'reply_comments': reply_comments,
                'accepted_comments': accepted_comments,
                'pending_comments': pending_comments,
                'regenerate_needed': regenerate_needed
            }
    
    def is_comment_exists(self, comment_id: int) -> bool:
        """检查评论是否存在"""
        with db_manager.session() as session:
            return session.query(DocumentComment).filter(
                and_(
                    DocumentComment.id == comment_id,
                    DocumentComment.is_delete == False
                )
            ).first() is not None
