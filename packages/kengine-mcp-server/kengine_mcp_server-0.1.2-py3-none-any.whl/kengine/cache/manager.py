"""
全局缓存管理器模块

基于 functools.lru_cache 实现的增强缓存系统，提供TTL支持、统计功能和线程安全保证。

重构历史：
- 2025-01-06: 初始版本，基于 functools.lru_cache 实现
"""

import functools
import threading
import time
import logging
import weakref
from typing import Any, Dict, Optional, Callable, TypeVar, Union
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


@dataclass
class CacheStats:
    """缓存统计信息"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expired_removals: int = 0
    
    @property
    def hit_rate(self) -> float:
        """计算缓存命中率"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    def reset(self) -> None:
        """重置统计信息"""
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.expired_removals = 0


@dataclass
class CacheEntry:
    """缓存条目，包含TTL信息"""
    value: Any
    created_at: float
    ttl: Optional[float] = None
    
    def is_expired(self) -> bool:
        """检查是否已过期"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl


class GlobalCacheManager:
    """
    全局缓存管理器
    
    基于 functools.lru_cache 的增强缓存系统，提供：
    - TTL（生存时间）支持
    - 缓存统计和监控
    - 线程安全操作
    - 缓存清理和管理
    """
    
    _instance: Optional['GlobalCacheManager'] = None
    _lock = threading.Lock()
    
    def __new__(cls, max_size: int = None) -> 'GlobalCacheManager':
        """单例模式实现"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, max_size: int = None):
        """初始化缓存管理器"""
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self._max_size = max_size or 1000
        self._stats = CacheStats()
        self._ttl_cache: Dict[str, CacheEntry] = {}
        self._cache_functions: Dict[str, Callable] = {}
        self._lock = threading.RLock()
        
        logger.info(f"全局缓存管理器初始化完成，最大缓存大小: {self._max_size}")
    
    def get_stats(self) -> CacheStats:
        """获取缓存统计信息"""
        with self._lock:
            stats = CacheStats(
                hits=self._stats.hits,
                misses=self._stats.misses,
                evictions=self._stats.evictions,
                expired_removals=self._stats.expired_removals
            )
            # 添加兼容属性
            stats.cache_hits = stats.hits
            stats.cache_misses = stats.misses
            stats.total_requests = stats.hits + stats.misses
            return stats
    
    def reset_stats(self) -> None:
        """重置统计信息"""
        with self._lock:
            self._stats.reset()
            logger.info("缓存统计信息已重置")
    
    def clear_all_caches(self) -> None:
        """清理所有缓存"""
        with self._lock:
            # 清理TTL缓存
            self._ttl_cache.clear()
            
            # 清理所有注册的缓存函数
            for func_name, func in self._cache_functions.items():
                if hasattr(func, 'cache_clear'):
                    func.cache_clear()
                    logger.debug(f"已清理函数缓存: {func_name}")
            
            self._stats.evictions += 1
            logger.info("所有缓存已清理")
    
    def clear_all(self) -> None:
        """清理所有缓存 - 兼容方法"""
        self.clear_all_caches()
    
    def get_cache_size(self) -> int:
        """获取缓存大小"""
        with self._lock:
            # 清理过期缓存后再计算大小
            self._cleanup_expired_entries()
            return len(self._ttl_cache)
    
    def cleanup_expired(self) -> None:
        """清理过期缓存 - 兼容方法"""
        self._cleanup_expired_entries()
    
    def _cleanup_expired_entries(self) -> None:
        """清理过期的TTL缓存条目"""
        expired_keys = []
        current_time = time.time()
        
        for key, entry in self._ttl_cache.items():
            if entry.is_expired():
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._ttl_cache[key]
            self._stats.expired_removals += 1
        
        if expired_keys:
            logger.debug(f"清理了 {len(expired_keys)} 个过期缓存条目")
    
    def get_cache_info(self, func_name: Optional[str] = None) -> Dict[str, Any]:
        """
        获取缓存信息
        
        Args:
            func_name: 函数名，如果为None则返回全局信息
            
        Returns:
            Dict[str, Any]: 缓存信息
        """
        with self._lock:
            info = {
                "global_stats": {
                    "hits": self._stats.hits,
                    "misses": self._stats.misses,
                    "hit_rate": self._stats.hit_rate,
                    "evictions": self._stats.evictions,
                    "expired_removals": self._stats.expired_removals
                },
                "ttl_cache_size": len(self._ttl_cache),
                "registered_functions": len(self._cache_functions)
            }
            
            if func_name and func_name in self._cache_functions:
                func = self._cache_functions[func_name]
                if hasattr(func, 'cache_info'):
                    info[f"{func_name}_cache_info"] = func.cache_info()._asdict()
            
            return info


# 全局缓存管理器实例
_cache_manager = GlobalCacheManager()


def get_cache_manager() -> GlobalCacheManager:
    """获取全局缓存管理器实例"""
    return _cache_manager


def lru_cache_with_ttl(
    maxsize: int = 256,
    ttl: Optional[float] = None,
    typed: bool = False
) -> Callable[[F], F]:
    """
    带TTL支持的LRU缓存装饰器
    
    结合 functools.lru_cache 和 TTL 功能的增强缓存装饰器。
    
    优化说明：
    - 将默认maxsize从128增加到256，提供更大的缓存空间
    - 优化缓存策略，减少过早的缓存清理
    
    Args:
        maxsize: 最大缓存大小
        ttl: 生存时间（秒），None表示永不过期
        typed: 是否区分参数类型
        
    Returns:
        装饰器函数
    """
    def decorator(func: F) -> F:
        # 使用 functools.lru_cache 作为基础
        cached_func = functools.lru_cache(maxsize=maxsize, typed=typed)(func)
        
        # 注册到全局管理器
        func_name = f"{func.__module__}.{func.__qualname__}"
        _cache_manager._cache_functions[func_name] = cached_func
        
        if ttl is None:
            # 如果没有TTL，直接返回lru_cache装饰的函数
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    result = cached_func(*args, **kwargs)
                    _cache_manager._stats.hits += 1
                    return result
                except Exception:
                    _cache_manager._stats.misses += 1
                    raise
            
            # 保留cache_info和cache_clear方法
            wrapper.cache_info = cached_func.cache_info
            wrapper.cache_clear = cached_func.cache_clear
            return wrapper
        
        # 带TTL的实现
        ttl_cache = {}
        cache_lock = threading.RLock()
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            key = str(args) + str(sorted(kwargs.items()))
            
            with cache_lock:
                # 检查TTL缓存
                if key in ttl_cache:
                    entry = ttl_cache[key]
                    if not entry.is_expired():
                        _cache_manager._stats.hits += 1
                        logger.debug(f"TTL缓存命中: {func_name}")
                        return entry.value
                    else:
                        # 过期，删除条目
                        del ttl_cache[key]
                        _cache_manager._stats.expired_removals += 1
                        logger.debug(f"TTL缓存过期: {func_name}")
                
                # 缓存未命中，调用原函数
                _cache_manager._stats.misses += 1
                result = func(*args, **kwargs)
                
                # 存储到TTL缓存
                ttl_cache[key] = CacheEntry(
                    value=result,
                    created_at=time.time(),
                    ttl=ttl
                )
                
                logger.debug(f"TTL缓存存储: {func_name}, TTL: {ttl}s")
                return result
        
        def cache_clear():
            """清理缓存"""
            with cache_lock:
                ttl_cache.clear()
                cached_func.cache_clear()
                logger.debug(f"已清理缓存: {func_name}")
        
        def cache_info():
            """获取缓存信息"""
            with cache_lock:
                base_info = cached_func.cache_info()
                return {
                    "hits": base_info.hits,
                    "misses": base_info.misses,
                    "maxsize": base_info.maxsize,
                    "currsize": base_info.currsize,
                    "ttl_cache_size": len(ttl_cache),
                    "ttl": ttl
                }
        
        wrapper.cache_clear = cache_clear
        wrapper.cache_info = cache_info
        
        return wrapper
    
    return decorator


def load_cache_config() -> Dict[str, Any]:
    """
    从配置文件加载缓存配置
    
    Returns:
        Dict[str, Any]: 缓存配置
    """
    from ..config.application_config import get_application_config
    config = get_application_config()
    cache_config = config.get('cache_config', {})
    logger.info(f"缓存配置加载成功: {cache_config}")
    return cache_config
        


# 便捷的缓存装饰器，使用配置文件中的默认值
def cached(maxsize: Optional[int] = None, ttl: Optional[float] = None):
    """
    便捷的缓存装饰器，自动使用配置文件中的默认值
    
    Args:
        maxsize: 最大缓存大小，None使用配置文件默认值
        ttl: TTL时间，None使用配置文件默认值
        
    Returns:
        装饰器函数
    """
    config = load_cache_config()
    
    if not config.get("enable_caching", True):
        # 如果缓存被禁用，返回原函数
        def no_cache_decorator(func):
            return func
        return no_cache_decorator
    
    actual_maxsize = maxsize if maxsize is not None else config.get("max_cache_size", 256)
    actual_ttl = ttl if ttl is not None else config.get("cache_ttl", 300)
    
    return lru_cache_with_ttl(maxsize=actual_maxsize, ttl=actual_ttl)