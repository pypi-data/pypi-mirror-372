"""
仓库依赖关系服务

提供仓库依赖关系相关的业务逻辑处理
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ...db.database_manager import db_manager
from ..models.repository_dependency import RepositoryDependency


class RepositoryDependencyService:
    """仓库依赖关系服务类"""
    
    def __init__(self):
        """初始化仓库依赖关系服务"""
        pass
    
    def create_dependency(self, source_repo_id: int, target_endpoint_url: str,
                         target_repo_id: int = None, target_endpoint_id: int = None,
                         **kwargs) -> RepositoryDependency:
        """创建仓库依赖关系"""
        with db_manager.transaction() as session:
            dependency = RepositoryDependency(
                source_repo_id=source_repo_id,
                target_repo_id=target_repo_id,
                target_endpoint_id=target_endpoint_id,
                target_endpoint_url=target_endpoint_url,
                **kwargs
            )
            session.add(dependency)
            session.flush()  # 获取 ID
            session.expunge(dependency)  # 从会话中分离
            return dependency
    
    def get_dependency_by_id(self, dependency_id: int) -> Optional[RepositoryDependency]:
        """根据ID获取依赖关系"""
        with db_manager.session() as session:
            dependency = session.query(RepositoryDependency).filter(
                RepositoryDependency.id == dependency_id
            ).first()
            if dependency:
                session.expunge(dependency)
            return dependency
    
    def get_dependencies_by_source_repo(self, source_repo_id: int) -> List[RepositoryDependency]:
        """根据源仓库ID获取所有依赖关系"""
        with db_manager.session() as session:
            dependencies = session.query(RepositoryDependency).filter(
                RepositoryDependency.source_repo_id == source_repo_id
            ).all()
            for dependency in dependencies:
                session.expunge(dependency)
            return dependencies
    
    def get_dependencies_by_target_repo(self, target_repo_id: int) -> List[RepositoryDependency]:
        """根据目标仓库ID获取所有依赖关系"""
        with db_manager.session() as session:
            dependencies = session.query(RepositoryDependency).filter(
                RepositoryDependency.target_repo_id == target_repo_id
            ).all()
            for dependency in dependencies:
                session.expunge(dependency)
            return dependencies
    
    def get_dependencies_by_target_endpoint(self, target_endpoint_id: int) -> List[RepositoryDependency]:
        """根据目标端点ID获取所有依赖关系"""
        with db_manager.session() as session:
            dependencies = session.query(RepositoryDependency).filter(
                RepositoryDependency.target_endpoint_id == target_endpoint_id
            ).all()
            for dependency in dependencies:
                session.expunge(dependency)
            return dependencies
    
    def get_internal_dependencies(self, source_repo_id: int = None) -> List[RepositoryDependency]:
        """获取内部依赖关系（有目标仓库的依赖）"""
        with db_manager.session() as session:
            query = session.query(RepositoryDependency).filter(
                RepositoryDependency.target_repo_id.isnot(None)
            )
            if source_repo_id:
                query = query.filter(RepositoryDependency.source_repo_id == source_repo_id)
            dependencies = query.all()
            for dependency in dependencies:
                session.expunge(dependency)
            return dependencies
    
    def get_external_dependencies(self, source_repo_id: int = None) -> List[RepositoryDependency]:
        """获取外部依赖关系（无目标仓库的依赖）"""
        with db_manager.session() as session:
            query = session.query(RepositoryDependency).filter(
                RepositoryDependency.target_repo_id.is_(None)
            )
            if source_repo_id:
                query = query.filter(RepositoryDependency.source_repo_id == source_repo_id)
            dependencies = query.all()
            for dependency in dependencies:
                session.expunge(dependency)
            return dependencies
    
    def get_all_dependencies(self, limit: Optional[int] = None,
                           order_by: str = 'created_at', desc_order: bool = True) -> List[RepositoryDependency]:
        """获取所有依赖关系"""
        with db_manager.session() as session:
            query = session.query(RepositoryDependency)
            if hasattr(RepositoryDependency, order_by):
                order_field = getattr(RepositoryDependency, order_by)
                if desc_order:
                    query = query.order_by(order_field.desc())
                else:
                    query = query.order_by(order_field.asc())
            if limit:
                query = query.limit(limit)
            dependencies = query.all()
            for dependency in dependencies:
                session.expunge(dependency)
            return dependencies
    
    def update_dependency(self, dependency_id: int, **kwargs) -> Optional[RepositoryDependency]:
        """更新依赖关系"""
        with db_manager.transaction() as session:
            dependency = session.query(RepositoryDependency).filter(
                RepositoryDependency.id == dependency_id
            ).first()
            if dependency:
                for key, value in kwargs.items():
                    if hasattr(dependency, key):
                        setattr(dependency, key, value)
                dependency.updated_at = datetime.utcnow()
                session.flush()
                session.expunge(dependency)
                return dependency
            return None
    
    def update_target_endpoint(self, dependency_id: int, endpoint_url: str,
                             endpoint_id: int = None, user: str = None) -> Optional[RepositoryDependency]:
        """更新目标端点"""
        update_data = {
            'target_endpoint_url': endpoint_url
        }
        if endpoint_id:
            update_data['target_endpoint_id'] = endpoint_id
        if user:
            update_data['update_user'] = user
        return self.update_dependency(dependency_id, **update_data)
    
    def delete_dependency(self, dependency_id: int) -> bool:
        """删除依赖关系"""
        with db_manager.transaction() as session:
            dependency = session.query(RepositoryDependency).filter(
                RepositoryDependency.id == dependency_id
            ).first()
            if dependency:
                session.delete(dependency)
                return True
            return False
    
    def delete_dependencies_by_source_repo(self, source_repo_id: int) -> int:
        """删除指定源仓库的所有依赖关系"""
        with db_manager.transaction() as session:
            count = session.query(RepositoryDependency).filter(
                RepositoryDependency.source_repo_id == source_repo_id
            ).delete()
            return count
    
    def delete_dependencies_by_target_repo(self, target_repo_id: int) -> int:
        """删除指定目标仓库的所有依赖关系"""
        with db_manager.transaction() as session:
            count = session.query(RepositoryDependency).filter(
                RepositoryDependency.target_repo_id == target_repo_id
            ).delete()
            return count
    
    def get_dependency_statistics(self) -> Dict[str, Any]:
        """获取依赖关系统计信息"""
        with db_manager.session() as session:
            total_count = session.query(RepositoryDependency).count()
            internal_count = session.query(RepositoryDependency).filter(
                RepositoryDependency.target_repo_id.isnot(None)
            ).count()
            external_count = session.query(RepositoryDependency).filter(
                RepositoryDependency.target_repo_id.is_(None)
            ).count()
            
            return {
                'total_dependencies': total_count,
                'internal_dependencies': internal_count,
                'external_dependencies': external_count,
                'internal_percentage': round(internal_count / total_count * 100, 2) if total_count > 0 else 0,
                'external_percentage': round(external_count / total_count * 100, 2) if total_count > 0 else 0
            }
    
    def find_circular_dependencies(self, source_repo_id: int) -> List[List[int]]:
        """查找循环依赖"""
        with db_manager.session() as session:
            # 获取所有内部依赖关系
            dependencies = session.query(RepositoryDependency).filter(
                RepositoryDependency.target_repo_id.isnot(None)
            ).all()
            
            # 构建依赖图
            dependency_graph = {}
            for dep in dependencies:
                if dep.source_repo_id not in dependency_graph:
                    dependency_graph[dep.source_repo_id] = []
                dependency_graph[dep.source_repo_id].append(dep.target_repo_id)
            
            # 使用深度优先搜索查找循环依赖
            visited = set()
            rec_stack = set()
            cycles = []
            
            def dfs(node, path):
                if node in rec_stack:
                    # 找到循环依赖
                    cycle_start = path.index(node)
                    cycles.append(path[cycle_start:] + [node])
                    return
                
                if node in visited:
                    return
                
                visited.add(node)
                rec_stack.add(node)
                path.append(node)
                
                if node in dependency_graph:
                    for neighbor in dependency_graph[node]:
                        dfs(neighbor, path[:])
                
                rec_stack.remove(node)
                path.pop()
            
            dfs(source_repo_id, [])
            return cycles


# 全局仓库依赖关系服务实例
repository_dependency_service = RepositoryDependencyService()