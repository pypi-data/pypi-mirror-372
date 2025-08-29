"""
IO 接口模块

提供统一的文件读写接口，支持本地存储和OSS对象存储
"""
import os
import logging
from typing import Optional, Union
from .io import IO
from .local import create_doc_file_io

logger = logging.getLogger(__name__)

# 存储类型枚举
STORAGE_LOCAL = "local"
STORAGE_OSS = "oss"

# 默认存储类型（可通过环境变量配置）
DEFAULT_STORAGE_TYPE = os.getenv('KENGINE_STORAGE_TYPE', STORAGE_OSS)

# 导出接口
__all__ = [
    'IO',
    'create_io',
    'create_oss_io',
    'create_local_io',
    'set_default_storage_type',
    'get_default_storage_type',
    'STORAGE_LOCAL',
    'STORAGE_OSS'
]


def create_io(repo_group: str, repo_name: str, version: str = None, 
              storage_type: Optional[str] = None) -> IO:
    """
    创建IO实例的统一入口
    
    Args:
        repo_group: 仓库组名
        repo_name: 仓库名
        version: 版本号
        storage_type: 存储类型 ('local' 或 'oss')，默认使用全局配置
        
    Returns:
        IO实例
    """
    storage_type = storage_type or DEFAULT_STORAGE_TYPE
    
    if storage_type == STORAGE_OSS:
        return create_oss_io(repo_group, repo_name, version)
    else:
        return create_local_io(repo_group, repo_name, version)


def create_local_io(repo_group: str, repo_name: str, version: str = None) -> IO:
    """
    创建本地文件IO实例
    
    Args:
        repo_group: 仓库组名
        repo_name: 仓库名
        version: 版本号
        
    Returns:
        本地文件IO实例
    """
    return create_doc_file_io(repo_group=repo_group, repo_name=repo_name, version=version)


def create_oss_io(repo_group: str, repo_name: str, version: str = None) -> IO:
    """
    创建OSS对象存储IO实例
    
    Args:
        repo_group: 仓库组名
        repo_name: 仓库名
        version: 版本号
        
    Returns:
        OSS IO实例
    """
    try:
        from .oss_io import create_document_oss_io
        from kengine.io.oss_config import oss_config_manager
        
        # 检查OSS配置是否可用
        if not oss_config_manager.get_config():
            logger.warning("OSS配置未初始化，回退到本地存储")
            return create_local_io(repo_group, repo_name, version)
        
        return create_document_oss_io(
            domain=repo_group,
            repo_name=repo_name,
            version=version
        )
        
    except ImportError as e:
        logger.error(f"OSS模块导入失败: {e}")
        logger.warning("回退到本地存储")
        return create_local_io(repo_group, repo_name, version)
    except Exception as e:
        logger.error(f"创建OSS IO实例失败: {e}")
        logger.warning("回退到本地存储")
        return create_local_io(repo_group, repo_name, version)


def set_default_storage_type(storage_type: str):
    """
    设置默认存储类型
    
    Args:
        storage_type: 存储类型 ('local' 或 'oss')
    """
    global DEFAULT_STORAGE_TYPE
    
    if storage_type not in [STORAGE_LOCAL, STORAGE_OSS]:
        raise ValueError(f"不支持的存储类型: {storage_type}")
    
    DEFAULT_STORAGE_TYPE = storage_type
    logger.info(f"默认存储类型已设置为: {storage_type}")


def get_default_storage_type() -> str:
    """
    获取当前默认存储类型
    
    Returns:
        当前默认存储类型
    """
    return DEFAULT_STORAGE_TYPE


def is_oss_available() -> bool:
    """
    检查OSS存储是否可用
    
    Returns:
        OSS是否可用
    """
    try:
        from kengine.io.oss_config import oss_config_manager
        return oss_config_manager.get_config() is not None
    except ImportError:
        return False
    except Exception:
        return False


def get_storage_info() -> dict:
    """
    获取存储配置信息
    
    Returns:
        存储配置信息字典
    """
    info = {
        'default_storage_type': DEFAULT_STORAGE_TYPE,
        'local_available': True,  # 本地存储总是可用
        'oss_available': is_oss_available(),
        'supported_types': [STORAGE_LOCAL, STORAGE_OSS]
    }
    
    if info['oss_available']:
        try:
            from kengine.io.oss_config import oss_config_manager
            config = oss_config_manager.get_config()
            if config:
                info['oss_config'] = {
                    'bucket_name': config.bucket_name,
                    'region': config.region,
                    'inner_endpoint': config.inner_endpoint,
                    'out_endpoint': config.out_endpoint
                }
        except Exception as e:
            logger.debug(f"获取OSS配置信息失败: {e}")
    
    return info


# 向后兼容的别名
doc_fileio = create_io


# 模块初始化日志
logger.info(f"IO模块初始化完成，默认存储类型: {DEFAULT_STORAGE_TYPE}")
if is_oss_available():
    logger.info("OSS存储可用")
else:
    logger.info("OSS存储不可用，将使用本地存储")
