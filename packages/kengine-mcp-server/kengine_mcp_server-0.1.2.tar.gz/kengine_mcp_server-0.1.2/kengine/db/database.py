"""
数据库配置和基础设置

提供SQLAlchemy数据库连接、会话管理和基础模型类
"""

import os
import logging
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# 数据库配置
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./kengine_tasks.db')

# 创建数据库引擎
if DATABASE_URL.startswith('sqlite'):
    # SQLite配置
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=os.getenv('SQL_DEBUG', 'false').lower() == 'true'
    )
else:
    # PostgreSQL/MySQL配置
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=os.getenv('SQL_DEBUG', 'false').lower() == 'true'
    )

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

# 元数据
metadata = MetaData()


@contextmanager
def get_db_session():
    """数据库会话上下文管理器"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"数据库操作失败: {e}")
        raise
    finally:
        db.close()

