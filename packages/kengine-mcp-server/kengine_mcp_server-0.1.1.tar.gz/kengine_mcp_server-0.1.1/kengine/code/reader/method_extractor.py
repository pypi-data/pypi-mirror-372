"""
方法提取器核心模块
负责从代码文件中提取指定方法的完整代码
"""

import logging
from pathlib import Path
from typing import List, Union, Optional, Dict, Any
from ..language_loader import support_file, get_language_for_extension

logger = logging.getLogger(__name__)

try:
    from tree_sitter import Parser
except ImportError:
    Parser = None
    logger.error("tree-sitter库未安装，方法提取功能将不可用")


class MethodExtractor:
    """方法提取器类"""
    
    def __init__(self):
        """初始化方法提取器"""
        self.parsers = {}  # 缓存解析器
        self.language_handlers = {}  # 缓存语言处理器
    
    def extract_method(self, file_path: Union[str, Path], method_name: str, arg_types: List[str] = None) -> str:
        """
        从代码文件中提取指定方法
        
        Args:
            file_path: 代码文件路径
            method_name: 方法名
            arg_types: 参数类型列表，为空时取第一个匹配方法名的方法
            
        Returns:
            str: 方法的完整代码
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 文件类型不支持或方法不存在
            RuntimeError: tree-sitter相关错误
        """
        if Parser is None:
            raise RuntimeError("tree-sitter库未安装，无法进行方法提取")
        
        # 验证文件路径
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 检查文件是否支持
        if not support_file(file_path):
            raise ValueError(f"不支持的文件类型: {file_path.suffix}")
        
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            # 获取语言处理器
            handler = self._get_language_handler(file_path)
            if not handler:
                raise ValueError(f"无法获取语言处理器: {file_path.suffix}")
            
            # 解析代码
            tree = self._parse_code(code_content, file_path)
            if not tree:
                raise RuntimeError(f"代码解析失败: {file_path}")
            
            # 提取方法
            method_code = handler.extract_method(tree, code_content, method_name, arg_types or [])
            if not method_code:
                if arg_types:
                    raise ValueError(f"未找到匹配的方法: {method_name}({', '.join(arg_types)})")
                else:
                    raise ValueError(f"未找到方法: {method_name}")
            
            return method_code
            
        except Exception as e:
            logger.error(f"提取方法时发生错误: {e}")
            raise
    
    def _get_language_handler(self, file_path: Path):
        """获取语言处理器"""
        extension = file_path.suffix.lower()
        
        if extension in self.language_handlers:
            return self.language_handlers[extension]
        
        # 动态导入语言处理器
        try:
            if extension == '.py':
                from .parsers.python_parser import PythonMethodParser
                handler = PythonMethodParser()
            elif extension == '.java':
                from .parsers.java_parser import JavaMethodParser
                handler = JavaMethodParser()
            elif extension in ['.js', '.ts', '.jsx', '.tsx']:
                from .parsers.javascript_parser import JavaScriptMethodParser
                handler = JavaScriptMethodParser()
            elif extension == '.go':
                from .parsers.go_parser import GoMethodParser
                handler = GoMethodParser()
            elif extension == '.cs':
                from .parsers.csharp_parser import CSharpMethodParser
                handler = CSharpMethodParser()
            elif extension in ['.c', '.h']:
                from .parsers.c_parser import CMethodParser
                handler = CMethodParser()
            elif extension in ['.cpp', '.cc', '.cxx', '.hpp']:
                from .parsers.cpp_parser import CppMethodParser
                handler = CppMethodParser()
            else:
                logger.error(f"不支持的文件扩展名: {extension}")
                return None
            
            self.language_handlers[extension] = handler
            return handler
            
        except ImportError as e:
            logger.error(f"导入语言处理器失败 {extension}: {e}")
            return None
    
    def _parse_code(self, code_content: str, file_path: Path):
        """解析代码"""
        extension = file_path.suffix.lower()
        
        if extension in self.parsers:
            parser = self.parsers[extension]
        else:
            # 创建新的解析器
            lang_lib, lang_name = get_language_for_extension(extension)
            if not lang_lib:
                logger.error(f"无法获取语言库: {extension}")
                return None
            
            parser = Parser(lang_lib)
            self.parsers[extension] = parser
        
        try:
            tree = parser.parse(bytes(code_content, 'utf-8'))
            return tree
        except Exception as e:
            logger.error(f"解析代码失败: {e}")
            return None