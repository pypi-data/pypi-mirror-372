"""
网络配置模块

用于配置网络相关设置，包括代理、超时、重试等参数
"""

import os
import httpx
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class NetworkConfig:
    """网络配置类"""
    
    def __init__(self):
        # 从环境变量读取配置
        self.http_proxy = os.getenv('HTTP_PROXY') or os.getenv('http_proxy')
        self.https_proxy = os.getenv('HTTPS_PROXY') or os.getenv('https_proxy')
        self.no_proxy = os.getenv('NO_PROXY') or os.getenv('no_proxy')
        
        # 超时配置 - 优化为更合理的值
        self.connect_timeout = int(os.getenv('CONNECT_TIMEOUT', '10'))  # 减少连接超时
        self.read_timeout = int(os.getenv('READ_TIMEOUT', '200'))      # 减少读取超时
        self.total_timeout = int(os.getenv('TOTAL_TIMEOUT', '200'))    # 减少总超时
        
        # 重试配置
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))          # 减少重试次数
        self.retry_delay = float(os.getenv('RETRY_DELAY', '1.0'))      # 减少重试延迟
        
    def get_httpx_client_config(self) -> Dict[str, Any]:
        """获取 httpx 客户端配置"""
        config = {
            'timeout': httpx.Timeout(
                connect=self.connect_timeout,
                read=self.read_timeout,
                write=self.read_timeout,
                pool=self.total_timeout
            ),
            'limits': httpx.Limits(
                max_keepalive_connections=10,    # 减少保持连接数
                max_connections=50,              # 减少最大连接数
                keepalive_expiry=20              # 减少保持连接时间
            )
        }
        
        # 添加代理配置
        if self.http_proxy or self.https_proxy:
            proxies = {}
            if self.http_proxy:
                proxies['http://'] = self.http_proxy
            if self.https_proxy:
                proxies['https://'] = self.https_proxy
            config['proxies'] = proxies
            
        return config
    
    def get_openai_client_config(self) -> Dict[str, Any]:
        """获取 OpenAI 客户端配置"""
        config = {
            'timeout': self.total_timeout,
            'max_retries': self.max_retries
        }
        
        # OpenAI 客户端暂不支持直接设置 httpx 客户端
        # 代理配置需要通过环境变量设置
        
        return config
    
    def test_openai_connectivity(self) -> bool:
        """测试 OpenAI API 连接性"""
        try:
            import httpx
            
            config = self.get_httpx_client_config()
            with httpx.Client(**config) as client:
                # 测试连接到 OpenAI API
                # todo 使用了代理， 测试 openai 的网络无意义
                response = client.get('https://api.openai.com/v1/models', 
                                    headers={'User-Agent': 'connectivity-test'})
                
                if response.status_code in [200, 401]:  # 200成功，401未授权但能连通
                    logger.info("OpenAI API 连接正常")
                    return True
                else:
                    logger.warning(f"OpenAI API 连接异常，状态码: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"OpenAI API 连接测试失败: {e}")
            return False
    
    def log_config(self):
        """打印当前网络配置"""
        logger.debug("=== 网络配置信息 ===")
        logger.debug(f"HTTP 代理: {self.http_proxy or '未设置'}")
        logger.debug(f"HTTPS 代理: {self.https_proxy or '未设置'}")
        logger.debug(f"连接超时: {self.connect_timeout}秒")
        logger.debug(f"读取超时: {self.read_timeout}秒")
        logger.debug(f"总超时: {self.total_timeout}秒")
        logger.debug(f"最大重试: {self.max_retries}次")


# 全局网络配置实例
network_config = NetworkConfig()


def apply_network_optimizations():
    """应用网络优化设置"""
    
    # 设置 OpenAI 客户端的网络配置
    try:
        import openai
        
        # 获取配置
        config = network_config.get_openai_client_config()
        
        # 应用配置到 OpenAI 客户端
        if 'timeout' in config:
            openai.timeout = config['timeout']
        if 'max_retries' in config:
            openai.max_retries = config['max_retries']
        if 'http_client' in config:
            openai.http_client = config['http_client']
            
        logger.info("OpenAI 网络配置已应用")
        
    except ImportError:
        logger.warning("OpenAI 库未安装，跳过配置")
    except Exception as e:
        logger.error(f"应用 OpenAI 网络配置失败: {e}")


# 在模块导入时自动应用网络优化
apply_network_optimizations() 