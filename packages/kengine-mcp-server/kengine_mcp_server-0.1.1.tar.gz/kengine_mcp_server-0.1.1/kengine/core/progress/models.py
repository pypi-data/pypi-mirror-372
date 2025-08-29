"""
进度系统核心数据模型

包含进度信息和阶段配置的数据类定义
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, Optional

# 导入大模型统计模块
from ..llm_stats import llm_stats_manager

# 导入统一的枚举定义
from ..enums import ProgressStage, ProgressStatus


@dataclass
class ProgressInfo:
    """进度信息数据类"""
    task_id: int
    stage: ProgressStage
    status: ProgressStatus
    progress: float  # 0.0 - 1.0
    message: str
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: Optional[datetime] = None
    llm_stats: Optional[Dict[str, Any]] = None  # 大模型调用统计信息
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        
        # 自动获取大模型统计信息
        if self.llm_stats is None:
            task_stats = llm_stats_manager.get_task_stats(self.task_id)
            if task_stats:
                self.llm_stats = task_stats.get_summary()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于JSON序列化"""
        data = asdict(self)
        data['stage'] = self.stage.value
        data['status'] = self.status.value
        data['timestamp'] = self.timestamp.isoformat() if self.timestamp else None
        return data
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False)


@dataclass
class StageConfig:
    """阶段配置"""
    stage: ProgressStage
    description: str
    weight: float = 1.0  # 在总进度中的权重
    name: str = ""
    estimated_duration: int = 60  # 预估时长（秒）
    
    def __post_init__(self):
        if not self.name:
            self.name = self.stage.value