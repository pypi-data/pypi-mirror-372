"""
端点提取器包

多语言代码库端点提取器，支持Java、Python、JavaScript/TypeScript、
Go、C#、PHP等主流语言的端点识别。通过文件名模式、注解识别和目录结构分析，
实现高精度的代码库端点提取，并使用骨架提取技术获取代码结构信息。

主要特性：
- 支持6种主流编程语言的端点提取
- 多层次提取策略（文件名->注解->内容分析）
- 智能优先级排序算法
- 性能缓存机制
- 与代码骨架提取工具无缝集成
"""

import logging
from typing import Dict, Any

from .extractor import RepoEndpointExtractor

# 配置日志
from ...config.logging_config import setup_logging
setup_logging()

logger = logging.getLogger(__name__)

# 导出主要接口
__all__ = [
    # 主要功能函数
    'extract_repo_endpoint_skeletons',
    'extract_endpoints',  # 为了向后兼容
]

def extract_repo_endpoint_skeletons(repo_base_dir: str, **kwargs) -> Dict[str, Any]:
    """
    从代码库中提取端点骨架信息的主入口函数
    
    该函数实现了智能化的多语言端点提取，支持Java、Python、JavaScript/TypeScript、
    Go、C#、PHP等主流语言。通过文件名模式、注解识别和目录结构分析，
    实现高精度的端点识别和骨架提取。
    
    Args:
        repo_base_dir (str): 代码库根目录路径
        **kwargs: 可选参数
            - max_workers (int): 并行处理的最大工作线程数，默认为4
            - enable_cache (bool): 是否启用缓存机制，默认为True
            - confidence_threshold (float): 置信度阈值，默认为0.3
    
    Returns:
        Dict[str, Any]: 提取结果，包含以下字段：
            - repo_path: 代码库路径
            - total_files: 扫描的文件总数
            - candidates: 端点候选文件列表
            - summary: 统计摘要信息
            - microservices: 微服务结构信息
            - processing_time: 处理耗时（秒）
            - timestamp: 处理时间戳
            - error: 错误信息（如果有）
    
    支持的语言和框架：
        - Java: Spring Boot/MVC, Jersey, JAX-RS
        - Python: Django, Flask, FastAPI, Tornado
        - JavaScript/TypeScript: Express.js, NestJS, Next.js
        - Go: Gin, Echo, Fiber, Gorilla Mux
        - C#: ASP.NET Core, Web API
        - PHP: Laravel, Symfony, CodeIgniter
    
    提取规则：
        1. 文件名模式匹配（权重40%）
        2. 目录结构分析（权重30%）
        3. 注解/装饰器识别（权重30%）
    
    Example:
        >>> result = extract_repo_endpoint_skeletons("/path/to/repo")
        >>> print(f"发现 {result['summary']['total_candidates']} 个端点文件")
        >>> for candidate in result['candidates']:
        ...     print(f"  {candidate['file_path']} (置信度: {candidate['confidence_score']:.2f})")
    """
    # 提取可选参数
    max_workers = kwargs.get('max_workers', 4)
    enable_cache = kwargs.get('enable_cache', True)
    
    # 创建提取器实例
    extractor = RepoEndpointExtractor(max_workers=max_workers, enable_cache=enable_cache)
    
    # 执行提取
    return extractor.extract_endpoints(repo_base_dir)

# 为了向后兼容，添加别名
extract_endpoints = extract_repo_endpoint_skeletons