"""
统一文件扩展名配置管理模块

该模块提供统一的文件扩展名配置管理，解决多个模块中扩展名定义重复、分散、不一致的问题。
支持RAG文档检索、编程语言识别、文件分类等多种使用场景。

设计原则：
- 单一数据源，避免重复定义
- 按用途分组，便于维护
- 向后兼容，不破坏现有功能
- 高性能查询，使用集合优化查询速度
"""

from typing import Dict, Set, Optional, List
from dataclasses import dataclass
from enum import Enum


class FileType(Enum):
    """文件类型枚举"""
    SOURCE = "source"           # 源代码文件
    DOCUMENT = "document"       # 文档文件
    BINARY = "binary"          # 二进制文件
    CONFIG = "config"          # 配置文件
    UNKNOWN = "unknown"        # 未知类型


@dataclass
class ExtensionInfo:
    """扩展名信息数据类"""
    extension: str              # 扩展名（包含.）
    file_type: FileType        # 文件类型
    language: Optional[str] = None    # 编程语言名称（如果是源码文件）
    description: Optional[str] = None # 描述信息
    rag_supported: bool = False       # 是否支持RAG检索


class FileExtensionConfig:
    """
    统一文件扩展名配置管理器
    
    用途：
    - 为RAG系统提供支持的文件类型
    - 为项目分析提供语言识别映射
    - 为目录工具提供文件分类规则
    
    特性：
    - 统一管理所有扩展名定义
    - 支持大小写不敏感查询
    - 提供高性能的集合查询
    - 保持向后兼容性
    """
    
    def __init__(self):
        """初始化配置管理器"""
        self._extensions_info: Dict[str, ExtensionInfo] = {}
        self._initialize_extensions()
        
        # 预计算的查询集合，提高查询性能
        self._rag_extensions: Set[str] = set()
        self._source_extensions: Set[str] = set()
        self._document_extensions: Set[str] = set()
        self._binary_extensions: Set[str] = set()
        self._language_mapping: Dict[str, str] = {}
        
        self._build_query_caches()
    
    def _initialize_extensions(self) -> None:
        """初始化所有扩展名定义"""
        
        # 编程语言文件扩展名（源码文件）
        programming_extensions = [
            # 主流编程语言
            ('.py', 'Python', 'Python源代码文件', True),
            ('.js', 'JavaScript', 'JavaScript源代码文件', True),
            ('.ts', 'TypeScript', 'TypeScript源代码文件', True),
            ('.java', 'Java', 'Java源代码文件', True),
            ('.go', 'Go', 'Go语言源代码文件', False),
            ('.rs', 'Rust', 'Rust源代码文件', False),
            ('.cpp', 'C++', 'C++源代码文件', False),
            ('.c', 'C', 'C语言源代码文件', False),
            ('.cs', 'C#', 'C#源代码文件', False),
            ('.php', 'PHP', 'PHP源代码文件', False),
            ('.rb', 'Ruby', 'Ruby源代码文件', False),
            ('.swift', 'Swift', 'Swift源代码文件', False),
            ('.kt', 'Kotlin', 'Kotlin源代码文件', False),
            ('.scala', 'Scala', 'Scala源代码文件', False),
            
            # Web开发相关
            ('.html', 'HTML', 'HTML标记语言文件', False),
            ('.css', 'CSS', 'CSS样式表文件', False),
            ('.scss', 'SCSS', 'SCSS样式表文件', False),
            ('.sass', 'Sass', 'Sass样式表文件', False),
            ('.less', 'Less', 'Less样式表文件', False),
            ('.vue', 'Vue', 'Vue.js组件文件', True),
            ('.jsx', 'React JSX', 'React JSX组件文件', False),
            ('.tsx', 'React TSX', 'React TypeScript组件文件', False),
            
            # 脚本语言
            ('.sh', 'Shell', 'Shell脚本文件', False),
            ('.bat', 'Batch', 'Windows批处理文件', False),
            ('.ps1', 'PowerShell', 'PowerShell脚本文件', False),
            ('.pl', 'Perl', 'Perl脚本文件', False),
            ('.lua', 'Lua', 'Lua脚本文件', False),
            
            # 数据库和查询语言
            ('.sql', 'SQL', 'SQL查询文件', False),
            
            # Android开发相关
            ('.kt', 'Kotlin', 'Kotlin源代码文件', True),
            ('.java', 'Java', 'Java源代码文件', True),
            ('.xml', 'XML', 'Android XML文件', True),
            ('.gradle', 'Gradle', 'Gradle构建脚本', True),
            ('.properties', 'Properties', 'Android属性配置文件', True),
            ('.pro', 'ProGuard', 'ProGuard配置文件', False),
            ('.aidl', 'AIDL', 'Android接口定义语言文件', False),
            
            # 其他编程语言
            ('.r', 'R', 'R语言脚本文件', False),
            ('.m', 'Objective-C', 'Objective-C源代码文件', False),
            ('.mm', 'Objective-C++', 'Objective-C++源代码文件', False),
            ('.dart', 'Dart', 'Dart语言源代码文件', False),
            ('.elm', 'Elm', 'Elm语言源代码文件', False),
            ('.clj', 'Clojure', 'Clojure源代码文件', False),
            ('.fs', 'F#', 'F#源代码文件', False),
            ('.vb', 'Visual Basic', 'Visual Basic源代码文件', False),
            ('.pas', 'Pascal', 'Pascal源代码文件', False),
            ('.asm', 'Assembly', '汇编语言源代码文件', False),
            ('.s', 'Assembly', '汇编语言源代码文件', False),
            ('.f', 'Fortran', 'Fortran源代码文件', False),
            ('.f90', 'Fortran 90', 'Fortran 90源代码文件', False),
            ('.f95', 'Fortran 95', 'Fortran 95源代码文件', False),
            ('.jl', 'Julia', 'Julia语言源代码文件', False),
            ('.nim', 'Nim', 'Nim语言源代码文件', False),
            
            # 头文件
            ('.h', 'C/C++ Header', 'C/C++头文件', False),
            ('.hpp', 'C++ Header', 'C++头文件', False),
        ]
        
        # 配置和数据文件（也归类为源码文件，因为通常是文本格式且可编辑）
        config_extensions = [
            ('.json', 'JSON', 'JSON数据文件', True),
            ('.yaml', 'YAML', 'YAML配置文件', True),
            ('.yml', 'YAML', 'YAML配置文件', True),
            ('.xml', 'XML', 'XML数据文件', False),
            ('.toml', 'TOML', 'TOML配置文件', False),
            ('.ini', 'INI', 'INI配置文件', False),
            ('.cfg', 'Config', '配置文件', False),
            ('.conf', 'Config', '配置文件', False),
        ]
        
        # 文档文件扩展名
        document_extensions = [
            # 纯文本和标记语言
            ('.md', 'Markdown', 'Markdown文档文件', True),
            ('.txt', 'Text', '纯文本文件', True),
            ('.rst', 'reStructuredText', 'reStructuredText文档', False),
            ('.adoc', 'AsciiDoc', 'AsciiDoc文档', False),
            ('.tex', 'LaTeX', 'LaTeX文档', False),
            ('.readme', 'README', 'README文档文件', False),
            ('.log', 'Log', '日志文件', False),
            
            # Office文档
            ('.doc', 'Word Document', 'Microsoft Word文档', False),
            ('.docx', 'Word Document', 'Microsoft Word文档', False),
            ('.pdf', 'PDF', 'PDF文档', False),
            ('.rtf', 'RTF', '富文本格式文档', False),
            ('.odt', 'OpenDocument Text', 'OpenDocument文本文档', False),
            ('.ods', 'OpenDocument Spreadsheet', 'OpenDocument电子表格', False),
            ('.odp', 'OpenDocument Presentation', 'OpenDocument演示文稿', False),
            
            # Apple办公文档
            ('.pages', 'Pages', 'Apple Pages文档', False),
            ('.numbers', 'Numbers', 'Apple Numbers电子表格', False),
            ('.key', 'Keynote', 'Apple Keynote演示文稿', False),
            
            # 电子书格式
            ('.epub', 'EPUB', 'EPUB电子书', False),
            ('.mobi', 'MOBI', 'MOBI电子书', False),
            ('.azw', 'AZW', 'Amazon Kindle电子书', False),
            ('.azw3', 'AZW3', 'Amazon Kindle电子书', False),
            ('.fb2', 'FB2', 'FictionBook电子书', False),
            ('.djvu', 'DjVu', 'DjVu文档', False),
            ('.xps', 'XPS', 'XML Paper Specification文档', False),
            ('.ps', 'PostScript', 'PostScript文档', False),
        ]
        
        # 二进制文件扩展名
        binary_extensions = [
            # 库文件和可执行文件
            ('.lib', 'Library', '静态库文件', False),
            ('.so', 'Shared Object', '共享库文件', False),
            ('.jar', 'Java Archive', 'Java归档文件', False),
            ('.dll', 'Dynamic Link Library', '动态链接库', False),
            ('.exe', 'Executable', '可执行文件', False),
            ('.bin', 'Binary', '二进制文件', False),
            ('.obj', 'Object File', '目标文件', False),
            ('.o', 'Object File', '目标文件', False),
            ('.a', 'Archive', '归档文件', False),
            ('.dylib', 'Dynamic Library', 'macOS动态库', False),
            
            # 应用程序包
            ('.war', 'Web Archive', 'Web应用归档', False),
            ('.ear', 'Enterprise Archive', '企业应用归档', False),
            ('.apk', 'Android Package', 'Android应用包', False),
            ('.ipa', 'iOS App Store Package', 'iOS应用包', False),
            ('.dex', 'Dalvik Executable', 'Android Dalvik可执行文件', False),
            ('.class', 'Java Class', 'Java字节码文件', False),
            
            # Python编译文件
            ('.pyc', 'Python Compiled', 'Python字节码文件', False),
            ('.pyo', 'Python Optimized', 'Python优化字节码文件', False),
            ('.pyd', 'Python Extension', 'Python扩展模块', False),
            ('.whl', 'Python Wheel', 'Python Wheel包', False),
            ('.egg', 'Python Egg', 'Python Egg包', False),
            
            # 包管理器文件
            ('.gem', 'Ruby Gem', 'Ruby Gem包', False),
            ('.nupkg', 'NuGet Package', 'NuGet包', False),
            ('.vsix', 'Visual Studio Extension', 'Visual Studio扩展', False),
            ('.crx', 'Chrome Extension', 'Chrome扩展', False),
            
            # 压缩文件
            ('.zip', 'ZIP Archive', 'ZIP压缩文件', False),
            ('.tar', 'TAR Archive', 'TAR归档文件', False),
            ('.gz', 'Gzip', 'Gzip压缩文件', False),
            ('.rar', 'RAR Archive', 'RAR压缩文件', False),
            ('.7z', '7-Zip Archive', '7-Zip压缩文件', False),
            ('.bz2', 'Bzip2', 'Bzip2压缩文件', False),
            ('.xz', 'XZ', 'XZ压缩文件', False),
            ('.lz', 'Lzip', 'Lzip压缩文件', False),
            ('.lzma', 'LZMA', 'LZMA压缩文件', False),
            ('.tgz', 'TAR.GZ', 'TAR.GZ压缩文件', False),
            ('.tbz2', 'TAR.BZ2', 'TAR.BZ2压缩文件', False),
            ('.txz', 'TAR.XZ', 'TAR.XZ压缩文件', False),
            
            # 系统安装包
            ('.deb', 'Debian Package', 'Debian软件包', False),
            ('.rpm', 'RPM Package', 'RPM软件包', False),
            ('.msi', 'Windows Installer', 'Windows安装程序', False),
            ('.dmg', 'macOS Disk Image', 'macOS磁盘映像', False),
            ('.iso', 'ISO Image', 'ISO镜像文件', False),
            ('.img', 'Disk Image', '磁盘映像文件', False),
            
            # 其他压缩格式
            ('.cab', 'Cabinet', 'Windows Cabinet文件', False),
            ('.ace', 'ACE Archive', 'ACE压缩文件', False),
            ('.arj', 'ARJ Archive', 'ARJ压缩文件', False),
            ('.z', 'Compress', 'Unix Compress文件', False),
        ]
        
        # 注册所有扩展名
        for ext, lang, desc, rag in programming_extensions:
            self._extensions_info[ext] = ExtensionInfo(
                extension=ext,
                file_type=FileType.SOURCE,
                language=lang,
                description=desc,
                rag_supported=rag
            )
        
        for ext, lang, desc, rag in config_extensions:
            self._extensions_info[ext] = ExtensionInfo(
                extension=ext,
                file_type=FileType.CONFIG,  # 配置文件单独分类，但查询时归入源码
                language=lang,
                description=desc,
                rag_supported=rag
            )
        
        for ext, format_name, desc, rag in document_extensions:
            self._extensions_info[ext] = ExtensionInfo(
                extension=ext,
                file_type=FileType.DOCUMENT,
                language=None,
                description=desc,
                rag_supported=rag
            )
        
        for ext, format_name, desc, rag in binary_extensions:
            self._extensions_info[ext] = ExtensionInfo(
                extension=ext,
                file_type=FileType.BINARY,
                language=None,
                description=desc,
                rag_supported=rag
            )
    
    def _build_query_caches(self) -> None:
        """构建查询缓存，提高查询性能"""
        for ext, info in self._extensions_info.items():
            if info.rag_supported:
                self._rag_extensions.add(ext)
            
            if info.file_type in (FileType.SOURCE, FileType.CONFIG):
                self._source_extensions.add(ext)
                if info.language:
                    self._language_mapping[ext] = info.language
            elif info.file_type == FileType.DOCUMENT:
                self._document_extensions.add(ext)
            elif info.file_type == FileType.BINARY:
                self._binary_extensions.add(ext)
    
    def get_rag_supported_extensions(self) -> Set[str]:
        """
        获取RAG系统支持的文件扩展名
        
        Returns:
            Set[str]: RAG支持的扩展名集合
        """
        return self._rag_extensions.copy()
    
    def get_language_by_extension(self, ext: str) -> Optional[str]:
        """
        根据扩展名获取编程语言名称
        
        Args:
            ext: 文件扩展名（支持大小写不敏感）
            
        Returns:
            Optional[str]: 编程语言名称，未找到返回None
        """
        ext_lower = ext.lower()
        if not ext_lower.startswith('.'):
            ext_lower = '.' + ext_lower
        return self._language_mapping.get(ext_lower)
    
    def get_source_extensions(self) -> Set[str]:
        """
        获取源代码文件扩展名（包括配置文件）
        
        Returns:
            Set[str]: 源代码文件扩展名集合
        """
        return self._source_extensions.copy()
    
    def get_document_extensions(self) -> Set[str]:
        """
        获取文档文件扩展名
        
        Returns:
            Set[str]: 文档文件扩展名集合
        """
        return self._document_extensions.copy()
    
    def get_binary_extensions(self) -> Set[str]:
        """
        获取二进制文件扩展名
        
        Returns:
            Set[str]: 二进制文件扩展名集合
        """
        return self._binary_extensions.copy()
    
    def classify_file_type(self, ext: str) -> FileType:
        """
        根据扩展名分类文件类型
        
        Args:
            ext: 文件扩展名（支持大小写不敏感）
            
        Returns:
            FileType: 文件类型枚举值
        """
        ext_lower = ext.lower()
        if not ext_lower.startswith('.'):
            ext_lower = '.' + ext_lower
        
        info = self._extensions_info.get(ext_lower)
        if info:
            # 配置文件在分类时归入源码文件
            if info.file_type == FileType.CONFIG:
                return FileType.SOURCE
            return info.file_type
        
        return FileType.UNKNOWN
    
    def is_programming_file(self, ext: str) -> bool:
        """
        判断是否为编程相关文件（源码或配置文件）
        
        Args:
            ext: 文件扩展名（支持大小写不敏感）
            
        Returns:
            bool: 是否为编程文件
        """
        return self.classify_file_type(ext) == FileType.SOURCE
    
    def is_document_file(self, ext: str) -> bool:
        """
        判断是否为文档文件
        
        Args:
            ext: 文件扩展名（支持大小写不敏感）
            
        Returns:
            bool: 是否为文档文件
        """
        return self.classify_file_type(ext) == FileType.DOCUMENT
    
    def is_binary_file(self, ext: str) -> bool:
        """
        判断是否为二进制文件
        
        Args:
            ext: 文件扩展名（支持大小写不敏感）
            
        Returns:
            bool: 是否为二进制文件
        """
        return self.classify_file_type(ext) == FileType.BINARY
    
    def is_rag_supported(self, ext: str) -> bool:
        """
        判断文件是否支持RAG检索
        
        Args:
            ext: 文件扩展名（支持大小写不敏感）
            
        Returns:
            bool: 是否支持RAG检索
        """
        ext_lower = ext.lower()
        if not ext_lower.startswith('.'):
            ext_lower = '.' + ext_lower
        return ext_lower in self._rag_extensions
    
    def get_language_mapping(self) -> Dict[str, str]:
        """
        获取扩展名到编程语言的完整映射
        
        Returns:
            Dict[str, str]: 扩展名到语言名称的映射字典
        """
        return self._language_mapping.copy()
    
    def get_extension_info(self, ext: str) -> Optional[ExtensionInfo]:
        """
        获取扩展名的详细信息
        
        Args:
            ext: 文件扩展名（支持大小写不敏感）
            
        Returns:
            Optional[ExtensionInfo]: 扩展名信息，未找到返回None
        """
        ext_lower = ext.lower()
        if not ext_lower.startswith('.'):
            ext_lower = '.' + ext_lower
        return self._extensions_info.get(ext_lower)
    
    def get_all_extensions(self) -> List[str]:
        """
        获取所有已定义的扩展名列表
        
        Returns:
            List[str]: 所有扩展名的排序列表
        """
        return sorted(self._extensions_info.keys())
    
    def get_statistics(self) -> Dict[str, int]:
        """
        获取扩展名统计信息
        
        Returns:
            Dict[str, int]: 各类型文件的扩展名数量统计
        """
        stats = {
            'total': len(self._extensions_info),
            'source': len(self._source_extensions),
            'document': len(self._document_extensions),
            'binary': len(self._binary_extensions),
            'rag_supported': len(self._rag_extensions),
            'with_language_mapping': len(self._language_mapping)
        }
        return stats


# 全局配置实例（单例模式）
_config_instance: Optional[FileExtensionConfig] = None


def get_config() -> FileExtensionConfig:
    """
    获取全局配置实例（单例模式）
    
    Returns:
        FileExtensionConfig: 配置管理器实例
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = FileExtensionConfig()
    return _config_instance


# 便捷函数，保持向后兼容性
def get_rag_supported_extensions() -> Set[str]:
    """获取RAG支持的扩展名"""
    return get_config().get_rag_supported_extensions()


def get_language_by_extension(ext: str) -> Optional[str]:
    """根据扩展名获取编程语言"""
    return get_config().get_language_by_extension(ext)


def get_source_extensions() -> Set[str]:
    """获取源代码文件扩展名"""
    return get_config().get_source_extensions()


def get_document_extensions() -> Set[str]:
    """获取文档文件扩展名"""
    return get_config().get_document_extensions()


def get_binary_extensions() -> Set[str]:
    """获取二进制文件扩展名"""
    return get_config().get_binary_extensions()


def classify_file_type(ext: str) -> FileType:
    """分类文件类型"""
    return get_config().classify_file_type(ext)


def is_programming_file(ext: str) -> bool:
    """判断是否为编程文件"""
    return get_config().is_programming_file(ext)


def is_document_file(ext: str) -> bool:
    """判断是否为文档文件"""
    return get_config().is_document_file(ext)


def is_binary_file(ext: str) -> bool:
    """判断是否为二进制文件"""
    return get_config().is_binary_file(ext)


def is_rag_supported(ext: str) -> bool:
    """判断是否支持RAG检索"""
    return get_config().is_rag_supported(ext)


def get_language_mapping() -> Dict[str, str]:
    """获取语言映射"""
    return get_config().get_language_mapping()


# 使用示例和测试代码
if __name__ == "__main__":
    # 创建配置实例
    config = FileExtensionConfig()
    
    # 打印统计信息
    print("=== 文件扩展名配置统计 ===")
    stats = config.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n=== RAG支持的扩展名 ===")
    rag_exts = config.get_rag_supported_extensions()
    print(f"共 {len(rag_exts)} 个: {sorted(rag_exts)}")
    
    print("\n=== 编程语言映射示例 ===")
    test_extensions = ['.py', '.js', '.ts', '.java', '.go', '.rs']
    for ext in test_extensions:
        lang = config.get_language_by_extension(ext)
        print(f"{ext} -> {lang}")
    
    print("\n=== 文件分类测试 ===")
    test_files = ['.py', '.md', '.exe', '.unknown']
    for ext in test_files:
        file_type = config.classify_file_type(ext)
        print(f"{ext} -> {file_type.value}")