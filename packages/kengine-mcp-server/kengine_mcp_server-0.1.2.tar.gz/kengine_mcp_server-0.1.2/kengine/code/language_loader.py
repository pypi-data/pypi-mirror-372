"""
Tree-sitter语言库加载器
负责动态加载各种编程语言的tree-sitter解析器
"""

import logging
from pathlib import Path
from typing import List, Optional, Tuple, Union
from tree_sitter import Language

logger = logging.getLogger(__name__)

try:
    
    def load_language(lang_name: str) -> Optional[Language]:
        """动态加载tree-sitter语言库"""
        try:
            import tree_sitter_python
            import tree_sitter_java
            import tree_sitter_javascript
            import tree_sitter_go
            import tree_sitter_c_sharp
            import tree_sitter_c
            import tree_sitter_cpp
            import tree_sitter_kotlin
            
            lang_modules = {
                'python': tree_sitter_python,
                'java': tree_sitter_java,
                'javascript': tree_sitter_javascript,
                'go': tree_sitter_go,
                'c_sharp': tree_sitter_c_sharp,
                'c': tree_sitter_c,
                'cpp': tree_sitter_cpp,
                'kotlin': tree_sitter_kotlin,
            }
            
            if lang_name in lang_modules:
                lang_capsule = lang_modules[lang_name].language()
                lang_obj = Language(lang_capsule)
                return lang_obj
            else:
                logger.error(f"不支持的语言: {lang_name}")
                return None
                
        except ImportError as e:
            logger.error(f"导入语言库失败 {lang_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"加载语言库时发生错误 {lang_name}: {e}")
            return None

except ImportError as e:
    logger.error(f"导入tree-sitter失败: {e}")
    Language = None
    
    def load_language(lang_name: str) -> Optional[Language]:
        """当tree-sitter未安装时的占位函数"""
        return None


def get_supported_languages() -> dict:
    """
    获取支持的语言映射
    
    Returns:
        dict: 文件扩展名到(语言库, 语言名)的映射
    """
    # 支持的语言映射
    supported_languages = {
        '.py': (load_language('python'), 'python'),
        '.java': (load_language('java'), 'java'),
        '.js': (load_language('javascript'), 'javascript'),
        '.ts': (load_language('javascript'), 'javascript'),
        '.jsx': (load_language('javascript'), 'javascript'),
        '.tsx': (load_language('javascript'), 'javascript'),
        '.go': (load_language('go'), 'go'),
        '.cs': (load_language('c_sharp'), 'c_sharp'),
        '.c': (load_language('c'), 'c'),
        '.cc': (load_language('cpp'), 'cpp'),
        '.cpp': (load_language('cpp'), 'cpp'),
        '.cxx': (load_language('cpp'), 'cpp'),
        '.h': (load_language('c'), 'c'),
        '.hpp': (load_language('cpp'), 'cpp'),
        '.kt': (load_language('kotlin'), 'kotlin'),
        '.kts': (load_language('kotlin'), 'kotlin'),
    }
    
    # 返回所有语言映射，包括加载失败的（None值）
    return {
        ext: (lang_lib, lang_name) 
        for ext, (lang_lib, lang_name) in supported_languages.items()
    }


def get_language_for_extension(extension: str) -> Tuple[Optional[Language], Optional[str]]:
    """
    根据文件扩展名获取对应的语言库和语言名
    
    Args:
        extension: 文件扩展名（如 '.py'）
        
    Returns:
        Tuple[Language, str]: (语言库, 语言名) 或 (None, None)
    """
    supported_languages = get_supported_languages()
    return supported_languages.get(extension.lower(), (None, None))



def support_file(file_path: Union[str, Path]) -> bool:
    """
    检查指定文件是否支持骨架提取
    
    Args:
        file_path: 文件路径，支持字符串或Path对象
        
    Returns:
        bool: 如果文件类型被支持则返回True，否则返回False
        
    Examples:
        >>> support_file("example.py")
        True
        >>> support_file("example.txt")
        False
        >>> support_file(Path("example.java"))
        True
    """
    try:
        # 处理空路径或None的情况
        if not file_path:
            return False
        
        # 统一转换为Path对象处理
        path = Path(file_path)
        
        # 获取文件扩展名（转换为小写以确保一致性）
        ext = path.suffix.lower()
        
        # 检查扩展名是否在支持的文件类型列表中
        supported_types = get_supported_file_types()
        return ext in supported_types
        
    except Exception:
        # 如果在处理过程中发生任何异常，返回False
        # 这包括路径解析错误、类型错误等
        return False
    
    
def get_supported_file_types() -> List[str]:
    """
    获取支持的文件类型列表
    
    Returns:
        支持的文件扩展名列表
    """
    return list(get_supported_languages().keys())

