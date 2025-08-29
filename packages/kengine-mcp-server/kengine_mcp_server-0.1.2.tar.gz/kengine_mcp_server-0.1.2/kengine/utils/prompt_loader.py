"""
Prompt 加载器 - 支持动态提示词加载和分类映射，简化版本
"""

import os
import logging
import time
import threading
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    Observer = None
    FileSystemEventHandler = None
    WATCHDOG_AVAILABLE = False
    logging.getLogger(__name__).warning("watchdog 库未安装，文件监控功能将被禁用")

logger = logging.getLogger(__name__)

# 简单的全局缓存存储
_prompt_cache: Dict[str, Tuple[str, float]] = {}  # {file_path: (content, mtime)}
_cache_lock = threading.RLock()
_file_observer: Optional[Observer] = None
_observer_started = False


class PromptFileEventHandler(FileSystemEventHandler):
    """提示词文件变化监控处理器 - 简化版"""
    
    def on_modified(self, event):
        """文件修改事件处理"""
        if not event.is_directory and event.src_path.endswith('.md'):
            self._clear_file_cache(event.src_path)
    
    def on_deleted(self, event):
        """文件删除事件处理"""
        if not event.is_directory and event.src_path.endswith('.md'):
            self._clear_file_cache(event.src_path)
    
    def on_created(self, event):
        """文件创建事件处理"""
        if not event.is_directory and event.src_path.endswith('.md'):
            self._clear_file_cache(event.src_path)
    
    def _clear_file_cache(self, file_path: str):
        """清除指定文件的缓存"""
        try:
            with _cache_lock:
                if file_path in _prompt_cache:
                    del _prompt_cache[file_path]
                    logger.debug(f"文件变化，清除缓存: {file_path}")
        except Exception as e:
            logger.error(f"清除文件缓存时出错: {file_path}, 错误: {e}")


def _start_file_watcher():
    """启动文件监控 - 简化版"""
    global _file_observer, _observer_started
    
    if not WATCHDOG_AVAILABLE or _observer_started:
        return
    
    try:
        with _cache_lock:
            if _file_observer is None:
                _file_observer = Observer()
                prompt_base_path = _get_prompt_base_path()
                _file_observer.schedule(PromptFileEventHandler(), prompt_base_path, recursive=True)
                _file_observer.start()
                _observer_started = True
                logger.debug(f"启动提示词文件监控: {prompt_base_path}")
    except Exception as e:
        logger.error(f"启动文件监控失败: {e}")


def _get_prompt_base_path() -> str:
    """获取提示词模板的基础路径"""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'prompts-template')


def _resolve_prompt_paths(prompt_name: str, prompt_category: str = None, prompt_version: str = None, 
                         strategy_mode: str = "prompt", fallback_to_default: bool = True) -> List[Tuple[str, str]]:
    """
    解析提示词文件的所有可能路径
    
    Args:
        prompt_name: 提示词文件名（不含扩展名）
        prompt_category: 提示词分类目录
        prompt_version: 提示词版本（可选）
        strategy_mode: 策略模式，'agent' 或 'prompt'，默认 'prompt'
        fallback_to_default: 如果指定提示词不存在，是否回退到默认提示词
        
    Returns:
        List[Tuple[str, str]]: 路径和描述的元组列表，按优先级排序
    """
    prompt_base_path = _get_prompt_base_path()
    paths = []
    
    # 根据策略模式确定基础路径
    if strategy_mode == "agent":
        mode_path = os.path.join(prompt_base_path, "agent")
    elif strategy_mode == "prompt":
        mode_path = os.path.join(prompt_base_path, "prompt")
    else:
        # 向后兼容：如果模式不识别，使用旧的根目录逻辑
        mode_path = prompt_base_path
        logger.warning(f"未识别的策略模式 '{strategy_mode}'，使用默认路径")
    
    # 如果指定了分类目录，按优先级添加路径
    if prompt_category:
        # 1. 优先尝试版本化的提示词
        if prompt_version:
            versioned_path = os.path.join(mode_path, prompt_category, prompt_version, prompt_name + '.md')
            paths.append((versioned_path, f"版本化提示词: {strategy_mode}/{prompt_category}/{prompt_version}/{prompt_name}"))
            
            # 如果不允许回退，只返回版本化路径
            if not fallback_to_default:
                return paths
        
        # 2. 尝试从分类目录加载（无版本）
        category_path = os.path.join(mode_path, prompt_category, prompt_name + '.md')
        paths.append((category_path, f"分类提示词: {strategy_mode}/{prompt_category}/{prompt_name}"))
        
        # 如果不允许回退，只返回分类路径
        if not fallback_to_default:
            return paths
    
    # 3. 回退策略：添加当前模式的根目录
    mode_root_path = os.path.join(mode_path, prompt_name + '.md')
    paths.append((mode_root_path, f"{strategy_mode}模式根目录"))
    
    # 4. 如果是agent模式没找到，尝试prompt模式（向下兼容）
    if strategy_mode == "agent":
        prompt_mode_path = os.path.join(prompt_base_path, "prompt")
        if prompt_category:
            prompt_category_path = os.path.join(prompt_mode_path, prompt_category, prompt_name + '.md')
            paths.append((prompt_category_path, "prompt模式分类目录"))
        prompt_root_path = os.path.join(prompt_mode_path, prompt_name + '.md')
        paths.append((prompt_root_path, "prompt模式根目录"))
    
    # 5. 最后尝试旧的根目录（完全向后兼容）
    legacy_path = os.path.join(prompt_base_path, prompt_name + '.md')
    paths.append((legacy_path, "旧根目录"))
    
    return paths


def _read_prompt_file(file_path: str, description: str) -> str:
    """
    从指定路径读取提示词文件内容，支持简单缓存
    
    Args:
        file_path: 文件路径
        description: 路径描述，用于日志记录
        
    Returns:
        文件内容
        
    Raises:
        FileNotFoundError: 文件不存在
        IOError: 文件读取错误
    """
    # 确保文件监控已启动
    _start_file_watcher()
    
    # 检查缓存
    with _cache_lock:
        if file_path in _prompt_cache:
            cached_content, cached_mtime = _prompt_cache[file_path]
            
            # 检查文件是否被修改
            if os.path.exists(file_path):
                current_mtime = os.path.getmtime(file_path)
                if current_mtime <= cached_mtime:
                    logger.debug(f"从缓存加载提示词: {description}")
                    return cached_content
                else:
                    # 文件已修改，删除缓存
                    del _prompt_cache[file_path]
                    logger.debug(f"文件已修改，删除缓存: {file_path}")
            else:
                # 文件不存在，删除缓存
                del _prompt_cache[file_path]
                logger.debug(f"文件不存在，删除缓存: {file_path}")
    
    # 缓存未命中或已过期，从文件读取
    try:
        with open(file_path, 'rt', encoding='utf-8') as reader:
            content = reader.read()
            
            # 将内容放入缓存
            with _cache_lock:
                current_mtime = os.path.getmtime(file_path)
                _prompt_cache[file_path] = (content, current_mtime)
            
            logger.info(f"成功从{description}加载提示词并缓存")
            return content
    except FileNotFoundError:
        raise FileNotFoundError(f"提示词文件不存在: {file_path}")
    except IOError as e:
        raise IOError(f"读取提示词文件失败: {file_path}, 错误: {e}")


def load_prompt(prompt_name: str, prompt_category: str = None, prompt_version: str = None, 
               strategy_mode: str = "prompt", fallback_to_default: bool = True) -> str:
    """
    加载提示词模板，支持agent和prompt模式区分
    
    Args:
        prompt_name: 提示词文件名（不含扩展名）
        prompt_category: 提示词分类目录
        prompt_version: 提示词版本（可选）
        strategy_mode: 策略模式，'agent' 或 'prompt'，默认 'prompt'
        fallback_to_default: 如果指定提示词不存在，是否回退到默认提示词
        
    Returns:
        提示词内容
        
    Raises:
        FileNotFoundError: 提示词文件不存在且未启用回退
        IOError: 文件读取错误
    """
    # 1. 解析所有可能的文件路径
    possible_paths = _resolve_prompt_paths(
        prompt_name=prompt_name,
        prompt_category=prompt_category,
        prompt_version=prompt_version,
        strategy_mode=strategy_mode,
        fallback_to_default=fallback_to_default
    )
    
    # 2. 按优先级尝试读取文件
    last_error = None
    for file_path, description in possible_paths:
        if os.path.exists(file_path):
            try:
                return _read_prompt_file(file_path, description)
            except IOError as e:
                last_error = e
                logger.warning(f"文件存在但读取失败: {file_path}, 错误: {e}")
                continue
        else:
            logger.debug(f"文件不存在: {file_path}")
    
    # 3. 所有路径都不存在或读取失败
    if last_error:
        raise last_error
    else:
        attempted_paths = [path for path, _ in possible_paths]
        raise FileNotFoundError(f"提示词文件不存在: {prompt_name}，已尝试路径: {attempted_paths}")


def load_summerize_prompt(prompt_name: str) -> str:
    """
    加载总结提示词
    
    Args:
        prompt_name: 提示词文件名（不含扩展名）
        
    Returns:
        提示词内容
        
    Raises:
        FileNotFoundError: 提示词文件不存在
        IOError: 文件读取错误
    """
    return load_custom_prompt('summerize', prompt_name)


def load_custom_prompt(prompt_dirname: str, prompt_name: str) -> str:
    """
    加载自定义目录提示词
    
    Args:
        prompt_dirname: 提示词目录名
        prompt_name: 提示词文件名（不含扩展名）
        
    Returns:
        提示词内容
        
    Raises:
        FileNotFoundError: 提示词文件不存在
        IOError: 文件读取错误
    """
    prompt_path = os.path.join(_get_prompt_base_path(), prompt_dirname, prompt_name + '.md')
    return _read_prompt_file(prompt_path, f"{prompt_dirname}目录{prompt_name}提示词")


def load_classification_prompt(category_name: str = None) -> str:
    """
    加载统一的分类提示词（从shared目录）
    
    Args:
        category_name: 分类名称（保留参数以保持兼容性，但不影响实际行为）
        
    Returns:
        分类提示词内容
        
    Raises:
        RuntimeError: 分类提示词文件不存在
    """
    prompt_base_path = _get_prompt_base_path()
    
    # 优先从shared目录加载
    shared_path = os.path.join(prompt_base_path, "shared", "RepositoryClassification.md")
    if os.path.exists(shared_path):
        return _read_prompt_file(shared_path, "shared目录分类提示词")
    raise RuntimeError(f'can not find classification prompt {shared_path}')


def get_available_prompts(category: str = None, strategy_mode: str = None) -> Dict[str, Any]:
    """
    获取可用的提示词列表
    
    Args:
        category: 分类目录，如果为None则扫描所有目录
        strategy_mode: 策略模式，'agent'、'prompt'或None（扫描所有模式）
        
    Returns:
        可用提示词信息字典
    """
    prompts = {}
    prompt_base_path = Path(_get_prompt_base_path())
    
    # 确定要扫描的模式目录
    scan_modes = []
    if strategy_mode == "agent":
        scan_modes = [("agent", prompt_base_path / "agent")]
    elif strategy_mode == "prompt":
        scan_modes = [("prompt", prompt_base_path / "prompt")]
    elif strategy_mode is None:
        scan_modes = [
            ("agent", prompt_base_path / "agent"),
            ("prompt", prompt_base_path / "prompt"),
            ("shared", prompt_base_path / "shared"),
            ("legacy", prompt_base_path)  # 旧的根目录文件
        ]
    else:
        # 未知模式，回退到旧逻辑
        scan_modes = [("legacy", prompt_base_path)]
    
    for mode_name, mode_path in scan_modes:
        if not mode_path.exists():
            continue
            
        if category:
            # 扫描指定分类目录
            category_path = mode_path / category
            if category_path.exists():
                for prompt_file in category_path.glob("*.md"):
                    prompt_name = prompt_file.stem
                    key = f"{mode_name}/{category}/{prompt_name}"
                    prompts[key] = {
                        "name": prompt_name,
                        "category": category,
                        "mode": mode_name,
                        "path": str(prompt_file),
                        "size": prompt_file.stat().st_size
                    }
        else:
            # 扫描模式目录下的所有文件
            for prompt_file in mode_path.rglob("*.md"):
                relative_path = prompt_file.relative_to(mode_path)
                category_name = relative_path.parent.name if relative_path.parent != Path('.') else "default"
                prompt_name = prompt_file.stem
                
                key = f"{mode_name}/{category_name}/{prompt_name}" if category_name != "default" else f"{mode_name}/{prompt_name}"
                prompts[key] = {
                    "name": prompt_name,
                    "category": category_name,
                    "mode": mode_name,
                    "path": str(prompt_file),
                    "size": prompt_file.stat().st_size
                }
    
    return prompts


def extract_variables_from_prompt(prompt_content: str) -> set:
    """
    从模板内容中提取变量名
    
    从模板内容中提取所有 {变量名} 格式的变量，支持：
    - 基本变量：{repository_name}
    - 带连字符的变量：{key-endpoint-definitions}
    - 带下划线的变量：{readme_content}
    - 点号表达式：{a.b} 提取变量名 a
    
    Args:
        prompt_content: 模板内容字符串
        
    Returns:
        set: 包含所有变量名的集合（不包含大括号）
        
    Examples:
        >>> extract_variables_from_prompt("Hello {name}, your {age} is valid")
        {'name', 'age'}
        
        >>> extract_variables_from_prompt("No variables here")
        set()
    """
    import re
    
    if not isinstance(prompt_content, str):
        logger.warning(f"输入内容不是字符串类型: {type(prompt_content)}")
        return set()
    
    if not prompt_content.strip():
        return set()
    
    # 正则表达式匹配 {变量名} 格式
    # 变量名可以包含字母、数字、下划线、连字符
    # 支持大括号内的前后空格：{ variable_name }
    # 支持点号表达式：{a.b} 提取变量名 a
    pattern = r'\{\s*([a-zA-Z_][a-zA-Z0-9_-]*)(?:\.[a-zA-Z0-9_.-]*)?\s*\}'
    
    try:
        matches = re.findall(pattern, prompt_content)
        # 去重并返回集合
        variables = set(matches)
        
        logger.debug(f"从模板中提取到 {len(variables)} 个变量: {variables}")
        return variables
        
    except re.error as e:
        error_msg = f"正则表达式处理错误，模式: '{pattern}', 错误详情: {e}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e
    except Exception as e:
        error_msg = f"提取变量时发生未知错误，输入内容长度: {len(prompt_content)}, 错误详情: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


# 向后兼容的函数（保留但标记为废弃）
def validate_prompt_exists(prompt_name: str, prompt_category: str = None, strategy_mode: str = "prompt") -> bool:
    """
    验证提示词是否存在（废弃函数，保留向后兼容性）
    
    Args:
        prompt_name: 提示词文件名
        prompt_category: 提示词分类目录
        strategy_mode: 策略模式
        
    Returns:
        bool: 提示词是否存在
    """
    logger.warning("validate_prompt_exists 函数已废弃，建议直接使用 load_prompt 并捕获异常")
    try:
        load_prompt(prompt_name, prompt_category, strategy_mode=strategy_mode)
        return True
    except FileNotFoundError:
        return False