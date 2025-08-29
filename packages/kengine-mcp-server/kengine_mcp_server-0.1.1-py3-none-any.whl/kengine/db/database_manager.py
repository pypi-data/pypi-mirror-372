"""
数据库管理器

提供统一的数据库会话管理和事务控制
"""

from typing import Generator
from contextlib import contextmanager
from sqlalchemy.orm import Session
from .database import get_db_session
from contextlib import contextmanager


class DatabaseManager:
    """数据库管理器类"""
    
    def __init__(self):
        """初始化数据库管理器"""
        pass
    
    @contextmanager
    def transaction(self) -> Generator[Session, None, None]:
        """
        获取数据库事务会话
        
        使用方式:
        with db_manager.transaction() as session:
            # 数据库操作
            session.add(model_instance)
            # 自动提交或回滚
        
        Returns:
            Session: 数据库会话对象
        """
        with get_db_session() as session:
            try:
                yield session
                # 如果没有异常，会话会自动提交
            except Exception:
                # 如果有异常，会话会自动回滚
                raise
    
    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """
        获取普通数据库会话（不自动提交）
        
        使用方式:
        with db_manager.session() as session:
            # 数据库查询操作
            result = session.query(Model).all()
        
        Returns:
            Session: 数据库会话对象
        """
        with get_db_session() as session:
            yield session


# 全局数据库管理器实例
db_manager = DatabaseManager()