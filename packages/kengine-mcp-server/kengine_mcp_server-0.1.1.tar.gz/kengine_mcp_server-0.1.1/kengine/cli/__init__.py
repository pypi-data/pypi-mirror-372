"""
CLI模块

提供命令行接口功能
"""

from dotenv import load_dotenv
from kengine.config.logging_config import setup_logging
from .cli import EnhancedCLIController

__all__ = ['EnhancedCLIController']

# 加载环境变量和日志配置
load_dotenv()
setup_logging()