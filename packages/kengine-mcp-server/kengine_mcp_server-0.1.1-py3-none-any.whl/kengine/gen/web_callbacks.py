"""
Web相关的进度回调实现
包含SSE和WebSocket进度回调功能
"""

import json
import logging
import threading
from typing import Any, Dict, Optional, List

from .models import ProgressUpdate
from ..core.enums import ProgressType
from ..core.progress import ProgressCallback, ProgressInfo, websocket_manager

logger = logging.getLogger(__name__)


class SSEProgressCallback(ProgressCallback):
    """Server-Sent Events进度回调"""
    
    def __init__(self, task_id: int):
        self.task_id = task_id
        self.clients = set()  # 连接的客户端
        self._lock = threading.Lock()
    
    def add_client(self, client_id: str):
        """添加客户端"""
        with self._lock:
            self.clients.add(client_id)
    
    def remove_client(self, client_id: str):
        """移除客户端"""
        with self._lock:
            self.clients.discard(client_id)
    
    async def on_progress_update(self, progress_info: ProgressInfo):
        """进度更新回调"""
        try:
            # 确定更新类型
            if progress_info.error:
                update_type = ProgressType.ERROR
            elif progress_info.progress >= 1.0:
                update_type = ProgressType.COMPLETE
            elif progress_info.progress == 0.0:
                update_type = ProgressType.STAGE_START
            else:
                update_type = ProgressType.STAGE_PROGRESS
            
            # 创建进度更新
            progress_update = ProgressUpdate.from_progress_info(
                progress_info, self.task_id, update_type
            )
            
            # 通知所有连接的客户端
            await self._broadcast_update(progress_update)
            
        except Exception as e:
            logger.error(f"进度更新回调失败: {e}")
    
    async def on_stage_start(self, progress_info: ProgressInfo):
        """阶段开始回调"""
        await self.on_progress_update(progress_info)
    
    async def on_stage_complete(self, progress_info: ProgressInfo):
        """阶段完成回调"""
        await self.on_progress_update(progress_info)
    
    async def on_error(self, progress_info: ProgressInfo):
        """错误回调"""
        await self.on_progress_update(progress_info)
    
    async def _broadcast_update(self, progress_update: ProgressUpdate):
        """广播更新到所有客户端"""
        try:
            # 通过WebSocket管理器广播更新
            message = {
                "type": "progress_update",
                "task_id": self.task_id,
                "data": progress_update.to_dict()
            }
            
            # 异步发送消息到WebSocket客户端
            await websocket_manager.broadcast_to_task(self.task_id, message)
                
        except Exception as e:
            logger.error(f"广播进度更新失败: {e}")


class WebProgressCallback(ProgressCallback):
    """Web环境通用进度回调 - 同时支持SSE和WebSocket"""
    
    def __init__(self, task_id: int, enable_sse: bool = True, enable_websocket: bool = True):
        self.task_id = task_id
        self.enable_sse = enable_sse
        self.enable_websocket = enable_websocket
        self.logger = logging.getLogger(__name__)
        
        # SSE客户端管理
        self.sse_clients = set()
        self._lock = threading.Lock()
    
    def add_sse_client(self, client_id: str):
        """添加SSE客户端"""
        if self.enable_sse:
            with self._lock:
                self.sse_clients.add(client_id)
    
    def remove_sse_client(self, client_id: str):
        """移除SSE客户端"""
        if self.enable_sse:
            with self._lock:
                self.sse_clients.discard(client_id)
    
    async def on_progress_update(self, progress_info: ProgressInfo):
        """进度更新回调"""
        try:
            # WebSocket广播
            if self.enable_websocket:
                await websocket_manager.broadcast_to_task(
                    self.task_id,
                    {
                        "type": "progress_update",
                        "data": progress_info.to_dict()
                    }
                )
            
            # SSE广播（如果需要的话，可以在这里添加SSE特定的逻辑）
            if self.enable_sse and self.sse_clients:
                # 创建SSE格式的进度更新
                update_type = self._determine_update_type(progress_info)
                progress_update = ProgressUpdate.from_progress_info(
                    progress_info, self.task_id, update_type
                )
                
                # 这里可以添加SSE特定的广播逻辑
                self.logger.debug(f"SSE广播进度更新到 {len(self.sse_clients)} 个客户端")
                
        except Exception as e:
            self.logger.error(f"Web进度更新失败: {e}")
    
    async def on_stage_start(self, progress_info: ProgressInfo):
        """阶段开始回调"""
        try:
            if self.enable_websocket:
                await websocket_manager.broadcast_to_task(
                    self.task_id,
                    {
                        "type": "stage_start",
                        "data": progress_info.to_dict()
                    }
                )
        except Exception as e:
            self.logger.error(f"Web阶段开始通知失败: {e}")
    
    async def on_stage_complete(self, progress_info: ProgressInfo):
        """阶段完成回调"""
        try:
            if self.enable_websocket:
                await websocket_manager.broadcast_to_task(
                    self.task_id,
                    {
                        "type": "stage_complete",
                        "data": progress_info.to_dict()
                    }
                )
        except Exception as e:
            self.logger.error(f"Web阶段完成通知失败: {e}")
    
    async def on_error(self, progress_info: ProgressInfo):
        """错误回调"""
        try:
            if self.enable_websocket:
                await websocket_manager.broadcast_to_task(
                    self.task_id,
                    {
                        "type": "error",
                        "data": progress_info.to_dict()
                    }
                )
        except Exception as e:
            self.logger.error(f"Web错误通知失败: {e}")
    
    def _determine_update_type(self, progress_info: ProgressInfo) -> ProgressType:
        """确定更新类型"""
        if progress_info.error:
            return ProgressType.ERROR
        elif progress_info.progress >= 1.0:
            return ProgressType.COMPLETE
        elif progress_info.progress == 0.0:
            return ProgressType.STAGE_START
        else:
            return ProgressType.STAGE_PROGRESS