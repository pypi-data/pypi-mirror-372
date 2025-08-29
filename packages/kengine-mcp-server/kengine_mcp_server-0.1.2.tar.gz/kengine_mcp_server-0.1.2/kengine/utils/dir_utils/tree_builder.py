"""
目录树构建模块 - 重新设计的压缩版本

按照新的三步骤实现：
1. 第一步：获得完整的路径树（不进行任何压缩）
2. 第二步：如果启用压缩则执行压缩
3. 第三步：按压缩后的路径树过滤前 max_depth 深度的路径树返回

主要改进：
1. 分离树构建和压缩逻辑
2. max_depth 参数作用于压缩后的结构
3. 确保压缩算法真正生效
4. 简化代码逻辑，提高可维护性
"""

from pathlib import Path
from typing import Dict, List, Optional, Set
from .core import parse_gitignore_patterns, is_ignored_by_gitignore
from .compression import DirectoryCompressor


def get_directory_tree(dir_path: str, 
                       max_depth: Optional[int] = None, 
                       include_hidden: bool = False,
                       include_files: bool = True, 
                       include_size: bool = False,
                       respect_gitignore: bool = True,
                       exclude_extensions: Optional[Set[str]] = None,
                       enable_compression: bool = True) -> Dict:
    """
    获取目录的子目录/子文件树结构
    
    Args:
        dir_path (str): 目录路径
        max_depth (Optional[int]): 返回的路径最大深度，压缩后的路径深度为1，None表示无限制
        include_hidden (bool): 是否包含隐藏文件和目录，默认为 False
        include_files (bool): 是否包含文件，默认为 True
        include_size (bool): 是否包含文件大小信息，默认为 False
        respect_gitignore (bool): 是否遵循.gitignore规则，默认为 True
        exclude_extensions (Optional[Set[str]]): 要排除的文件扩展名集合
        enable_compression (bool): 是否启用智能目录压缩，默认为 True
        
    Returns:
        Dict: 目录树结构字典，包含以下字段：
            - name: 目录/文件名
            - type: 'directory' 或 'file'
            - path: 完整路径
            - children: 子项数组（仅目录有此字段）
            - size: 文件大小（仅当include_size=True且为文件时）
            - is_hidden: 是否为隐藏文件/目录
            - 压缩相关字段（如 is_compressed 等，仅在启用压缩时）
            
    Raises:
        FileNotFoundError: 当目录不存在时
        PermissionError: 当没有访问权限时
        ValueError: 当路径不是目录时
    """
    root_path = Path(dir_path)
    
    # 验证路径
    if not root_path.exists():
        raise FileNotFoundError(f"目录不存在: {dir_path}")
    
    if not root_path.is_dir():
        raise ValueError(f"路径不是目录: {dir_path}")
    
    # 处理 exclude_extensions 参数，支持列表和集合
    if exclude_extensions is not None:
        if isinstance(exclude_extensions, list):
            exclude_extensions = set(exclude_extensions)
        elif not isinstance(exclude_extensions, set):
            exclude_extensions = set(exclude_extensions) if exclude_extensions else None
    
    try:
        # 解析gitignore规则
        gitignore_patterns = []
        if respect_gitignore:
            gitignore_patterns = parse_gitignore_patterns(root_path)
        # 第一步：获得完整的路径树（不进行任何压缩）
        complete_tree = _build_complete_directory_tree(
            root_path, include_hidden, include_files, include_size,
            gitignore_patterns, root_path, exclude_extensions
        )
        
        # 第二步：如果启用压缩则执行压缩
        if enable_compression:
            compressed_tree = _apply_compression_to_tree(complete_tree)
        else:
            compressed_tree = complete_tree
        
        # 第三步：按压缩后的路径树过滤前 max_depth 深度的路径树返回
        if max_depth is not None:
            final_tree = _apply_depth_limit_to_compressed_tree(compressed_tree, max_depth)
        else:
            final_tree = compressed_tree
        
        return final_tree
        
    except PermissionError as e:
        raise PermissionError(f"没有访问权限，目录路径='{dir_path}', 错误: {str(e)}") from e
    except (OSError, UnicodeDecodeError) as e:
        # 这些是gitignore解析可能出现的异常，重新抛出
        raise e
    except Exception as e:
        raise RuntimeError(f"构建目录树时发生错误，目录路径='{dir_path}', max_depth={max_depth}, 错误: {str(e)}") from e


def _build_complete_directory_tree(path: Path, include_hidden: bool, include_files: bool,
                                 include_size: bool, gitignore_patterns: List[str], 
                                 root_path: Path, exclude_extensions: Optional[Set[str]] = None) -> Dict:
    """
    第一步：递归构建完整的目录树结构（不进行任何压缩）
    
    Args:
        path (Path): 当前路径
        include_hidden (bool): 是否包含隐藏文件
        include_files (bool): 是否包含文件
        include_size (bool): 是否包含文件大小
        gitignore_patterns (List[str]): gitignore模式列表
        root_path (Path): 根目录路径
        exclude_extensions (Optional[Set[str]]): 要排除的文件扩展名集合
        
    Returns:
        Dict: 完整的目录树节点
    """
    is_hidden = path.name.startswith('.')
    
    # 构建基本节点信息
    node = {
        'name': path.name,
        'type': 'directory' if path.is_dir() else 'file',
        'path': str(path.relative_to(root_path)),
        'is_hidden': is_hidden
    }
    
    # 如果是文件，添加文件特有信息
    if path.is_file():
        if include_size:
            try:
                node['size'] = path.stat().st_size
            except (OSError, PermissionError):
                node['size'] = 0
        return node
    
    # 如果是目录，处理子项
    node['children'] = []
    
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
            
            # 递归构建子项
            child_node = _build_complete_directory_tree(
                item, include_hidden, include_files, include_size,
                gitignore_patterns, root_path, exclude_extensions
            )
            node['children'].append(child_node)
            
    except PermissionError as e:
        # 权限错误应该向上传播，让上层处理
        raise PermissionError(f"没有访问权限，目录路径='{path}', 错误: {str(e)}") from e
    
    return node


def _apply_compression_to_tree(tree: Dict) -> Dict:
    """
    第二步：对完整的目录树应用压缩算法
    
    Args:
        tree (Dict): 完整的目录树
        
    Returns:
        Dict: 压缩后的目录树
    """
    if tree['type'] != 'directory' or not tree.get('children'):
        return tree
    
    # 创建压缩器实例
    compressor = DirectoryCompressor()
    
    # 对当前节点的子项进行压缩
    compressed_results = compressor.compress_tree(tree, enable_compression=True)
    
    # 将压缩结果转换为树节点
    compressed_children = []
    
    for result in compressed_results:
        if result['type'] == 'compressed':
            # 创建压缩节点
            compressed_node = _create_compressed_node_from_result(result, tree)
            compressed_children.append(compressed_node)
        elif result['type'] == 'normal':
            # 递归处理正常节点
            normal_tree = result['tree']
            compressed_normal_tree = _apply_compression_to_tree(normal_tree)
            compressed_children.append(compressed_normal_tree)
    
    # 更新树的子项
    compressed_tree = tree.copy()
    compressed_tree['children'] = compressed_children
    
    return compressed_tree


def _create_compressed_node_from_result(result: Dict, parent_tree: Dict) -> Dict:
    """
    从压缩结果创建压缩节点
    
    Args:
        result (Dict): 压缩结果
        parent_tree (Dict): 父树节点
        
    Returns:
        Dict: 压缩节点
    """
    compressed_path = result['path']
    compression_info = result.get('compression_info', {})
    
    # 创建压缩节点
    compressed_node = {
        'name': compressed_path,
        'type': 'directory',
        'path': f"{parent_tree['path']}/{compressed_path}" if parent_tree['path'] else compressed_path,
        'is_hidden': False,
        'is_compressed': True,
        'original_depth': compression_info.get('original_depth', 1),
        'compression_strategy': compression_info.get('strategy', 'unknown'),
        'children': []
    }
    
    # 递归处理压缩节点的子项
    if 'children' in result and result['children']:
        for child in result['children']:
            compressed_child = _apply_compression_to_tree(child)
            compressed_node['children'].append(compressed_child)
    
    return compressed_node


def _apply_depth_limit_to_compressed_tree(tree: Dict, max_depth: int) -> Dict:
    """
    第三步：对压缩后的树应用深度限制
    
    Args:
        tree (Dict): 压缩后的目录树
        max_depth (int): 最大深度限制
        
    Returns:
        Dict: 应用深度限制后的目录树
    """
    return _apply_depth_limit_recursive(tree, max_depth, 0)


def _apply_depth_limit_recursive(node: Dict, max_depth: int, current_depth: int) -> Dict:
    """
    递归应用深度限制
    
    Args:
        node (Dict): 当前节点
        max_depth (int): 最大深度限制
        current_depth (int): 当前深度
        
    Returns:
        Dict: 应用深度限制后的节点
    """
    # 复制节点
    limited_node = node.copy()
    
    # 如果是文件或没有子项，直接返回
    if node['type'] == 'file' or not node.get('children'):
        return limited_node
    
    # 如果达到最大深度，清空子项
    if current_depth >= max_depth:
        limited_node['children'] = []
        return limited_node
    
    # 递归处理子项
    limited_children = []
    for child in node['children']:
        # 压缩节点算作1层深度
        if child.get('is_compressed'):
            child_depth_increment = 1
        else:
            child_depth_increment = 1
        
        limited_child = _apply_depth_limit_recursive(
            child, max_depth, current_depth + child_depth_increment
        )
        limited_children.append(limited_child)
    
    limited_node['children'] = limited_children
    return limited_node


# 保持向后兼容的函数
def get_compressed_tree_structure(dir_path: str, 
                                max_depth: Optional[int] = None,
                                include_hidden: bool = False,
                                include_files: bool = True,
                                respect_gitignore: bool = True,
                                exclude_extensions: Optional[Set[str]] = None) -> Dict:
    """
    获取带压缩功能的目录树结构的便捷函数
    
    这是 get_directory_tree 的简化版本，默认启用压缩功能
    
    Args:
        dir_path (str): 目录路径
        max_depth (Optional[int]): 最大递归深度，None表示无限制
        include_hidden (bool): 是否包含隐藏文件和目录，默认为 False
        include_files (bool): 是否包含文件，默认为 True
        respect_gitignore (bool): 是否遵循.gitignore规则，默认为 True
        exclude_extensions (Optional[Set[str]]): 要排除的文件扩展名集合
        
    Returns:
        Dict: 带压缩信息的目录树结构字典
    """
    return get_directory_tree(
        dir_path=dir_path,
        max_depth=max_depth,
        include_hidden=include_hidden,
        include_files=include_files,
        include_size=False,
        respect_gitignore=respect_gitignore,
        exclude_extensions=exclude_extensions,
        enable_compression=True
    )


def extract_compressed_paths(tree: Dict) -> List[str]:
    """
    从压缩树中提取所有压缩路径
    
    Args:
        tree (Dict): 带压缩信息的目录树
        
    Returns:
        List[str]: 压缩路径列表
    """
    compressed_paths = []
    
    def _extract_paths(node: Dict):
        if node.get('children'):
            for child in node['children']:
                if child.get('is_compressed'):
                    compressed_paths.append(child['path'])
                
                # 递归处理子项
                if child['type'] == 'directory':
                    _extract_paths(child)
    
    _extract_paths(tree)
    return compressed_paths