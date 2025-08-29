"""
OSS配置管理模块

提供京东云OSS的配置管理功能，支持从环境变量或配置文件读取OSS参数
"""
import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class OSSConfig:
    """OSS配置类"""
    access_key: str
    secret_key: str
    inner_endpoint: str
    out_endpoint: str
    bucket_name: str
    region: str = "cn-north-1"
    
    @classmethod
    def from_env(cls) -> 'OSSConfig':
        """
        从环境变量创建OSS配置
        
        Returns:
            OSSConfig实例
            
        Raises:
            ValueError: 当必需的环境变量缺失时
        """
        access_key = os.getenv('OSS_ACCESS_KEY')
        secret_key = os.getenv('OSS_SECRET_KEY')
        inner_endpoint = os.getenv('OSS_INNER_ENDPOINT')
        out_endpoint = os.getenv('OSS_OUT_ENDPOINT')
        bucket_name = os.getenv('OSS_BUCKET_NAME')
        region = os.getenv('OSS_REGION', 'cn-north-1')
        
        if not all([access_key, secret_key, inner_endpoint, out_endpoint, bucket_name]):
            missing = []
            if not access_key: missing.append('OSS_ACCESS_KEY')
            if not secret_key: missing.append('OSS_SECRET_KEY')
            if not inner_endpoint: missing.append('OSS_INNER_ENDPOINT')
            if not out_endpoint: missing.append('OSS_OUT_ENDPOINT')
            if not bucket_name: missing.append('OSS_BUCKET_NAME')
            raise ValueError(f"缺少必需的环境变量: {', '.join(missing)}")
        
        return cls(
            access_key=access_key,
            secret_key=secret_key,
            inner_endpoint=inner_endpoint,
            out_endpoint=out_endpoint,
            bucket_name=bucket_name,
            region=region
        )
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> 'OSSConfig':
        """
        从字典创建OSS配置
        
        Args:
            config_dict: 包含OSS配置的字典
            
        Returns:
            OSSConfig实例
        """
        return cls(
            access_key=config_dict['accessKey'],
            secret_key=config_dict['secretKey'],
            inner_endpoint=config_dict['innerEndpoint'],
            out_endpoint=config_dict['outEndpoint'],
            bucket_name=config_dict['bucketName'],
            region=config_dict.get('region', 'cn-north-1')
        )
    
    def get_endpoint(self, use_internal: bool = True) -> str:
        """
        获取端点URL
        
        Args:
            use_internal: 是否使用内网端点
            
        Returns:
            端点URL
        """
        endpoint = self.inner_endpoint if use_internal else self.out_endpoint
        if not endpoint.startswith('http'):
            endpoint = f"https://{endpoint}"
        return endpoint
    
    def validate(self) -> bool:
        """
        验证配置是否有效
        
        Returns:
            配置是否有效
        """
        return all([
            self.access_key,
            self.secret_key,
            self.inner_endpoint,
            self.out_endpoint,
            self.bucket_name
        ])


class OSSConfigManager:
    """OSS配置管理器"""
    
    def __init__(self):
        self._config: Optional[OSSConfig] = None
    
    def load_config(self, config_dict: Optional[dict] = None) -> OSSConfig:
        """
        加载OSS配置
        
        Args:
            config_dict: 可选的配置字典，如果不提供则从环境变量读取
            
        Returns:
            OSSConfig实例
        """
        if config_dict:
            self._config = OSSConfig.from_dict(config_dict)
        else:
            self._config = OSSConfig.from_env()
        
        if not self._config.validate():
            raise ValueError("OSS配置验证失败")
        
        return self._config
    
    def get_config(self) -> Optional[OSSConfig]:
        """
        获取当前配置
        
        Returns:
            当前的OSS配置，如果未加载则返回None
        """
        return self._config
    
    def test_connection(self) -> bool:
        """
        测试OSS连接
        
        Returns:
            连接是否成功
        """
        if not self._config:
            return False
        
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            # 创建S3客户端
            s3_client = boto3.client(
                's3',
                aws_access_key_id=self._config.access_key,
                aws_secret_access_key=self._config.secret_key,
                endpoint_url=self._config.get_endpoint(),
                region_name=self._config.region
            )
            
            # 尝试列出存储桶来测试连接
            s3_client.head_bucket(Bucket=self._config.bucket_name)
            return True
            
        except (ClientError, Exception):
            return False


# 全局配置管理器实例
oss_config_manager = OSSConfigManager()


def get_oss_config() -> Optional[OSSConfig]:
    """
    获取全局OSS配置
    
    Returns:
        OSS配置实例
    """
    return oss_config_manager.get_config()


def load_oss_config(config_dict: Optional[dict] = None) -> OSSConfig:
    """
    加载全局OSS配置
    
    Args:
        config_dict: 可选的配置字典
        
    Returns:
        OSS配置实例
    """
    return oss_config_manager.load_config(config_dict)