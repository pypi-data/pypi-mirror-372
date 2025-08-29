"""
文档生成服务的数据模型
"""

import json
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List
from enum import Enum

from ..core.enums import ExecuteStep, ProgressType


@dataclass
class DocumentGenerationRequest:
    """文档生成请求"""
    repo_group: str
    repo_name: str
    branch: str = "master"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentGenerationRequest':
        """从字典创建请求对象"""
        return cls(
            repo_group=data['repo_group'],
            repo_name=data['repo_name'],
            branch=data.get('branch', 'master')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class ProgressUpdate:
    """进度更新数据"""
    type: ProgressType
    task_id: int
    stage: Optional[str] = None
    progress: float = 0.0
    message: str = ""
    overall_progress: float = 0.0
    current_stage: Optional[str] = None
    completed_documents: int = 0
    total_documents: int = 0
    estimated_remaining: Optional[int] = None
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    llm_stats: Optional[Dict[str, Any]] = None
    
    def to_json_string(self) -> str:
        """转换为JSON字符串"""
        data = asdict(self)
        # 处理枚举类型
        data['type'] = self.type.value
        return json.dumps(data, ensure_ascii=False)
    
    @classmethod
    def from_progress_info(cls, progress_info, task_id: int, update_type: ProgressType) -> 'ProgressUpdate':
        """从ProgressInfo创建ProgressUpdate"""
        return cls(
            type=update_type,
            task_id=task_id,
            stage=progress_info.stage.value if progress_info.stage else None,
            progress=progress_info.stage_progress,
            message=progress_info.message,
            overall_progress=progress_info.overall_progress,
            current_stage=progress_info.stage.value if progress_info.stage else None,
            completed_documents=progress_info.completed_documents,
            total_documents=progress_info.total_documents,
            estimated_remaining=progress_info.estimated_remaining,
            error=progress_info.error,
            data=progress_info.extra_data
        )


@dataclass
class TaskInfo:
    """任务信息"""
    task_id: int
    status: str
    repo_group: str
    repo_name: str
    created_at: str
    overall_progress: float = 0.0
    current_stage: Optional[str] = None
    completed_documents: int = 0
    total_documents: int = 0
    error: Optional[str] = None
    output_path: Optional[str] = None
    llm_stats: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)