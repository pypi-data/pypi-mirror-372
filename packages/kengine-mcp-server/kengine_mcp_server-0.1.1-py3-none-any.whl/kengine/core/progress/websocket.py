"""
WebSocket进度推送系统

包含WebSocket连接管理和WebSocket进度回调实现
"""

import json
import logging
from typing import Dict, Any, List, Optional

# 导入回调基类
from .callbacks import ProgressCallback
from .models import ProgressInfo


class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.connections: Dict[int, List[Any]] = {}  # task_id -> [websocket_connections]
        self.logger = logging.getLogger(__name__)
    
    def add_connection(self, task_id: int, websocket):
        """添加WebSocket连接"""
        if task_id not in self.connections:
            self.connections[task_id] = []
        self.connections[task_id].append(websocket)
        self.logger.info(f"添加WebSocket连接到任务 {task_id}, 当前连接数: {len(self.connections[task_id])}")
    
    def remove_connection(self, task_id: int, websocket):
        """移除WebSocket连接"""
        if task_id in self.connections and websocket in self.connections[task_id]:
            self.connections[task_id].remove(websocket)
            if not self.connections[task_id]:
                del self.connections[task_id]
            self.logger.info(f"移除WebSocket连接从任务 {task_id}")
    
    async def broadcast_to_task(self, task_id: int, message: Dict[str, Any]):
        """向指定任务的所有连接广播消息"""
        if task_id not in self.connections:
            return
        
        # 移除已断开的连接
        active_connections = []
        for websocket in self.connections[task_id]:
            try:
                await websocket.send(json.dumps(message, ensure_ascii=False))
                active_connections.append(websocket)
            except Exception as e:
                self.logger.warning(f"WebSocket连接已断开: {e}")
        
        # 更新活跃连接列表
        if active_connections:
            self.connections[task_id] = active_connections
        else:
            del self.connections[task_id]
    
    def get_connection_count(self, task_id: int) -> int:
        """获取指定任务的连接数"""
        return len(self.connections.get(task_id, []))
    
    def get_all_task_ids(self) -> List[int]:
        """获取所有有连接的任务ID"""
        return list(self.connections.keys())


class WebSocketProgressCallback(ProgressCallback):
    """WebSocket进度回调实现"""
    
    def __init__(self, websocket_manager: WebSocketManager, task_id: int):
        self.websocket_manager = websocket_manager
        self.task_id = task_id
        self.logger = logging.getLogger(__name__)
    async def on_progress_update(self, progress_info: ProgressInfo):
        """发送进度更新到WebSocket客户端"""
        try:
            await self.websocket_manager.broadcast_to_task(
                self.task_id, 
                {
                    "type": "progress_update",
                    "data": progress_info.to_dict()
                }
            )
        except Exception as e:
            self.logger.error(f"WebSocket进度更新失败: {e}")
    
    async def on_stage_start(self, progress_info: ProgressInfo):
        """发送阶段开始通知到WebSocket客户端"""
        try:
            await self.websocket_manager.broadcast_to_task(
                self.task_id,
                {
                    "type": "stage_start",
                    "data": progress_info.to_dict()
                }
            )
        except Exception as e:
            self.logger.error(f"WebSocket阶段开始通知失败: {e}")
    
    async def on_stage_complete(self, progress_info: ProgressInfo):
        """发送阶段完成通知到WebSocket客户端"""
        try:
            await self.websocket_manager.broadcast_to_task(
                self.task_id,
                {
                    "type": "stage_complete",
                    "data": progress_info.to_dict()
                }
            )
        except Exception as e:
            self.logger.error(f"WebSocket阶段完成通知失败: {e}")
    
    async def on_error(self, progress_info: ProgressInfo):
        """发送错误通知到WebSocket客户端"""
        try:
            await self.websocket_manager.broadcast_to_task(
                self.task_id,
                {
                    "type": "error",
                    "data": progress_info.to_dict()
                }
            )
        except Exception as e:
            self.logger.error(f"WebSocket错误通知失败: {e}")