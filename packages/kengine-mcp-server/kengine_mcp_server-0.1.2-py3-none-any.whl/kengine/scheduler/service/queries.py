"""
数据库查询辅助类

封装复杂的数据库查询逻辑，避免在 Service 中写重复的查询代码
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc

from ..models import Task
from ..models import TaskProgress
from ..models import LLMStats, LLMCallRecord
from ...core.enums import TaskStatus


class TaskQueries:
    """任务相关查询"""
    
    @staticmethod
    def get_task_with_relations(session: Session, task_id: int) -> Optional[Task]:
        """获取任务及其关联数据"""
        return session.query(Task).options(
            joinedload(Task.progress_records),
            joinedload(Task.llm_stats)
        ).filter(Task.id == task_id).first()
    
    @staticmethod
    def get_tasks_by_status(session: Session, status: str, limit: Optional[int] = None) -> List[Task]:
        """根据状态获取任务"""
        query = session.query(Task).filter(Task.status == status)
        query = query.order_by(desc(Task.created_at))
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def get_running_tasks(session: Session) -> List[Task]:
        """获取正在运行的任务"""
        return TaskQueries.get_tasks_by_status(session, TaskStatus.RUNNING.value)
    
    @staticmethod
    def get_pending_tasks(session: Session, limit: Optional[int] = None) -> List[Task]:
        """获取待处理的任务"""
        return TaskQueries.get_tasks_by_status(session, TaskStatus.PENDING.value, limit)
    
    @staticmethod
    def get_completed_tasks(session: Session, limit: Optional[int] = None) -> List[Task]:
        """获取已完成的任务"""
        return TaskQueries.get_tasks_by_status(session, TaskStatus.COMPLETED.value, limit)
    
    @staticmethod
    def get_failed_tasks(session: Session, limit: Optional[int] = None) -> List[Task]:
        """获取失败的任务"""
        return TaskQueries.get_tasks_by_status(session, TaskStatus.FAILED.value, limit)
    
    @staticmethod
    def get_tasks_by_repo(session: Session, repo_group: str, repo_name: str, 
                         limit: Optional[int] = None) -> List[Task]:
        """根据仓库获取任务"""
        query = session.query(Task).filter(
            and_(Task.repo_group == repo_group, Task.repo_name == repo_name)
        ).order_by(desc(Task.created_at))
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def get_pending_task_by_repo(session: Session, repo_group: str, repo_name: str) -> Optional[Task]:
        """根据仓库获取待处理的任务"""
        return session.query(Task).filter(
            and_(
                Task.repo_group == repo_group,
                Task.repo_name == repo_name,
                Task.status == TaskStatus.PENDING.value
            )
        ).order_by(desc(Task.created_at)).first()
    
    @staticmethod
    def get_recent_tasks(session: Session, days: int = 7, limit: Optional[int] = None) -> List[Task]:
        """获取最近的任务"""
        since_date = datetime.utcnow() - timedelta(days=days)
        query = session.query(Task).filter(Task.created_at >= since_date)
        query = query.order_by(desc(Task.created_at))
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def get_task_statistics(session: Session) -> Dict[str, Any]:
        """获取任务统计信息"""
        # 按状态统计任务数量
        status_counts = session.query(
            Task.status,
            func.count(Task.id).label('count')
        ).group_by(Task.status).all()
        
        # 总任务数
        total_tasks = session.query(func.count(Task.id)).scalar()
        
        # 今日任务数
        today = datetime.utcnow().date()
        today_tasks = session.query(func.count(Task.id)).filter(
            func.date(Task.created_at) == today
        ).scalar()
        
        return {
            'total_tasks': total_tasks,
            'today_tasks': today_tasks,
            'status_counts': {status: count for status, count in status_counts}
        }


class TaskProgressQueries:
    """任务进度相关查询"""
    
    @staticmethod
    def get_task_progress_records(session: Session, task_id: int) -> List[TaskProgress]:
        """获取任务的所有进度记录"""
        return session.query(TaskProgress).filter(
            TaskProgress.task_id == task_id
        ).order_by(TaskProgress.created_at).all()
    
    @staticmethod
    def get_latest_progress(session: Session, task_id: int) -> Optional[TaskProgress]:
        """获取任务的最新进度记录"""
        return session.query(TaskProgress).filter(
            TaskProgress.task_id == task_id
        ).order_by(desc(TaskProgress.created_at)).first()
    
    @staticmethod
    def get_progress_by_stage(session: Session, task_id: int, stage: str) -> List[TaskProgress]:
        """获取指定阶段的进度记录"""
        return session.query(TaskProgress).filter(
            and_(TaskProgress.task_id == task_id, TaskProgress.stage == stage)
        ).order_by(TaskProgress.created_at).all()


class LLMStatsQueries:
    """大模型统计相关查询"""
    
    @staticmethod
    def get_task_llm_stats(session: Session, task_id: int) -> Optional[LLMStats]:
        """获取任务的大模型统计信息"""
        return session.query(LLMStats).filter(LLMStats.task_id == task_id).first()
    
    @staticmethod
    def get_llm_call_records(session: Session, task_id: int) -> List[LLMCallRecord]:
        """获取任务的大模型调用记录"""
        return session.query(LLMCallRecord).filter(
            LLMCallRecord.task_id == task_id
        ).order_by(LLMCallRecord.created_at).all()