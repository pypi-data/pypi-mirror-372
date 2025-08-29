"""
项目信息提取工具模块

提供从本地目录提取项目信息的功能，包括README文件、配置文件、目录结构分析等。
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, NamedTuple
from dataclasses import dataclass

from .text_reader import TextReader
from .dir_utils import classify_files_by_type
from .dir_utils.markdown_generator import generate_directory_markdown
from ..config.file_extensions import get_language_by_extension

logger = logging.getLogger(__name__)

# 缓存功能已通过 @cached 装饰器实现


MAX_CONFIG_FILE_SIZE = 50000
MAX_STRUCTURE_LINES = 1000
README_MAX_LENGTH = 1000

@dataclass
class ProjectInfo:
    """项目信息数据类"""
    directory_path: str
    project_name: str = ""
    readme_content: Optional[str] = None
    config_files: Dict[str, str] = None
    file_statistics: Dict[str, int] = None
    language_statistics: Dict[str, int] = None
    primary_language: Optional[str] = None
    directory_structure: Optional[str] = None
    
    def __post_init__(self):
        if self.config_files is None:
            self.config_files = {}
        if self.file_statistics is None:
            self.file_statistics = {}
        if self.language_statistics is None:
            self.language_statistics = {}


class ProjectAnalyzer:
    """项目分析器，用于提取项目信息"""
    
    # 常见的README文件名
    README_FILENAMES = [
        "README.md", "README.txt", "README.rst", "README", "readme.md", 
        "readme.txt", "readme.rst", "readme", "Readme.md", "Readme.txt"
    ]
    
    # 项目配置文件名（用于获取项目信息）
    PROJECT_CONFIG_FILES = [
        "package.json", "setup.py", "requirements.txt", "Cargo.toml", "go.mod",
        "pom.xml", "build.gradle", "composer.json", "Gemfile", "pubspec.yaml",
        "project.clj", "mix.exs", "stack.yaml", "Pipfile", "pyproject.toml"
    ]
    
    
    
    def __init__(self, max_config_file_size: int = MAX_CONFIG_FILE_SIZE, max_structure_lines: int = MAX_STRUCTURE_LINES):
        """
        初始化项目分析器
        
        Args:
            max_config_file_size: 配置文件最大读取字符数
            max_structure_lines: 目录结构最大显示行数
        """
        self.text_reader = TextReader()
        self.max_config_file_size = max_config_file_size
        self.max_structure_lines = max_structure_lines
    
    def analyze_project(self, directory_path: str) -> ProjectInfo:
        """
        分析项目目录，提取项目信息
        
        Args:
            directory_path: 项目目录路径
            
        Returns:
            ProjectInfo对象，包含项目的各种信息
            
        Raises:
            ValueError: 目录路径无效
            FileNotFoundError: 目录不存在
        """
        if not directory_path or not isinstance(directory_path, str):
            raise ValueError("目录路径不能为空")
        
        dir_path = Path(directory_path)
        if not dir_path.exists():
            raise FileNotFoundError(f"目录不存在: {directory_path}")
        
        if not dir_path.is_dir():
            raise ValueError(f"路径不是目录: {directory_path}")
        
        logger.info(f"开始分析项目: {directory_path}")
        
        # 提取项目名称（目录路径的最后一段）
        project_name = Path(directory_path).name
        
        project_info = ProjectInfo(directory_path=directory_path, project_name=project_name)
        
        # 1. 读取README文件
        # 对 readme进行必要精简
        readme = self._find_and_read_readme(dir_path)
        
        if readme and len(readme) > README_MAX_LENGTH:
            from kengine.core.utils.summerize import summerize
            logger.info(f"summerize readme to {README_MAX_LENGTH}")
            readme = summerize(readme, "default", README_MAX_LENGTH)
            
        project_info.readme_content = readme
        
        # 2. 读取配置文件
        project_info.config_files = self._read_config_files(dir_path)
        
        # 3. 分析文件统计和编程语言
        self._analyze_files_and_languages(dir_path, project_info)
        
        # 4. 生成目录结构
        project_info.directory_structure = self._generate_directory_structure(dir_path)
        
        logger.info(f"项目分析完成: {directory_path}")
        return project_info
    
    def _find_and_read_readme(self, dir_path: Path) -> Optional[str]:
        """
        查找并读取README文件
        
        Args:
            dir_path: 目录路径
            
        Returns:
            README文件内容，未找到返回None
        """
        for readme_name in self.README_FILENAMES:
            readme_path = dir_path / readme_name
            if readme_path.exists() and readme_path.is_file():
                content = self.text_reader.read_text_file(str(readme_path))
                if content:
                    logger.info(f"找到README文件: {readme_path}")
                    return content
        
        logger.info("未找到README文件")
        return None
    
    def _read_config_files(self, dir_path: Path) -> Dict[str, str]:
        """
        读取项目配置文件
        
        Args:
            dir_path: 目录路径
            
        Returns:
            配置文件名到内容的映射字典
        """
        config_files = {}
        
        for config_file in self.PROJECT_CONFIG_FILES:
            config_path = dir_path / config_file
            if config_path.exists() and config_path.is_file():
                content = self.text_reader.read_text_file(
                    str(config_path), 
                    max_length=self.max_config_file_size
                )
                if content:
                    config_files[config_file] = content
                    logger.info(f"读取配置文件: {config_path}")
        
        return config_files
    
    def _analyze_files_and_languages(self, dir_path: Path, project_info: ProjectInfo) -> None:
        """
        分析文件统计和编程语言分布
        
        Args:
            dir_path: 目录路径
            project_info: 项目信息对象，会被修改
        """
        try:
            source_files, doc_files, binary_files = classify_files_by_type(
                str(dir_path), recursive=True, include_hidden=False
            )
            
            # 文件统计
            project_info.file_statistics = {
                'total': len(source_files) + len(doc_files) + len(binary_files),
                'source': len(source_files),
                'document': len(doc_files),
                'binary': len(binary_files)
            }
            
            # 编程语言统计
            if source_files:
                project_info.language_statistics = self._analyze_programming_languages(source_files)
                # 检测主要编程语言
                project_info.primary_language = self._detect_primary_language(source_files, project_info.language_statistics)
            
            logger.info(f"文件分析完成: 总计 {project_info.file_statistics['total']} 个文件")
            if project_info.primary_language:
                logger.info(f"检测到主要编程语言: {project_info.primary_language}")
            
        except Exception as e:
            logger.warning(f"文件分析失败: {e}")
            project_info.file_statistics = {'total': 0, 'source': 0, 'document': 0, 'binary': 0}
            project_info.language_statistics = {}
    
    def _analyze_programming_languages(self, source_files: List[str]) -> Dict[str, int]:
        """
        分析编程语言分布
        
        Args:
            source_files: 源代码文件路径列表
            
        Returns:
            编程语言统计字典
        """
        language_stats = {}
        
        for file_path in source_files:
            ext = Path(file_path).suffix.lower()
            
            # 使用统一配置模块获取语言名称，提供降级方案
            try:
                language = get_language_by_extension(ext)
                if language is None:
                    language = f"其他({ext})"
            except Exception as e:
                logger.warning(f"无法从统一配置获取语言信息，使用默认处理: {e}")
                language = f"其他({ext})"
            
            language_stats[language] = language_stats.get(language, 0) + 1
        
        # 按文件数量排序，返回前10个
        sorted_stats = dict(sorted(language_stats.items(), key=lambda x: x[1], reverse=True)[:10])
        return sorted_stats
    
    def _detect_primary_language(self, source_files: List[str], language_statistics: Dict[str, int]) -> Optional[str]:
        """
        检测项目的主要编程语言
        
        基于以下策略进行检测：
        1. 排除配置文件、文档文件等非核心代码文件
        2. 考虑文件数量权重
        3. 考虑文件大小权重（大文件应该有更高权重）
        4. 处理多语言项目的情况
        
        Args:
            source_files: 源代码文件路径列表
            language_statistics: 语言统计字典
            
        Returns:
            主要编程语言名称，未检测到返回None
        """
        if not source_files or not language_statistics:
            return None
        
        try:
            # 定义需要排除的语言类型（配置文件、标记语言等）
            excluded_languages = {
                'JSON', 'YAML', 'XML', 'TOML', 'INI', 'Config',
                'HTML', 'CSS', 'SCSS', 'Sass', 'Less',
                'Markdown', 'Text'
            }
            
            # 计算加权分数
            language_scores = {}
            
            for file_path in source_files:
                try:
                    file_path_obj = Path(file_path)
                    ext = file_path_obj.suffix.lower()
                    
                    # 获取语言名称
                    language = get_language_by_extension(ext)
                    if not language:
                        continue
                    
                    # 跳过排除的语言类型
                    if language in excluded_languages:
                        continue
                    
                    # 跳过以"其他"开头的语言
                    if language.startswith("其他"):
                        continue
                    
                    # 获取文件大小权重
                    try:
                        file_size = file_path_obj.stat().st_size if file_path_obj.exists() else 0
                        # 文件大小权重：小文件权重1，大文件权重更高
                        size_weight = min(max(file_size / 1000, 1), 10)  # 1KB = 权重1，最大权重10
                    except (OSError, FileNotFoundError):
                        size_weight = 1
                    
                    # 累加权重分数
                    if language not in language_scores:
                        language_scores[language] = 0
                    language_scores[language] += size_weight
                    
                except Exception as e:
                    logger.debug(f"处理文件 {file_path} 时出错: {e}")
                    continue
            
            if not language_scores:
                # 如果没有有效的编程语言，从统计中选择文件数最多的非排除语言
                for language, count in sorted(language_statistics.items(), key=lambda x: x[1], reverse=True):
                    if language not in excluded_languages and not language.startswith("其他"):
                        return language
                return None
            
            # 找到得分最高的语言
            sorted_languages = sorted(language_scores.items(), key=lambda x: x[1], reverse=True)
            primary_language, primary_weight = sorted_languages[0]
            
            # 验证主语言的合理性
            primary_count = language_statistics.get(primary_language, 0)
            total_programming_files = sum(
                count for lang, count in language_statistics.items()
                if lang not in excluded_languages and not lang.startswith("其他")
            )
            
            # 计算权重比例
            total_weight = sum(language_scores.values())
            weight_ratio = primary_weight / total_weight if total_weight > 0 else 0
            
            # 改进的阈值条件：
            # 1. 至少2个文件，或
            # 2. 文件数占比超过30%，或
            # 3. 权重占比超过50%（考虑大文件的重要性）
            file_ratio = primary_count / total_programming_files if total_programming_files > 0 else 0
            
            if (primary_count >= 2 or
                file_ratio >= 0.3 or
                weight_ratio >= 0.5):
                return primary_language
            
            return None
            
        except Exception as e:
            logger.warning(f"主语言检测失败: {e}")
            # 降级方案：返回文件数最多的非排除语言
            try:
                excluded_languages = {'JSON', 'YAML', 'XML', 'HTML', 'CSS', 'Markdown'}
                for language, count in sorted(language_statistics.items(), key=lambda x: x[1], reverse=True):
                    if language not in excluded_languages and not language.startswith("其他"):
                        return language
            except Exception:
                pass
            return None
    
    def _generate_directory_structure(self, dir_path: Path) -> Optional[str]:
        """
        生成目录结构
        
        Args:
            dir_path: 目录路径
            
        Returns:
            目录结构字符串，生成失败返回None
        """
        max_depth = 4
        structure = generate_directory_markdown(
            str(dir_path), 
            max_depth,
            exclude_extensions=['.png', '.jpeg', '.gif', '.jpg' ,'.bmp', '.tiff', '.svg', '.ico',
                                '.lib', '.so' ,'.dll', '.exe', '.jar', 
                                '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.7z',
                                '.iso', '.img', '.apk', '.deb', '.rpm', '.msi', '.app', 
                                '.dmg', '.pkg', '.exe', '.bat', 
                                '.sql', '.xml', '.json', '.csv', '.tsv', '.log', '.md',
                                '.txt', '.rst', '.yml', '.yaml', '.ini', '.cfg','.http',
                                '.conf', '.properties', '.env', '.bat', '.sh'])
        logger.info(f'project directory \n{structure}')
        return structure


class ProjectInfoFormatter:
    """项目信息格式化器，将ProjectInfo转换为文本格式"""
    
    @staticmethod
    def format_project_info(project_info: ProjectInfo) -> str:
        """
        将项目信息格式化为文本
        
        Args:
            project_info: 项目信息对象
            
        Returns:
            格式化后的项目信息文本
        """
        sections = []
        
        # 项目名称
        if project_info.project_name:
            sections.append("=== 项目信息 ===")
            sections.append(f"项目名称: {project_info.project_name}")
            sections.append(f"项目路径: {project_info.directory_path}")
            if project_info.primary_language:
                sections.append(f"主要编程语言: {project_info.primary_language}")
        
        # README内容
        if project_info.readme_content:
            sections.append("=== README 内容 ===")
            sections.append(project_info.readme_content)
        
        # 项目配置信息
        if project_info.config_files:
            sections.append("=== 项目配置信息 ===")
            config_parts = []
            for filename, content in project_info.config_files.items():
                config_parts.append(f"--- {filename} ---")
                config_parts.append(content)
            sections.append("\n\n".join(config_parts))
        
        # 目录结构分析
        if project_info.file_statistics or project_info.language_statistics or project_info.directory_structure:
            sections.append("=== 目录结构分析 ===")
            analysis_parts = []
            
            # 文件统计
            if project_info.file_statistics and project_info.file_statistics.get('total', 0) > 0:
                stats = project_info.file_statistics
                analysis_parts.append(f"文件统计: 总计 {stats['total']} 个文件")
                analysis_parts.append(f"- 源代码文件: {stats['source']} 个")
                analysis_parts.append(f"- 文档文件: {stats['document']} 个")
                analysis_parts.append(f"- 二进制文件: {stats['binary']} 个")
            
            # 编程语言统计
            if project_info.language_statistics:
                analysis_parts.append("\n主要编程语言:")
                for lang, count in project_info.language_statistics.items():
                    analysis_parts.append(f"- {lang}: {count} 个文件")
            
            # 目录结构
            if project_info.directory_structure:
                analysis_parts.append(f"\n目录结构概览:\n{project_info.directory_structure}")
            
            if analysis_parts:
                sections.append("\n".join(analysis_parts))
        
        # 如果没有任何信息，提供基本信息
        if not sections:
            sections.append("=== 基本目录信息 ===")
            sections.append(f"目录路径: {project_info.directory_path}")
        
        return "\n\n".join(sections)


# 便捷函数 - 使用缓存装饰器
from ..cache.manager import cached

@cached(maxsize=50, ttl=1800)  # 缓存50个项目，30分钟TTL
def analyze_project(directory_path: str) -> ProjectInfo:
    """
    便捷的项目分析函数（带缓存）
    
    Args:
        directory_path: 项目目录路径
        
    Returns:
        ProjectInfo对象
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"🔍 [CACHE] analyze_project() 缓存未命中，开始分析项目: {directory_path}")
    
    import traceback
    stack_trace = traceback.format_stack()
    caller_info = stack_trace[-2].strip() if len(stack_trace) >= 2 else "未知调用者"
    logger.warning(f"🔍 [DEBUG] analyze_project() 调用者: {caller_info}")
    
    analyzer = ProjectAnalyzer()
    return analyzer.analyze_project(directory_path)


@cached(maxsize=50, ttl=1800)  # 缓存50个项目文本，30分钟TTL
def get_project_info_text(directory_path: str) -> str:
    """
    便捷的项目信息获取函数，直接返回格式化的文本（带缓存）
    
    Args:
        directory_path: 项目目录路径
        
    Returns:
        格式化的项目信息文本
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"🔍 [CACHE] get_project_info_text() 缓存未命中，开始生成文本: {directory_path}")
    
    project_info = analyze_project(directory_path)
    return ProjectInfoFormatter.format_project_info(project_info)


# 原始分析函数（不使用缓存）
def analyze_project_direct(directory_path: str) -> ProjectInfo:
    """
    直接分析项目（不使用缓存）
    
    Args:
        directory_path: 项目目录路径
        
    Returns:
        ProjectInfo对象
    """
    analyzer = ProjectAnalyzer()
    return analyzer.analyze_project(directory_path)


# 缓存管理函数
def clear_project_info_cache():
    """清除项目信息缓存"""
    import logging
    logger = logging.getLogger(__name__)
    
    if hasattr(analyze_project, 'cache_clear'):
        analyze_project.cache_clear()
        logger.info("已清除 analyze_project 缓存")
    
    if hasattr(get_project_info_text, 'cache_clear'):
        get_project_info_text.cache_clear()
        logger.info("已清除 get_project_info_text 缓存")


def get_project_info_cache_stats():
    """获取项目信息缓存统计"""
    stats = {}
    
    if hasattr(analyze_project, 'cache_info'):
        stats['analyze_project'] = analyze_project.cache_info()
    
    if hasattr(get_project_info_text, 'cache_info'):
        stats['get_project_info_text'] = get_project_info_text.cache_info()
    
    return stats