from pathlib import Path
from .io import IO
import os
from ..utils.path_utils import sanitize_path



_project_root = os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(
                            os.path.abspath(__file__))))

class FileIO(IO):
    """文件 IO 实现"""
    
    def __init__(self, base_dir: str):
        """
        初始化 FileIO 实例
        
        Args:
            base_dir: 文件操作的基础目录
        """
        self.base_dir = Path(base_dir).resolve()
    
    def _get_safe_path(self, path: str) -> Path:
        """
        获取安全的绝对路径，防止路径遍历攻击
        
        Args:
            path: 相对路径
            
        Returns:
            安全的绝对路径
            
        Raises:
            ValueError: 当路径不安全时抛出异常
        """
        # 将相对路径与 base_dir 结合
        if path[0] == '/': 
            path = path.lstrip('/')
        full_path = (self.base_dir / path).resolve()
        
        # 检查路径是否在 base_dir 范围内，防止路径遍历攻击
        try:
            full_path.relative_to(self.base_dir)
        except ValueError:
            raise ValueError(f"路径 '{path}' 超出了基础目录范围，可能存在安全风险")
        
        return full_path
    
    def read(self, path: str) -> str:
        """
        读取文件内容
        
        Args:
            path: 相对于 base_dir 的文件路径
            
        Returns:
            文件内容字符串
        """
        safe_path = self._get_safe_path(path)
        with open(safe_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def write(self, path: str, content: str) -> str:
        """
        写入文件内容
        
        Args:
            path: 相对于 base_dir 的文件路径
            content: 要写入的内容
            
        Returns:
            操作结果信息
        """
        path = sanitize_path(path)
        safe_path = self._get_safe_path(path)
        
        # 确保目录存在
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(safe_path, 'w', encoding='utf-8') as f:
            f.write(content)
        if path.startswith(_project_root):
            path = path[len(_project_root):]
        if path.startswith('/') or path.startswith('\\'):
            path = path[1:]
        return path
    
    def exists(self, path: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            path: 相对于 base_dir 的文件路径
            
        Returns:
            文件是否存在
        """
        try:
            safe_path = self._get_safe_path(path)
            return safe_path.exists()
        except (ValueError, OSError):
            return False
    
    def delete(self, path: str) -> bool:
        """
        删除文件
        
        Args:
            path: 相对于 base_dir 的文件路径
            
        Returns:
            删除是否成功
        """
        try:
            safe_path = self._get_safe_path(path)
            if safe_path.exists():
                safe_path.unlink()
                return True
            return False
        except (ValueError, OSError):
            return False
    
    def generate_presigned_url(self, path: str, operation: str = "GET",
                             expiration: int = 3600, use_external: bool = False) -> str:
        """
        生成预签名URL（本地存储不支持此功能）
        
        Args:
            path: 文件路径
            operation: 操作类型 (GET/PUT)
            expiration: URL有效期（秒）
            use_external: 是否使用外网端点
            
        Returns:
            预签名URL
            
        Raises:
            NotImplementedError: 本地存储不支持预签名URL
        """
        raise NotImplementedError("本地存储不支持预签名URL功能")
    
    def generate_download_url(self, path: str, filename: str = None,
                            expiration: int = 3600, use_external: bool = False) -> str:
        """
        生成下载URL（本地存储不支持此功能）
        
        Args:
            path: 文件路径
            filename: 下载时的文件名
            expiration: URL有效期（秒）
            use_external: 是否使用外网端点
            
        Returns:
            下载URL
            
        Raises:
            NotImplementedError: 本地存储不支持下载URL
        """
        raise NotImplementedError("本地存储不支持下载URL功能")
    
    def switch_endpoint(self, use_internal: bool = True) -> None:
        """
        切换端点（本地存储不支持此功能）
        
        Args:
            use_internal: 是否使用内网端点
            
        Raises:
            NotImplementedError: 本地存储不支持端点切换
        """
        raise NotImplementedError("本地存储不支持端点切换功能")


_project_root = os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(
                            os.path.abspath(__file__))))

# 创建 doc_file 实例，用于操作 docs4demo 目录
def create_doc_file_io(repo_group: str, repo_name: str, version: str = None) -> IO:
    if version:
        base_dir = os.path.join(
            _project_root,
            "docs4demo",
            repo_group,
            f"{repo_name}-{version}")
    else:
        base_dir = os.path.join(
            _project_root,
            "docs4demo",
            repo_group,
            repo_name)
    return FileIO(base_dir=base_dir)
