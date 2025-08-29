"""
文件内容精简工具模块

提供针对不同文件类型的精简功能，包括：
- pom.xml 文件的Maven项目信息提取
- build.gradle 文件的Gradle项目信息提取  
- 其他代码文件的智能精简处理

重构历史：
- 2025-01-05: 初始实现，支持多种文件类型的精简策略
"""

import hashlib
import logging
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple, Union, Optional

from ...utils.safe_file import safe_file_operation
from .exceptions import SummarizeError
from .summerize import summerize
from ...code.skeleton import extract_skeleton, support_file
from ...config.application_config import get_application_config

logger = logging.getLogger(__name__)

# 文件大小阈值（5KB）
FILE_SIZE_THRESHOLD = 5 * 1024


class FileSummarizeCache:
    """
    文件精简缓存管理器
    
    提供基于内容哈希的缓存机制，支持TTL过期和内存限制。
    缓存键基于文件路径、内容哈希和期望长度生成。
    """
    
    def __init__(self, max_size: int = 100):
        """
        初始化缓存管理器
        
        Args:
            max_size: 最大缓存条目数，防止内存无限增长
        """
        self._cache: Dict[str, Dict[str, Union[str, float]]] = {}
        self._max_size = max_size
        
    def _generate_cache_key(self, file_path: str, content: str, expected_length: int) -> str:
        """
        生成缓存键
        
        Args:
            file_path: 文件路径
            content: 文件内容
            expected_length: 期望长度
            
        Returns:
            缓存键字符串
        """
        # 对大内容使用哈希值避免内存问题
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        cache_key = f"{file_path}:{content_hash}:{expected_length}"
        return cache_key
    
    def get(self, file_path: str, content: str, expected_length: int, cache_ttl: int) -> Optional[str]:
        """
        从缓存获取结果
        
        Args:
            file_path: 文件路径
            content: 文件内容
            expected_length: 期望长度
            cache_ttl: 缓存TTL（秒）
            
        Returns:
            缓存的结果，如果不存在或已过期则返回None
        """
        cache_key = self._generate_cache_key(file_path, content, expected_length)
        
        if cache_key not in self._cache:
            return None
            
        cache_entry = self._cache[cache_key]
        current_time = time.time()
        
        # 检查是否过期
        if current_time - cache_entry['timestamp'] > cache_ttl:
            del self._cache[cache_key]
            logger.debug(f"缓存条目已过期并被删除: {cache_key}")
            return None
            
        logger.debug(f"缓存命中: {cache_key}")
        return cache_entry['result']
    
    def put(self, file_path: str, content: str, expected_length: int, result: str) -> None:
        """
        将结果存入缓存
        
        Args:
            file_path: 文件路径
            content: 文件内容
            expected_length: 期望长度
            result: 精简结果
        """
        cache_key = self._generate_cache_key(file_path, content, expected_length)
        
        # 如果缓存已满，删除最旧的条目
        if len(self._cache) >= self._max_size:
            oldest_key = min(self._cache.keys(),
                           key=lambda k: self._cache[k]['timestamp'])
            del self._cache[oldest_key]
            logger.debug(f"缓存已满，删除最旧条目: {oldest_key}")
        
        self._cache[cache_key] = {
            'result': result,
            'timestamp': time.time()
        }
        logger.debug(f"结果已缓存: {cache_key}")
    
    def clear(self) -> None:
        """清空所有缓存"""
        self._cache.clear()
        logger.debug("缓存已清空")
    
    def size(self) -> int:
        """获取当前缓存条目数"""
        return len(self._cache)


# 全局缓存实例
_file_summarize_cache = FileSummarizeCache()


class FileSummarizeError(SummarizeError):
    """文件精简相关异常"""
    pass


@safe_file_operation("解析Maven POM文件")
def _parse_pom_xml(content: str) -> Dict[str, Union[str, List[Tuple[str, str]], List[Tuple[str, str, str]]]]:
    """
    解析Maven POM文件内容
    
    Args:
        content: POM文件内容
        
    Returns:
        包含项目信息的字典，格式为：
        {
            'groupId': str,
            'artifactId': str, 
            'version': str,
            'children': [(groupId, artifactId), ...],
            'dependencies': [(groupId, artifactId, version), ...]
        }
        
    Raises:
        FileSummarizeError: 解析POM文件失败
    """
    try:
        # 解析XML
        root = ET.fromstring(content)
        
        # 获取命名空间
        namespace = ''
        if root.tag.startswith('{'):
            namespace = root.tag.split('}')[0] + '}'
        
        result = {
            'groupId': '',
            'artifactId': '',
            'version': '',
            'children': [],
            'dependencies': []
        }
        
        # 提取基本项目信息
        group_id_elem = root.find(f'{namespace}groupId')
        if group_id_elem is not None:
            result['groupId'] = group_id_elem.text or ''
        
        artifact_id_elem = root.find(f'{namespace}artifactId')
        if artifact_id_elem is not None:
            result['artifactId'] = artifact_id_elem.text or ''
        
        version_elem = root.find(f'{namespace}version')
        if version_elem is not None:
            result['version'] = version_elem.text or ''
        
        # 如果没有找到groupId或version，尝试从parent中获取
        parent_elem = root.find(f'{namespace}parent')
        if parent_elem is not None:
            if not result['groupId']:
                parent_group_id = parent_elem.find(f'{namespace}groupId')
                if parent_group_id is not None:
                    result['groupId'] = parent_group_id.text or ''
            
            if not result['version']:
                parent_version = parent_elem.find(f'{namespace}version')
                if parent_version is not None:
                    result['version'] = parent_version.text or ''
        
        # 提取子模块信息
        modules_elem = root.find(f'{namespace}modules')
        if modules_elem is not None:
            for module_elem in modules_elem.findall(f'{namespace}module'):
                if module_elem.text:
                    # 子模块通常继承父项目的groupId
                    result['children'].append((result['groupId'], module_elem.text))
        
        # 提取依赖信息
        dependencies_elem = root.find(f'{namespace}dependencies')
        if dependencies_elem is not None:
            for dep_elem in dependencies_elem.findall(f'{namespace}dependency'):
                dep_group_id = dep_elem.find(f'{namespace}groupId')
                dep_artifact_id = dep_elem.find(f'{namespace}artifactId')
                dep_version = dep_elem.find(f'{namespace}version')
                
                if dep_group_id is not None and dep_artifact_id is not None:
                    group_id = dep_group_id.text or ''
                    artifact_id = dep_artifact_id.text or ''
                    version = dep_version.text if dep_version is not None else ''
                    result['dependencies'].append((group_id, artifact_id, version))
        
        logger.info(f"成功解析POM文件，找到 {len(result['children'])} 个子模块，{len(result['dependencies'])} 个依赖")
        return result
        
    except ET.ParseError as e:
        error_msg = f"POM文件XML格式错误: {str(e)}"
        logger.error(error_msg)
        raise FileSummarizeError(error_msg) from e
    except Exception as e:
        error_msg = f"解析POM文件时发生未知错误: {str(e)}"
        logger.error(error_msg)
        raise FileSummarizeError(error_msg) from e


@safe_file_operation("解析Gradle构建文件")
def _parse_gradle_build(content: str) -> Dict[str, Union[str, List[Tuple[str, str]], List[Tuple[str, str, str]]]]:
    """
    解析Gradle构建文件内容
    
    Args:
        content: Gradle构建文件内容
        
    Returns:
        包含项目信息的字典，格式与POM文件相同
        
    Raises:
        FileSummarizeError: 解析Gradle文件失败
    """
    try:
        result = {
            'groupId': '',
            'artifactId': '',
            'version': '',
            'children': [],
            'dependencies': []
        }
        
        # 提取group信息
        group_match = re.search(r'group\s*[=:]\s*[\'"]([^\'"]+)[\'"]', content)
        if group_match:
            result['groupId'] = group_match.group(1)
        
        # 提取artifactId（通常在settings.gradle中的rootProject.name或build.gradle中的archivesBaseName）
        artifact_patterns = [
            r'rootProject\.name\s*[=:]\s*[\'"]([^\'"]+)[\'"]',
            r'archivesBaseName\s*[=:]\s*[\'"]([^\'"]+)[\'"]',
            r'jar\s*\{[^}]*baseName\s*[=:]\s*[\'"]([^\'"]+)[\'"]'
        ]
        
        for pattern in artifact_patterns:
            artifact_match = re.search(pattern, content, re.DOTALL)
            if artifact_match:
                result['artifactId'] = artifact_match.group(1)
                break
        
        # 提取version信息
        version_match = re.search(r'version\s*[=:]\s*[\'"]([^\'"]+)[\'"]', content)
        if version_match:
            result['version'] = version_match.group(1)
        
        # 提取子项目信息（include语句）
        include_matches = re.findall(r'include\s*[\'"]([^\'"]+)[\'"]', content)
        for subproject in include_matches:
            # 移除子项目名称前的冒号
            clean_subproject = subproject.lstrip(':')
            result['children'].append((result['groupId'], clean_subproject))
        
        # 提取依赖信息
        # 匹配dependencies块中的依赖
        deps_pattern = r'dependencies\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}'
        deps_match = re.search(deps_pattern, content, re.DOTALL)
        
        if deps_match:
            deps_content = deps_match.group(1)
            
            # 匹配各种依赖声明格式
            dep_patterns = [
                # implementation 'group:artifact:version'
                r'(?:implementation|compile|api|testImplementation|testCompile|runtimeOnly|compileOnly)\s+[\'"]([^:\'\"]+):([^:\'\"]+):([^\'\"]+)[\'"]',
                # implementation 'group:artifact' (没有版本)
                r'(?:implementation|compile|api|testImplementation|testCompile|runtimeOnly|compileOnly)\s+[\'"]([^:\'\"]+):([^:\'\"]+)[\'"]',
                # implementation group: 'group', name: 'artifact', version: 'version'
                r'(?:implementation|compile|api|testImplementation|testCompile|runtimeOnly|compileOnly)\s+group:\s*[\'"]([^\'"]+)[\'"],\s*name:\s*[\'"]([^\'"]+)[\'"],\s*version:\s*[\'"]([^\'"]+)[\'"]',
                # implementation group: 'group', name: 'artifact' (没有版本)
                r'(?:implementation|compile|api|testImplementation|testCompile|runtimeOnly|compileOnly)\s+group:\s*[\'"]([^\'"]+)[\'"],\s*name:\s*[\'"]([^\'"]+)[\'"]'
            ]
            
            for pattern in dep_patterns:
                matches = re.findall(pattern, deps_content)
                for match in matches:
                    if len(match) == 3:
                        result['dependencies'].append((match[0], match[1], match[2]))
                    elif len(match) == 2:
                        # 没有版本信息的依赖
                        result['dependencies'].append((match[0], match[1], ''))
        
        logger.info(f"成功解析Gradle文件，找到 {len(result['children'])} 个子项目，{len(result['dependencies'])} 个依赖")
        return result
        
    except Exception as e:
        error_msg = f"解析Gradle文件时发生错误: {str(e)}"
        logger.error(error_msg)
        raise FileSummarizeError(error_msg) from e


def _format_build_file_summary(parsed_data: Dict[str, Union[str, List[Tuple[str, str]], List[Tuple[str, str, str]]]]) -> str:
    """
    格式化构建文件解析结果为摘要文本
    
    Args:
        parsed_data: 解析后的构建文件数据
        
    Returns:
        格式化的摘要文本
    """
    lines = []
    
    # 基本项目信息
    lines.append("项目信息:")
    lines.append(f"  GroupId: {parsed_data['groupId']}")
    lines.append(f"  ArtifactId: {parsed_data['artifactId']}")
    lines.append(f"  Version: {parsed_data['version']}")
    
    # 子模块信息
    children = parsed_data.get('children', [])
    if children:
        lines.append(f"\n子模块 ({len(children)}个):")
        for group_id, artifact_id in children:
            lines.append(f"  - {group_id}:{artifact_id}")
    
    # 依赖信息
    dependencies = parsed_data.get('dependencies', [])
    if dependencies:
        lines.append(f"\n依赖 ({len(dependencies)}个):")
        for group_id, artifact_id, version in dependencies:
            version_str = f":{version}" if version else ""
            lines.append(f"  - {group_id}:{artifact_id}{version_str}")
    
    return "\n".join(lines)


def _quote_compress(input):
    return f"文件内容过长压缩为：{input}"


@safe_file_operation("文件内容精简")
def summerize_file(file_path: str, content: str, expected_length: int) -> str:
    """
    对文件内容做精简，不同的文件类型有不同的精简方式
    
    精简策略：
    - pom.xml: 提取groupId, artifactId, version；提取子模块；提取依赖
    - build.gradle: 和pom.xml类似的处理方式
    - 其他代码文件:
      - 如果content >= 5K，先通过code.skeleton模块的extract_skeleton方法提取代码骨架
        如果提取的代码骨架长度依然大于expected_length，再通过summerize模块的summerize方法来做精简
      - 如果content < 5K，直接通过summerize模块的summerize方法来做精简
    
    缓存机制：
    - 基于文件路径、内容哈希和期望长度生成缓存键
    - 支持全局缓存配置（enable_caching、cache_ttl）
    - 缓存命中时直接返回结果，避免重复计算
    
    Args:
        file_path: 要精简的文件路径
        content: 文件内容
        expected_length: 期望精简的长度
        
    Returns:
        精简后的内容
        
    Raises:
        FileSummarizeError: 文件精简过程中发生错误
        ValueError: 参数验证失败
        
    Examples:
        >>> content = "<?xml version='1.0'?>..."  # POM文件内容
        >>> result = summerize_file("pom.xml", content, 500)
        >>> print(result)
        "项目信息:\n  GroupId: com.example\n..."
    """
    # 参数验证
    if not isinstance(file_path, str) or not file_path.strip():
        raise ValueError("文件路径不能为空")
    
    if not isinstance(content, str):
        raise ValueError("文件内容必须是字符串类型")
    
    # 允许空内容，但需要是字符串类型
    # 允许零或负数的期望长度，但需要是整数类型
    if not isinstance(expected_length, int):
        raise ValueError("期望长度必须是整数类型")
    
    try:
        # 获取应用配置
        summarize_settings = get_application_config().get('summarize_settings', {})
        cache_options = summarize_settings.get('cache_options', {})
        enable_caching = cache_options.get('enable_caching', True)
        cache_ttl = cache_options.get('cache_ttl', 3600)
        
        # 检查缓存
        if enable_caching:
            cached_result = _file_summarize_cache.get(file_path, content, expected_length, cache_ttl)
            if cached_result is not None:
                logger.info(f"缓存命中，直接返回结果: {file_path}, 结果长度: {len(cached_result)}")
                return cached_result
        
        file_path_obj = Path(file_path)
        file_name = file_path_obj.name.lower()
        
        logger.info(f"开始精简文件: {file_path}, 内容长度: {len(content)}, 期望长度: {expected_length}")
        
        # 处理POM文件
        if file_name == "pom.xml":
            logger.debug("识别为Maven POM文件，使用POM解析策略")
            parsed_data = _parse_pom_xml(content)
            summary = _format_build_file_summary(parsed_data)
            
            # 如果摘要仍然过长，进行进一步精简
            if len(summary) > expected_length:
                logger.debug(f"POM摘要长度({len(summary)})超过期望长度，进行进一步精简")
                summary = summerize(summary, "default", expected_length)
            
            # 存储到缓存
            if enable_caching:
                _file_summarize_cache.put(file_path, content, expected_length, summary)
            
            logger.info(f"POM文件精简完成，最终长度: {len(summary)}")
            return _quote_compress(summary)
        
        # 处理Gradle构建文件
        elif file_name == "build.gradle" or file_name == "build.gradle.kts":
            logger.debug("识别为Gradle构建文件，使用Gradle解析策略")
            parsed_data = _parse_gradle_build(content)
            summary = _format_build_file_summary(parsed_data)
            
            # 如果摘要仍然过长，进行进一步精简
            if len(summary) > expected_length:
                logger.debug(f"Gradle摘要长度({len(summary)})超过期望长度，进行进一步精简")
                summary = summerize(summary, "default", expected_length)
            
            # 存储到缓存
            if enable_caching:
                _file_summarize_cache.put(file_path, content, expected_length, summary)
            
            logger.info(f"Gradle文件精简完成，最终长度: {len(summary)}")
            return _quote_compress(summary)
        
        # 处理其他代码文件
        else:
            logger.debug("识别为普通代码文件，使用代码精简策略")
            
            # 判断文件大小是否超过阈值
            if len(content) >= FILE_SIZE_THRESHOLD:
                logger.debug(f"文件内容({len(content)}字节)超过阈值({FILE_SIZE_THRESHOLD}字节)，先提取代码骨架")
                
                # 首先判断文件是否支持骨架提取
                if support_file(file_path):
                    logger.debug(f"文件 {file_path} 支持骨架提取，使用骨架提取策略")
                    try:
                        # 提取代码骨架
                        skeleton = extract_skeleton(file_path)
                        logger.debug(f"代码骨架提取完成，骨架长度: {len(skeleton)}")
                        
                        # 如果骨架长度仍然超过 10K，使用CodeSkeletonSummary模板进行进一步精简
                        if len(skeleton) > 10000:
                            logger.debug(f"代码骨架长度({len(skeleton)})仍超过期望长度，使用CodeSkeletonSummary模板进行精简")
                            summary = summerize(skeleton, "CodeSkeletonSummary", expected_length)
                        else:
                            summary = skeleton
                            
                    except Exception as e:
                        # 如果代码骨架提取失败，回退到直接精简策略
                        logger.warning(f"代码骨架提取失败: {str(e)}，回退到直接精简策略")
                        summary = summerize(content, "default", expected_length)
                else:
                    logger.debug(f"文件 {file_path} 不支持骨架提取，使用默认精简策略")
                    summary = summerize(content, "default", expected_length)
            else:
                logger.debug(f"文件内容({len(content)}字节)未超过阈值，直接进行精简")
                summary = summerize(content, "default", expected_length)
            
            # 存储到缓存
            if enable_caching:
                _file_summarize_cache.put(file_path, content, expected_length, summary)
            
            logger.info(f"代码文件精简完成，最终长度: {len(summary)}")
            return _quote_compress(summary)
            
    except (ValueError, FileSummarizeError):
        # 重新抛出已知的异常类型
        raise
    except Exception as e:
        error_msg = f"文件精简过程中发生未知错误: {str(e)}"
        logger.error(error_msg)
        raise FileSummarizeError(error_msg) from e


def clear_file_summarize_cache() -> None:
    """
    清空文件精简缓存
    
    提供给外部调用的缓存清理接口，用于测试或手动清理缓存。
    """
    _file_summarize_cache.clear()
    logger.info("文件精简缓存已清空")


def get_file_summarize_cache_size() -> int:
    """
    获取当前缓存大小
    
    Returns:
        当前缓存中的条目数量
    """
    return _file_summarize_cache.size()