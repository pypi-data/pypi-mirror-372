"""
知识生成任务调度器

本模块负责管理知识生成任务的调度和执行，实现职责分离：
- 任务创建和状态管理
- 后台线程执行
- 进度跟踪和错误处理
- 与 KnowledgeService 的协调

重构历史：
- 2024-XX-XX: 从 knowledge_service.py 中分离任务管理逻辑
"""

import logging
import threading
from typing import Optional, Dict, Any
from datetime import datetime

from ..core.types import KnowledgeGenerationRequest
from ..utils.safe_file import safe_file_operation
from ..scheduler.service.task_service import TaskService
from ..scheduler.models.task import TaskStatus


logger = logging.getLogger(__name__)


class KnowledgeScheduler:
    """
    知识生成任务调度器
    
    负责管理知识生成任务的完整生命周期：
    - 任务创建和验证
    - 后台异步执行
    - 进度跟踪和状态更新
    - 错误处理和恢复
    
    与 KnowledgeService 协作，实现职责分离：
    - KnowledgeScheduler: 任务管理和调度
    - KnowledgeService: 知识生成核心逻辑
    """
    
    def __init__(self):
        """初始化调度器"""
        self.task_service = TaskService()
        self._active_tasks: Dict[str, threading.Thread] = {}
        
    @safe_file_operation
    def schedule_generation_task(self, request: KnowledgeGenerationRequest, auto_start: bool = False) -> Dict[str, Any]:
        """
        调度知识生成任务
        
        Args:
            request: 知识生成请求参数
            auto_start: 是否自动启动生成任务，默认为False
            
        Returns:
            Dict[str, Any]: 包含任务ID和状态的响应
            
        Raises:
            ValueError: 当请求参数无效时
            RuntimeError: 当任务创建失败时
        """
        try:
            # 1. 验证请求参数
            self._validate_request(request)
            
            # 2. 检查是否已有相同任务在执行
            existing_task = self.task_service.get_pending_task_by_repo(
                request.repo_group, 
                request.repo_name
            )
            
            if existing_task:
                logger.info(f"仓库 {request.repo_group}/{request.repo_name} 已有任务在执行中")
                return {
                    "success": True,
                    "task_id": existing_task.id,
                    "status": "already_running",
                    "message": f"仓库 {request.repo_group}/{request.repo_name} 已有任务在执行中"
                }
            
            # 3. 创建新任务
            task = self.task_service.create_task(
                repo_group=request.repo_group,
                repo_name=request.repo_name,
                model_name=request.model_name,
                branch=request.branch,
                prompt_version=request.prompt_version,
                force_project_type=request.force_project_type,
                execute_step=request.execute_step.value,
                specify_document_path=request.specify_document_path
            )
            
            logger.info(f"创建知识生成任务: {task.id}")
            
            # 4. 根据auto_start参数决定是否启动后台执行线程
            if auto_start:
                self._start_background_execution(task.id, request)
                status = "started"
                message = f"知识生成任务已启动，任务ID: {task.id}"
            else:
                status = "created"
                message = f"知识生成任务已创建但未启动，任务ID: {task.id}。可稍后手动启动。"
            
            return {
                "success": True,
                "task_id": task.id,
                "status": status,
                "message": message
            }
            
        except Exception as e:
            logger.error(f"调度知识生成任务失败: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"调度任务失败: {str(e)}",
                "message": "任务调度过程中发生错误，请检查日志获取详细信息"
            }
    
    def _validate_request(self, request: KnowledgeGenerationRequest) -> None:
        """
        验证请求参数
        
        Args:
            request: 知识生成请求参数
            
        Raises:
            ValueError: 当参数无效时
        """
        if not request.repo_group:
            raise ValueError("repo_group 参数不能为空")
        if not request.repo_name:
            raise ValueError("repo_name 参数不能为空")
        if not request.model_name:
            raise ValueError("model_name 参数不能为空")
    
    def _start_background_execution(self, task_id: str, request: KnowledgeGenerationRequest) -> None:
        """
        启动后台执行线程
        
        Args:
            task_id: 任务ID
            request: 知识生成请求参数
        """
        def execute_task():
            """后台任务执行函数"""
            try:
                # 更新任务状态为运行中
                self.task_service.update_task(task_id, status=TaskStatus.RUNNING)
                
                # 导入并执行知识生成
                from ..core.knowledge_service import KnowledgeService
                knowledge_service = KnowledgeService()
                
                # 执行知识生成（KnowledgeService 内部管理 tracker 创建）
                result = knowledge_service.generate_knowledge(
                    request=request,
                    task_id=task_id
                )
                
                # 更新任务状态
                if result.success:
                    self.task_service.update_task(
                        task_id, 
                        status=TaskStatus.COMPLETED,
                        result=result.__dict__
                    )
                    logger.info(f"任务 {task_id} 执行成功")
                else:
                    self.task_service.update_task(
                        task_id, 
                        status=TaskStatus.FAILED,
                        error_message=result.error or "知识生成失败"
                    )
                    logger.error(f"任务 {task_id} 执行失败: {result.error}")
                    
            except Exception as e:
                # 处理执行过程中的异常
                error_msg = f"任务执行异常: {str(e)}"
                logger.error(f"任务 {task_id} 执行异常: {error_msg}", exc_info=True)
                
                self.task_service.update_task(
                    task_id,
                    status=TaskStatus.FAILED,
                    error_message=error_msg
                )
            finally:
                # 清理活跃任务记录
                if task_id in self._active_tasks:
                    del self._active_tasks[task_id]
        
        # 创建并启动后台线程
        thread = threading.Thread(
            target=execute_task,
            name=f"KnowledgeGeneration-{task_id}",
            daemon=True
        )
        
        self._active_tasks[task_id] = thread
        thread.start()
        
        logger.info(f"后台任务线程已启动: {task_id}")
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            Optional[Dict[str, Any]]: 任务状态信息，如果任务不存在则返回None
        """
        try:
            task = self.task_service.get_task_by_id(task_id)
            if not task:
                return None
                
            # 获取进度信息
            progress_info = self.progress_manager.get_progress(task_id)
            
            return {
                "task_id": task.id,
                "status": task.status.value,
                "repo_group": task.repo_group,
                "repo_name": task.repo_name,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None,
                "progress": progress_info,
                "error_message": task.error_message,
                "is_active": task_id in self._active_tasks
            }
            
        except Exception as e:
            logger.error(f"获取任务状态失败 {task_id}: {str(e)}", exc_info=True)
            return None
    
    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict[str, Any]: 取消操作结果
        """
        try:
            # 检查任务是否存在
            task = self.task_service.get_task_by_id(task_id)
            if not task:
                return {
                    "success": False,
                    "message": f"任务 {task_id} 不存在"
                }
            
            # 检查任务状态
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                return {
                    "success": False,
                    "message": f"任务 {task_id} 已结束，无法取消"
                }
            
            # 更新任务状态为已取消
            self.task_service.update_task(task_id, status=TaskStatus.CANCELLED)
            
            # 如果有活跃线程，尝试清理（注意：Python线程无法强制终止）
            if task_id in self._active_tasks:
                del self._active_tasks[task_id]
                logger.warning(f"任务 {task_id} 已标记为取消，但后台线程可能仍在运行")
            
            logger.info(f"任务 {task_id} 已取消")
            
            return {
                "success": True,
                "message": f"任务 {task_id} 已取消"
            }
            
        except Exception as e:
            logger.error(f"取消任务失败 {task_id}: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"取消任务失败: {str(e)}"
            }
    
    def get_active_tasks(self) -> Dict[str, Any]:
        """
        获取所有活跃任务
        
        Returns:
            Dict[str, Any]: 活跃任务信息
        """
        try:
            active_task_ids = list(self._active_tasks.keys())
            tasks_info = []
            
            for task_id in active_task_ids:
                task_status = self.get_task_status(task_id)
                if task_status:
                    tasks_info.append(task_status)
            
            return {
                "success": True,
                "active_count": len(tasks_info),
                "tasks": tasks_info
            }
            
        except Exception as e:
            logger.error(f"获取活跃任务失败: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"获取活跃任务失败: {str(e)}"
            }


# 全局调度器实例（单例模式）
_scheduler_instance: Optional[KnowledgeScheduler] = None


def get_knowledge_scheduler() -> KnowledgeScheduler:
    """
    获取知识调度器实例（单例模式）
    
    Returns:
        KnowledgeScheduler: 调度器实例
    """
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = KnowledgeScheduler()
    return _scheduler_instance