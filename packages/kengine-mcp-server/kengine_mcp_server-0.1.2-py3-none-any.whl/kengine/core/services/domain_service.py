"""
业务领域服务

提供业务领域相关的业务逻辑处理
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import joinedload
from sqlalchemy import and_, or_, func, desc, asc

from ...db.database_manager import db_manager
from ..models.domain import Domain
from ..models.repository import Repository


class DomainService:
    """业务领域相关查询"""
    
    @staticmethod
    def get_domain_with_relations(session, domain_id: int) -> Optional[Domain]:
        """获取业务领域及其关联数据"""
        return session.query(Domain).options(
            joinedload(Domain.repositories)
        ).filter(Domain.id == domain_id).first()
    
    @staticmethod
    def get_domains_by_parent_id(session, parent_id: int, limit: Optional[int] = None) -> List[Domain]:
        """根据父级ID获取子领域"""
        query = session.query(Domain).filter(Domain.parent_id == parent_id)
        query = query.order_by(asc(Domain.domain_code))
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def get_root_domains(session, limit: Optional[int] = None) -> List[Domain]:
        """获取根级领域"""
        query = session.query(Domain).filter(
            or_(Domain.parent_id == 0, Domain.parent_id.is_(None))
        )
        query = query.order_by(asc(Domain.domain_code))
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def get_domains_by_level(session, level: int, limit: Optional[int] = None) -> List[Domain]:
        """根据层级获取领域"""
        query = session.query(Domain).filter(Domain.level == level)
        query = query.order_by(asc(Domain.domain_code))
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def get_domains_by_department(session, department: str, limit: Optional[int] = None) -> List[Domain]:
        """根据部门获取领域"""
        query = session.query(Domain).filter(Domain.department == department)
        query = query.order_by(asc(Domain.domain_code))
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def search_domains_by_name(session, name_keyword: str, limit: Optional[int] = None) -> List[Domain]:
        """根据名称关键字搜索领域"""
        query = session.query(Domain).filter(
            Domain.domain_name.like(f'%{name_keyword}%')
        )
        query = query.order_by(asc(Domain.domain_code))
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def get_domain_statistics(session) -> Dict[str, Any]:
        """获取领域统计信息"""
        total_count = session.query(func.count(Domain.id)).scalar()
        root_count = session.query(func.count(Domain.id)).filter(
            or_(Domain.parent_id == 0, Domain.parent_id.is_(None))
        ).scalar()
        
        # 按层级统计
        level_stats = session.query(
            Domain.level, func.count(Domain.id)
        ).group_by(Domain.level).all()
        
        # 按部门统计
        dept_stats = session.query(
            Domain.department, func.count(Domain.id)
        ).filter(Domain.department.isnot(None)).group_by(Domain.department).all()
        
        return {
            'total_count': total_count,
            'root_count': root_count,
            'level_statistics': {level: count for level, count in level_stats},
            'department_statistics': {dept: count for dept, count in dept_stats}
        }
    
    @staticmethod
    def check_domain_code_exists(session, domain_code: str, exclude_id: Optional[int] = None) -> bool:
        """检查领域编码是否已存在"""
        query = session.query(Domain).filter(Domain.domain_code == domain_code)
        if exclude_id:
            query = query.filter(Domain.id != exclude_id)
        return query.first() is not None


class DomainManager:
    """业务领域服务类"""
    
    def __init__(self):
        """初始化业务领域服务"""
        # DomainService 自己管理 db_manager，不需要外部传递
        pass
    
    def create_domain(self, domain_code: str, domain_name: str, 
                     parent_id: Optional[int] = None, level: Optional[int] = None,
                     department: Optional[str] = None, **kwargs) -> Domain:
        """创建业务领域"""
        with db_manager.transaction() as session:
            # 检查领域编码是否已存在
            if DomainService.check_domain_code_exists(session, domain_code):
                raise ValueError(f"领域编码 '{domain_code}' 已存在")
            
            # 如果没有指定层级，根据父级自动计算
            if level is None:
                if parent_id and parent_id > 0:
                    parent_domain = session.query(Domain).filter(Domain.id == parent_id).first()
                    if parent_domain:
                        level = parent_domain.level + 1
                    else:
                        raise ValueError(f"父级领域 ID {parent_id} 不存在")
                else:
                    level = 0  # 根级领域
            
            domain = Domain(
                domain_code=domain_code,
                domain_name=domain_name,
                parent_id=parent_id or 0,
                level=level,
                department=department or '',
                **kwargs
            )
            session.add(domain)
            session.flush()  # 获取 ID
            session.expunge(domain)  # 从会话中分离
            return domain
    
    def get_domain_by_id(self, domain_id: int) -> Optional[Domain]:
        """根据ID获取业务领域"""
        with db_manager.session() as session:
            domain = session.query(Domain).filter(Domain.id == domain_id).first()
            if domain:
                session.expunge(domain)
            return domain
    
    def get_domain_by_code(self, domain_code: str) -> Optional[Domain]:
        """根据编码获取业务领域"""
        with db_manager.session() as session:
            domain = session.query(Domain).filter(Domain.domain_code == domain_code).first()
            if domain:
                session.expunge(domain)
            return domain
    
    def get_domain_with_relations(self, domain_id: int) -> Optional[Domain]:
        """获取业务领域及其关联数据"""
        with db_manager.session() as session:
            domain = DomainService.get_domain_with_relations(session, domain_id)
            if domain:
                session.expunge(domain)
            return domain
    
    def get_all_domains(self, limit: Optional[int] = None, 
                       order_by: str = 'domain_code', desc_order: bool = False) -> List[Domain]:
        """获取所有业务领域"""
        with db_manager.session() as session:
            query = session.query(Domain)
            if hasattr(Domain, order_by):
                order_field = getattr(Domain, order_by)
                if desc_order:
                    query = query.order_by(order_field.desc())
                else:
                    query = query.order_by(order_field.asc())
            if limit:
                query = query.limit(limit)
            domains = query.all()
            for domain in domains:
                session.expunge(domain)
            return domains
    
    def get_root_domains(self, limit: Optional[int] = None) -> List[Domain]:
        """获取根级业务领域"""
        with db_manager.session() as session:
            domains = DomainService.get_root_domains(session, limit)
            for domain in domains:
                session.expunge(domain)
            return domains
    
    def get_child_domains(self, parent_id: int, limit: Optional[int] = None) -> List[Domain]:
        """获取子级业务领域"""
        with db_manager.session() as session:
            domains = DomainService.get_domains_by_parent_id(session, parent_id, limit)
            for domain in domains:
                session.expunge(domain)
            return domains
    
    def get_domains_by_level(self, level: int, limit: Optional[int] = None) -> List[Domain]:
        """根据层级获取业务领域"""
        with db_manager.session() as session:
            domains = DomainService.get_domains_by_level(session, level, limit)
            for domain in domains:
                session.expunge(domain)
            return domains
    
    def get_domains_by_department(self, department: str, limit: Optional[int] = None) -> List[Domain]:
        """根据部门获取业务领域"""
        with db_manager.session() as session:
            domains = DomainService.get_domains_by_department(session, department, limit)
            for domain in domains:
                session.expunge(domain)
            return domains
    
    def search_domains_by_name(self, name_keyword: str, limit: Optional[int] = None) -> List[Domain]:
        """根据名称关键字搜索业务领域"""
        with db_manager.session() as session:
            domains = DomainService.search_domains_by_name(session, name_keyword, limit)
            for domain in domains:
                session.expunge(domain)
            return domains
    
    def get_domain_statistics(self) -> Dict[str, Any]:
        """获取业务领域统计信息"""
        with db_manager.session() as session:
            return DomainService.get_domain_statistics(session)
    
    def update_domain(self, domain_id: int, **kwargs) -> Optional[Domain]:
        """更新业务领域"""
        with db_manager.transaction() as session:
            domain = session.query(Domain).filter(Domain.id == domain_id).first()
            if domain:
                # 如果要更新领域编码，检查是否重复
                if 'domain_code' in kwargs:
                    new_code = kwargs['domain_code']
                    if DomainService.check_domain_code_exists(session, new_code, domain_id):
                        raise ValueError(f"领域编码 '{new_code}' 已存在")
                
                # 如果要更新父级ID，需要重新计算层级
                if 'parent_id' in kwargs:
                    parent_id = kwargs['parent_id']
                    if parent_id and parent_id > 0:
                        parent_domain = session.query(Domain).filter(Domain.id == parent_id).first()
                        if parent_domain:
                            kwargs['level'] = parent_domain.level + 1
                        else:
                            raise ValueError(f"父级领域 ID {parent_id} 不存在")
                    else:
                        kwargs['level'] = 0
                
                for key, value in kwargs.items():
                    if hasattr(domain, key):
                        setattr(domain, key, value)
                domain.updated_at = datetime.utcnow()
                session.flush()
                session.expunge(domain)
                return domain
            return None
    
    def delete_domain(self, domain_id: int) -> bool:
        """删除业务领域"""
        with db_manager.transaction() as session:
            domain = session.query(Domain).filter(Domain.id == domain_id).first()
            if domain:
                # 检查是否有子领域
                child_count = session.query(func.count(Domain.id)).filter(
                    Domain.parent_id == domain_id
                ).scalar()
                if child_count > 0:
                    raise ValueError("存在子级领域，无法删除")
                
                # 检查是否有关联的仓库
                repo_count = session.query(func.count(Repository.id)).filter(
                    Repository.domain_id == domain_id
                ).scalar()
                if repo_count > 0:
                    raise ValueError("存在关联的仓库，无法删除")
                
                session.delete(domain)
                return True
            return False
    
    def get_domain_tree(self, root_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取领域树结构"""
        with db_manager.session() as session:
            if root_id:
                root_domains = [session.query(Domain).filter(Domain.id == root_id).first()]
                if not root_domains[0]:
                    return []
            else:
                root_domains = DomainService.get_root_domains(session)
            
            def build_tree(domain: Domain) -> Dict[str, Any]:
                children = DomainService.get_domains_by_parent_id(session, domain.id)
                return {
                    'id': domain.id,
                    'domain_code': domain.domain_code,
                    'domain_name': domain.domain_name,
                    'parent_id': domain.parent_id,
                    'level': domain.level,
                    'department': domain.department,
                    'repository_count': len(domain.repositories) if domain.repositories else 0,
                    'children': [build_tree(child) for child in children]
                }
            
            return [build_tree(domain) for domain in root_domains]
    
    def get_domain_path(self, domain_id: int) -> List[Domain]:
        """获取领域的完整路径（从根到当前领域）"""
        with db_manager.session() as session:
            path = []
            current_domain = session.query(Domain).filter(Domain.id == domain_id).first()
            
            while current_domain:
                path.insert(0, current_domain)
                if current_domain.parent_id and current_domain.parent_id > 0:
                    current_domain = session.query(Domain).filter(
                        Domain.id == current_domain.parent_id
                    ).first()
                else:
                    break
            
            # 从会话中分离所有对象
            for domain in path:
                session.expunge(domain)
            
            return path
    
    def move_domain(self, domain_id: int, new_parent_id: Optional[int]) -> Optional[Domain]:
        """移动领域到新的父级下"""
        with db_manager.transaction() as session:
            domain = session.query(Domain).filter(Domain.id == domain_id).first()
            if not domain:
                return None
            
            # 检查新父级是否存在（如果指定了的话）
            new_level = 0
            if new_parent_id and new_parent_id > 0:
                parent_domain = session.query(Domain).filter(Domain.id == new_parent_id).first()
                if not parent_domain:
                    raise ValueError(f"新父级领域 ID {new_parent_id} 不存在")
                
                # 检查是否会形成循环引用
                if self._would_create_cycle(session, domain_id, new_parent_id):
                    raise ValueError("移动操作会形成循环引用")
                
                new_level = parent_domain.level + 1
            
            # 更新领域的父级和层级
            domain.parent_id = new_parent_id or 0
            domain.level = new_level
            domain.updated_at = datetime.utcnow()
            
            # 递归更新所有子领域的层级
            self._update_children_levels(session, domain_id, new_level)
            
            session.flush()
            session.expunge(domain)
            return domain
    
    def _would_create_cycle(self, session, domain_id: int, new_parent_id: int) -> bool:
        """检查移动操作是否会创建循环引用"""
        current_id = new_parent_id
        while current_id:
            if current_id == domain_id:
                return True
            parent_domain = session.query(Domain).filter(Domain.id == current_id).first()
            if parent_domain and parent_domain.parent_id and parent_domain.parent_id > 0:
                current_id = parent_domain.parent_id
            else:
                break
        return False
    
    def _update_children_levels(self, session, parent_id: int, parent_level: int):
        """递归更新子领域的层级"""
        children = DomainService.get_domains_by_parent_id(session, parent_id)
        for child in children:
            child.level = parent_level + 1
            child.updated_at = datetime.utcnow()
            self._update_children_levels(session, child.id, child.level)