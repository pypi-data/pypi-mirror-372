"""
进度回调系统

重构后的进度回调系统，按职责拆分为多个模块：
- models: 核心数据类
- callbacks: 回调接口和实现
- websocket: WebSocket管理
- tracker: 进度跟踪器
- manager: 进度管理器

提供与原模块兼容的接口
"""

import time
from typing import Optional, List, Dict, Any

# 导入所有核心类
from .models import ProgressInfo, StageConfig
from .callbacks import ProgressCallback, DatabaseProgressCallback, notify_callbacks
from .websocket import WebSocketManager, WebSocketProgressCallback
from .tracker import ProgressTracker
from .manager import ProgressManager

# 创建全局实例
progress_manager = ProgressManager()
websocket_manager = WebSocketManager()


# 便捷函数 - 供其他模块使用，保持与原模块的兼容性
def create_progress_tracker(task_id: int,
                          enable_database: bool = True,
                          auto_detect_websocket: bool = False) -> ProgressTracker:
    """创建进度跟踪器的便捷函数
    
    Args:
        task_id: 任务ID（必选参数）
        enable_database: 是否启用数据库回调（默认启用）
        auto_detect_websocket: 是否自动检测Web环境并启用WebSocket回调（默认禁用）
    
    Returns:
        ProgressTracker: 配置好的进度跟踪器实例
    
    Example:
        # 创建带数据库回调的跟踪器
        tracker = create_progress_tracker(task_id=123)
        
        # 创建带数据库和WebSocket回调的跟踪器
        tracker = create_progress_tracker(task_id=123, auto_detect_websocket=True)
    """
    return progress_manager.create_tracker(
        task_id=task_id,
        enable_database=enable_database,
        auto_detect_websocket=auto_detect_websocket
    )


def create_database_progress_tracker(task_id: int) -> ProgressTracker:
    """创建仅带数据库回调的进度跟踪器
    
    Args:
        task_id: 任务ID（必选参数）
    
    Returns:
        ProgressTracker: 配置好的进度跟踪器实例
    """
    return progress_manager.create_database_tracker(task_id)


def create_full_progress_tracker(task_id: int) -> ProgressTracker:
    """创建带有完整回调功能的进度跟踪器（数据库 + WebSocket）
    
    Args:
        task_id: 任务ID（必选参数）
    
    Returns:
        ProgressTracker: 配置好的进度跟踪器实例
    """
    return progress_manager.create_full_tracker(task_id)


def get_progress_tracker(task_id: int) -> Optional[ProgressTracker]:
    """获取已存在的进度跟踪器
    
    Args:
        task_id: 任务ID
    
    Returns:
        Optional[ProgressTracker]: 进度跟踪器实例，如果不存在则返回None
    """
    return progress_manager.get_tracker(task_id)


def remove_progress_tracker(task_id: int):
    """移除进度跟踪器
    
    Args:
        task_id: 任务ID
    """
    progress_manager.remove_tracker(task_id)


def get_task_progress_info(task_id: int) -> Optional[Dict[str, Any]]:
    """获取任务的详细进度信息
    
    Args:
        task_id: 任务ID
    
    Returns:
        Optional[Dict[str, Any]]: 包含进度、阶段、LLM统计等信息的字典
    """
    return progress_manager.get_task_progress(task_id)


# 导出主要类和函数，保持与原模块的兼容性
__all__ = [
    # 核心类
    'ProgressInfo',
    'StageConfig',
    'ProgressCallback',
    'DatabaseProgressCallback',
    'WebSocketProgressCallback',
    'ProgressTracker',
    'ProgressManager',
    'WebSocketManager',
    
    # 全局实例
    'progress_manager',
    'websocket_manager',
    
    # 便捷函数
    'create_progress_tracker',
    'create_database_progress_tracker',
    'create_full_progress_tracker',
    'get_progress_tracker',
    'remove_progress_tracker',
    'get_task_progress_info',
    'notify_callbacks',
]