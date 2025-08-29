"""
大模型调用统计模块

提供大模型调用的详细统计信息，包括调用次数、响应时间、token使用量等
支持不同阶段的大模型调用统计和性能分析
"""

import time
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


# 导入统一的枚举定义
from .enums import LLMCallType


@dataclass
class LLMCallRecord:
    """单次大模型调用记录"""
    call_id: str
    call_type: LLMCallType
    model_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[int] = None
    
    # Token统计
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    
    # 请求和响应信息
    prompt_length: int = 0
    response_length: int = 0
    
    # 状态信息
    success: bool = True
    error_message: Optional[str] = None
    
    # 额外信息
    stage: Optional[str] = None
    document_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def finish_call(self, success: bool = True, error_message: Optional[str] = None):
        """完成调用记录"""
        self.end_time = datetime.now()
        self.duration_ms = int((self.end_time - self.start_time).total_seconds() * 1000)
        self.success = success
        self.error_message = error_message
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['call_type'] = self.call_type.value
        data['start_time'] = self.start_time.isoformat() if self.start_time else None
        data['end_time'] = self.end_time.isoformat() if self.end_time else None
        return data


@dataclass
class LLMStageStats:
    """阶段大模型调用统计"""
    stage_name: str
    call_type: LLMCallType
    
    # 调用统计
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    
    # 时间统计
    total_duration_ms: int = 0
    avg_duration_ms: float = 0.0
    min_duration_ms: Optional[int] = None
    max_duration_ms: Optional[int] = None
    
    # Token统计
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0
    avg_tokens_per_call: float = 0.0
    
    # 成本估算（基于token数量）
    estimated_cost_usd: float = 0.0
    
    def update_from_record(self, record: LLMCallRecord):
        """从调用记录更新统计"""
        self.total_calls += 1
        
        if record.success:
            self.successful_calls += 1
        else:
            self.failed_calls += 1
        
        if record.duration_ms:
            self.total_duration_ms += record.duration_ms
            self.avg_duration_ms = self.total_duration_ms / self.total_calls
            
            if self.min_duration_ms is None or record.duration_ms < self.min_duration_ms:
                self.min_duration_ms = record.duration_ms
            if self.max_duration_ms is None or record.duration_ms > self.max_duration_ms:
                self.max_duration_ms = record.duration_ms
        
        # 更新token统计
        self.total_prompt_tokens += record.prompt_tokens
        self.total_completion_tokens += record.completion_tokens
        self.total_tokens += record.total_tokens
        self.avg_tokens_per_call = self.total_tokens / self.total_calls if self.total_calls > 0 else 0
        
        # 简单的成本估算（GPT-4的大概价格）
        self.estimated_cost_usd = (self.total_prompt_tokens * 0.00003 + 
                                 self.total_completion_tokens * 0.00006)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['call_type'] = self.call_type.value
        return data


@dataclass
class LLMTaskStats:
    """任务级别的大模型调用统计"""
    task_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    
    # 总体统计
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_duration_ms: int = 0
    total_tokens: int = 0
    estimated_total_cost_usd: float = 0.0
    
    # 各阶段统计
    stage_stats: Dict[str, LLMStageStats] = field(default_factory=dict)
    
    # 调用记录
    call_records: List[LLMCallRecord] = field(default_factory=list)
    
    def add_call_record(self, record: LLMCallRecord):
        """添加调用记录"""
        self.call_records.append(record)
        
        # 更新总体统计
        self.total_calls += 1
        if record.success:
            self.successful_calls += 1
        else:
            self.failed_calls += 1
        
        if record.duration_ms:
            self.total_duration_ms += record.duration_ms
        
        self.total_tokens += record.total_tokens
        
        # 更新阶段统计
        stage_key = f"{record.stage}_{record.call_type.value}" if record.stage else record.call_type.value
        if stage_key not in self.stage_stats:
            self.stage_stats[stage_key] = LLMStageStats(
                stage_name=record.stage or "unknown",
                call_type=record.call_type
            )
        
        self.stage_stats[stage_key].update_from_record(record)
        
        # 更新总成本
        self.estimated_total_cost_usd = sum(stats.estimated_cost_usd for stats in self.stage_stats.values())
    
    def finish_task(self):
        """完成任务统计"""
        self.end_time = datetime.now()
    
    def get_summary(self) -> Dict[str, Any]:
        """获取统计摘要"""
        return {
            "task_id": self.task_id,
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "success_rate": self.successful_calls / self.total_calls if self.total_calls > 0 else 0,
            "total_duration_ms": self.total_duration_ms,
            "avg_duration_ms": self.total_duration_ms / self.total_calls if self.total_calls > 0 else 0,
            "total_tokens": self.total_tokens,
            "avg_tokens_per_call": self.total_tokens / self.total_calls if self.total_calls > 0 else 0,
            "estimated_total_cost_usd": self.estimated_total_cost_usd,
            "stage_count": len(self.stage_stats),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat() if self.start_time else None
        data['end_time'] = self.end_time.isoformat() if self.end_time else None
        data['stage_stats'] = {k: v.to_dict() for k, v in self.stage_stats.items()}
        data['call_records'] = [record.to_dict() for record in self.call_records]
        return data


class LLMStatsManager:
    """大模型调用统计管理器"""
    
    def __init__(self):
        self.task_stats: Dict[int, LLMTaskStats] = {}
        self.active_calls: Dict[str, LLMCallRecord] = {}
        self.logger = logging.getLogger(__name__)
    
    def start_task(self, task_id: int) -> LLMTaskStats:
        """开始任务统计"""
        task_stats = LLMTaskStats(
            task_id=task_id,
            start_time=datetime.now()
        )
        self.task_stats[task_id] = task_stats
        self.logger.info(f"开始大模型调用统计 - 任务ID: {task_id}")
        return task_stats
    
    def start_call(self, task_id: int, call_type: LLMCallType, model_name: str, 
                   stage: Optional[str] = None, document_name: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """开始大模型调用"""
        import uuid
        call_id = str(uuid.uuid4())
        
        record = LLMCallRecord(
            call_id=call_id,
            call_type=call_type,
            model_name=model_name,
            start_time=datetime.now(),
            stage=stage,
            document_name=document_name,
            metadata=metadata or {}
        )
        
        self.active_calls[call_id] = record
        self.logger.debug(f"开始大模型调用 - 调用ID: {call_id}, 类型: {call_type.value}")
        return call_id
    
    def finish_call(self, call_id: str, success: bool = True, error_message: Optional[str] = None,
                    prompt_tokens: int = 0, completion_tokens: int = 0, total_tokens: int = 0,
                    prompt_length: int = 0, response_length: int = 0):
        """完成大模型调用"""
        if call_id not in self.active_calls:
            self.logger.warning(f"未找到活跃的调用记录: {call_id}")
            return
        
        record = self.active_calls.pop(call_id)
        record.finish_call(success, error_message)
        
        # 更新token和长度信息
        record.prompt_tokens = prompt_tokens
        record.completion_tokens = completion_tokens
        record.total_tokens = total_tokens or (prompt_tokens + completion_tokens)
        record.prompt_length = prompt_length
        record.response_length = response_length
        
        # 查找对应的任务统计
        task_stats = None
        for stats in self.task_stats.values():
            if any(r.call_id == call_id for r in stats.call_records):
                task_stats = stats
                break
        
        # 如果没有找到对应的任务，尝试从最近的任务中添加
        if not task_stats and self.task_stats:
            task_stats = list(self.task_stats.values())[-1]
        
        if task_stats:
            task_stats.add_call_record(record)
        
        self.logger.debug(f"完成大模型调用 - 调用ID: {call_id}, 成功: {success}, 耗时: {record.duration_ms}ms")
    
    def finish_task(self, task_id: int):
        """完成任务统计"""
        if task_id in self.task_stats:
            self.task_stats[task_id].finish_task()
            self.logger.info(f"完成大模型调用统计 - 任务ID: {task_id}")
    
    def get_task_stats(self, task_id: int) -> Optional[LLMTaskStats]:
        """获取任务统计"""
        return self.task_stats.get(task_id)
    
    def get_task_summary(self, task_id: int) -> Optional[Dict[str, Any]]:
        """获取任务统计摘要"""
        task_stats = self.get_task_stats(task_id)
        return task_stats.get_summary() if task_stats else None
    
    def remove_task_stats(self, task_id: int):
        """移除任务统计"""
        if task_id in self.task_stats:
            del self.task_stats[task_id]
            self.logger.info(f"移除大模型调用统计 - 任务ID: {task_id}")


# 全局实例
llm_stats_manager = LLMStatsManager()