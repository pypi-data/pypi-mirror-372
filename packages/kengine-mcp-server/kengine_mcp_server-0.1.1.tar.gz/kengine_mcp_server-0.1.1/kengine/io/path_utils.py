"""
OSS路径处理工具函数

提供OSS存储路径的标准化、验证和转换功能
"""
import os
import re
from typing import Optional, Tuple
from urllib.parse import quote, unquote


class OSSPathUtils:
    """OSS路径处理工具类"""
    
    # OSS对象键的限制
    MAX_KEY_LENGTH = 1024
    INVALID_CHARS = ['\\', '\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07', 
                     '\x08', '\x09', '\x0a', '\x0b', '\x0c', '\x0d', '\x0e', '\x0f']
    
    @staticmethod
    def normalize_path(path: str) -> str:
        """
        标准化OSS路径
        
        Args:
            path: 原始路径
            
        Returns:
            标准化后的路径
        """
        if not path:
            return ""
        
        # 移除开头的斜杠
        path = path.lstrip('/')
        
        # 标准化路径分隔符
        path = path.replace('\\', '/')
        
        # 移除多余的斜杠
        path = re.sub(r'/+', '/', path)
        
        # 移除结尾的斜杠（除非是根目录）
        if path.endswith('/') and len(path) > 1:
            path = path.rstrip('/')
        
        return path
    
    @staticmethod
    def validate_path(path: str) -> Tuple[bool, Optional[str]]:
        """
        验证OSS路径是否有效
        
        Args:
            path: 要验证的路径
            
        Returns:
            (是否有效, 错误信息)
        """
        if not path:
            return False, "路径不能为空"
        
        # 检查长度
        if len(path) > OSSPathUtils.MAX_KEY_LENGTH:
            return False, f"路径长度不能超过{OSSPathUtils.MAX_KEY_LENGTH}字符"
        
        # 检查无效字符
        for char in OSSPathUtils.INVALID_CHARS:
            if char in path:
                return False, f"路径包含无效字符: {repr(char)}"
        
        # 检查是否以../开头或包含/../
        if path.startswith('../') or '/../' in path:
            return False, "路径不能包含相对路径引用(../)"
        
        return True, None
    
    @staticmethod
    def join_path(*parts: str) -> str:
        """
        连接多个路径部分
        
        Args:
            *parts: 路径部分
            
        Returns:
            连接后的路径
        """
        if not parts:
            return ""
        
        # 过滤空部分
        valid_parts = [part for part in parts if part]
        if not valid_parts:
            return ""
        
        # 连接路径
        path = '/'.join(valid_parts)
        
        # 标准化
        return OSSPathUtils.normalize_path(path)
    
    @staticmethod
    def split_path(path: str) -> Tuple[str, str]:
        """
        分割路径为目录和文件名
        
        Args:
            path: 完整路径
            
        Returns:
            (目录路径, 文件名)
        """
        path = OSSPathUtils.normalize_path(path)
        if not path:
            return "", ""
        
        if '/' not in path:
            return "", path
        
        parts = path.rsplit('/', 1)
        return parts[0], parts[1]
    
    @staticmethod
    def get_extension(path: str) -> str:
        """
        获取文件扩展名
        
        Args:
            path: 文件路径
            
        Returns:
            文件扩展名（包含点号）
        """
        _, filename = OSSPathUtils.split_path(path)
        if '.' not in filename:
            return ""
        
        return '.' + filename.rsplit('.', 1)[1]
    
    @staticmethod
    def change_extension(path: str, new_ext: str) -> str:
        """
        更改文件扩展名
        
        Args:
            path: 原始路径
            new_ext: 新扩展名（可以包含或不包含点号）
            
        Returns:
            更改扩展名后的路径
        """
        if not new_ext:
            return path
        
        # 确保扩展名以点号开头
        if not new_ext.startswith('.'):
            new_ext = '.' + new_ext
        
        dir_path, filename = OSSPathUtils.split_path(path)
        
        # 移除原有扩展名
        if '.' in filename:
            filename = filename.rsplit('.', 1)[0]
        
        # 添加新扩展名
        new_filename = filename + new_ext
        
        return OSSPathUtils.join_path(dir_path, new_filename)
    
    @staticmethod
    def url_encode_path(path: str) -> str:
        """
        URL编码路径（用于生成签名URL）
        
        Args:
            path: 原始路径
            
        Returns:
            URL编码后的路径
        """
        return quote(path, safe='/')
    
    @staticmethod
    def url_decode_path(encoded_path: str) -> str:
        """
        URL解码路径
        
        Args:
            encoded_path: URL编码的路径
            
        Returns:
            解码后的路径
        """
        return unquote(encoded_path)
    
    @staticmethod
    def is_directory_path(path: str) -> bool:
        """
        判断路径是否为目录路径
        
        Args:
            path: 路径
            
        Returns:
            是否为目录路径
        """
        return path.endswith('/')
    
    @staticmethod
    def ensure_directory_path(path: str) -> str:
        """
        确保路径以目录形式结尾
        
        Args:
            path: 原始路径
            
        Returns:
            目录路径
        """
        path = OSSPathUtils.normalize_path(path)
        if path and not path.endswith('/'):
            path += '/'
        return path
    
    @staticmethod
    def generate_unique_path(base_path: str, extension: str = "") -> str:
        """
        生成唯一路径（添加时间戳）
        
        Args:
            base_path: 基础路径
            extension: 文件扩展名
            
        Returns:
            唯一路径
        """
        import time
        import uuid
        
        timestamp = int(time.time() * 1000)  # 毫秒时间戳
        unique_id = str(uuid.uuid4())[:8]    # 短UUID
        
        dir_path, filename = OSSPathUtils.split_path(base_path)
        
        # 移除原有扩展名
        if '.' in filename:
            filename = filename.rsplit('.', 1)[0]
        
        # 构建唯一文件名
        unique_filename = f"{filename}_{timestamp}_{unique_id}"
        
        if extension:
            if not extension.startswith('.'):
                extension = '.' + extension
            unique_filename += extension
        
        return OSSPathUtils.join_path(dir_path, unique_filename)
    
    @staticmethod
    def get_relative_path(full_path: str, base_path: str) -> str:
        """
        获取相对于基础路径的相对路径
        
        Args:
            full_path: 完整路径
            base_path: 基础路径
            
        Returns:
            相对路径
        """
        full_path = OSSPathUtils.normalize_path(full_path)
        base_path = OSSPathUtils.normalize_path(base_path)
        
        if not base_path:
            return full_path
        
        # 确保基础路径以/结尾
        if not base_path.endswith('/'):
            base_path += '/'
        
        if full_path.startswith(base_path):
            return full_path[len(base_path):]
        
        return full_path
    
    @staticmethod
    def build_storage_path(domain: str, repo_name: str, filename: str, 
                          version: Optional[str] = None) -> str:
        """
        构建标准的存储路径
        
        Args:
            domain: 领域名称
            repo_name: 仓库名称
            filename: 文件名
            version: 版本号（可选）
            
        Returns:
            标准存储路径
        """
        parts = [domain, repo_name]
        
        if version:
            parts.append(f"v{version}")
        
        parts.append(filename)
        
        return OSSPathUtils.join_path(*parts)


# 便捷函数
def normalize_oss_path(path: str) -> str:
    """标准化OSS路径的便捷函数"""
    return OSSPathUtils.normalize_path(path)


def validate_oss_path(path: str) -> Tuple[bool, Optional[str]]:
    """验证OSS路径的便捷函数"""
    return OSSPathUtils.validate_path(path)


def join_oss_path(*parts: str) -> str:
    """连接OSS路径的便捷函数"""
    return OSSPathUtils.join_path(*parts)


def build_document_storage_path(domain: str, repo_name: str, filename: str, 
                               version: Optional[str] = None) -> str:
    """构建文档存储路径的便捷函数"""
    return OSSPathUtils.build_storage_path(domain, repo_name, filename, version)