"""
路径和文件名处理工具

提供路径操作和文件名清理等实用功能
"""

import re
from pathlib import Path
from typing import Optional


def sanitize_filename(filename: str, max_length: int = 100, replacement_char: str = '_') -> str:
    """
    清理文件名中的特殊字符，确保文件名在各个操作系统上都是有效的
    
    Args:
        filename: 原始文件名
        max_length: 文件名最大长度限制
        replacement_char: 用于替换无效字符的字符
        
    Returns:
        清理后的安全文件名
        
    Raises:
        ValueError: 当输入参数无效时
    """
    if not isinstance(filename, str):
        raise ValueError("filename必须是字符串类型")
    
    if max_length <= 0:
        raise ValueError("max_length必须是正整数")
    
    if not replacement_char or len(replacement_char) != 1:
        raise ValueError("replacement_char必须是单个字符")
    
    # 定义在文件名中无效的字符（Windows + Linux + macOS 兼容）
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    
    # 替换无效字符
    sanitized = filename
    for char in invalid_chars:
        sanitized = sanitized.replace(char, replacement_char)
    
    # 移除控制字符（ASCII 0-31）
    sanitized = re.sub(r'[\x00-\x1f]', replacement_char, sanitized)
    
    # 移除首尾空格和点号（Windows不允许文件名以点结尾）
    sanitized = sanitized.strip(' .')
    
    # 限制长度
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip(' .')
    
    # 如果清理后为空或只包含替换字符，使用默认名称
    if not sanitized or sanitized.replace(replacement_char, '').strip() == '':
        sanitized = "unnamed"
    
    # 避免Windows保留名称（CON, PRN, AUX, NUL等）
    windows_reserved = {
        'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5',
        'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4',
        'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    
    # 检查是否为Windows保留名称（忽略大小写和扩展名）
    base_name = Path(sanitized).stem.upper()
    if base_name in windows_reserved:
        sanitized = f"{replacement_char}{sanitized}"
    
    return sanitized


def sanitize_path(path: str, max_length: int = 255) -> str:
    """
    清理路径中的无效部分
    
    Args:
        path: 原始路径
        max_length: 路径最大长度限制
        
    Returns:
        清理后的路径
    """
    if not isinstance(path, str):
        raise ValueError("path必须是字符串类型")
    
    # 分离路径组件并逐个清理
    path_obj = Path(path)
    parts = []
    
    for part in path_obj.parts:
        if part in ('/', '\\'):  # 跳过根目录标识符
            continue
        clean_part = sanitize_filename(part, max_length=50)  # 单个路径组件长度限制
        if clean_part:  # 只添加非空部分
            parts.append(clean_part)
    
    # 重新组合路径
    if not parts:
        return "unnamed"
    
    result_path = str(Path(*parts))
    
    # 限制总路径长度
    if len(result_path) > max_length:
        # 如果路径太长，从中间开始截断
        parts_str = " / ".join(parts)
        if len(parts_str) > max_length:
            truncated = f"...{parts_str[-(max_length-3):]}"
            result_path = truncated.replace(" / ", "/")
        else:
            result_path = parts_str.replace(" / ", "/")
    
    return result_path


def ensure_safe_path(base_path: str, target_path: str) -> Optional[str]:
    """
    确保目标路径在基础路径内，防止路径遍历攻击
    
    Args:
        base_path: 基础路径（安全边界）
        target_path: 目标路径
        
    Returns:
        如果安全则返回规范化的目标路径，否则返回None
    """
    try:
        base = Path(base_path).resolve()
        target = (base / target_path).resolve()
        
        # 检查target是否在base路径内
        try:
            target.relative_to(base)
            return str(target)
        except ValueError:
            # target不在base路径内
            return None
            
    except (OSError, ValueError):
        return None


def get_safe_output_filename(base_name: str, extension: str = "", suffix: str = "") -> str:
    """
    生成安全的输出文件名
    
    Args:
        base_name: 基础文件名
        extension: 文件扩展名（不含点号）
        suffix: 文件名后缀
        
    Returns:
        安全的完整文件名
    """
    # 清理基础名称
    clean_base = sanitize_filename(base_name)
    
    # 添加后缀
    if suffix:
        clean_suffix = sanitize_filename(suffix)
        clean_base = f"{clean_base}_{clean_suffix}"
    
    # 添加扩展名
    if extension:
        # 确保扩展名不包含点号，然后添加
        clean_extension = extension.lstrip('.')
        return f"{clean_base}.{clean_extension}"
    
    return clean_base
