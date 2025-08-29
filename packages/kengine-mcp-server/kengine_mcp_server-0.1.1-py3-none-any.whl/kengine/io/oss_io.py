"""
OSS对象存储IO实现

基于京东云OSS的文件读写操作实现
"""
import logging
from typing import Optional, Dict, Any, BinaryIO
from io import BytesIO, StringIO
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from botocore.config import Config

from .io import IO
from kengine.io.oss_config import OSSConfigManager, OSSConfig, oss_config_manager
from .path_utils import OSSPathUtils, normalize_oss_path, validate_oss_path

logger = logging.getLogger(__name__)


class OSSIOError(Exception):
    """OSS IO操作异常"""
    pass


class OSSIO(IO):
    """OSS对象存储IO实现"""
    
    def __init__(self, config: Optional[OSSConfig] = None, use_internal: bool = True):
        """
        初始化OSSIO实例
        
        Args:
            config: OSS配置，如果为None则使用全局配置
            use_internal: 是否使用内网端点
        """
        self.config = config or oss_config_manager.get_config()
        if not self.config:
            raise OSSIOError("OSS配置未初始化，请先配置OSS参数")
        
        self.use_internal = use_internal
        self._client = None
        self._setup_client()
    
    def _setup_client(self):
        """设置boto3 S3客户端"""
        try:
            self._client = self._create_client(self.use_internal)
            
            endpoint_url = self.config.inner_endpoint if self.use_internal else self.config.out_endpoint
            logger.info(f"OSS客户端初始化成功，使用{'内网' if self.use_internal else '外网'}端点: {endpoint_url}")
            
        except NoCredentialsError:
            logger.error("OSS认证信息缺失")
            raise OSSIOError("OSS认证信息缺失，请检查access_key和secret_key配置")
        except Exception as e:
            logger.error(f"OSS客户端初始化失败: {e}")
            raise OSSIOError(f"OSS客户端初始化失败: {e}")
    
    def _validate_and_normalize_path(self, path: str) -> str:
        """验证并标准化路径"""
        if not path:
            raise OSSIOError("路径不能为空")
        
        # 标准化路径
        normalized_path = normalize_oss_path(path)
        
        # 验证路径
        is_valid, error_msg = validate_oss_path(normalized_path)
        if not is_valid:
            raise OSSIOError(f"路径验证失败: {error_msg}")
        
        return normalized_path
    
    def _handle_client_error(self, error: ClientError, operation: str, path: str):
        """处理boto3客户端错误"""
        error_code = error.response.get('Error', {}).get('Code', 'Unknown')
        error_message = error.response.get('Error', {}).get('Message', str(error))
        
        if error_code == 'NoSuchKey':
            raise OSSIOError(f"文件不存在: {path}")
        elif error_code == 'NoSuchBucket':
            raise OSSIOError(f"存储桶不存在: {self.config.bucket_name}")
        elif error_code == 'AccessDenied':
            raise OSSIOError(f"访问被拒绝，请检查权限配置")
        elif error_code == 'InvalidAccessKeyId':
            raise OSSIOError(f"无效的AccessKey")
        elif error_code == 'SignatureDoesNotMatch':
            raise OSSIOError(f"签名不匹配，请检查SecretKey")
        else:
            raise OSSIOError(f"{operation}操作失败 [{error_code}]: {error_message}")
    
    def read(self, path: str) -> str:
        """
        从OSS读取文件内容
        
        Args:
            path: OSS对象键路径
            
        Returns:
            文件内容字符串
            
        Raises:
            OSSIOError: 读取失败时抛出异常
        """
        normalized_path = self._validate_and_normalize_path(path)
        
        try:
            logger.debug(f"开始从OSS读取文件: {normalized_path}")
            
            response = self._client.get_object(
                Bucket=self.config.bucket_name,
                Key=normalized_path
            )
            
            # 读取内容并解码为字符串
            content = response['Body'].read().decode('utf-8')
            
            logger.info(f"成功从OSS读取文件: {normalized_path}, 大小: {len(content)} 字符")
            return content
            
        except ClientError as e:
            logger.error(f"OSS读取文件失败: {normalized_path}, 错误: {e}")
            self._handle_client_error(e, "读取", normalized_path)
        except UnicodeDecodeError as e:
            logger.error(f"文件解码失败: {normalized_path}, 错误: {e}")
            raise OSSIOError(f"文件解码失败，可能不是文本文件: {normalized_path}")
        except Exception as e:
            logger.error(f"读取文件时发生未知错误: {normalized_path}, 错误: {e}")
            raise OSSIOError(f"读取文件失败: {e}")
    
    def write(self, path: str, content: str) -> str:
        """
        向OSS写入文件内容
        
        Args:
            path: OSS对象键路径
            content: 要写入的内容
            
        Returns:
            操作结果信息（返回标准化后的路径）
            
        Raises:
            OSSIOError: 写入失败时抛出异常
        """
        normalized_path = self._validate_and_normalize_path(path)
        
        try:
            logger.debug(f"开始向OSS写入文件: {normalized_path}")
            
            # 将字符串内容编码为字节
            content_bytes = content.encode('utf-8')
            
            # 上传到OSS - 使用最简单的参数以兼容京东云OSS
            self._client.put_object(
                Bucket=self.config.bucket_name,
                Key=normalized_path,
                Body=content_bytes
            )
            
            logger.info(f"成功向OSS写入文件: {normalized_path}, 大小: {len(content_bytes)} 字节")
            return normalized_path
            
        except ClientError as e:
            logger.error(f"OSS写入文件失败: {normalized_path}, 错误: {e}")
            self._handle_client_error(e, "写入", normalized_path)
        except Exception as e:
            logger.error(f"写入文件时发生未知错误: {normalized_path}, 错误: {e}")
            raise OSSIOError(f"写入文件失败: {e}")
    
    def read_binary(self, path: str) -> bytes:
        """
        从OSS读取二进制文件内容
        
        Args:
            path: OSS对象键路径
            
        Returns:
            文件二进制内容
        """
        normalized_path = self._validate_and_normalize_path(path)
        
        try:
            logger.debug(f"开始从OSS读取二进制文件: {normalized_path}")
            
            response = self._client.get_object(
                Bucket=self.config.bucket_name,
                Key=normalized_path
            )
            
            content = response['Body'].read()
            
            logger.info(f"成功从OSS读取二进制文件: {normalized_path}, 大小: {len(content)} 字节")
            return content
            
        except ClientError as e:
            logger.error(f"OSS读取二进制文件失败: {normalized_path}, 错误: {e}")
            self._handle_client_error(e, "读取", normalized_path)
        except Exception as e:
            logger.error(f"读取二进制文件时发生未知错误: {normalized_path}, 错误: {e}")
            raise OSSIOError(f"读取二进制文件失败: {e}")
    
    def write_binary(self, path: str, content: bytes, content_type: str = 'application/octet-stream') -> str:
        """
        向OSS写入二进制文件内容
        
        Args:
            path: OSS对象键路径
            content: 要写入的二进制内容
            content_type: 内容类型
            
        Returns:
            操作结果信息（返回标准化后的路径）
        """
        normalized_path = self._validate_and_normalize_path(path)
        
        try:
            logger.debug(f"开始向OSS写入二进制文件: {normalized_path}")
            
            self._client.put_object(
                Bucket=self.config.bucket_name,
                Key=normalized_path,
                Body=content,
                ContentType=content_type
            )
            
            logger.info(f"成功向OSS写入二进制文件: {normalized_path}, 大小: {len(content)} 字节")
            return normalized_path
            
        except ClientError as e:
            logger.error(f"OSS写入二进制文件失败: {normalized_path}, 错误: {e}")
            self._handle_client_error(e, "写入", normalized_path)
        except Exception as e:
            logger.error(f"写入二进制文件时发生未知错误: {normalized_path}, 错误: {e}")
            raise OSSIOError(f"写入二进制文件失败: {e}")
    
    def exists(self, path: str) -> bool:
        """
        检查OSS中文件是否存在
        
        Args:
            path: OSS对象键路径
            
        Returns:
            文件是否存在
        """
        normalized_path = self._validate_and_normalize_path(path)
        
        try:
            self._client.head_object(
                Bucket=self.config.bucket_name,
                Key=normalized_path
            )
            return True
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'NoSuchKey':
                return False
            else:
                logger.error(f"检查文件存在性时发生错误: {normalized_path}, 错误: {e}")
                raise OSSIOError(f"检查文件存在性失败: {e}")
        except Exception as e:
            logger.error(f"检查文件存在性时发生未知错误: {normalized_path}, 错误: {e}")
            raise OSSIOError(f"检查文件存在性失败: {e}")
    
    def delete(self, path: str) -> bool:
        """
        删除OSS中的文件
        
        Args:
            path: OSS对象键路径
            
        Returns:
            是否删除成功
        """
        normalized_path = self._validate_and_normalize_path(path)
        
        try:
            logger.debug(f"开始删除OSS文件: {normalized_path}")
            
            self._client.delete_object(
                Bucket=self.config.bucket_name,
                Key=normalized_path
            )
            
            logger.info(f"成功删除OSS文件: {normalized_path}")
            return True
            
        except ClientError as e:
            logger.error(f"OSS删除文件失败: {normalized_path}, 错误: {e}")
            self._handle_client_error(e, "删除", normalized_path)
        except Exception as e:
            logger.error(f"删除文件时发生未知错误: {normalized_path}, 错误: {e}")
            raise OSSIOError(f"删除文件失败: {e}")
    
    def get_file_info(self, path: str) -> Dict[str, Any]:
        """
        获取OSS文件信息
        
        Args:
            path: OSS对象键路径
            
        Returns:
            文件信息字典
        """
        normalized_path = self._validate_and_normalize_path(path)
        
        try:
            response = self._client.head_object(
                Bucket=self.config.bucket_name,
                Key=normalized_path
            )
            
            return {
                'path': normalized_path,
                'size': response.get('ContentLength', 0),
                'content_type': response.get('ContentType', ''),
                'last_modified': response.get('LastModified'),
                'etag': response.get('ETag', '').strip('"'),
                'metadata': response.get('Metadata', {})
            }
            
        except ClientError as e:
            logger.error(f"获取OSS文件信息失败: {normalized_path}, 错误: {e}")
            self._handle_client_error(e, "获取信息", normalized_path)
        except Exception as e:
            logger.error(f"获取文件信息时发生未知错误: {normalized_path}, 错误: {e}")
            raise OSSIOError(f"获取文件信息失败: {e}")
    
    def list_objects(self, prefix: str = "", max_keys: int = 1000) -> list:
        """
        列出OSS中的对象
        
        Args:
            prefix: 对象键前缀
            max_keys: 最大返回数量
            
        Returns:
            对象信息列表
        """
        try:
            if prefix:
                prefix = normalize_oss_path(prefix)
            
            response = self._client.list_objects_v2(
                Bucket=self.config.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            objects = []
            for obj in response.get('Contents', []):
                objects.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'etag': obj['ETag'].strip('"')
                })
            
            return objects
            
        except ClientError as e:
            logger.error(f"列出OSS对象失败, 前缀: {prefix}, 错误: {e}")
            self._handle_client_error(e, "列出对象", prefix)
        except Exception as e:
            logger.error(f"列出对象时发生未知错误, 前缀: {prefix}, 错误: {e}")
            raise OSSIOError(f"列出对象失败: {e}")
    
    def switch_endpoint(self, use_internal: bool):
        """
        切换内外网端点
        
        Args:
            use_internal: 是否使用内网端点
        """
        if self.use_internal != use_internal:
            self.use_internal = use_internal
            self._setup_client()
            logger.info(f"已切换到{'内网' if use_internal else '外网'}端点")
    
    def generate_presigned_url(self, path: str, expiration: int = 63072000,
                              http_method: str = 'GET', use_external: bool = True) -> str:
        """
        生成预签名URL
        
        Args:
            path: OSS对象键路径
            expiration: 过期时间（秒），默认2年（63072000秒）
            http_method: HTTP方法，默认GET
            use_external: 是否使用外网端点生成URL
            
        Returns:
            预签名URL
        """
        normalized_path = self._validate_and_normalize_path(path)
        
        try:
            # 如果需要使用外网端点且当前是内网，临时切换
            original_use_internal = self.use_internal
            temp_client = None
            
            if use_external and self.use_internal:
                # 创建临时的外网客户端
                temp_client = self._create_client(use_internal=False)
                client_to_use = temp_client
            else:
                client_to_use = self._client
            
            logger.debug(f"开始生成预签名URL: {normalized_path}, 过期时间: {expiration}秒")
            
            # 生成预签名URL
            presigned_url = client_to_use.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.config.bucket_name,
                    'Key': normalized_path
                },
                ExpiresIn=expiration,
                HttpMethod=http_method
            )
            
            logger.info(f"成功生成预签名URL: {normalized_path}, 使用{'外网' if use_external else '内网'}端点")
            return presigned_url
            
        except ClientError as e:
            logger.error(f"生成预签名URL失败: {normalized_path}, 错误: {e}")
            self._handle_client_error(e, "生成预签名URL", normalized_path)
        except Exception as e:
            logger.error(f"生成预签名URL时发生未知错误: {normalized_path}, 错误: {e}")
            raise OSSIOError(f"生成预签名URL失败: {e}")
    
    def generate_upload_presigned_url(self, path: str, expiration: int = 3600,
                                     content_type: str = None, use_external: bool = True) -> Dict[str, Any]:
        """
        生成上传预签名URL
        
        Args:
            path: OSS对象键路径
            expiration: 过期时间（秒），默认1小时
            content_type: 内容类型限制
            use_external: 是否使用外网端点生成URL
            
        Returns:
            包含预签名URL和字段的字典
        """
        normalized_path = self._validate_and_normalize_path(path)
        
        try:
            # 如果需要使用外网端点且当前是内网，创建临时客户端
            if use_external and self.use_internal:
                client_to_use = self._create_client(use_internal=False)
            else:
                client_to_use = self._client
            
            logger.debug(f"开始生成上传预签名URL: {normalized_path}, 过期时间: {expiration}秒")
            
            # 准备上传参数
            conditions = []
            if content_type:
                conditions.append(["eq", "$Content-Type", content_type])
            
            # 生成预签名POST数据
            presigned_post = client_to_use.generate_presigned_post(
                Bucket=self.config.bucket_name,
                Key=normalized_path,
                ExpiresIn=expiration,
                Conditions=conditions
            )
            
            logger.info(f"成功生成上传预签名URL: {normalized_path}, 使用{'外网' if use_external else '内网'}端点")
            return presigned_post
            
        except ClientError as e:
            logger.error(f"生成上传预签名URL失败: {normalized_path}, 错误: {e}")
            self._handle_client_error(e, "生成上传预签名URL", normalized_path)
        except Exception as e:
            logger.error(f"生成上传预签名URL时发生未知错误: {normalized_path}, 错误: {e}")
            raise OSSIOError(f"生成上传预签名URL失败: {e}")
    
    def generate_download_url(self, path: str, filename: str = None,
                             expiration: int = 63072000, use_external: bool = True) -> str:
        """
        生成下载URL（带文件名）
        
        Args:
            path: OSS对象键路径
            filename: 下载时的文件名
            expiration: 过期时间（秒），默认2年
            use_external: 是否使用外网端点生成URL
            
        Returns:
            下载URL
        """
        normalized_path = self._validate_and_normalize_path(path)
        
        try:
            # 如果需要使用外网端点且当前是内网，创建临时客户端
            if use_external and self.use_internal:
                client_to_use = self._create_client(use_internal=False)
            else:
                client_to_use = self._client
            
            logger.debug(f"开始生成下载URL: {normalized_path}, 文件名: {filename}")
            
            # 准备参数
            params = {
                'Bucket': self.config.bucket_name,
                'Key': normalized_path
            }
            
            # 如果指定了文件名，添加响应头
            if filename:
                params['ResponseContentDisposition'] = f'attachment; filename="{filename}"'
            
            # 生成预签名URL
            download_url = client_to_use.generate_presigned_url(
                'get_object',
                Params=params,
                ExpiresIn=expiration
            )
            
            logger.info(f"成功生成下载URL: {normalized_path}, 使用{'外网' if use_external else '内网'}端点")
            return download_url
            
        except ClientError as e:
            logger.error(f"生成下载URL失败: {normalized_path}, 错误: {e}")
            self._handle_client_error(e, "生成下载URL", normalized_path)
        except Exception as e:
            logger.error(f"生成下载URL时发生未知错误: {normalized_path}, 错误: {e}")
            raise OSSIOError(f"生成下载URL失败: {e}")
    
    def _create_client(self, use_internal: bool = None):
        """
        创建boto3客户端（内部方法）
        
        Args:
            use_internal: 是否使用内网端点，None时使用实例设置
            
        Returns:
            boto3 S3客户端
        """
        if use_internal is None:
            use_internal = self.use_internal
            
        # 选择端点
        endpoint_url = self.config.inner_endpoint if use_internal else self.config.out_endpoint
        
        # 确保端点URL包含协议前缀
        if endpoint_url and not endpoint_url.startswith(('http://', 'https://')):
            endpoint_url = f"https://{endpoint_url}"
        
        # 配置boto3客户端 - 禁用校验和以兼容京东云OSS
        boto_config = Config(
            region_name=self.config.region,
            retries={'max_attempts': 3, 'mode': 'adaptive'},
            max_pool_connections=50,
            s3={
                'addressing_style': 'path',
                'use_accelerate_endpoint': False,
                'use_dualstack_endpoint': False,
            },
            signature_version='s3v4',
            # 禁用校验和验证以兼容京东云OSS
            disable_request_compression=True
        )
        
        # 设置环境变量禁用校验和
        import os
        os.environ['AWS_S3_DISABLE_MULTIREGION_ACCESS_POINTS'] = 'true'
        
        return boto3.client(
            's3',
            aws_access_key_id=self.config.access_key,
            aws_secret_access_key=self.config.secret_key,
            endpoint_url=endpoint_url,
            config=boto_config,
            # 禁用SSL验证校验和
            use_ssl=True
        )


# 工厂函数
def create_oss_io(config: Optional[OSSConfig] = None, use_internal: bool = True) -> OSSIO:
    """
    创建OSSIO实例的工厂函数
    
    Args:
        config: OSS配置
        use_internal: 是否使用内网端点
        
    Returns:
        OSSIO实例
    """
    return OSSIO(config=config, use_internal=use_internal)


def create_document_oss_io(domain: str, repo_name: str, version: Optional[str] = None) -> OSSIO:
    """
    创建用于文档存储的OSSIO实例
    
    Args:
        domain: 领域名称
        repo_name: 仓库名称  
        version: 版本号
        
    Returns:
        OSSIO实例
    """
    # 这里可以根据需要添加特定的配置逻辑
    # 比如根据domain/repo设置不同的路径前缀等
    return create_oss_io()