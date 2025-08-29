"""
仓库信息服务

提供仓库信息相关的业务逻辑处理
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ...db.database_manager import db_manager
from ..models.repository import Repository


class RepositoryService:
    """仓库信息服务类"""
    
    def __init__(self):
        """初始化仓库信息服务"""
        pass
    
    def create_repository(self, domain_id: int, repo_code: str, repo_name: str,
                         repo_related_group: str, repo_type: str, main_language: str,
                         repo_url: str, repo_default_branch: str = "master",
                         description: str = "", **kwargs) -> Repository:
        """创建仓库"""
        with db_manager.transaction() as session:
            repository = Repository(
                domain_id=domain_id,
                repo_code=repo_code,
                repo_name=repo_name,
                repo_related_group=repo_related_group,
                description=description,
                repo_type=repo_type,
                main_language=main_language,
                repo_url=repo_url,
                repo_default_branch=repo_default_branch,
                **kwargs
            )
            session.add(repository)
            session.flush()  # 获取 ID
            session.expunge(repository)  # 从会话中分离
            return repository
    
    def get_repository_by_id(self, repo_id: int) -> Optional[Repository]:
        """根据ID获取仓库"""
        with db_manager.session() as session:
            repository = session.query(Repository).filter(Repository.id == repo_id).first()
            if repository:
                session.expunge(repository)
            return repository
    
    def get_repository_by_code(self, repo_code: str) -> Optional[Repository]:
        """根据仓库编码获取仓库"""
        with db_manager.session() as session:
            repository = session.query(Repository).filter(Repository.repo_code == repo_code).first()
            if repository:
                session.expunge(repository)
            return repository
    
    def get_repositories_by_domain(self, domain_id: int, enabled_only: bool = True) -> List[Repository]:
        """根据业务领域ID获取仓库列表"""
        with db_manager.session() as session:
            query = session.query(Repository).filter(Repository.domain_id == domain_id)
            if enabled_only:
                query = query.filter(Repository.disable_flag == False)
            repositories = query.all()
            for repository in repositories:
                session.expunge(repository)
            return repositories
    
    def get_repositories_by_group(self, repo_related_group: str, enabled_only: bool = True) -> List[Repository]:
        """根据仓库关联群组获取仓库列表"""
        with db_manager.session() as session:
            query = session.query(Repository).filter(Repository.repo_related_group == repo_related_group)
            if enabled_only:
                query = query.filter(Repository.disable_flag == False)
            repositories = query.all()
            for repository in repositories:
                session.expunge(repository)
            return repositories
    
    def get_repositories_by_type(self, repo_type: str, enabled_only: bool = True) -> List[Repository]:
        """根据仓库类型获取仓库列表"""
        with db_manager.session() as session:
            query = session.query(Repository).filter(Repository.repo_type == repo_type)
            if enabled_only:
                query = query.filter(Repository.disable_flag == False)
            repositories = query.all()
            for repository in repositories:
                session.expunge(repository)
            return repositories
    
    def get_repositories_by_language(self, main_language: str, enabled_only: bool = True) -> List[Repository]:
        """根据主要编程语言获取仓库列表"""
        with db_manager.session() as session:
            query = session.query(Repository).filter(Repository.main_language == main_language)
            if enabled_only:
                query = query.filter(Repository.disable_flag == False)
            repositories = query.all()
            for repository in repositories:
                session.expunge(repository)
            return repositories
    
    def get_all_repositories(self, limit: Optional[int] = None, enabled_only: bool = True,
                           order_by: str = 'created_at', desc_order: bool = True) -> List[Repository]:
        """获取所有仓库"""
        with db_manager.session() as session:
            query = session.query(Repository)
            if enabled_only:
                query = query.filter(Repository.disable_flag == False)
            if hasattr(Repository, order_by):
                order_field = getattr(Repository, order_by)
                if desc_order:
                    query = query.order_by(order_field.desc())
                else:
                    query = query.order_by(order_field.asc())
            if limit:
                query = query.limit(limit)
            repositories = query.all()
            for repository in repositories:
                session.expunge(repository)
            return repositories
    
    def get_enabled_repositories(self, limit: Optional[int] = None) -> List[Repository]:
        """获取启用的仓库"""
        return self.get_all_repositories(limit=limit, enabled_only=True)
    
    def get_disabled_repositories(self, limit: Optional[int] = None) -> List[Repository]:
        """获取禁用的仓库"""
        with db_manager.session() as session:
            query = session.query(Repository).filter(Repository.disable_flag == True)
            if limit:
                query = query.limit(limit)
            repositories = query.all()
            for repository in repositories:
                session.expunge(repository)
            return repositories
    
    def search_repositories(self, keyword: str, enabled_only: bool = True) -> List[Repository]:
        """搜索仓库（根据名称、编码、描述）"""
        with db_manager.session() as session:
            query = session.query(Repository).filter(
                (Repository.repo_name.contains(keyword)) |
                (Repository.repo_code.contains(keyword)) |
                (Repository.description.contains(keyword))
            )
            if enabled_only:
                query = query.filter(Repository.disable_flag == False)
            repositories = query.all()
            for repository in repositories:
                session.expunge(repository)
            return repositories
    
    def update_repository(self, repo_id: int, **kwargs) -> Optional[Repository]:
        """更新仓库信息"""
        with db_manager.transaction() as session:
            repository = session.query(Repository).filter(Repository.id == repo_id).first()
            if repository:
                for key, value in kwargs.items():
                    if hasattr(repository, key):
                        setattr(repository, key, value)
                repository.updated_at = datetime.utcnow()
                session.flush()
                session.expunge(repository)
                return repository
            return None
    
    def update_analyzed_time(self, repo_id: int, analyzed_time: datetime = None) -> Optional[Repository]:
        """更新最后分析时间"""
        update_time = analyzed_time or datetime.utcnow()
        return self.update_repository(repo_id, last_analyzed_time=update_time)
    
    def update_current_version(self, repo_id: int, version: str, user: str = None) -> Optional[Repository]:
        """更新当前版本"""
        update_data = {'current_version': version}
        if user:
            update_data['update_user'] = user
        return self.update_repository(repo_id, **update_data)
    
    def enable_repository(self, repo_id: int, user: str = None) -> Optional[Repository]:
        """启用仓库"""
        update_data = {'disable_flag': False}
        if user:
            update_data['update_user'] = user
        return self.update_repository(repo_id, **update_data)
    
    def disable_repository(self, repo_id: int, user: str = None) -> Optional[Repository]:
        """禁用仓库"""
        update_data = {'disable_flag': True}
        if user:
            update_data['update_user'] = user
        return self.update_repository(repo_id, **update_data)
    
    def delete_repository(self, repo_id: int) -> bool:
        """删除仓库（软删除，实际上是禁用）"""
        result = self.disable_repository(repo_id)
        return result is not None
    
    def get_repository_statistics(self) -> Dict[str, Any]:
        """获取仓库统计信息"""
        with db_manager.session() as session:
            total_count = session.query(Repository).count()
            enabled_count = session.query(Repository).filter(Repository.disable_flag == False).count()
            disabled_count = session.query(Repository).filter(Repository.disable_flag == True).count()
            
            # 按类型统计
            type_stats = session.query(
                Repository.repo_type,
                session.query(Repository).filter(Repository.repo_type == Repository.repo_type).count()
            ).group_by(Repository.repo_type).all()
            
            # 按语言统计
            language_stats = session.query(
                Repository.main_language,
                session.query(Repository).filter(Repository.main_language == Repository.main_language).count()
            ).group_by(Repository.main_language).all()
            
            return {
                'total_repositories': total_count,
                'enabled_repositories': enabled_count,
                'disabled_repositories': disabled_count,
                'enabled_percentage': round(enabled_count / total_count * 100, 2) if total_count > 0 else 0,
                'type_distribution': dict(type_stats),
                'language_distribution': dict(language_stats)
            }
    
    def get_repositories_with_relations(self, repo_ids: List[int] = None) -> List[Repository]:
        """获取仓库及其关联数据"""
        with db_manager.session() as session:
            query = session.query(Repository)
            if repo_ids:
                query = query.filter(Repository.id.in_(repo_ids))
            
            # 预加载关联数据
            repositories = query.options(
                session.joinedload(Repository.endpoints),
                session.joinedload(Repository.source_dependencies),
                session.joinedload(Repository.target_dependencies),
                session.joinedload(Repository.document_versions)
            ).all()
            
            for repository in repositories:
                session.expunge(repository)
            return repositories
    
    def get_repository_summary(self, repo_id: int) -> Optional[Dict[str, Any]]:
        """获取仓库摘要信息"""
        repository = self.get_repository_by_id(repo_id)
        if not repository:
            return None
        
        with db_manager.session() as session:
            # 获取端点数量
            endpoint_count = session.query(Repository).join(Repository.endpoints).filter(
                Repository.id == repo_id
            ).count()
            
            # 获取依赖数量
            dependency_count = session.query(Repository).join(Repository.source_dependencies).filter(
                Repository.id == repo_id
            ).count()
            
            # 获取文档版本数量
            version_count = session.query(Repository).join(Repository.document_versions).filter(
                Repository.id == repo_id
            ).count()
            
            return {
                'repository': repository.to_dict(),
                'endpoint_count': endpoint_count,
                'dependency_count': dependency_count,
                'document_version_count': version_count,
                'is_enabled': repository.is_enabled,
                'full_repo_name': repository.full_repo_name,
                'last_analyzed': repository.last_analyzed_time.isoformat() if repository.last_analyzed_time else None
            }
    
    def batch_enable_repositories(self, repo_ids: List[int], user: str = None) -> int:
        """批量启用仓库"""
        with db_manager.transaction() as session:
            update_data = {'disable_flag': False, 'updated_at': datetime.utcnow()}
            if user:
                update_data['update_user'] = user
            
            count = session.query(Repository).filter(
                Repository.id.in_(repo_ids)
            ).update(update_data, synchronize_session=False)
            return count
    
    def batch_disable_repositories(self, repo_ids: List[int], user: str = None) -> int:
        """批量禁用仓库"""
        with db_manager.transaction() as session:
            update_data = {'disable_flag': True, 'updated_at': datetime.utcnow()}
            if user:
                update_data['update_user'] = user
            
            count = session.query(Repository).filter(
                Repository.id.in_(repo_ids)
            ).update(update_data, synchronize_session=False)
            return count


# 全局仓库信息服务实例
repository_service = RepositoryService()