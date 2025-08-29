"""
目录工具核心模块

提供目录遍历和文件树构建的核心功能，供其他模块复用。
"""

import os
import fnmatch
from pathlib import Path
from typing import Dict, List, Set, Union, Optional


def collect_file_tree(root_path: Path, max_depth: int = 0, 
                     include_hidden: bool = False,
                     include_files: bool = True,
                     respect_gitignore: bool = True,
                     exclude_extensions: Optional[List[str]] = None) -> Dict:
    """
    收集目录的文件树结构
    
    Args:
        root_path (Path): 根目录路径
        max_depth (int): 最大递归深度，0表示不限制
        include_hidden (bool): 是否包含隐藏文件
        include_files (bool): 是否包含文件
        respect_gitignore (bool): 是否遵循.gitignore规则
        exclude_extensions (Optional[List[str]]): 要排除的文件扩展名列表
        
    Returns:
        Dict: 文件树结构字典
        
    Raises:
        FileNotFoundError: 当目录不存在时
        PermissionError: 当没有访问权限时
    """
    if not root_path.exists():
        raise FileNotFoundError(f"目录不存在: {root_path}")
    
    if not root_path.is_dir():
        raise ValueError(f"路径不是目录: {root_path}")
    
    try:
        # 解析gitignore规则
        gitignore_patterns = []
        if respect_gitignore:
            gitignore_patterns = parse_gitignore_patterns(root_path)
        
        return _build_file_tree_recursive(
            root_path, max_depth, include_hidden, include_files,
            1, gitignore_patterns, root_path, exclude_extensions
        )
        
    except PermissionError as e:
        raise PermissionError(f"没有访问权限，目录路径='{root_path}', 错误: {str(e)}") from e
    except Exception as e:
        raise RuntimeError(f"构建文件树时发生错误，目录路径='{root_path}', 错误: {str(e)}") from e


def _build_file_tree_recursive(path: Path, max_depth: int, include_hidden: bool,
                              include_files: bool, current_depth: int,
                              gitignore_patterns: List[str], root_path: Path,
                              exclude_extensions: Optional[List[str]] = None) -> Dict:
    """
    递归构建文件树结构
    
    Args:
        path (Path): 当前路径
        max_depth (int): 最大递归深度
        include_hidden (bool): 是否包含隐藏文件
        include_files (bool): 是否包含文件
        current_depth (int): 当前递归深度
        gitignore_patterns (List[str]): gitignore模式列表
        root_path (Path): 根目录路径
        exclude_extensions (Optional[List[str]]): 要排除的文件扩展名列表
        
    Returns:
        Dict: 文件树节点
    """
    is_hidden = path.name.startswith('.')
    
    # 构建基本节点信息
    node = {
        'name': path.name,
        'type': 'directory' if path.is_dir() else 'file',
        'path': str(path),
        'is_hidden': is_hidden
    }
    
    # 如果是文件，添加文件特有信息
    if path.is_file():
        node['extension'] = path.suffix.lower()
        try:
            node['size'] = path.stat().st_size
        except (OSError, PermissionError):
            node['size'] = 0
        return node
    
    # 如果是目录，处理子项
    node['children'] = {}
    
    # 检查是否达到最大深度
    if max_depth > 0 and current_depth >= max_depth:
        return node
    
    try:
        # 获取子项并排序
        items = list(path.iterdir())
        items.sort(key=lambda x: (x.is_file(), x.name.lower()))
        
        for item in items:
            # 跳过隐藏文件/目录（除非明确要求包含）
            if not include_hidden and item.name.startswith('.'):
                continue
            
            # 检查是否被gitignore忽略
            if gitignore_patterns and is_ignored_by_gitignore(item, gitignore_patterns, root_path):
                continue
            
            # 跳过文件（如果不包含文件）
            if item.is_file() and not include_files:
                continue
            
            # 检查是否需要排除特定扩展名的文件
            if item.is_file() and exclude_extensions:
                file_extension = item.suffix.lower()
                if file_extension in exclude_extensions:
                    continue
            
            # 递归构建子树
            child_node = _build_file_tree_recursive(
                item, max_depth, include_hidden, include_files,
                current_depth + 1, gitignore_patterns, root_path, exclude_extensions
            )
            node['children'][item.name] = child_node
            
    except PermissionError:
        # 如果没有权限访问目录，标记为受限
        node['restricted'] = True
    
    return node


def parse_gitignore_patterns(root_path: Path) -> List[str]:
    """
    解析.gitignore文件中的模式
    
    Args:
        root_path (Path): 项目根目录路径
        
    Returns:
        List[str]: gitignore模式列表
        
    Raises:
        OSError: 当读取.gitignore文件失败时
        UnicodeDecodeError: 当文件编码有问题时
    """
    patterns = []
    gitignore_file = root_path / '.gitignore'
    
    if not gitignore_file.exists():
        return patterns
    
    try:
        with open(gitignore_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # 跳过空行和注释
                if not line or line.startswith('#'):
                    continue
                
                # 处理否定模式（以!开头）
                if line.startswith('!'):
                    # 暂时不处理否定模式，这需要更复杂的逻辑
                    continue
                
                # 移除尾部的斜杠
                if line.endswith('/'):
                    line = line[:-1]
                
                patterns.append(line)
                
    except OSError as e:
        raise OSError(f"读取.gitignore文件失败，文件路径='{gitignore_file}', 错误: {str(e)}") from e
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(e.encoding, e.object, e.start, e.end,
                               f".gitignore文件编码错误: {gitignore_file}") from e
    
    return patterns


def is_ignored_by_gitignore(path: Path, patterns: List[str], root_path: Path) -> bool:
    """
    检查路径是否被gitignore规则忽略
    
    Args:
        path (Path): 要检查的路径
        patterns (List[str]): gitignore模式列表
        root_path (Path): 项目根目录路径
        
    Returns:
        bool: 如果被忽略返回True，否则返回False
        
    Raises:
        ValueError: 当路径处理出现问题时
    """
    if not patterns:
        return False
    
    try:
        # 获取相对于根目录的路径
        relative_path = path.relative_to(root_path)
        path_str = str(relative_path).replace('\\', '/')
        
        # 检查每个模式
        for pattern in patterns:
            # 处理不同类型的模式
            if match_gitignore_pattern(path_str, pattern, path.is_dir()):
                return True
                
        return False
        
    except ValueError as e:
        # 如果路径不在根目录下，这是一个错误情况，应该抛出异常
        raise ValueError(f"路径 {path} 不在根目录 {root_path} 下") from e
    except Exception as e:
        raise RuntimeError(f"检查gitignore规则时发生错误，路径='{path}', 根目录='{root_path}', 错误: {str(e)}") from e


def match_gitignore_pattern(path_str: str, pattern: str, is_directory: bool) -> bool:
    """
    检查路径是否匹配gitignore模式
    
    Args:
        path_str (str): 相对路径字符串
        pattern (str): gitignore模式
        is_directory (bool): 是否为目录
        
    Returns:
        bool: 如果匹配返回True，否则返回False
        
    Raises:
        ValueError: 当模式或路径格式有问题时
    """
    if not path_str or not pattern:
        raise ValueError("路径字符串和模式都不能为空")
    
    try:
        # 处理目录模式（以/结尾或在模式中包含/）
        if '/' in pattern:
            # 绝对路径模式（以/开头）
            if pattern.startswith('/'):
                pattern = pattern[1:]
                return fnmatch.fnmatch(path_str, pattern)
            else:
                # 相对路径模式，可能匹配任何层级
                parts = path_str.split('/')
                for i in range(len(parts)):
                    sub_path = '/'.join(parts[i:])
                    if fnmatch.fnmatch(sub_path, pattern):
                        return True
                return False
        else:
            # 简单文件名模式
            # 检查文件名本身
            filename = path_str.split('/')[-1]
            if fnmatch.fnmatch(filename, pattern):
                return True
            
            # 检查目录名（如果是目录）
            if is_directory and fnmatch.fnmatch(path_str.split('/')[-1], pattern):
                return True
            
            # 检查路径中的任何部分
            parts = path_str.split('/')
            for part in parts:
                if fnmatch.fnmatch(part, pattern):
                    return True
                    
            return False
            
    except Exception as e:
        raise RuntimeError(f"匹配gitignore模式时发生错误，pattern='{pattern}', path='{path_str}', is_directory={is_directory}, 错误: {str(e)}") from e