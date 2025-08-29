"""
进度回调系统

包含回调接口定义和数据库回调实现
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor

from ..enums import ProgressStatus, TaskStatus
from .models import ProgressInfo

from ...scheduler import task_service, llm_stats_service

class ProgressCallback(ABC):
    """进度回调抽象基类"""
    
    @abstractmethod
    async def on_progress_update(self, progress_info: ProgressInfo):
        """进度更新回调"""
        pass
    
    @abstractmethod
    async def on_stage_start(self, progress_info: ProgressInfo):
        """阶段开始回调"""
        pass
    
    @abstractmethod
    async def on_stage_complete(self, progress_info: ProgressInfo):
        """阶段完成回调"""
        pass
    
    @abstractmethod
    async def on_error(self, progress_info: ProgressInfo):
        """错误回调"""
        pass
    
    def on_progress(self, progress_info: ProgressInfo):
        """通用进度回调方法（同步版本）- 根据状态调用相应的异步方法"""
        import asyncio
        
        try:
            # 获取当前事件循环，如果没有则创建新的
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                # 如果没有运行中的事件循环，创建新的
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            # 根据状态调用相应的异步方法
            if progress_info.status == ProgressStatus.RUNNING:
                if progress_info.progress == 0:
                    # 阶段开始
                    self._run_async_method(loop, self.on_stage_start, progress_info)
                else:
                    # 进度更新
                    self._run_async_method(loop, self.on_progress_update, progress_info)
            elif progress_info.status == ProgressStatus.COMPLETED:
                # 阶段完成
                self._run_async_method(loop, self.on_stage_complete, progress_info)
            elif progress_info.status == ProgressStatus.FAILED:
                # 错误处理
                self._run_async_method(loop, self.on_error, progress_info)
            else:
                # 默认情况，调用进度更新
                self._run_async_method(loop, self.on_progress_update, progress_info)
                
        except Exception as e:
            # 使用子类的logger，如果没有则使用默认logger
            logger = getattr(self, 'logger', logging.getLogger(__name__))
            logger.error(f"进度回调处理失败: {e}")
    
    def _run_async_method(self, loop, method, progress_info: ProgressInfo):
        """运行异步方法的辅助函数"""
        if loop.is_running():
            # 如果循环正在运行，创建任务并确保它被调度执行
            task = asyncio.create_task(method(progress_info))
            # 不等待任务完成，但确保异常被处理
            task.add_done_callback(self._handle_task_exception)
        else:
            # 如果循环未运行，直接运行
            loop.run_until_complete(method(progress_info))
    
    def _handle_task_exception(self, task):
        """处理异步任务的异常"""
        try:
            task.result()  # 这会重新抛出任务中的异常（如果有的话）
        except Exception as e:
            logger = getattr(self, 'logger', logging.getLogger(__name__))
            logger.error(f"异步任务执行失败: {e}")


class DatabaseProgressCallback(ProgressCallback):
    """数据库进度回调实现 - 将进度信息持久化到数据库"""
    
    def __init__(self, task_id: int):
        """初始化数据库进度回调
        
        Args:
            task_id: 任务ID (整数类型)
        """
        self.task_id = task_id
        self.logger = logging.getLogger(__name__)
    
    async def on_progress_update(self, progress_info: ProgressInfo):
        """进度更新回调 - 更新数据库中的进度记录"""
        try:
            # 更新阶段进度
            task_service.update_stage_progress(
                task_id=self.task_id,
                stage=progress_info.stage.value,
                message=progress_info.message
            )
            
            # 更新大模型统计信息
            if progress_info.llm_stats:
                await self._update_llm_stats(progress_info.llm_stats)
            
            self.logger.debug(f"数据库进度更新完成: {self.task_id} - {progress_info.stage.value}")
            
        except Exception as e:
            self.logger.error(f"数据库进度更新失败: {e}")
    
    async def on_stage_start(self, progress_info: ProgressInfo):
        """阶段开始回调 - 在数据库中创建新的阶段记录"""
        try:
            # 使用新的服务层
            # 开始阶段，自动将任务状态设置为运行中
            task_service.start_stage(
                task_id=self.task_id,
                stage=progress_info.stage.value,
                message=progress_info.message
            )
            
            self.logger.info(f"数据库阶段开始记录完成: {self.task_id} - {progress_info.stage.value}")
            
        except Exception as e:
            self.logger.error(f"数据库阶段开始记录失败: {e}")
    
    async def on_stage_complete(self, progress_info: ProgressInfo):
        """阶段完成回调 - 标记数据库中的阶段为完成"""
        try:
            # 完成阶段
            task_service.complete_stage(
                task_id=self.task_id,
                stage=progress_info.stage.value,
                message=progress_info.message
            )
            
            # 更新大模型统计信息
            if progress_info.llm_stats:
                await self._update_llm_stats(progress_info.llm_stats)
            
            self.logger.info(f"数据库阶段完成记录完成: {self.task_id} - {progress_info.stage.value}")
            
        except Exception as e:
            self.logger.error(f"数据库阶段完成记录失败: {e}")
    
    async def on_error(self, progress_info: ProgressInfo):
        """错误回调 - 在数据库中记录错误信息"""
        try:
            # 使用统一的事务方法同时更新进度和任务状态
            task_service.fail_stage_with_task_status(
                task_id=self.task_id,
                stage=progress_info.stage.value,
                error_message=progress_info.error or progress_info.message,
                task_status=TaskStatus.FAILED.value
            )
            
            self.logger.error(f"数据库错误记录完成: {self.task_id} - {progress_info.error}")
            
        except Exception as e:
            self.logger.error(f"数据库错误记录失败: {e}")
    
    async def _update_llm_stats(self, llm_stats: dict):
        """更新大模型统计信息
        
        Args:
            llm_stats: 大模型统计数据
        """
        try:
            # 记录API调用统计
            llm_stats_service.record_api_call(
                task_id=self.task_id,
                model_name=llm_stats.get('model_name', 'unknown'),
                prompt_tokens=llm_stats.get('total_input_tokens', 0),
                completion_tokens=llm_stats.get('total_output_tokens', 0),
                cost=llm_stats.get('total_cost', 0.0)
            )
            
        except Exception as e:
            self.logger.error(f"更新LLM统计信息失败: {e}")


async def notify_callbacks(callbacks, method_name: str, progress_info: ProgressInfo):
    """通知所有回调的工具函数"""
    logger = logging.getLogger(__name__)
    
    for callback in callbacks:
        try:
            method = getattr(callback, method_name)
            if asyncio.iscoroutinefunction(method):
                await method(progress_info)
            else:
                # 如果不是协程函数，在线程池中执行
                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor() as executor:
                    await loop.run_in_executor(executor, method, progress_info)
        except Exception as e:
            logger.error(f"回调通知失败 {method_name}: {e}")