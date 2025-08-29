"""
缓存模块

提供全局缓存管理功能，包括基于 functools.lru_cache 的增强缓存系统。

主要组件：
- GlobalCacheManager: 全局缓存管理器
- lru_cache_with_ttl: 带TTL支持的LRU缓存装饰器
- cached: 便捷的缓存装饰器
"""

from .manager import (
    GlobalCacheManager,
    get_cache_manager,
    lru_cache_with_ttl,
    cached,
    CacheStats,
    CacheEntry
)

__all__ = [
    'GlobalCacheManager',
    'get_cache_manager', 
    'lru_cache_with_ttl',
    'cached',
    'CacheStats',
    'CacheEntry'
]