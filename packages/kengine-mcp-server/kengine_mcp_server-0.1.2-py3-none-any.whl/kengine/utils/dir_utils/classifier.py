"""
文件分类模块

提供按文件类型分类文件的功能。
"""

import os
from pathlib import Path
from typing import Dict, List, Set, Union, Optional, Tuple
from ...config.file_extensions import get_source_extensions, get_document_extensions, get_binary_extensions


def classify_files_by_type(dir_path: str, recursive: bool = True, include_hidden: bool = False) -> Tuple[List[str], List[str], List[str]]:
    """
    根据文件扩展名将目录中的文件分类为源代码文件、文档文件和二进制文件
    
    Args:
        dir_path (str): 要分析的目录路径
        recursive (bool): 是否递归遍历子目录，默认为 True
        include_hidden (bool): 是否包含隐藏文件（以.开头的文件），默认为 False
        
    Returns:
        Tuple[List[str], List[str], List[str]]: 返回三个列表的元组：
            - 源代码文件列表
            - 文档文件列表  
            - 二进制文件列表
            
    Raises:
        FileNotFoundError: 当目录不存在时
        PermissionError: 当没有访问权限时
        ValueError: 当路径不是目录时
    """
    # 使用统一配置模块获取文件扩展名分类，提供降级方案
    source_extensions = get_source_extensions()
    document_extensions = get_document_extensions()
    binary_extensions = get_binary_extensions()
    
    try:
        root_path = Path(dir_path)
        
        # 验证路径
        if not root_path.exists():
            raise FileNotFoundError(f"目录不存在: {dir_path}")
        
        if not root_path.is_dir():
            raise ValueError(f"路径不是目录: {dir_path}")
        
        # 初始化结果列表
        source_files = []
        document_files = []
        binary_files = []
        
        def classify_file(file_path: Path) -> None:
            """内部函数：对单个文件进行分类"""
            # 检查是否包含隐藏文件
            if not include_hidden and file_path.name.startswith('.'):
                return
            
            # 获取文件扩展名（转为小写）
            extension = file_path.suffix.lower()
            file_path_str = str(file_path)
            
            # 根据扩展名分类
            if extension in source_extensions:
                source_files.append(file_path_str)
            elif extension in document_extensions:
                document_files.append(file_path_str)
            elif extension in binary_extensions:
                binary_files.append(file_path_str)
            else:
                # 对于未知扩展名的文件，尝试通过其他特征判断
                # 如果没有扩展名但文件名包含常见的可执行文件名，归类为二进制
                if not extension and file_path.name.lower() in {
                    'makefile', 'dockerfile', 'vagrantfile', 'rakefile', 'gemfile'
                }:
                    source_files.append(file_path_str)
                elif not extension:
                    # 没有扩展名的文件默认归类为文档文件
                    document_files.append(file_path_str)
                else:
                    # 有扩展名但不在已知分类中的文件，根据扩展名长度判断
                    # 通常二进制文件的扩展名较短
                    if len(extension) <= 4:
                        binary_files.append(file_path_str)
                    else:
                        document_files.append(file_path_str)
        
        def process_directory(dir_path: Path) -> None:
            """内部函数：处理目录中的文件"""
            try:
                for item in dir_path.iterdir():
                    # 跳过隐藏目录（除非明确要求包含）
                    if not include_hidden and item.name.startswith('.'):
                        continue
                    
                    if item.is_file():
                        classify_file(item)
                    elif item.is_dir() and recursive:
                        process_directory(item)
                        
            except PermissionError:
                # 如果没有权限访问某个目录，跳过但不抛出异常
                pass
        
        # 开始处理
        process_directory(root_path)
        
        # 对结果进行排序以保证输出的一致性
        source_files.sort()
        document_files.sort()
        binary_files.sort()
        
        return (source_files, document_files, binary_files)
        
    except PermissionError as e:
        raise PermissionError(f"没有访问权限，目录路径='{dir_path}', 错误: {str(e)}") from e
    except (FileNotFoundError, ValueError) as e:
        # 重新抛出具体的异常类型，不包装成RuntimeError
        raise e
    except Exception as e:
        raise RuntimeError(f"分类文件时发生错误，目录路径='{dir_path}', recursive={recursive}, include_hidden={include_hidden}, 错误: {str(e)}") from e