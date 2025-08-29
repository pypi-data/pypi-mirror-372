"""
文本文件读取工具模块

提供多编码容错的文本文件读取功能，支持常见的编码格式自动检测和处理。
"""

import logging
from pathlib import Path
from typing import Optional, List, Tuple
import chardet

logger = logging.getLogger(__name__)

# 常见编码列表，按优先级排序
COMMON_ENCODINGS = [
    'utf-8',
    'utf-8-sig',  # UTF-8 with BOM
    'gbk',
    'gb2312',
    'big5',
    'latin1',
    'cp1252',
    'iso-8859-1'
]


class TextReader:
    """
    文本文件读取器，支持多编码容错处理
    """
    
    def __init__(self, max_file_size: int = 10 * 1024 * 1024):  # 10MB
        """
        初始化文本读取器
        
        Args:
            max_file_size: 最大文件大小限制（字节），默认10MB
        """
        self.max_file_size = max_file_size
    
    def read_text_file(self, file_path: str, max_length: Optional[int] = None) -> Optional[str]:
        """
        读取文本文件内容，自动处理编码问题
        
        Args:
            file_path: 文件路径
            max_length: 最大读取长度，超过则截断
            
        Returns:
            文件内容字符串，读取失败返回None
        """
        path = Path(file_path)
        
        if not path.exists() or not path.is_file():
            logger.warning(f"文件不存在或不是文件: {file_path}")
            return None
        
        # 检查文件大小
        try:
            file_size = path.stat().st_size
            if file_size > self.max_file_size:
                logger.warning(f"文件过大，跳过读取: {file_path} ({file_size} bytes)")
                return None
            
            if file_size == 0:
                logger.info(f"文件为空: {file_path}")
                return ""
                
        except OSError as e:
            logger.error(f"无法获取文件信息，文件路径='{file_path}', 错误: {e}")
            return None
        
        # 尝试读取文件内容
        content = self._read_with_encoding_detection(path)
        
        if content is not None and max_length and len(content) > max_length:
            content = content[:max_length] + "\n... (内容已截断)"
            logger.info(f"文件内容已截断到 {max_length} 字符: {file_path}")
        
        return content
    
    def _read_with_encoding_detection(self, path: Path) -> Optional[str]:
        """
        使用编码检测读取文件
        
        Args:
            path: 文件路径对象
            
        Returns:
            文件内容字符串，读取失败返回None
        """
        # 首先尝试使用chardet检测编码
        detected_encoding = self._detect_encoding(path)
        if detected_encoding:
            content = self._try_read_with_encoding(path, detected_encoding)
            if content is not None:
                logger.debug(f"使用检测到的编码 {detected_encoding} 成功读取: {path}")
                return content
        
        # 如果检测失败，尝试常见编码
        for encoding in COMMON_ENCODINGS:
            content = self._try_read_with_encoding(path, encoding)
            if content is not None:
                logger.debug(f"使用编码 {encoding} 成功读取: {path}")
                return content
        
        logger.error(f"所有编码尝试失败，无法读取文件: {path}")
        return None
    
    def _detect_encoding(self, path: Path) -> Optional[str]:
        """
        检测文件编码
        
        Args:
            path: 文件路径对象
            
        Returns:
            检测到的编码名称，检测失败返回None
        """
        try:
            # 读取文件的前几KB用于编码检测
            with open(path, 'rb') as f:
                raw_data = f.read(min(8192, path.stat().st_size))
            
            if not raw_data:
                return None
            
            result = chardet.detect(raw_data)
            if result and result['encoding'] and result['confidence'] > 0.7:
                return result['encoding']
                
        except Exception as e:
            logger.debug(f"编码检测失败，文件路径='{path}', 错误: {e}")
        
        return None
    
    def _try_read_with_encoding(self, path: Path, encoding: str) -> Optional[str]:
        """
        尝试使用指定编码读取文件
        
        Args:
            path: 文件路径对象
            encoding: 编码名称
            
        Returns:
            文件内容字符串，读取失败返回None
        """
        try:
            with open(path, 'r', encoding=encoding, errors='ignore') as f:
                content = f.read().strip()
                # 验证内容是否合理（不全是乱码）
                if self._is_valid_text_content(content):
                    return content
                    
        except (UnicodeDecodeError, UnicodeError, OSError) as e:
            logger.debug(f"编码 {encoding} 读取失败，文件路径='{path}', 错误: {e}")
        
        return None
    
    def _is_valid_text_content(self, content: str) -> bool:
        """
        验证文本内容是否合理（简单的乱码检测）
        
        Args:
            content: 文本内容
            
        Returns:
            内容是否合理
        """
        if not content:
            return True
        
        # 检查是否包含过多的控制字符或不可打印字符
        printable_chars = sum(1 for c in content if c.isprintable() or c.isspace())
        total_chars = len(content)
        
        if total_chars == 0:
            return True
        
        # 如果可打印字符比例太低，可能是乱码
        printable_ratio = printable_chars / total_chars
        return printable_ratio > 0.8
    
    def read_multiple_files(self, file_paths: List[str], max_length_per_file: Optional[int] = None) -> List[Tuple[str, Optional[str]]]:
        """
        批量读取多个文件
        
        Args:
            file_paths: 文件路径列表
            max_length_per_file: 每个文件的最大读取长度
            
        Returns:
            (文件路径, 文件内容)的元组列表，读取失败的文件内容为None
        """
        results = []
        for file_path in file_paths:
            content = self.read_text_file(file_path, max_length_per_file)
            results.append((file_path, content))
        
        return results


# 便捷函数
def read_text_file(file_path: str, max_length: Optional[int] = None, max_file_size: int = 10 * 1024 * 1024) -> Optional[str]:
    """
    便捷的文本文件读取函数
    
    Args:
        file_path: 文件路径
        max_length: 最大读取长度
        max_file_size: 最大文件大小限制
        
    Returns:
        文件内容字符串，读取失败返回None
    """
    reader = TextReader(max_file_size=max_file_size)
    return reader.read_text_file(file_path, max_length)


def read_multiple_text_files(file_paths: List[str], max_length_per_file: Optional[int] = None) -> List[Tuple[str, Optional[str]]]:
    """
    便捷的批量文本文件读取函数
    
    Args:
        file_paths: 文件路径列表
        max_length_per_file: 每个文件的最大读取长度
        
    Returns:
        (文件路径, 文件内容)的元组列表
    """
    reader = TextReader()
    return reader.read_multiple_files(file_paths, max_length_per_file)