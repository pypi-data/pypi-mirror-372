"""
代码骨架提取包
提供与原始code.skeleton.py文件完全兼容的API接口
"""

from pathlib import Path
from typing import List, Tuple, Union

from .extractor import CodeSkeletonExtractor
from ..language_loader import support_file, get_supported_file_types, load_language
from .. import language_loader

# 导出主要类和函数，保持API兼容性
__all__ = [
    'CodeSkeletonExtractor',
    'extract_skeleton',
    'support_file',
    'get_supported_file_types',
    'load_language',
    'language_loader',
    'validate_file_for_skeleton_extraction'
]


def validate_file_for_skeleton_extraction(file_path: str) -> Tuple[bool, str]:
    """
    验证文件是否可以进行骨架提取
    
    Args:
        file_path: 文件路径
        
    Returns:
        Tuple[bool, str]: (是否可以提取骨架, 验证消息)
    """
    try:
        if not file_path:
            return False, "路径不能为空"
        
        path = Path(file_path)
        if not path.exists():
            return False, "文件不存在"
        
        ext = path.suffix.lower()
        supported_types = get_supported_file_types()
        
        if ext not in supported_types:
            return False, f"不支持的文件类型: {ext}"
        
        return True, "验证通过"
    except Exception as e:
        return False, f"验证过程中发生错误: {str(e)}"


def extract_skeleton(code_file_path: str) -> str:
    """
    便捷函数：提取代码骨架
    
    Args:
        code_file_path: 代码文件路径
        
    Returns:
        骨架代码字符串
    """
    extractor = CodeSkeletonExtractor()
    return extractor.extract_skeleton(code_file_path)