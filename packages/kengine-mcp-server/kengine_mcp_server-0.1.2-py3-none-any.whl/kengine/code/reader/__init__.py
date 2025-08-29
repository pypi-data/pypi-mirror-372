
from pathlib import Path
from typing import List, Union
from .method_extractor import MethodExtractor
from .dependency_extractor import DependencyExtractor

# 全局实例
_method_extractor = None
_dependency_extractor = None

def get_method_extractor() -> MethodExtractor:
    """获取方法提取器实例（单例模式）"""
    global _method_extractor
    if _method_extractor is None:
        _method_extractor = MethodExtractor()
    return _method_extractor

def get_dependency_extractor() -> DependencyExtractor:
    """获取依赖提取器实例（单例模式）"""
    global _dependency_extractor
    if _dependency_extractor is None:
        _dependency_extractor = DependencyExtractor()
    return _dependency_extractor

def read_method(file_path: Union[str, Path], method_name: str, arg_types: List[str] = None) -> str:
    """
    从代码文件中提取指定方法
    
    首先判断file_path是否支持，可使用language_loader中的support_file判断
    如果支持则使用tree sitter实现方法体的提取，若不支持则抛出异常
    使用language_loader中提供的tree sitter实现方法体的提取
    如果arg_types为空则不考虑参数，取第一个方法名匹配的方法
    如果arg_types不为空则考虑参数，取精确匹配的方法
    
    Args:
        file_path: 代码文件路径
        method_name: 方法名
        arg_types: 参数类型列表，为None或空列表时不考虑参数匹配
        
    Returns:
        str: 方法的完整代码
        
    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 文件类型不支持或方法不存在
        RuntimeError: tree-sitter相关错误
        
    Examples:
        >>> # 提取Python方法（不考虑参数）
        >>> code = read_method("example.py", "calculate_sum")
        
        >>> # 提取Java方法（精确匹配参数类型）
        >>> code = read_method("Example.java", "processData", ["String", "int"])
        
        >>> # 提取JavaScript函数
        >>> code = read_method("utils.js", "formatDate", ["Date"])
    """
    if arg_types is None:
        arg_types = []
    
    extractor = get_method_extractor()
    return extractor.extract_method(file_path, method_name, arg_types)


def read_dependencies(project_path: Union[str, Path], file_path: Union[str, Path]) -> List[str]:
    """
    从代码文件中解析依赖
    
    首先判断file_path是否支持，可使用language_loader中的support_file判断
    如果支持则使用tree sitter实现依赖的提取，若不支持则抛出异常
    
    提取依赖后
    1. 排除语言本身的依赖， 比如对于java语言来讲常见的语言依赖有 java.lang.*, java.io等
    2. 排除三方包依赖， 要通过依赖的类名/模块名在项目目录中通过glob进行搜索， 若存在则确认是本项目依赖
    
    Args:
        project_path: 项目根路径
        file_path: 要分析的文件路径
        
    Returns:
        List[str]: 依赖文件列表，文件为相对于 project_path 的相对路径
        
    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 文件类型不支持
        RuntimeError: tree-sitter相关错误
        
    Examples:
        >>> # 提取Python文件依赖
        >>> deps = read_dependencies("/path/to/project", "src/main.py")
        
        >>> # 提取Java文件依赖
        >>> deps = read_dependencies("/path/to/project", "src/Main.java")
        
        >>> # 提取JavaScript文件依赖
        >>> deps = read_dependencies("/path/to/project", "src/app.js")
    """
    try:
        extractor = get_dependency_extractor()
        return extractor.extract_dependencies(project_path, file_path)
    except Exception as e:
        # 使用中文输出错误信息
        if isinstance(e, FileNotFoundError):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        elif isinstance(e, ValueError):
            if "不支持的文件类型" in str(e):
                raise ValueError(f"不支持的文件类型: {file_path}")
            elif "无法加载语言库" in str(e):
                raise ValueError(f"无法加载对应的语言解析库: {file_path}")
            else:
                raise ValueError(f"参数错误: {e}")
        else:
            raise RuntimeError(f"依赖解析过程中发生错误: {e}")