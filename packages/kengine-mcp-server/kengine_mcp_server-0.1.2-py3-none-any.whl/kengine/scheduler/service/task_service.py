"""
任务服务

提供任务和任务进度相关的业务逻辑处理
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ...db.database_manager import db_manager
from ..models.task import Task
from ..models.task_progress import TaskProgress
from .queries import TaskQueries, TaskProgressQueries
from ...core.enums import TaskStatus


class TaskService:
    """任务服务类"""
    
    def __init__(self):
        """初始化任务服务"""
        # TaskService 自己管理 db_manager，不需要外部传递
        pass
    
    def create_task(self, name: str, repo_group: str, repo_name: str, 
                         branch: str = "master", model_name: str = "default",
                         execute_step: str = "full", **kwargs) -> Task:
        """创建任务"""
        with db_manager.transaction() as session:
            task = Task(
                name=name,
                repo_group=repo_group,
                repo_name=repo_name,
                branch=branch,
                model_name=model_name,
                execute_step=execute_step,
                status=TaskStatus.PENDING.value,
                **kwargs
            )
            session.add(task)
            session.flush()  # 获取 ID
            session.expunge(task)  # 从会话中分离
            return task
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """根据ID获取任务"""
        with db_manager.session() as session:
            task = session.query(Task).filter(Task.id == task_id).first()
            if task:
                session.expunge(task)
            return task
    
    def get_task_with_relations(self, task_id: int) -> Optional[Task]:
        """获取任务及其关联数据"""
        with db_manager.session() as session:
            task = TaskQueries.get_task_with_relations(session, task_id)
            if task:
                session.expunge(task)
            return task
    
    def get_all_tasks(self, limit: Optional[int] = None, 
                           order_by: str = 'created_at', desc_order: bool = True) -> List[Task]:
        """获取所有任务"""
        with db_manager.session() as session:
            query = session.query(Task)
            if hasattr(Task, order_by):
                order_field = getattr(Task, order_by)
                if desc_order:
                    query = query.order_by(order_field.desc())
                else:
                    query = query.order_by(order_field.asc())
            if limit:
                query = query.limit(limit)
            tasks = query.all()
            for task in tasks:
                session.expunge(task)
            return tasks
    
    def get_tasks_by_status(self, status: str, limit: Optional[int] = None) -> List[Task]:
        """根据状态获取任务"""
        with db_manager.session() as session:
            tasks = TaskQueries.get_tasks_by_status(session, status, limit)
            for task in tasks:
                session.expunge(task)
            return tasks
    
    def get_running_tasks(self) -> List[Task]:
        """获取正在运行的任务"""
        return self.get_tasks_by_status(TaskStatus.RUNNING.value)
    
    def get_pending_tasks(self, limit: Optional[int] = None) -> List[Task]:
        """获取待处理的任务"""
        return self.get_tasks_by_status(TaskStatus.PENDING.value, limit)
    
    def get_completed_tasks(self, limit: Optional[int] = None) -> List[Task]:
        """获取已完成的任务"""
        return self.get_tasks_by_status(TaskStatus.COMPLETED.value, limit)
    
    def get_failed_tasks(self, limit: Optional[int] = None) -> List[Task]:
        """获取失败的任务"""
        return self.get_tasks_by_status(TaskStatus.FAILED.value, limit)
    
    def get_pending_task_by_repo(self, repo_group: str, repo_name: str) -> Optional[Task]:
        """根据仓库获取待处理的任务"""
        with db_manager.session() as session:
            task = TaskQueries.get_pending_task_by_repo(session, repo_group, repo_name)
            if task:
                session.expunge(task)
            return task
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """获取任务统计信息"""
        with db_manager.session() as session:
            return TaskQueries.get_task_statistics(session)
    
    def update_task(self, task_id: int, **kwargs) -> Optional[Task]:
        """更新任务"""
        with db_manager.transaction() as session:
            task = session.query(Task).filter(Task.id == task_id).first()
            if task:
                for key, value in kwargs.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                task.updated_at = datetime.utcnow()
                session.flush()
                session.expunge(task)
                return task
            return None
    
    def update_task_status(self, task_id: int, status: str) -> Optional[Task]:
        """更新任务状态"""
        return self.update_task(task_id, status=status)
    
    def start_task(self, task_id: int) -> Optional[Task]:
        """启动任务"""
        return self.update_task(task_id, 
                                    status=TaskStatus.RUNNING.value,
                                    started_at=datetime.utcnow())
    
    def complete_task(self, task_id: int, project_path: str = None, 
                           **kwargs) -> Optional[Task]:
        """完成任务"""
        update_data = {
            'status': TaskStatus.COMPLETED.value,
            'completed_at': datetime.utcnow(),
            **kwargs
        }
        if project_path:
            update_data['project_path'] = project_path
        return self.update_task(task_id, **update_data)
    
    def fail_task(self, task_id: int, error_message: str, 
                       **kwargs) -> Optional[Task]:
        """标记任务失败"""
        return self.update_task(task_id,
                                    status=TaskStatus.FAILED.value,
                                    error_message=error_message,
                                    completed_at=datetime.utcnow(),
                                    **kwargs)
    
    def cancel_task(self, task_id: int) -> Optional[Task]:
        """取消任务"""
        return self.update_task(task_id, status=TaskStatus.CANCELLED.value)
        
    def create_progress_record(self, task_id: int, stage: str, message: str,
                                   status: str = 'started', **kwargs) -> TaskProgress:
        """创建进度记录"""
        with db_manager.transaction() as session:
            progress = TaskProgress(
                task_id=task_id,
                stage=stage,
                message=message,
                status=status,
                **kwargs
            )
            session.add(progress)
            session.flush()
            session.expunge(progress)
            return progress
    
    def get_task_progress_records(self, task_id: int) -> List[TaskProgress]:
        """获取任务的所有进度记录"""
        with db_manager.session() as session:
            records = TaskProgressQueries.get_task_progress_records(session, task_id)
            for record in records:
                session.expunge(record)
            return records
    
    def get_latest_progress(self, task_id: int) -> Optional[TaskProgress]:
        """获取任务的最新进度记录"""
        with db_manager.session() as session:
            progress = TaskProgressQueries.get_latest_progress(session, task_id)
            if progress:
                session.expunge(progress)
            return progress
    
    # ==================== 统一的事务方法（解决原来的事务分离问题）====================
    
    def start_stage(self, task_id: int, stage: str, message: str) -> None:
        """开始阶段并自动将任务状态设置为运行中"""
        with db_manager.transaction() as session:
            # 1. 创建进度记录
            progress = TaskProgress(
                task_id=task_id,
                stage=stage,
                message=message,
                status='started'
            )
            session.add(progress)
            
            # 2. 更新任务状态为运行中
            task = session.query(Task).filter(Task.id == task_id).first()
            if task:
                task.status = TaskStatus.RUNNING.value
                task.updated_at = datetime.utcnow()
    
    def complete_stage(self, task_id: int, stage: str, message: str) -> None:
        """完成阶段"""
        self.create_progress_record(task_id, stage, message, 'completed')
    
    def fail_stage_with_task_status(self, task_id: int, stage: str,
                                        error_message: str, task_status: str = None) -> None:
        """在同一事务中标记阶段失败并更新任务状态"""
        with db_manager.transaction() as session:
            # 1. 创建失败进度记录
            progress = TaskProgress(
                task_id=task_id,
                stage=stage,
                message=error_message,
                status='failed'
            )
            session.add(progress)
            
            # 2. 更新任务状态
            if task_status:
                task = session.query(Task).filter(Task.id == task_id).first()
                if task:
                    task.status = task_status
                    task.error_message = error_message
                    task.updated_at = datetime.utcnow()
    
    def update_stage_progress(self, task_id: int, stage: str, message: str) -> None:
        """更新阶段进度"""
        self.create_progress_record(task_id, stage, message, 'in_progress')


# 全局任务服务实例
task_service = TaskService()