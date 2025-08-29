
from abc import ABC, abstractmethod
from typing import Any, Optional

class IO(ABC):
    """IO 接口定义，支持上下文管理器"""
    
    @abstractmethod
    def read(self, path: str) -> str:
        """
        读取文件内容
        
        Args:
            path: 文件路径
            
        Returns:
            文件内容字符串
        """
        pass
    
    @abstractmethod
    def write(self, path: str, content: str) -> str:
        """
        写入文件内容
        
        Args:
            path: 文件路径
            content: 要写入的内容
            
        Returns:
            操作结果信息
        """
        pass
    
    @abstractmethod
    def exists(self, path: str) -> bool:
        """
        判断文件是否存在
        
        Args:
            path: 文件路径
            
        Returns:
            文件是否存在
        """
        pass
    
    def __enter__(self) -> 'IO':
        """
        进入上下文管理器
        
        Returns:
            IO 实例本身
        """
        return self
    
    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> None:
        """
        退出上下文管理器
        
        Args:
            exc_type: 异常类型
            exc_val: 异常值
            exc_tb: 异常回溯信息
        """
        # 默认实现不需要特殊清理操作
        pass
