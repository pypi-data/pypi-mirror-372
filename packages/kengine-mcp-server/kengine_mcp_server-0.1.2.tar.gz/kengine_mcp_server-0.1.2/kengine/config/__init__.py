from dotenv import load_dotenv
# 加载环境变量， 防止在某些场景下无法加载 application_config.py 中的配置
load_dotenv()

from .logging_config import setup_logging
from .application_config import get_application_config

__all__ = [
     'setup_logging',
     'get_application_config'
]

# 导出全局配置实例
config = get_application_config()
