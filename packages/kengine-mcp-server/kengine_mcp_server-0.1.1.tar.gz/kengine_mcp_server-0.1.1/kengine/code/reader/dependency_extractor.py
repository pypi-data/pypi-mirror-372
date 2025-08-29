"""
依赖提取器
负责从代码文件中提取依赖关系
"""

import logging
import glob
from pathlib import Path
from typing import List, Union, Set, Dict
from tree_sitter import Parser

from ..language_loader import support_file, get_language_for_extension
from .parsers.python_parser import PythonMethodParser
from .parsers.java_parser import JavaMethodParser
from .parsers.javascript_parser import JavaScriptMethodParser
from .parsers.go_parser import GoMethodParser
from .parsers.csharp_parser import CSharpMethodParser
from .parsers.cpp_parser import CppMethodParser
from .parsers.c_parser import CMethodParser

logger = logging.getLogger(__name__)


class DependencyInfo:
    """依赖信息类"""
    
    def __init__(self, import_name: str, import_type: str, file_path: str = "", 
                 is_builtin: bool = False, is_third_party: bool = False):
        self.import_name = import_name  # 导入的模块/类名
        self.import_type = import_type  # 导入类型：import, from_import, include等
        self.file_path = file_path      # 对应的文件路径（如果是项目内依赖）
        self.is_builtin = is_builtin    # 是否为语言内置依赖
        self.is_third_party = is_third_party  # 是否为第三方依赖
    
    def __str__(self):
        return f"{self.import_type}: {self.import_name}"
    
    def __repr__(self):
        return f"DependencyInfo(name='{self.import_name}', type='{self.import_type}', builtin={self.is_builtin}, third_party={self.is_third_party})"


class DependencyFilter:
    """依赖过滤器 - 负责过滤内置和第三方依赖"""
    
    # 各语言的内置依赖模式
    BUILTIN_PATTERNS = {
        'python': {
            'os', 'sys', 'json', 'datetime', 'collections', 'itertools', 
            'functools', 're', 'math', 'random', 'urllib', 'http', 'pathlib',
            'typing', 'abc', 'logging', 'unittest', 'asyncio', 'threading',
            'multiprocessing', 'subprocess', 'tempfile', 'glob', 'shutil',
            'pickle', 'csv', 'xml', 'sqlite3', 'hashlib', 'base64'
        },
        'java': {
            'java.lang', 'java.util', 'java.io', 'java.nio', 'java.net',
            'java.time', 'java.math', 'java.text', 'java.sql', 'java.awt',
            'javax.swing', 'javax.servlet', 'javax.annotation'
        },
        'javascript': {
            # Node.js 内置模块
            'fs', 'path', 'http', 'https', 'url', 'util', 'events', 'stream',
            'buffer', 'os', 'child_process', 'process', 'console', 'assert',
            'crypto', 'dns', 'net', 'tls', 'dgram', 'readline', 'repl',
            'vm', 'zlib', 'cluster', 'domain', 'punycode', 'querystring',
            'string_decoder', 'timers',
            # 浏览器全局对象
            'window', 'document', 'navigator', 'location', 'history', 'screen',
            'localStorage', 'sessionStorage', 'XMLHttpRequest', 'fetch',
            'Promise', 'Array', 'Object', 'String', 'Number', 'Boolean',
            'Date', 'RegExp', 'Error', 'JSON', 'Math', 'parseInt', 'parseFloat',
            'isNaN', 'isFinite', 'encodeURI', 'decodeURI', 'encodeURIComponent',
            'decodeURIComponent', 'setTimeout', 'setInterval', 'clearTimeout',
            'clearInterval', 'alert', 'confirm', 'prompt'
        },
        'go': {
            'fmt', 'os', 'io', 'net', 'http', 'strings', 'strconv', 'time',
            'math', 'sync', 'context', 'errors', 'log', 'testing', 'unsafe',
            'reflect', 'runtime', 'sort', 'unicode'
        },
        'c_sharp': {
            'System', 'System.IO', 'System.Net', 'System.Text', 'System.Linq',
            'System.Collections', 'System.Threading', 'System.Diagnostics',
            'Microsoft.CSharp', 'Microsoft.VisualBasic'
        },
        'cpp': {
            'iostream', 'fstream', 'sstream', 'string', 'vector', 'map',
            'set', 'list', 'queue', 'stack', 'algorithm', 'functional',
            'memory', 'thread', 'mutex', 'chrono', 'random', 'cmath',
            'cstdio', 'cstdlib', 'cstring', 'ctime'
        },
        'c': {
            'stdio.h', 'stdlib.h', 'string.h', 'math.h', 'time.h', 'ctype.h',
            'stddef.h', 'stdint.h', 'stdbool.h', 'errno.h', 'limits.h',
            'float.h', 'locale.h', 'setjmp.h', 'signal.h', 'stdarg.h'
        },
        'kotlin': {
            'kotlin', 'kotlin.collections', 'kotlin.io', 'kotlin.math', 
            'kotlin.random', 'kotlin.reflect', 'kotlin.system', 'kotlin.text',
            'kotlin.time', 'kotlin.concurrent'
        }
    }
    
    def __init__(self, language: str):
        self.language = language
        self.builtin_patterns = self.BUILTIN_PATTERNS.get(language, set())
    
    def is_builtin_dependency(self, import_name: str) -> bool:
        """检查是否为内置依赖"""
        # 直接匹配
        if import_name in self.builtin_patterns:
            return True
        
        # 前缀匹配
        for pattern in self.builtin_patterns:
            if import_name.startswith(pattern):
                return True
        
        return False
    
    def filter_dependencies(self, dependencies: List[DependencyInfo]) -> List[DependencyInfo]:
        """过滤依赖，标记内置和第三方依赖"""
        filtered = []
        
        for dep in dependencies:
            # 标记内置依赖
            if self.is_builtin_dependency(dep.import_name):
                dep.is_builtin = True
            
            # 如果不是内置依赖且没有找到对应文件，标记为第三方依赖
            if not dep.is_builtin and not dep.file_path:
                dep.is_third_party = True
            
            filtered.append(dep)
        
        return filtered


class ProjectFileSearcher:
    """项目文件搜索器 - 负责在项目中搜索依赖对应的文件"""
    
    def __init__(self, project_path: Union[str, Path]):
        self.project_path = Path(project_path)
        self._file_cache = {}  # 缓存文件搜索结果
    
    def find_dependency_file(self, import_name: str, language: str) -> str:
        """
        在项目中查找依赖对应的文件
        
        Args:
            import_name: 导入名称
            language: 编程语言
            
        Returns:
            str: 相对于project_path的文件路径，如果未找到返回空字符串
        """
        if import_name in self._file_cache:
            return self._file_cache[import_name]
        
        file_path = ""
        
        try:
            if language == 'python':
                file_path = self._find_python_file(import_name)
            elif language == 'java':
                file_path = self._find_java_file(import_name)
            elif language == 'javascript':
                file_path = self._find_javascript_file(import_name)
            elif language == 'go':
                file_path = self._find_go_file(import_name)
            elif language in ['c_sharp']:
                file_path = self._find_csharp_file(import_name)
            elif language in ['cpp', 'c']:
                file_path = self._find_cpp_file(import_name)
            elif language == 'kotlin':
                file_path = self._find_kotlin_file(import_name)
            
            # 缓存结果
            self._file_cache[import_name] = file_path
            
        except Exception as e:
            logger.error(f"搜索依赖文件时发生错误 {import_name}: {e}")
        
        return file_path
    
    def _find_python_file(self, import_name: str) -> str:
        """查找Python文件"""
        # 将模块名转换为文件路径
        module_parts = import_name.split('.')
        
        # 尝试查找 .py 文件
        for i in range(len(module_parts), 0, -1):
            partial_path = '/'.join(module_parts[:i])
            
            # 查找文件
            patterns = [
                f"**/{partial_path}.py",
                f"**/{partial_path}/__init__.py"
            ]
            
            for pattern in patterns:
                matches = list(self.project_path.glob(pattern))
                if matches:
                    return str(matches[0].relative_to(self.project_path))
        
        return ""
    
    def _find_java_file(self, import_name: str) -> str:
        """查找Java文件"""
        # Java类名通常对应文件名
        class_parts = import_name.split('.')
        class_name = class_parts[-1]
        
        # 查找 .java 文件
        pattern = f"**/{class_name}.java"
        matches = list(self.project_path.glob(pattern))
        
        if matches:
            return str(matches[0].relative_to(self.project_path))
        
        return ""
    
    def _find_javascript_file(self, import_name: str) -> str:
        """查找JavaScript文件"""
        # 移除相对路径前缀
        clean_name = import_name.lstrip('./')
        
        # 尝试不同的文件扩展名
        extensions = ['.js', '.ts', '.jsx', '.tsx']
        
        for ext in extensions:
            patterns = [
                f"**/{clean_name}{ext}",
                f"**/{clean_name}/index{ext}"
            ]
            
            for pattern in patterns:
                matches = list(self.project_path.glob(pattern))
                if matches:
                    return str(matches[0].relative_to(self.project_path))
        
        return ""
    
    def _find_go_file(self, import_name: str) -> str:
        """查找Go文件"""
        # Go包名通常对应目录名
        package_parts = import_name.split('/')
        package_name = package_parts[-1]
        
        # 查找 .go 文件
        pattern = f"**/{package_name}/*.go"
        matches = list(self.project_path.glob(pattern))
        
        if matches:
            return str(matches[0].relative_to(self.project_path))
        
        return ""
    
    def _find_csharp_file(self, import_name: str) -> str:
        """查找C#文件"""
        # C#命名空间通常对应文件结构
        namespace_parts = import_name.split('.')
        class_name = namespace_parts[-1]
        
        # 查找 .cs 文件
        pattern = f"**/{class_name}.cs"
        matches = list(self.project_path.glob(pattern))
        
        if matches:
            return str(matches[0].relative_to(self.project_path))
        
        return ""
    
    def _find_cpp_file(self, import_name: str) -> str:
        """查找C++文件"""
        # 移除文件扩展名
        header_name = import_name.replace('.h', '').replace('.hpp', '')
        
        # 尝试不同的文件扩展名
        extensions = ['.h', '.hpp', '.cpp', '.cc', '.cxx']
        
        for ext in extensions:
            pattern = f"**/{header_name}{ext}"
            matches = list(self.project_path.glob(pattern))
            if matches:
                return str(matches[0].relative_to(self.project_path))
        
        return ""
    
    def _find_kotlin_file(self, import_name: str) -> str:
        """查找Kotlin文件"""
        # Kotlin类名通常对应文件名
        class_parts = import_name.split('.')
        class_name = class_parts[-1]
        
        # 查找 .kt 文件
        pattern = f"**/{class_name}.kt"
        matches = list(self.project_path.glob(pattern))
        
        if matches:
            return str(matches[0].relative_to(self.project_path))
        
        return ""


class DependencyExtractor:
    """依赖提取器主类"""
    
    def __init__(self):
        # 导入KotlinMethodParser
        try:
            from .parsers.kotlin_parser import KotlinMethodParser
            kotlin_parser_available = True
        except ImportError:
            kotlin_parser_available = False
            logger.warning("无法导入KotlinMethodParser")
        
        self.parsers = {
            'python': PythonMethodParser(),
            'java': JavaMethodParser(),
            'javascript': JavaScriptMethodParser(),
            'go': GoMethodParser(),
            'c_sharp': CSharpMethodParser(),
            'cpp': CppMethodParser(),
            'c': CMethodParser()
        }
        
        # 如果Kotlin解析器可用，添加到parsers字典中
        if kotlin_parser_available:
            self.parsers['kotlin'] = KotlinMethodParser()
    
    def extract_dependencies(self, project_path: Union[str, Path], 
                           file_path: Union[str, Path]) -> List[str]:
        """
        从代码文件中提取依赖
        
        Args:
            project_path: 项目根路径
            file_path: 要分析的文件路径
            
        Returns:
            List[str]: 项目内依赖文件的相对路径列表
            
        Raises:
            ValueError: 文件类型不支持或文件不存在
            RuntimeError: tree-sitter相关错误
        """
        try:
            # 检查文件是否支持
            if not support_file(file_path):
                raise ValueError(f"不支持的文件类型: {file_path}")
            
            # 检查文件是否存在
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 获取语言信息
            lang_lib, language = get_language_for_extension(file_path.suffix)
            if not lang_lib:
                raise ValueError(f"无法加载语言库: {file_path.suffix}")
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            # 解析代码
            parser = Parser()
            parser.language = lang_lib
            tree = parser.parse(bytes(code_content, 'utf-8'))
            
            # 获取对应的解析器
            method_parser = self.parsers.get(language)
            if not method_parser:
                raise ValueError(f"不支持的语言: {language}")
            
            # 提取依赖
            dependencies = method_parser.extract_dependencies(tree, code_content)
            
            # 创建文件搜索器和依赖过滤器
            file_searcher = ProjectFileSearcher(project_path)
            dependency_filter = DependencyFilter(language)
            
            # 搜索依赖对应的文件
            for dep in dependencies:
                if not dep.file_path:
                    dep.file_path = file_searcher.find_dependency_file(dep.import_name, language)
            
            # 过滤依赖
            filtered_dependencies = dependency_filter.filter_dependencies(dependencies)
            
            # 只返回项目内依赖的相对路径
            project_dependencies = []
            for dep in filtered_dependencies:
                if not dep.is_builtin and not dep.is_third_party and dep.file_path:
                    project_dependencies.append(dep.file_path)
            
            return project_dependencies
            
        except Exception as e:
            logger.error(f"提取依赖时发生错误: {e}")
            raise
    
    def extract_method(self, file_path: Union[str, Path], method_name: str, 
                       arg_types: List[str] = None) -> str:
        """
        从代码文件中提取指定方法
        
        Args:
            file_path: 要分析的文件路径
            method_name: 方法名
            arg_types: 参数类型列表（可选）
            
        Returns:
            str: 方法的完整代码，如果未找到则返回空字符串
            
        Raises:
            ValueError: 文件类型不支持或文件不存在
            RuntimeError: tree-sitter相关错误
        """
        try:
            # 检查文件是否支持
            if not support_file(file_path):
                raise ValueError(f"不支持的文件类型: {file_path}")
            
            # 检查文件是否存在
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 获取语言信息
            lang_lib, language = get_language_for_extension(file_path.suffix)
            if not lang_lib:
                raise ValueError(f"无法加载语言库: {file_path.suffix}")
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            # 解析代码
            parser = Parser()
            parser.language = lang_lib
            tree = parser.parse(bytes(code_content, 'utf-8'))
            
            # 获取对应的解析器
            method_parser = self.parsers.get(language)
            if not method_parser:
                raise ValueError(f"不支持的语言: {language}")
            
            # 提取指定方法
            method_code = method_parser.extract_method(tree, code_content, method_name, arg_types or [])
            
            return method_code
            
        except Exception as e:
            logger.error(f"提取方法时发生错误: {e}")
            raise