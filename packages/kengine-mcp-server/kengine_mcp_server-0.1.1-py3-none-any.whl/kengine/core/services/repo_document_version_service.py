"""
仓库文档版本服务

提供仓库文档版本相关的业务逻辑处理
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ...db.database_manager import db_manager
from ..models.repo_document_version import RepoDocumentVersion


class RepoDocumentVersionService:
    """仓库文档版本服务类"""
    
    def __init__(self):
        """初始化仓库文档版本服务"""
        pass
    
    def create_version(self, repo_id: int, version: str, git_commit: str = "",
                      analysis_config: Dict[str, Any] = None, type: int = 1,
                      status: int = 1, **kwargs) -> RepoDocumentVersion:
        """创建仓库文档版本"""
        with db_manager.transaction() as session:
            repo_version = RepoDocumentVersion(
                repo_id=repo_id,
                version=version,
                git_commit=git_commit,
                analysis_config=analysis_config,
                type=type,
                status=status,
                **kwargs
            )
            session.add(repo_version)
            session.flush()  # 获取 ID
            session.expunge(repo_version)  # 从会话中分离
            return repo_version
    
    def get_version_by_id(self, version_id: int) -> Optional[RepoDocumentVersion]:
        """根据ID获取版本"""
        with db_manager.session() as session:
            version = session.query(RepoDocumentVersion).filter(
                RepoDocumentVersion.id == version_id
            ).first()
            if version:
                session.expunge(version)
            return version
    
    def get_versions_by_repo(self, repo_id: int, status: int = None) -> List[RepoDocumentVersion]:
        """根据仓库ID获取所有版本"""
        with db_manager.session() as session:
            query = session.query(RepoDocumentVersion).filter(
                RepoDocumentVersion.repo_id == repo_id
            )
            if status is not None:
                query = query.filter(RepoDocumentVersion.status == status)
            versions = query.order_by(RepoDocumentVersion.created_at.desc()).all()
            for version in versions:
                session.expunge(version)
            return versions
    
    def get_version_by_repo_and_version(self, repo_id: int, version: str) -> Optional[RepoDocumentVersion]:
        """根据仓库ID和版本号获取版本"""
        with db_manager.session() as session:
            version_obj = session.query(RepoDocumentVersion).filter(
                RepoDocumentVersion.repo_id == repo_id,
                RepoDocumentVersion.version == version
            ).first()
            if version_obj:
                session.expunge(version_obj)
            return version_obj
    
    def get_version_by_git_commit(self, repo_id: int, git_commit: str) -> Optional[RepoDocumentVersion]:
        """根据Git提交号获取版本"""
        with db_manager.session() as session:
            version = session.query(RepoDocumentVersion).filter(
                RepoDocumentVersion.repo_id == repo_id,
                RepoDocumentVersion.git_commit == git_commit
            ).first()
            if version:
                session.expunge(version)
            return version
    
    def get_latest_version_by_repo(self, repo_id: int, type: int = None) -> Optional[RepoDocumentVersion]:
        """获取仓库的最新版本"""
        with db_manager.session() as session:
            query = session.query(RepoDocumentVersion).filter(
                RepoDocumentVersion.repo_id == repo_id,
                RepoDocumentVersion.status == 1  # 只获取有效状态的版本
            )
            if type is not None:
                query = query.filter(RepoDocumentVersion.type == type)
            version = query.order_by(RepoDocumentVersion.created_at.desc()).first()
            if version:
                session.expunge(version)
            return version
    
    def get_versions_by_type(self, type: int, repo_id: int = None) -> List[RepoDocumentVersion]:
        """根据类型获取版本列表"""
        with db_manager.session() as session:
            query = session.query(RepoDocumentVersion).filter(
                RepoDocumentVersion.type == type
            )
            if repo_id:
                query = query.filter(RepoDocumentVersion.repo_id == repo_id)
            versions = query.order_by(RepoDocumentVersion.created_at.desc()).all()
            for version in versions:
                session.expunge(version)
            return versions
    
    def search_versions(self, keyword: str, repo_id: int = None) -> List[RepoDocumentVersion]:
        """搜索版本（根据版本号、Git提交号）"""
        with db_manager.session() as session:
            query = session.query(RepoDocumentVersion).filter(
                (RepoDocumentVersion.version.contains(keyword)) |
                (RepoDocumentVersion.git_commit.contains(keyword))
            )
            if repo_id:
                query = query.filter(RepoDocumentVersion.repo_id == repo_id)
            versions = query.order_by(RepoDocumentVersion.created_at.desc()).all()
            for version in versions:
                session.expunge(version)
            return versions
    
    def get_all_versions(self, limit: Optional[int] = None,
                        order_by: str = 'created_at', desc_order: bool = True) -> List[RepoDocumentVersion]:
        """获取所有版本"""
        with db_manager.session() as session:
            query = session.query(RepoDocumentVersion)
            if hasattr(RepoDocumentVersion, order_by):
                order_field = getattr(RepoDocumentVersion, order_by)
                if desc_order:
                    query = query.order_by(order_field.desc())
                else:
                    query = query.order_by(order_field.asc())
            if limit:
                query = query.limit(limit)
            versions = query.all()
            for version in versions:
                session.expunge(version)
            return versions
    
    def get_versions_with_git_commit(self, repo_id: int = None) -> List[RepoDocumentVersion]:
        """获取有Git提交号的版本"""
        with db_manager.session() as session:
            query = session.query(RepoDocumentVersion).filter(
                RepoDocumentVersion.git_commit.isnot(None),
                RepoDocumentVersion.git_commit != ''
            )
            if repo_id:
                query = query.filter(RepoDocumentVersion.repo_id == repo_id)
            versions = query.order_by(RepoDocumentVersion.created_at.desc()).all()
            for version in versions:
                session.expunge(version)
            return versions
    
    def get_versions_without_git_commit(self, repo_id: int = None) -> List[RepoDocumentVersion]:
        """获取无Git提交号的版本"""
        with db_manager.session() as session:
            query = session.query(RepoDocumentVersion).filter(
                (RepoDocumentVersion.git_commit.is_(None)) |
                (RepoDocumentVersion.git_commit == '')
            )
            if repo_id:
                query = query.filter(RepoDocumentVersion.repo_id == repo_id)
            versions = query.order_by(RepoDocumentVersion.created_at.desc()).all()
            for version in versions:
                session.expunge(version)
            return versions
    
    def update_version(self, version_id: int, **kwargs) -> Optional[RepoDocumentVersion]:
        """更新版本信息"""
        with db_manager.transaction() as session:
            version = session.query(RepoDocumentVersion).filter(
                RepoDocumentVersion.id == version_id
            ).first()
            if version:
                for key, value in kwargs.items():
                    if hasattr(version, key):
                        setattr(version, key, value)
                version.updated_at = datetime.utcnow()
                session.flush()
                session.expunge(version)
                return version
            return None
    
    def update_git_commit(self, version_id: int, git_commit: str, user: str = None) -> Optional[RepoDocumentVersion]:
        """更新Git提交号"""
        update_data = {'git_commit': git_commit}
        if user:
            update_data['update_user'] = user
        return self.update_version(version_id, **update_data)
    
    def update_analysis_config(self, version_id: int, analysis_config: Dict[str, Any], user: str = None) -> Optional[RepoDocumentVersion]:
        """更新分析配置"""
        update_data = {'analysis_config': analysis_config}
        if user:
            update_data['update_user'] = user
        return self.update_version(version_id, **update_data)
    
    def update_status(self, version_id: int, status: int, user: str = None) -> Optional[RepoDocumentVersion]:
        """更新状态"""
        update_data = {'status': status}
        if user:
            update_data['update_user'] = user
        return self.update_version(version_id, **update_data)
    
    def set_analysis_config_value(self, version_id: int, key: str, value: Any, user: str = None) -> Optional[RepoDocumentVersion]:
        """设置分析配置中的值"""
        version = self.get_version_by_id(version_id)
        if not version:
            return None
        
        with db_manager.transaction() as session:
            version_obj = session.query(RepoDocumentVersion).filter(
                RepoDocumentVersion.id == version_id
            ).first()
            if version_obj:
                if version_obj.analysis_config is None:
                    version_obj.analysis_config = {}
                version_obj.analysis_config[key] = value
                version_obj.updated_at = datetime.utcnow()
                if user:
                    version_obj.update_user = user
                session.flush()
                session.expunge(version_obj)
                return version_obj
            return None
    
    def delete_version(self, version_id: int) -> bool:
        """删除版本"""
        with db_manager.transaction() as session:
            version = session.query(RepoDocumentVersion).filter(
                RepoDocumentVersion.id == version_id
            ).first()
            if version:
                session.delete(version)
                return True
            return False
    
    def delete_versions_by_repo(self, repo_id: int) -> int:
        """删除指定仓库的所有版本"""
        with db_manager.transaction() as session:
            count = session.query(RepoDocumentVersion).filter(
                RepoDocumentVersion.repo_id == repo_id
            ).delete()
            return count
    
    def get_version_statistics(self) -> Dict[str, Any]:
        """获取版本统计信息"""
        with db_manager.session() as session:
            total_count = session.query(RepoDocumentVersion).count()
            
            # 按类型统计
            type_stats = {}
            type_results = session.query(
                RepoDocumentVersion.type,
                session.func.count(RepoDocumentVersion.id)
            ).group_by(RepoDocumentVersion.type).all()
            
            for version_type, count in type_results:
                type_stats[version_type] = count
            
            # 按状态统计
            status_stats = {}
            status_results = session.query(
                RepoDocumentVersion.status,
                session.func.count(RepoDocumentVersion.id)
            ).group_by(RepoDocumentVersion.status).all()
            
            for status, count in status_results:
                status_stats[status] = count
            
            # Git提交统计
            with_git_count = session.query(RepoDocumentVersion).filter(
                RepoDocumentVersion.git_commit.isnot(None),
                RepoDocumentVersion.git_commit != ''
            ).count()
            
            without_git_count = total_count - with_git_count
            
            # 分析配置统计
            with_config_count = session.query(RepoDocumentVersion).filter(
                RepoDocumentVersion.analysis_config.isnot(None)
            ).count()
            
            return {
                'total_versions': total_count,
                'type_distribution': type_stats,
                'status_distribution': status_stats,
                'with_git_commit': with_git_count,
                'without_git_commit': without_git_count,
                'with_analysis_config': with_config_count,
                'git_commit_percentage': round(with_git_count / total_count * 100, 2) if total_count > 0 else 0
            }
    
    def get_versions_with_relations(self, version_ids: List[int] = None) -> List[RepoDocumentVersion]:
        """获取版本及其关联数据"""
        with db_manager.session() as session:
            query = session.query(RepoDocumentVersion)
            if version_ids:
                query = query.filter(RepoDocumentVersion.id.in_(version_ids))
            
            # 预加载关联数据
            versions = query.options(
                session.joinedload(RepoDocumentVersion.repository),
                session.joinedload(RepoDocumentVersion.documents)
            ).all()
            
            for version in versions:
                session.expunge(version)
            return versions
    
    def get_version_documents_count(self, version_id: int) -> int:
        """获取版本的文档数量"""
        with db_manager.session() as session:
            from ..models.document import Document
            count = session.query(Document).filter(
                Document.repo_doc_version_id == version_id
            ).count()
            return count
    
    def batch_update_status(self, version_ids: List[int], status: int, user: str = None) -> int:
        """批量更新版本状态"""
        with db_manager.transaction() as session:
            update_data = {'status': status, 'updated_at': datetime.utcnow()}
            if user:
                update_data['update_user'] = user
            
            count = session.query(RepoDocumentVersion).filter(
                RepoDocumentVersion.id.in_(version_ids)
            ).update(update_data, synchronize_session=False)
            return count
    
    def batch_update_type(self, version_ids: List[int], type: int, user: str = None) -> int:
        """批量更新版本类型"""
        with db_manager.transaction() as session:
            update_data = {'type': type, 'updated_at': datetime.utcnow()}
            if user:
                update_data['update_user'] = user
            
            count = session.query(RepoDocumentVersion).filter(
                RepoDocumentVersion.id.in_(version_ids)
            ).update(update_data, synchronize_session=False)
            return count
    
    def get_version_summary(self, version_id: int) -> Optional[Dict[str, Any]]:
        """获取版本摘要信息"""
        version = self.get_version_by_id(version_id)
        if not version:
            return None
        
        document_count = self.get_version_documents_count(version_id)
        
        return {
            'version': version.to_dict(),
            'version_info': version.get_version_info(),
            'document_count': document_count,
            'has_git_commit': version.has_git_commit,
            'has_analysis_config': version.has_analysis_config
        }
    
    def find_duplicate_versions(self, repo_id: int = None) -> List[Dict[str, Any]]:
        """查找重复的版本号"""
        with db_manager.session() as session:
            query = session.query(
                RepoDocumentVersion.repo_id,
                RepoDocumentVersion.version,
                session.func.count(RepoDocumentVersion.id).label('count')
            ).group_by(
                RepoDocumentVersion.repo_id,
                RepoDocumentVersion.version
            ).having(
                session.func.count(RepoDocumentVersion.id) > 1
            )
            
            if repo_id:
                query = query.filter(RepoDocumentVersion.repo_id == repo_id)
            
            duplicates = query.all()
            
            result = []
            for repo_id_val, version, count in duplicates:
                # 获取具体的重复版本
                versions = session.query(RepoDocumentVersion).filter(
                    RepoDocumentVersion.repo_id == repo_id_val,
                    RepoDocumentVersion.version == version
                ).all()
                
                result.append({
                    'repo_id': repo_id_val,
                    'version': version,
                    'duplicate_count': count,
                    'versions': [{'id': v.id, 'created_at': v.created_at} for v in versions]
                })
            
            return result
    
    def get_repo_version_history(self, repo_id: int, limit: int = 10) -> List[RepoDocumentVersion]:
        """获取仓库版本历史"""
        with db_manager.session() as session:
            versions = session.query(RepoDocumentVersion).filter(
                RepoDocumentVersion.repo_id == repo_id
            ).order_by(
                RepoDocumentVersion.created_at.desc()
            ).limit(limit).all()
            
            for version in versions:
                session.expunge(version)
            return versions
    
    def compare_versions(self, version_id1: int, version_id2: int) -> Dict[str, Any]:
        """比较两个版本"""
        version1 = self.get_version_by_id(version_id1)
        version2 = self.get_version_by_id(version_id2)
        
        if not version1 or not version2:
            return {}
        
        doc_count1 = self.get_version_documents_count(version_id1)
        doc_count2 = self.get_version_documents_count(version_id2)
        
        return {
            'version1': {
                'info': version1.get_version_info(),
                'document_count': doc_count1
            },
            'version2': {
                'info': version2.get_version_info(),
                'document_count': doc_count2
            },
            'differences': {
                'document_count_diff': doc_count2 - doc_count1,
                'git_commit_changed': version1.git_commit != version2.git_commit,
                'analysis_config_changed': version1.analysis_config != version2.analysis_config
            }
        }


# 全局仓库文档版本服务实例
repo_document_version_service = RepoDocumentVersionService()