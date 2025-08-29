"""
进度管理器

包含ProgressManager类，负责管理多个任务的进度跟踪器
"""

import logging
import time
from dataclasses import asdict
from typing import Dict, List, Optional, Any

# 导入枚举定义
from ..enums import ProgressStage, ProgressStatus

# 导入数据模型
from .models import ProgressInfo
from .callbacks import ProgressCallback, DatabaseProgressCallback
from .websocket import WebSocketManager, WebSocketProgressCallback
from .tracker import ProgressTracker

# 导入大模型统计管理器
from ..llm_stats import llm_stats_manager


class ProgressManager:
    """进度管理器 - 管理多个任务的进度跟踪"""
    
    def __init__(self):
        self.trackers: Dict[int, ProgressTracker] = {}
        self.logger = logging.getLogger(__name__)
    
    def create_tracker(self, task_id: int,
                      enable_database: bool = True, 
                      auto_detect_websocket: bool = True,
                      enable_llm_stats: bool = True) -> ProgressTracker:
        """创建新的进度跟踪器
        
        Args:
            task_id: 任务ID（必选参数）
            enable_database: 是否启用数据库回调（默认启用）
            auto_detect_websocket: 是否自动检测Web环境并启用WebSocket回调（默认启用）
            enable_llm_stats: 是否启用LLM统计管理器（默认启用）
        """
        # 自动创建回调列表
        callbacks = []
        
        # 自动添加数据库回调
        if enable_database:
            db_callback = DatabaseProgressCallback(task_id)
            callbacks.append(db_callback)
            self.logger.info(f"为任务 {task_id} 自动添加数据库回调")
        
        # 自动检测Web环境并添加WebSocket回调
        if auto_detect_websocket:
            is_web_environment = self._is_web_environment()
            if is_web_environment:
                # 使用全局websocket_manager
                websocket_manager = globals().get('websocket_manager')
                
                if websocket_manager:
                    ws_callback = WebSocketProgressCallback(websocket_manager, task_id)
                    callbacks.append(ws_callback)
                    self.logger.info(f"为任务 {task_id} 自动添加WebSocket回调（检测到Web环境）")
                else:
                    self.logger.warning(f"Web环境检测到但未找到websocket_manager，跳过WebSocket回调")
            else:
                self.logger.info(f"非Web环境，跳过WebSocket回调创建")
        
        # 创建进度跟踪器
        tracker = ProgressTracker(task_id, callbacks)
        
        # 统一处理LLM统计管理器的创建
        if enable_llm_stats:
            self._setup_llm_stats_manager(tracker, task_id)
        
        # 注册并返回跟踪器
        self.trackers[task_id] = tracker
        self.logger.info(f"创建进度跟踪器: {task_id}, 自动创建回调数量: {len(callbacks)}")
        return tracker
    
    def create_database_tracker(self, task_id: int) -> ProgressTracker:
        """创建带有数据库回调的进度跟踪器（便捷方法）"""
        return self.create_tracker(task_id=task_id, enable_database=True, auto_detect_websocket=False)
    
    def create_websocket_tracker(self, task_id: int) -> ProgressTracker:
        """创建带有WebSocket回调的进度跟踪器（便捷方法）"""
        return self.create_tracker(task_id=task_id, enable_database=True, auto_detect_websocket=True)
    
    def create_full_tracker(self, task_id: int) -> ProgressTracker:
        """创建带有数据库和WebSocket回调的完整进度跟踪器（便捷方法）"""
        return self.create_tracker(task_id=task_id, enable_database=True, auto_detect_websocket=True)
    
    def get_tracker(self, task_id: int) -> Optional[ProgressTracker]:
        """获取进度跟踪器"""
        return self.trackers.get(task_id)
    
    def remove_tracker(self, task_id: int):
        """移除进度跟踪器"""
        if task_id in self.trackers:
            # 完成大模型统计
            llm_stats_manager.finish_task(task_id)
            del self.trackers[task_id]
            self.logger.info(f"移除进度跟踪器: {task_id}")
    
    def get_all_task_ids(self) -> List[int]:
        """获取所有任务ID"""
        return list(self.trackers.keys())
    
    def get_task_progress(self, task_id: int) -> Optional[Dict[str, Any]]:
        """获取任务进度信息"""
        tracker = self.get_tracker(task_id)
        if not tracker:
            return None
        
        # 获取大模型统计信息
        llm_stats = llm_stats_manager.get_task_summary(task_id)
        
        return {
            "task_id": task_id,
            "current_stage": tracker.current_stage.value if tracker.current_stage else None,
            "overall_progress": tracker.get_overall_progress(),
            "total_documents": tracker.total_documents,
            "completed_documents": tracker.completed_documents,
            "llm_stats": llm_stats,  # 添加大模型统计信息
            "stages": {
                stage.value: {
                    "progress": tracker.stage_progress[stage],
                    "status": tracker.stage_status[stage].value,
                    "config": asdict(tracker.stage_configs[stage])
                }
                for stage in ProgressStage
            }
        }
    
    def get_task_llm_stats(self, task_id: int) -> Optional[Dict[str, Any]]:
        """获取任务的大模型调用统计信息"""
        return llm_stats_manager.get_task_summary(task_id)
    
    def get_task_llm_details(self, task_id: int) -> Optional[Dict[str, Any]]:
        """获取任务的详细大模型调用信息"""
        task_stats = llm_stats_manager.get_task_stats(task_id)
        return task_stats.to_dict() if task_stats else None
    
    def get_progress(self, task_id: int) -> Optional[ProgressInfo]:
        """获取任务进度信息 - 返回ProgressInfo对象"""
        tracker = self.get_tracker(task_id)
        if not tracker:
            return None
        
        # 获取大模型统计信息
        llm_stats = llm_stats_manager.get_task_summary(task_id)
        
        # 创建ProgressInfo对象
        progress_info = ProgressInfo(
            task_id=task_id,
            stage=tracker.current_stage or ProgressStage.CLONE,  # 默认阶段
            status=ProgressStatus.RUNNING if tracker.current_stage else ProgressStatus.PENDING,
            progress=tracker.get_overall_progress(),
            message=f"当前阶段: {tracker.current_stage.value if tracker.current_stage else '未开始'}",
            details={
                "total_documents": tracker.total_documents,
                "completed_documents": tracker.completed_documents,
                "estimated_remaining": self._estimate_remaining_time(tracker),
            },
            llm_stats=llm_stats
        )
        
        return progress_info
    
    def _estimate_remaining_time(self, tracker: ProgressTracker) -> int:
        """估算剩余时间（秒）"""
        import time
        
        current_time = time.time()
        elapsed_time = current_time - tracker.start_time
        overall_progress = tracker.get_overall_progress()
        
        if overall_progress <= 0:
            # 如果还没有进度，基于阶段配置估算
            total_estimated = sum(config.estimated_duration for config in tracker.stage_configs.values())
            return total_estimated
        
        # 基于当前进度估算剩余时间
        estimated_total_time = elapsed_time / (overall_progress / 100.0)
        remaining_time = max(0, estimated_total_time - elapsed_time)
        
        return int(remaining_time)
    
    def _setup_llm_stats_manager(self, tracker: ProgressTracker, task_id: int):
        """统一设置LLM统计管理器的辅助方法"""
        try:
            # 动态导入以避免循环依赖
            from ..llm_stats import LLMStatsManager
            llm_stats_manager = LLMStatsManager()
            llm_stats_manager.start_task(task_id)
            tracker.llm_stats_manager = llm_stats_manager
            self.logger.info(f"为任务 {task_id} 自动创建LLM统计管理器")
        except ImportError as e:
            self.logger.warning(f"无法导入LLM统计管理器: {e}")
        except Exception as e:
            self.logger.error(f"创建LLM统计管理器失败: {e}")
    
    def _is_web_environment(self) -> bool:
        """
        检测当前线程是否为Flask Web请求线程

        优化后的检测方法：
        1. 优先检测Flask请求上下文（最准确的方法）
        2. 检测Flask应用上下文
        3. 检测环境变量
        4. 检测调用栈中的web相关模块

        Returns:
            bool: True表示在web环境中，False表示在非web环境中
        """
        try:
            # 方法1: 检测Flask请求上下文（最精确的方法）
            from flask import request
            # 尝试访问请求对象，如果存在则说明是Web请求线程
            if request is not None:
                return True
        except ImportError:
            # Flask未安装
            pass
        except RuntimeError:
            # 如果抛出 RuntimeError，说明没有请求上下文，不是Web请求线程
            pass
        # 默认返回False（非web环境）
        return False
