"""
进度跟踪器安全操作工具类

本模块提供了统一的进度跟踪器安全操作方法，用于处理可能为 None 的 tracker 对象。
将原本分散在各个服务类中的 tracker 操作方法提取为可复用的工具类。

重构历史:
- 2024: 从 KnowledgeService 和 DocumentService 中提取 tracker 安全操作方法
- 统一了两个服务中类似的 tracker 操作逻辑
- 提供了更好的错误处理和日志记录
"""

import asyncio
import logging
from typing import Optional, Any

from ..progress.tracker import ProgressTracker
from ..enums import ProgressStage, ProgressStatus

logger = logging.getLogger(__name__)


class SafeTrackerOperations:
    """
    进度跟踪器安全操作工具类
    
    提供统一的 tracker 安全操作方法，处理 tracker 可能为 None 的情况。
    所有方法都会进行空值检查，避免在 tracker 为 None 时出现异常。
    """
    
    @staticmethod
    def safe_tracker_start_stage(
        tracker: Optional[ProgressTracker], 
        stage: ProgressStage, 
        message: str
    ) -> None:
        """
        安全地开始进度跟踪阶段
        
        Args:
            tracker: 进度跟踪器实例，可能为 None
            stage: 进度阶段
            message: 阶段描述信息
        """
        if tracker:
            try:
                asyncio.run(tracker.start_stage(stage, message))
                logger.debug(f"Started progress stage: {stage.value} - {message}")
            except Exception as e:
                logger.error(f"Failed to start progress stage {stage.value}: {e}")
    
    @staticmethod
    def safe_tracker_complete_stage(
        tracker: Optional[ProgressTracker], 
        stage: ProgressStage, 
        message: str
    ) -> None:
        """
        安全地完成进度跟踪阶段
        
        Args:
            tracker: 进度跟踪器实例，可能为 None
            stage: 进度阶段
            message: 完成描述信息
        """
        if tracker:
            try:
                asyncio.run(tracker.complete_stage(stage, message))
                logger.debug(f"Completed progress stage: {stage.value} - {message}")
            except Exception as e:
                logger.error(f"Failed to complete progress stage {stage.value}: {e}")
    
    @staticmethod
    def safe_tracker_fail_stage(
        tracker: Optional[ProgressTracker], 
        stage: ProgressStage, 
        message: str
    ) -> None:
        """
        安全地标记进度跟踪阶段失败
        
        Args:
            tracker: 进度跟踪器实例，可能为 None
            stage: 进度阶段
            message: 失败描述信息
        """
        if tracker:
            try:
                asyncio.run(tracker.fail_stage(stage, message))
                logger.debug(f"Failed progress stage: {stage.value} - {message}")
            except Exception as e:
                logger.error(f"Failed to mark progress stage as failed {stage.value}: {e}")
    
    @staticmethod
    def safe_tracker_update_progress(
        tracker: Optional[ProgressTracker], 
        stage: ProgressStage, 
        current: int, 
        total: int, 
        message: str = ""
    ) -> None:
        """
        安全地更新进度跟踪器进度
        
        Args:
            tracker: 进度跟踪器实例，可能为 None
            stage: 进度阶段
            current: 当前进度
            total: 总进度
            message: 进度描述信息
        """
        if tracker:
            try:
                asyncio.run(tracker.update_progress(stage, current, total, message))
                logger.debug(f"Updated progress: {stage.value} - {current}/{total} - {message}")
            except Exception as e:
                logger.error(f"Failed to update progress for stage {stage.value}: {e}")
    
    @staticmethod
    def safe_tracker_report_error(
        tracker: Optional[ProgressTracker], 
        stage: ProgressStage, 
        error_message: str
    ) -> None:
        """
        安全地报告进度跟踪器错误
        
        Args:
            tracker: 进度跟踪器实例，可能为 None
            stage: 进度阶段
            error_message: 错误信息
        """
        if tracker:
            try:
                asyncio.run(tracker.report_error(stage, error_message))
                logger.debug(f"Reported error for stage: {stage.value} - {error_message}")
            except Exception as e:
                logger.error(f"Failed to report error for stage {stage.value}: {e}")
    
    @staticmethod
    def safe_tracker_set_document_count(
        tracker: Optional[ProgressTracker], 
        count: int
    ) -> None:
        """
        安全地设置文档数量
        
        Args:
            tracker: 进度跟踪器实例，可能为 None
            count: 文档数量
        """
        if tracker:
            try:
                asyncio.run(tracker.set_document_count(count))
                logger.debug(f"Set document count: {count}")
            except Exception as e:
                logger.error(f"Failed to set document count {count}: {e}")
    
    @staticmethod
    def safe_progress_manager_remove_tracker(
        progress_manager: Optional[Any], 
        tracker_id: str
    ) -> None:
        """
        安全地从进度管理器中移除跟踪器
        
        Args:
            progress_manager: 进度管理器实例，可能为 None
            tracker_id: 跟踪器ID
        """
        if progress_manager and tracker_id:
            try:
                asyncio.run(progress_manager.remove_tracker(tracker_id))
                logger.debug(f"Removed tracker: {tracker_id}")
            except Exception as e:
                logger.error(f"Failed to remove tracker {tracker_id}: {e}")

