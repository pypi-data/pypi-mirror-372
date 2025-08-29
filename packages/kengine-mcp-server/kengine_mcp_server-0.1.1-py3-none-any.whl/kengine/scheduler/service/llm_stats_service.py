"""
大模型统计服务

提供大模型使用统计相关的业务逻辑处理
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ...db.database_manager import db_manager
from ..models.llm_stats import LLMStats
from .queries import LLMStatsQueries


class LLMStatsService:
    """大模型统计服务类"""
    
    def __init__(self):
        """初始化大模型统计服务"""
        pass
    
    # ==================== 统计记录管理 ====================
    
    def create_stats_record(self, task_id: int, model_name: str,
                                 prompt_tokens: int = 0, completion_tokens: int = 0,
                                 total_tokens: int = 0, cost: float = 0.0,
                                 **kwargs) -> LLMStats:
        """创建统计记录"""
        with db_manager.transaction() as session:
            stats = LLMStats(
                task_id=task_id,
                model_name=model_name,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost=cost,
                **kwargs
            )
            session.add(stats)
            session.flush()
            session.expunge(stats)
            return stats
    
    def get_stats_by_id(self, stats_id: int) -> Optional[LLMStats]:
        """根据ID获取统计记录"""
        with db_manager.session() as session:
            stats = session.query(LLMStats).filter(LLMStats.id == stats_id).first()
            if stats:
                session.expunge(stats)
            return stats
    
    def get_stats_by_task(self, task_id: int) -> List[LLMStats]:
        """获取任务的所有统计记录"""
        with db_manager.session() as session:
            stats_list = LLMStatsQueries.get_stats_by_task(session, task_id)
            for stats in stats_list:
                session.expunge(stats)
            return stats_list
    
    def get_stats_by_model(self, model_name: str, 
                                limit: Optional[int] = None) -> List[LLMStats]:
        """获取指定模型的统计记录"""
        with db_manager.session() as session:
            stats_list = LLMStatsQueries.get_stats_by_model(session, model_name, limit)
            for stats in stats_list:
                session.expunge(stats)
            return stats_list
    
    def get_stats_by_date_range(self, start_date: datetime, 
                                     end_date: datetime) -> List[LLMStats]:
        """获取指定日期范围的统计记录"""
        with db_manager.session() as session:
            stats_list = LLMStatsQueries.get_stats_by_date_range(session, start_date, end_date)
            for stats in stats_list:
                session.expunge(stats)
            return stats_list
    
    # ==================== 统计分析方法 ====================
    
    def get_task_total_stats(self, task_id: int) -> Dict[str, Any]:
        """获取任务的总统计信息"""
        with db_manager.session() as session:
            return LLMStatsQueries.get_task_total_stats(session, task_id)
    
    def get_model_usage_summary(self, model_name: str, 
                                     days: int = 30) -> Dict[str, Any]:
        """获取模型使用汇总（最近N天）"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        with db_manager.session() as session:
            return LLMStatsQueries.get_model_usage_summary(session, model_name, start_date, end_date)
    
    def get_daily_usage_stats(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取每日使用统计（最近N天）"""
        with db_manager.session() as session:
            return LLMStatsQueries.get_daily_usage_stats(session, days)
    
    def get_model_comparison_stats(self, days: int = 30) -> List[Dict[str, Any]]:
        """获取模型对比统计"""
        with db_manager.session() as session:
            return LLMStatsQueries.get_model_comparison_stats(session, days)
    
    def get_cost_analysis(self, start_date: datetime = None, 
                               end_date: datetime = None) -> Dict[str, Any]:
        """获取成本分析"""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
            
        with db_manager.session() as session:
            return LLMStatsQueries.get_cost_analysis(session, start_date, end_date)
    
    def get_token_usage_trends(self, model_name: str = None, 
                                   days: int = 30) -> List[Dict[str, Any]]:
        """获取Token使用趋势"""
        with db_manager.session() as session:
            return LLMStatsQueries.get_token_usage_trends(session, model_name, days)
    
    # ==================== 批量操作方法 ====================
    
    def batch_create_stats(self, stats_data: List[Dict[str, Any]]) -> List[LLMStats]:
        """批量创建统计记录"""
        with db_manager.transaction() as session:
            stats_list = []
            for data in stats_data:
                stats = LLMStats(**data)
                session.add(stats)
                stats_list.append(stats)
            
            session.flush()
            for stats in stats_list:
                session.expunge(stats)
            return stats_list
    
    def update_stats(self, stats_id: int, **kwargs) -> Optional[LLMStats]:
        """更新统计记录"""
        with db_manager.transaction() as session:
            stats = session.query(LLMStats).filter(LLMStats.id == stats_id).first()
            if stats:
                for key, value in kwargs.items():
                    if hasattr(stats, key):
                        setattr(stats, key, value)
                stats.updated_at = datetime.utcnow()
                session.flush()
                session.expunge(stats)
                return stats
            return None
    
    def delete_stats(self, stats_id: int) -> bool:
        """删除统计记录"""
        with db_manager.transaction() as session:
            stats = session.query(LLMStats).filter(LLMStats.id == stats_id).first()
            if stats:
                session.delete(stats)
                return True
            return False
    
    def cleanup_old_stats(self, days: int = 90) -> int:
        """清理旧的统计记录"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        with db_manager.transaction() as session:
            deleted_count = session.query(LLMStats).filter(
                LLMStats.created_at < cutoff_date
            ).delete()
            return deleted_count
    
    # ==================== 实时统计方法 ====================
    
    def record_api_call(self, task_id: int, model_name: str,
                             prompt_tokens: int, completion_tokens: int,
                             cost: float = 0.0, **kwargs) -> LLMStats:
        """记录API调用统计"""
        total_tokens = prompt_tokens + completion_tokens
        return self.create_stats_record(
            task_id=task_id,
            model_name=model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost=cost,
            **kwargs
        )
    
    def get_current_usage(self, task_id: int) -> Dict[str, Any]:
        """获取当前任务的实时使用情况"""
        return self.get_task_total_stats(task_id)
    
    def get_quota_usage(self, model_name: str, 
                             period: str = 'daily') -> Dict[str, Any]:
        """获取配额使用情况"""
        if period == 'daily':
            start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif period == 'monthly':
            start_date = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if start_date.month == 12:
                end_date = start_date.replace(year=start_date.year + 1, month=1)
            else:
                end_date = start_date.replace(month=start_date.month + 1)
        else:
            raise ValueError(f"Unsupported period: {period}")
        
        stats_list = self.get_stats_by_date_range(start_date, end_date)
        model_stats = [s for s in stats_list if s.model_name == model_name]
        
        total_tokens = sum(s.total_tokens for s in model_stats)
        total_cost = sum(s.cost for s in model_stats)
        call_count = len(model_stats)
        
        return {
            'model_name': model_name,
            'period': period,
            'start_date': start_date,
            'end_date': end_date,
            'total_tokens': total_tokens,
            'total_cost': total_cost,
            'call_count': call_count
        }


# 全局大模型统计服务实例
llm_stats_service = LLMStatsService()