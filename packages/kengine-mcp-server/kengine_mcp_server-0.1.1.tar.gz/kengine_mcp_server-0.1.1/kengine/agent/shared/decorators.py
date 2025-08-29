"""
工具调用装饰器模块

提供防止重复调用和缓存管理的装饰器功能。
集成了 kengine.cache 模块的缓存实现。

重构历史：
- 2025-01-06: 集成 kengine.cache 模块，使用全局缓存管理器
"""

import logging
import time
from functools import wraps
from typing import Dict, Any, Callable, Optional
import hashlib

from ...cache import get_cache_manager, lru_cache_with_ttl, cached

logger = logging.getLogger(__name__)

def generate_cache_key(func: Callable, args: tuple, kwargs: dict) -> str:
    """
    生成缓存键
    
    Args:
        func: 被装饰的函数
        args: 位置参数
        kwargs: 关键字参数
        
    Returns:
        str: 唯一标识函数调用的缓存键
    """
    key_parts = [
        func.__name__,
        str(args),
        str(sorted(kwargs.items()))
    ]
    key_string = "|".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()

def prevent_duplicate_calls(ttl: int = 300):
    """
    防止重复工具调用的装饰器 - 统一缓存版本
    
    直接使用全局缓存管理器的统一缓存系统：
    - 在TTL有效期内返回缓存结果
    - 超过TTL时间后重新执行函数
    - 统计信息与全局管理器同步
    
    Args:
        ttl: 缓存生存时间（秒），超过此时间的缓存记录会被清理
    """
    def decorator(func: Callable):
        # 使用全局缓存管理器
        from ...cache.manager import get_cache_manager, GlobalCacheManager
        # 如果全局实例存在，使用它；否则获取默认实例
        if GlobalCacheManager._instance is not None:
            manager = GlobalCacheManager._instance
        else:
            manager = get_cache_manager()
        
        # 生成函数的唯一标识
        func_name = f"{func.__module__}.{func.__qualname__}"
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            key = f"{func_name}:{str(args)}:{str(sorted(kwargs.items()))}"
            
            try:
                # 检查缓存
                with manager._lock:
                    if key in manager._ttl_cache:
                        entry = manager._ttl_cache[key]
                        if not entry.is_expired():
                            # 缓存命中
                            manager._stats.hits += 1
                            logger.debug(f"缓存命中: {func.__name__}")
                            return entry.value
                        else:
                            # 缓存过期，删除
                            del manager._ttl_cache[key]
                            manager._stats.expired_removals += 1
                            logger.debug(f"缓存过期: {func.__name__}")
                    
                    # 缓存未命中，执行函数
                    manager._stats.misses += 1
                    logger.debug(f"缓存未命中，执行函数: {func.__name__}")
                
                # 执行原函数
                result = func(*args, **kwargs)
                
                # 存储到缓存
                with manager._lock:
                    from ...cache.manager import CacheEntry
                    import time
                    manager._ttl_cache[key] = CacheEntry(
                        value=result,
                        created_at=time.time(),
                        ttl=ttl
                    )
                    logger.debug(f"缓存存储: {func.__name__}, TTL: {ttl}s")
                
                return result
                
            except Exception as e:
                logger.error(f"装饰器执行失败: {func.__name__}, 错误: {e}")
                # 异常不缓存，重新抛出
                raise
        
        def cache_clear():
            """清理该函数的缓存"""
            with manager._lock:
                keys_to_remove = [k for k in manager._ttl_cache.keys() if k.startswith(f"{func_name}:")]
                for key in keys_to_remove:
                    del manager._ttl_cache[key]
                logger.debug(f"已清理函数缓存: {func.__name__}")
        
        def cache_info():
            """获取缓存信息"""
            with manager._lock:
                func_keys = [k for k in manager._ttl_cache.keys() if k.startswith(f"{func_name}:")]
                return {
                    "currsize": len(func_keys),
                    "maxsize": getattr(manager, '_max_size', 1000),
                    "hits": manager._stats.hits,
                    "misses": manager._stats.misses
                }
        
        # 保留缓存相关方法
        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache_clear
        wrapper._func_name = func_name
        wrapper._cache_manager = manager
        
        return wrapper
    return decorator
