"""
Markdown 生成模块

提供将目录结构转换为压缩Markdown格式的功能，支持智能路径合并和树状结构显示。
专门处理Maven项目结构、Java包结构等常见目录模式的压缩显示。

重构后使用 tree_builder.py 中的目录压缩功能，避免代码重复。
"""

import os
from pathlib import Path
from typing import Dict, List, Set, Union, Optional
from .tree_builder import get_directory_tree


def generate_directory_markdown(dir_path: str, max_depth: int = 0, enable_compression: bool = True,
                               exclude_extensions: Optional[List[str]] = None) -> str:
    """
    将目录结构转换为压缩的Markdown格式字符串输出
    
    该方法使用 tree_builder.py 中的智能目录压缩功能：
    1. 对于Java Maven项目中的src/main/java、src/test/resources等标准目录结构进行压缩
    2. 对于com/jd/wl这样的多层相同包路径进行压缩显示
    3. 保持Markdown格式的可读性
    4. 优化了max_depth参数，确保压缩路径被正确计算为一级目录
    
    Args:
        dir_path (str): 目录路径
        max_depth (int): 最大递归深度，默认为0表示不限制深度
                        如果值 < 0 则抛出异常
                        如果值 > 0 则只返回指定深度范围内的目录
                        注意：压缩路径（如src/main/java）被算作一级目录
        enable_compression (bool): 是否启用压缩功能，默认为True
        exclude_extensions (Optional[List[str]]): 要排除的文件扩展名列表，默认为None
                                                扩展名匹配不区分大小写，例如：['.pyc', '.log']
        
    Returns:
        str: 压缩的Markdown格式目录结构字符串
        
    Raises:
        FileNotFoundError: 当目录不存在时
        PermissionError: 当没有访问权限时
        ValueError: 当max_depth < 0时
    """
    # 验证max_depth参数
    if max_depth < 0:
        raise ValueError(f"max_depth参数不能为负数，当前值: {max_depth}")
    
    try:
        root_path = Path(dir_path)
        if not root_path.exists():
            raise FileNotFoundError(f"目录不存在: {dir_path}")
        
        if not root_path.is_dir():
            raise ValueError(f"路径不是目录: {dir_path}")
            
        # 使用 tree_builder.py 中的 get_directory_tree 函数获取目录树
        # 将 max_depth=0 转换为 None（tree_builder 的约定）
        tree_max_depth = None if max_depth == 0 else max_depth
        exclude_extensions = set(exclude_extensions) if exclude_extensions else None
        directory_tree = get_directory_tree(
            dir_path=dir_path,
            max_depth=tree_max_depth,
            include_hidden=False,
            include_files=True,
            include_size=False,
            respect_gitignore=True,
            exclude_extensions=exclude_extensions,
            enable_compression=enable_compression
        )
        
        # 生成压缩的Markdown格式输出
        markdown_output = _generate_markdown_from_tree(
            directory_tree, root_path.name, enable_compression
        )
        
        return markdown_output
        
    except (FileNotFoundError, ValueError) as e:
        # 重新抛出这些异常，保持原有的异常类型
        raise e
    except PermissionError as e:
        raise PermissionError(f"没有访问权限，目录路径='{dir_path}', 错误: {str(e)}") from e
    except Exception as e:
        raise RuntimeError(f"处理目录时发生错误，目录路径='{dir_path}', max_depth={max_depth}, 错误: {str(e)}") from e


def _generate_markdown_from_tree(tree: Dict, root_name: str = None, enable_compression: bool = True, 
                                prefix: str = "", is_last: bool = True) -> str:
    """
    从目录树生成Markdown格式输出
    
    Args:
        tree (Dict): 由 tree_builder.get_directory_tree 返回的目录树结构
        root_name (str): 根目录名称
        enable_compression (bool): 是否启用压缩功能
        prefix (str): 当前行的前缀
        is_last (bool): 是否是最后一个项目
        
    Returns:
        str: Markdown格式树状结构
    """
    lines = []
    
    # 当前项目的符号
    if prefix:
        connector = "└── " if is_last else "├── "
        icon = "📁" if tree['type'] == 'directory' else "📄"
        
        # 检查是否有访问限制
        restriction_note = " (访问受限)" if tree.get('access_denied', False) else ""
        
        # 显示节点名称（压缩节点会显示完整路径）
        lines.append(f"{prefix}{connector}{icon} {tree['name']}{restriction_note}")
    
    # 处理子项目
    if 'children' in tree and tree['children']:
        children = tree['children']
        
        # children 现在始终是列表格式
        child_items = children
        child_items.sort(key=lambda x: (x['type'] == 'file', x['name'].lower()))
        
        if child_items:
            new_prefix = prefix + ("    " if is_last else "│   ")
            
            for i, child_tree in enumerate(child_items):
                is_last_child = (i == len(child_items) - 1)
                child_lines = _generate_markdown_from_tree(
                    child_tree, None, enable_compression, new_prefix, is_last_child
                )
                lines.extend(child_lines.split('\n')[:-1])  # 移除最后的空行
    
    return '\n'.join(lines) + '\n'