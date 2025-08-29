"""
仓库端点信息服务

提供仓库端点信息相关的业务逻辑处理
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ...db.database_manager import db_manager
from ..models.repository_endpoint import RepositoryEndpoint


class RepositoryEndpointService:
    """仓库端点信息服务类"""
    
    def __init__(self):
        """初始化仓库端点信息服务"""
        pass
    
    def create_endpoint(self, repo_id: int, endpoint_type: int, endpoint_url: str,
                       doc_url: str = "", desc: str = "", **kwargs) -> RepositoryEndpoint:
        """创建仓库端点"""
        with db_manager.transaction() as session:
            endpoint = RepositoryEndpoint(
                repo_id=repo_id,
                endpoint_type=endpoint_type,
                endpoint_url=endpoint_url,
                doc_url=doc_url,
                desc=desc,
                **kwargs
            )
            session.add(endpoint)
            session.flush()  # 获取 ID
            session.expunge(endpoint)  # 从会话中分离
            return endpoint
    
    def get_endpoint_by_id(self, endpoint_id: int) -> Optional[RepositoryEndpoint]:
        """根据ID获取端点"""
        with db_manager.session() as session:
            endpoint = session.query(RepositoryEndpoint).filter(
                RepositoryEndpoint.id == endpoint_id
            ).first()
            if endpoint:
                session.expunge(endpoint)
            return endpoint
    
    def get_endpoints_by_repo(self, repo_id: int) -> List[RepositoryEndpoint]:
        """根据仓库ID获取所有端点"""
        with db_manager.session() as session:
            endpoints = session.query(RepositoryEndpoint).filter(
                RepositoryEndpoint.repo_id == repo_id
            ).all()
            for endpoint in endpoints:
                session.expunge(endpoint)
            return endpoints
    
    def get_endpoints_by_type(self, endpoint_type: int, repo_id: int = None) -> List[RepositoryEndpoint]:
        """根据端点类型获取端点列表"""
        with db_manager.session() as session:
            query = session.query(RepositoryEndpoint).filter(
                RepositoryEndpoint.endpoint_type == endpoint_type
            )
            if repo_id:
                query = query.filter(RepositoryEndpoint.repo_id == repo_id)
            endpoints = query.all()
            for endpoint in endpoints:
                session.expunge(endpoint)
            return endpoints
    
    def get_endpoint_by_url(self, endpoint_url: str) -> Optional[RepositoryEndpoint]:
        """根据端点URL获取端点"""
        with db_manager.session() as session:
            endpoint = session.query(RepositoryEndpoint).filter(
                RepositoryEndpoint.endpoint_url == endpoint_url
            ).first()
            if endpoint:
                session.expunge(endpoint)
            return endpoint
    
    def search_endpoints(self, keyword: str, repo_id: int = None) -> List[RepositoryEndpoint]:
        """搜索端点（根据URL、描述）"""
        with db_manager.session() as session:
            query = session.query(RepositoryEndpoint).filter(
                (RepositoryEndpoint.endpoint_url.contains(keyword)) |
                (RepositoryEndpoint.desc.contains(keyword))
            )
            if repo_id:
                query = query.filter(RepositoryEndpoint.repo_id == repo_id)
            endpoints = query.all()
            for endpoint in endpoints:
                session.expunge(endpoint)
            return endpoints
    
    def get_all_endpoints(self, limit: Optional[int] = None,
                         order_by: str = 'created_at', desc_order: bool = True) -> List[RepositoryEndpoint]:
        """获取所有端点"""
        with db_manager.session() as session:
            query = session.query(RepositoryEndpoint)
            if hasattr(RepositoryEndpoint, order_by):
                order_field = getattr(RepositoryEndpoint, order_by)
                if desc_order:
                    query = query.order_by(order_field.desc())
                else:
                    query = query.order_by(order_field.asc())
            if limit:
                query = query.limit(limit)
            endpoints = query.all()
            for endpoint in endpoints:
                session.expunge(endpoint)
            return endpoints
    
    def get_endpoints_with_documentation(self, repo_id: int = None) -> List[RepositoryEndpoint]:
        """获取有文档的端点"""
        with db_manager.session() as session:
            query = session.query(RepositoryEndpoint).filter(
                RepositoryEndpoint.doc_url.isnot(None),
                RepositoryEndpoint.doc_url != ''
            )
            if repo_id:
                query = query.filter(RepositoryEndpoint.repo_id == repo_id)
            endpoints = query.all()
            for endpoint in endpoints:
                session.expunge(endpoint)
            return endpoints
    
    def get_endpoints_without_documentation(self, repo_id: int = None) -> List[RepositoryEndpoint]:
        """获取无文档的端点"""
        with db_manager.session() as session:
            query = session.query(RepositoryEndpoint).filter(
                (RepositoryEndpoint.doc_url.is_(None)) |
                (RepositoryEndpoint.doc_url == '')
            )
            if repo_id:
                query = query.filter(RepositoryEndpoint.repo_id == repo_id)
            endpoints = query.all()
            for endpoint in endpoints:
                session.expunge(endpoint)
            return endpoints
    
    def update_endpoint(self, endpoint_id: int, **kwargs) -> Optional[RepositoryEndpoint]:
        """更新端点信息"""
        with db_manager.transaction() as session:
            endpoint = session.query(RepositoryEndpoint).filter(
                RepositoryEndpoint.id == endpoint_id
            ).first()
            if endpoint:
                for key, value in kwargs.items():
                    if hasattr(endpoint, key):
                        setattr(endpoint, key, value)
                endpoint.updated_at = datetime.utcnow()
                session.flush()
                session.expunge(endpoint)
                return endpoint
            return None
    
    def update_documentation(self, endpoint_id: int, doc_url: str, user: str = None) -> Optional[RepositoryEndpoint]:
        """更新端点文档地址"""
        update_data = {'doc_url': doc_url}
        if user:
            update_data['update_user'] = user
        return self.update_endpoint(endpoint_id, **update_data)
    
    def update_description(self, endpoint_id: int, description: str, user: str = None) -> Optional[RepositoryEndpoint]:
        """更新端点描述"""
        update_data = {'desc': description}
        if user:
            update_data['update_user'] = user
        return self.update_endpoint(endpoint_id, **update_data)
    
    def update_endpoint_url(self, endpoint_id: int, endpoint_url: str, user: str = None) -> Optional[RepositoryEndpoint]:
        """更新端点URL"""
        update_data = {'endpoint_url': endpoint_url}
        if user:
            update_data['update_user'] = user
        return self.update_endpoint(endpoint_id, **update_data)
    
    def delete_endpoint(self, endpoint_id: int) -> bool:
        """删除端点"""
        with db_manager.transaction() as session:
            endpoint = session.query(RepositoryEndpoint).filter(
                RepositoryEndpoint.id == endpoint_id
            ).first()
            if endpoint:
                session.delete(endpoint)
                return True
            return False
    
    def delete_endpoints_by_repo(self, repo_id: int) -> int:
        """删除指定仓库的所有端点"""
        with db_manager.transaction() as session:
            count = session.query(RepositoryEndpoint).filter(
                RepositoryEndpoint.repo_id == repo_id
            ).delete()
            return count
    
    def get_endpoint_statistics(self) -> Dict[str, Any]:
        """获取端点统计信息"""
        with db_manager.session() as session:
            total_count = session.query(RepositoryEndpoint).count()
            
            # 按类型统计
            type_stats = {}
            type_results = session.query(
                RepositoryEndpoint.endpoint_type,
                session.func.count(RepositoryEndpoint.id)
            ).group_by(RepositoryEndpoint.endpoint_type).all()
            
            for endpoint_type, count in type_results:
                type_stats[endpoint_type] = count
            
            # 文档统计
            with_doc_count = session.query(RepositoryEndpoint).filter(
                RepositoryEndpoint.doc_url.isnot(None),
                RepositoryEndpoint.doc_url != ''
            ).count()
            
            without_doc_count = total_count - with_doc_count
            
            return {
                'total_endpoints': total_count,
                'type_distribution': type_stats,
                'with_documentation': with_doc_count,
                'without_documentation': without_doc_count,
                'documentation_percentage': round(with_doc_count / total_count * 100, 2) if total_count > 0 else 0
            }
    
    def get_endpoints_with_relations(self, endpoint_ids: List[int] = None) -> List[RepositoryEndpoint]:
        """获取端点及其关联数据"""
        with db_manager.session() as session:
            query = session.query(RepositoryEndpoint)
            if endpoint_ids:
                query = query.filter(RepositoryEndpoint.id.in_(endpoint_ids))
            
            # 预加载关联数据
            endpoints = query.options(
                session.joinedload(RepositoryEndpoint.repository),
                session.joinedload(RepositoryEndpoint.dependencies)
            ).all()
            
            for endpoint in endpoints:
                session.expunge(endpoint)
            return endpoints
    
    def get_endpoint_dependencies(self, endpoint_id: int) -> List[Dict[str, Any]]:
        """获取端点的依赖关系"""
        with db_manager.session() as session:
            # 获取依赖此端点的仓库依赖关系
            from ..models.repository_dependency import RepositoryDependency
            dependencies = session.query(RepositoryDependency).filter(
                RepositoryDependency.target_endpoint_id == endpoint_id
            ).all()
            
            result = []
            for dep in dependencies:
                result.append({
                    'dependency_id': dep.id,
                    'source_repo_id': dep.source_repo_id,
                    'target_endpoint_url': dep.target_endpoint_url,
                    'dependency_type': dep.get_dependency_type()
                })
            
            return result
    
    def batch_update_documentation(self, endpoint_ids: List[int], doc_url: str, user: str = None) -> int:
        """批量更新端点文档地址"""
        with db_manager.transaction() as session:
            update_data = {'doc_url': doc_url, 'updated_at': datetime.utcnow()}
            if user:
                update_data['update_user'] = user
            
            count = session.query(RepositoryEndpoint).filter(
                RepositoryEndpoint.id.in_(endpoint_ids)
            ).update(update_data, synchronize_session=False)
            return count
    
    def batch_update_type(self, endpoint_ids: List[int], endpoint_type: int, user: str = None) -> int:
        """批量更新端点类型"""
        with db_manager.transaction() as session:
            update_data = {'endpoint_type': endpoint_type, 'updated_at': datetime.utcnow()}
            if user:
                update_data['update_user'] = user
            
            count = session.query(RepositoryEndpoint).filter(
                RepositoryEndpoint.id.in_(endpoint_ids)
            ).update(update_data, synchronize_session=False)
            return count
    
    def get_endpoint_summary(self, endpoint_id: int) -> Optional[Dict[str, Any]]:
        """获取端点摘要信息"""
        endpoint = self.get_endpoint_by_id(endpoint_id)
        if not endpoint:
            return None
        
        dependencies = self.get_endpoint_dependencies(endpoint_id)
        
        return {
            'endpoint': endpoint.to_dict(),
            'has_documentation': endpoint.has_documentation,
            'has_description': endpoint.has_description,
            'dependency_count': len(dependencies),
            'dependencies': dependencies
        }
    
    def find_duplicate_endpoints(self, repo_id: int = None) -> List[Dict[str, Any]]:
        """查找重复的端点URL"""
        with db_manager.session() as session:
            query = session.query(
                RepositoryEndpoint.endpoint_url,
                session.func.count(RepositoryEndpoint.id).label('count')
            ).group_by(RepositoryEndpoint.endpoint_url).having(
                session.func.count(RepositoryEndpoint.id) > 1
            )
            
            if repo_id:
                query = query.filter(RepositoryEndpoint.repo_id == repo_id)
            
            duplicates = query.all()
            
            result = []
            for url, count in duplicates:
                # 获取具体的重复端点
                endpoints = session.query(RepositoryEndpoint).filter(
                    RepositoryEndpoint.endpoint_url == url
                ).all()
                
                result.append({
                    'endpoint_url': url,
                    'duplicate_count': count,
                    'endpoints': [{'id': ep.id, 'repo_id': ep.repo_id} for ep in endpoints]
                })
            
            return result


# 全局仓库端点信息服务实例
repository_endpoint_service = RepositoryEndpointService()