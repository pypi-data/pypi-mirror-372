"""
日志配置加载器

提供日志配置的加载和应用功能，将日志配置与应用配置分离

重构历史:
- 2025-08-20: 极简重构 - 只保留 setup_logging() 作为唯一公共接口，移除过度设计
- 2025-08-20: 重构优化 - 减少公共接口暴露，增强封装性和安全性
- 2025-08-06: 添加 Pydantic 警告过滤器，屏蔽频繁的序列化警告
- 2025-08-06: 增强错误处理和类型注解
- 2025-08-06: 添加全面的单元测试支持
"""

import os
import json
import logging
import logging.config
import warnings
from typing import Dict, Any, Optional
from pathlib import Path
from copy import deepcopy

logger = logging.getLogger(__name__)


class PydanticWarningFilter(logging.Filter):
    """
    Pydantic 警告过滤器
    
    用于屏蔽 Pydantic 序列化相关的 UserWarning，避免日志输出过于频繁
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        过滤日志记录
        
        Args:
            record: 日志记录对象
            
        Returns:
            bool: True 表示允许记录，False 表示过滤掉
        """
        # 过滤 Pydantic 序列化警告
        if record.levelname == 'WARNING':
            message = record.getMessage()
            # 检查是否是 Pydantic 序列化警告
            if ('Pydantic serializer warnings' in message or 
                'PydanticSerializationUnexpectedValue' in message or
                'pydantic/main.py' in record.pathname):
                return False
        
        return True


def setup_logging(config_file: Optional[str] = None) -> None:
    """
    设置日志配置（唯一的公共接口）
    
    自动检测环境并应用相应配置，包含完整的错误处理和目录创建功能。
    
    Args:
        config_file: 日志配置文件路径，如果不指定则根据环境自动选择
        
    Raises:
        RuntimeError: 配置应用失败时的回退处理
    """
    try:
        # 解析配置文件路径
        resolved_config_file = _resolve_config_path(config_file)
        
        # 加载配置
        logging_config = _load_config(resolved_config_file)
        
        # 确保日志目录存在
        _ensure_log_directories(logging_config)
        
        # 添加 Pydantic 警告过滤器
        config_with_filters = _add_pydantic_filters(deepcopy(logging_config))
        
        # 应用日志配置
        logging.config.dictConfig(config_with_filters)
        
        # 设置 warnings 模块过滤器
        _setup_warnings_filter()
        
        # 配置成功后获取 logger 并记录成功信息
        logger = logging.getLogger(__name__)
        logger.info(f"成功应用日志配置文件: {resolved_config_file}")
        
    except Exception as e:
        # 如果日志配置失败，使用基本的日志配置
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        logger = logging.getLogger(__name__)
        logger.error(f"应用日志配置失败，使用基本配置: {e}")


def _resolve_config_path(config_file: Optional[str]) -> str:
    """
    解析配置文件路径
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        str: 解析后的绝对路径
        
    Raises:
        ValueError: 配置文件路径无效
    """
    if config_file is None:
        return _get_default_config_path()
    
    # 输入验证
    if not isinstance(config_file, str) or not config_file.strip():
        raise ValueError("配置文件路径必须是非空字符串")
    
    # 安全检查：防止路径遍历攻击
    config_path = Path(config_file).resolve()
    
    # 检查文件扩展名
    if config_path.suffix != '.json':
        raise ValueError(f"不支持的配置文件格式: {config_path.suffix}")
    
    # 检查路径是否包含危险字符
    path_str = str(config_path)
    if '..' in path_str or '~' in path_str:
        raise ValueError("配置文件路径包含不安全的字符")
    
    return str(config_path)


def _get_default_config_path() -> str:
    """
    获取默认日志配置文件路径，支持环境检测
    
    Returns:
        str: 默认配置文件的绝对路径
    """
    project_root = Path(__file__).parent.parent.parent
    
    # 检测环境变量
    env = os.getenv('KENGINE_ENV', 'production').lower()
    
    # 根据环境选择配置文件
    if env in ['test', 'testing']:
        config_file = "logging_config_test.json"
    else:
        config_file = "logging_config.json"
    
    return str(project_root / "config" / config_file)


def _load_config(config_file: str) -> Dict[str, Any]:
    """
    加载日志配置
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        Dict[str, Any]: 日志配置字典
        
    Raises:
        FileNotFoundError: 配置文件不存在
        ValueError: 配置文件格式错误
        RuntimeError: 加载配置失败
    """
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"日志配置文件不存在: {config_file}")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            logging_config = json.load(f)
        
        # 验证配置不为空
        if not isinstance(logging_config, dict):
            raise ValueError("配置文件内容必须是JSON对象")
        
        return logging_config
            
    except json.JSONDecodeError as e:
        raise ValueError(f"日志配置文件格式错误: {e}") from e
    except Exception as e:
        raise RuntimeError(f"加载日志配置失败: {e}") from e


def _add_pydantic_filters(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    向日志配置添加 Pydantic 警告过滤器
    
    Args:
        config: 原始日志配置
        
    Returns:
        Dict[str, Any]: 添加过滤器后的配置
    """
    # 添加过滤器定义
    if 'filters' not in config:
        config['filters'] = {}
    
    config['filters']['pydantic_warning_filter'] = {
        '()': 'kengine.config.logging_config.PydanticWarningFilter'
    }
    
    # 为所有处理器添加过滤器
    handlers = config.get('handlers', {})
    for handler_name, handler_config in handlers.items():
        if 'filters' not in handler_config:
            handler_config['filters'] = []
        
        # 避免重复添加
        if 'pydantic_warning_filter' not in handler_config['filters']:
            handler_config['filters'].append('pydantic_warning_filter')
    
    return config


def _setup_warnings_filter() -> None:
    """设置 Python warnings 模块的过滤器"""
    # 过滤 Pydantic 相关的 UserWarning
    warnings.filterwarnings(
        'ignore',
        category=UserWarning,
        module='pydantic.*'
    )
    
    # 过滤特定的 Pydantic 序列化警告
    warnings.filterwarnings(
        'ignore',
        message='.*Pydantic serializer warnings.*',
        category=UserWarning
    )


def _ensure_log_directories(logging_config: Dict[str, Any]) -> None:
    """
    确保日志目录存在
    
    Args:
        logging_config: 日志配置字典
    """
    handlers = logging_config.get('handlers', {})
    
    for handler_name, handler_config in handlers.items():
        if 'filename' in handler_config:
            log_file = Path(handler_config['filename'])
            log_dir = log_file.parent
            
            if not log_dir.exists():
                log_dir.mkdir(parents=True, exist_ok=True)
                logger.debug(f"创建日志目录: {log_dir}")
