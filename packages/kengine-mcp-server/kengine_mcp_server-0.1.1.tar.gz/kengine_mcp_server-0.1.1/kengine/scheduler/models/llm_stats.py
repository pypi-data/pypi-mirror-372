"""
大模型统计模型

定义大模型调用统计的数据模型，记录任务执行过程中的大模型使用情况
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, Text, JSON, Integer, ForeignKey, Index, Numeric, Boolean
from sqlalchemy.orm import relationship
from ...db import Base
from ...core.enums import LLMCallType


class LLMStats(Base):
    """大模型统计记录模型"""
    __tablename__ = "llm_stats"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 关联任务
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False, comment="关联任务ID")
    
    # 调用信息
    call_type = Column(String(50), nullable=False, comment="调用类型")
    model_name = Column(String(100), nullable=False, comment="模型名称")
    stage = Column(String(50), nullable=True, comment="所属阶段")
    
    # 统计信息
    total_calls = Column(Integer, nullable=False, default=0, comment="总调用次数")
    successful_calls = Column(Integer, nullable=False, default=0, comment="成功调用次数")
    failed_calls = Column(Integer, nullable=False, default=0, comment="失败调用次数")
    
    # Token统计
    total_input_tokens = Column(Integer, nullable=False, default=0, comment="总输入Token数")
    total_output_tokens = Column(Integer, nullable=False, default=0, comment="总输出Token数")
    total_tokens = Column(Integer, nullable=False, default=0, comment="总Token数")
    
    # 成本统计
    total_cost = Column(Numeric(10,4), nullable=False, default=0.0000, comment="总成本")
    input_cost = Column(Numeric(10,4), nullable=False, default=0.0000, comment="输入成本")
    output_cost = Column(Numeric(10,4), nullable=False, default=0.0000, comment="输出成本")
    
    # 时间统计
    total_duration_ms = Column(Integer, nullable=False, default=0, comment="总耗时(毫秒)")
    avg_duration_ms = Column(Numeric(10,2), nullable=False, default=0.00, comment="平均耗时(毫秒)")
    min_duration_ms = Column(Integer, nullable=True, comment="最小耗时(毫秒)")
    max_duration_ms = Column(Integer, nullable=True, comment="最大耗时(毫秒)")
    
    # 详细信息
    details = Column(JSON, nullable=True, comment="详细统计信息")
    error_details = Column(JSON, nullable=True, comment="错误详情")
    
    # 时间信息
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    first_call_at = Column(DateTime, nullable=True, comment="首次调用时间")
    last_call_at = Column(DateTime, nullable=True, comment="最后调用时间")
    
    # 关系
    task = relationship("Task", back_populates="llm_stats")
    
    # 索引
    __table_args__ = (
        Index('idx_llm_stats_task_id', 'task_id'),
        Index('idx_llm_stats_call_type', 'call_type'),
        Index('idx_llm_stats_model', 'model_name'),
        Index('idx_llm_stats_stage', 'stage'),
        Index('idx_llm_stats_created_at', 'created_at'),
        Index('idx_llm_stats_task_type', 'task_id', 'call_type'),
    )
    
    
    def __repr__(self):
        return f"<LLMStats(id={self.id}, task_id={self.task_id}, call_type='{self.call_type}', model='{self.model_name}')>"
    
    @property
    def success_rate(self) -> float:
        """获取成功率"""
        if self.total_calls == 0:
            return 0.0
        return self.successful_calls / self.total_calls
    
    @property
    def failure_rate(self) -> float:
        """获取失败率"""
        if self.total_calls == 0:
            return 0.0
        return self.failed_calls / self.total_calls
    
    @property
    def avg_input_tokens(self) -> float:
        """获取平均输入Token数"""
        if self.successful_calls == 0:
            return 0.0
        return self.total_input_tokens / self.successful_calls
    
    @property
    def avg_output_tokens(self) -> float:
        """获取平均输出Token数"""
        if self.successful_calls == 0:
            return 0.0
        return self.total_output_tokens / self.successful_calls
    
    @property
    def avg_tokens(self) -> float:
        """获取平均Token数"""
        if self.successful_calls == 0:
            return 0.0
        return self.total_tokens / self.successful_calls
    
    @property
    def avg_cost(self) -> float:
        """获取平均成本"""
        if self.successful_calls == 0:
            return 0.0
        return self.total_cost / self.successful_calls
    
    @property
    def total_duration_seconds(self) -> float:
        """获取总耗时（秒）"""
        return self.total_duration_ms / 1000.0
    
    @property
    def avg_duration_seconds(self) -> float:
        """获取平均耗时（秒）"""
        return self.avg_duration_ms / 1000.0
    
    def add_call_record(self, input_tokens: int, output_tokens: int, duration_ms: int, 
                       cost: float = 0.0, input_cost: float = 0.0, output_cost: float = 0.0,
                       success: bool = True, error_info: Dict[str, Any] = None):
        """添加调用记录"""
        # 更新调用次数
        self.total_calls += 1
        if success:
            self.successful_calls += 1
        else:
            self.failed_calls += 1
        
        # 更新Token统计（只统计成功的调用）
        if success:
            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens
            self.total_tokens += (input_tokens + output_tokens)
        
        # 更新成本统计
        self.total_cost += cost
        self.input_cost += input_cost
        self.output_cost += output_cost
        
        # 更新时间统计
        self.total_duration_ms += duration_ms
        if self.total_calls > 0:
            self.avg_duration_ms = self.total_duration_ms / self.total_calls
        
        # 更新最小/最大耗时
        if self.min_duration_ms is None or duration_ms < self.min_duration_ms:
            self.min_duration_ms = duration_ms
        if self.max_duration_ms is None or duration_ms > self.max_duration_ms:
            self.max_duration_ms = duration_ms
        
        # 更新时间戳
        now = datetime.utcnow()
        if self.first_call_at is None:
            self.first_call_at = now
        self.last_call_at = now
        self.updated_at = now
        
        # 记录错误信息
        if not success and error_info:
            if self.error_details is None:
                self.error_details = []
            self.error_details.append({
                'timestamp': now.isoformat(),
                'error_info': error_info
            })
    
    def set_detail(self, key: str, value: Any):
        """设置详细信息"""
        if self.details is None:
            self.details = {}
        self.details[key] = value
        self.updated_at = datetime.utcnow()
    
    def get_detail(self, key: str, default: Any = None) -> Any:
        """获取详细信息"""
        if self.details is None:
            return default
        return self.details.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'call_type': self.call_type,
            'model_name': self.model_name,
            'stage': self.stage,
            'total_calls': self.total_calls,
            'successful_calls': self.successful_calls,
            'failed_calls': self.failed_calls,
            'success_rate': self.success_rate,
            'failure_rate': self.failure_rate,
            'total_input_tokens': self.total_input_tokens,
            'total_output_tokens': self.total_output_tokens,
            'total_tokens': self.total_tokens,
            'avg_input_tokens': self.avg_input_tokens,
            'avg_output_tokens': self.avg_output_tokens,
            'avg_tokens': self.avg_tokens,
            'total_cost': self.total_cost,
            'input_cost': self.input_cost,
            'output_cost': self.output_cost,
            'avg_cost': self.avg_cost,
            'total_duration_ms': self.total_duration_ms,
            'total_duration_seconds': self.total_duration_seconds,
            'avg_duration_ms': self.avg_duration_ms,
            'avg_duration_seconds': self.avg_duration_seconds,
            'min_duration_ms': self.min_duration_ms,
            'max_duration_ms': self.max_duration_ms,
            'details': self.details,
            'error_details': self.error_details,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'first_call_at': self.first_call_at.isoformat() if self.first_call_at else None,
            'last_call_at': self.last_call_at.isoformat() if self.last_call_at else None,
        }
    
    @classmethod
    def create_stats_record(cls, task_id: int, call_type: str, model_name: str, stage: str = None) -> 'LLMStats':
        """创建统计记录"""
        return cls(
            task_id=task_id,
            call_type=call_type,
            model_name=model_name,
            stage=stage,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    @classmethod
    def get_call_type_display_name(cls, call_type: str) -> str:
        """获取调用类型显示名称"""
        type_names = {
            LLMCallType.CLASSIFICATION.value: "项目分类",
            LLMCallType.OVERVIEW_GENERATION.value: "概览生成",
            LLMCallType.CATALOGUE_GENERATION.value: "目录生成",
            LLMCallType.DOCUMENT_GENERATION.value: "文档生成",
            LLMCallType.SUMMARY_GENERATION.value: "摘要生成",
            LLMCallType.OTHER.value: "其他",
        }
        return type_names.get(call_type, call_type)


class LLMCallRecord(Base):
    """大模型调用详细记录模型"""
    __tablename__ = "llm_call_records"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 关联任务和统计
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False, comment="关联任务ID")
    llm_stats_id = Column(Integer, ForeignKey('llm_stats.id', ondelete='CASCADE'), nullable=True, comment="关联统计ID")
    
    # 调用信息
    call_type = Column(String(50), nullable=False, comment="调用类型")
    model_name = Column(String(100), nullable=False, comment="模型名称")
    stage = Column(String(50), nullable=True, comment="所属阶段")
    
    # 请求信息
    prompt = Column(Text, nullable=True, comment="提示词")
    input_tokens = Column(Integer, nullable=False, default=0, comment="输入Token数")
    output_tokens = Column(Integer, nullable=False, default=0, comment="输出Token数")
    total_tokens = Column(Integer, nullable=False, default=0, comment="总Token数")
    
    # 响应信息
    response = Column(Text, nullable=True, comment="响应内容")
    success = Column(Boolean, nullable=False, default=True, comment="是否成功")
    
    # 成本信息
    cost = Column(Numeric(10,4), nullable=False, default=0.0000, comment="总成本")
    input_cost = Column(Numeric(10,4), nullable=False, default=0.0000, comment="输入成本")
    output_cost = Column(Numeric(10,4), nullable=False, default=0.0000, comment="输出成本")
    
    # 时间信息
    duration_ms = Column(Integer, nullable=False, default=0, comment="耗时(毫秒)")
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="开始时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    
    # 错误信息
    error_message = Column(Text, nullable=True, comment="错误信息")
    error_code = Column(String(50), nullable=True, comment="错误代码")
    
    # 元数据
    call_metadata = Column(JSON, nullable=True, comment="元数据")
    
    # 索引
    __table_args__ = (
        Index('idx_call_record_task_id', 'task_id'),
        Index('idx_call_record_stats_id', 'llm_stats_id'),
        Index('idx_call_record_call_type', 'call_type'),
        Index('idx_call_record_model', 'model_name'),
        Index('idx_call_record_started_at', 'started_at'),
        Index('idx_call_record_success', 'success'),
    )
    
    
    def __repr__(self):
        return f"<LLMCallRecord(id={self.id}, task_id={self.task_id}, call_type='{self.call_type}', success={bool(self.success)})>"
    
    @property
    def is_success(self) -> bool:
        """判断调用是否成功"""
        return bool(self.success)
    
    @property
    def duration_seconds(self) -> float:
        """获取耗时（秒）"""
        return self.duration_ms / 1000.0
    
    def complete_call(self, response: str, output_tokens: int, cost: float = 0.0, 
                     input_cost: float = 0.0, output_cost: float = 0.0):
        """完成调用"""
        self.response = response
        self.output_tokens = output_tokens
        self.total_tokens = self.input_tokens + output_tokens
        self.cost = cost
        self.input_cost = input_cost
        self.output_cost = output_cost
        self.success = 1
        self.completed_at = datetime.utcnow()
        
        # 计算耗时
        if self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds()
            self.duration_ms = int(duration * 1000)
    
    def fail_call(self, error_message: str, error_code: str = None):
        """调用失败"""
        self.error_message = error_message
        self.error_code = error_code
        self.success = 0
        self.completed_at = datetime.utcnow()
        
        # 计算耗时
        if self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds()
            self.duration_ms = int(duration * 1000)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'llm_stats_id': self.llm_stats_id,
            'call_type': self.call_type,
            'model_name': self.model_name,
            'stage': self.stage,
            'prompt': self.prompt,
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'total_tokens': self.total_tokens,
            'response': self.response,
            'success': self.success,
            'is_success': self.is_success,
            'cost': self.cost,
            'input_cost': self.input_cost,
            'output_cost': self.output_cost,
            'duration_ms': self.duration_ms,
            'duration_seconds': self.duration_seconds,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'error_code': self.error_code,
            'metadata': self.call_metadata,
        }