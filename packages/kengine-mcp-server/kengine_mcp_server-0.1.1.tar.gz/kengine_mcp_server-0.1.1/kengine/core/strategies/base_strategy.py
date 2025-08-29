"""
文档生成策略抽象基类 - 简化版本

定义所有策略必须实现的核心接口，提供基础的变量组织支持
"""

from abc import ABC, abstractmethod
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum

from kengine.core.utils.catalogue_data_utils import set_catalogue_saved_path

from ..types import GenerationContext, StepGenerationResult
from .strategy_utils import StrategyUtils
from ...io import create_io

class GenerationMode(Enum):
    """文档生成模式枚举"""
    SERIAL = "serial"      # 串行模式
    PARALLEL = "parallel"  # 并行模式


class DocumentGenerationStrategy(ABC):
    """文档生成策略抽象基类 - 简化的变量管理"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化策略
        
        Args:
            config: 策略特定的配置选项
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """
        返回策略名称，用于日志和调试
        
        Returns:
            策略名称
        """
        pass
    
    @abstractmethod
    def generate_catalogue(self, context: GenerationContext) -> StepGenerationResult:
        """
        生成文档目录结构
        
        Args:
            context: 生成上下文信息
            
        Returns:
            包含目录结构的生成结果
        """
        pass
    
    @abstractmethod
    def generate_documents(self,
                          catalogue_data: Dict[str, Any],
                          context: GenerationContext,
                          mode: GenerationMode = GenerationMode.SERIAL,
                          max_workers: Optional[int] = None) -> StepGenerationResult:
        """
        生成文档内容
        
        Args:
            catalogue_data: 文档目录结构数据
            context: 生成上下文信息（包含输出路径）
            mode: 生成模式（串行或并行）
            max_workers: 并行模式下的最大工作线程数，None表示使用默认值
            
        Returns:
            包含生成统计信息的生成结果
        """
        pass
    
    def _on_generate_documents(self,
                              catalogue_data: Dict[str, Any],
                              context: GenerationContext) -> None:
        """
        文档生成前的预处理逻辑，子类应在generate_documents方法开始时调用此方法
        
        Args:
            catalogue_data: 文档目录结构数据
            context: 生成上下文信息
        """
        # 在开始文档生成前，设置总文档数用于进度跟踪
        if context.tracker and "items" in catalogue_data:
            tasks = self._collect_document_tasks(catalogue_data["items"])
            total_documents = len(tasks)
            context.tracker.set_document_count(total_documents)
            self.logger.info(f"设置文档总数: {total_documents}")
    
    @abstractmethod
    def _generate_document(self,
                          document_path: str,
                          catalogue_data: Dict[str, Any],
                          context: GenerationContext) -> Optional[str]:
        """
        生成单个文档的内容
        
        Args:
            document_path: 文档在目录结构中的路径（用于定位文档项）
            catalogue_data: 文档目录结构数据
            context: 生成上下文信息
            
        Returns:
            生成的文档内容，如果生成失败则返回None
        """
        pass
    
    @abstractmethod
    def generate_overview(self, context: GenerationContext) -> StepGenerationResult:
        """
        生成项目概览文档
        
        Args:
            context: 生成上下文信息
            
        Returns:
            包含概览内容的生成结果
        """
        pass
    
    def _get_shared_project_variables(self, context: GenerationContext) -> Dict[str, Any]:
        """获取共享的项目变量（避免重复调用 get_project_info）"""
        # 获取项目信息（使用缓存避免重复调用）
        project_info = context.get_project_info()
        
        return {
            "project_path": context.project_path,
            "project_type": context.project_type,
            "project_info": project_info,
            "project_directory_structure": project_info.directory_structure,
            "repository_name": project_info.project_name,
            "readme_content": project_info.readme_content,
            "git_repository": context.git_repository_url or "",
            "git_repository_root_url": StrategyUtils.process_git_repository_url(context),
            "git_branch": context.branch or "master",
        }
    
    def _build_catalogue_variables(self, context: GenerationContext,
                                 previous_catalog: str = "",
                                 previous_catalog_issues: str = "") -> Dict[str, Any]:
        """
        构建目录生成的统一变量
        
        Args:
            context: 生成上下文
            previous_catalog: 之前的目录（用于修复）
            previous_catalog_issues: 之前目录的问题（用于修复）
            
        Returns:
            目录生成变量字典
        """
        # 使用共享项目变量，避免重复调用 get_project_info()
        
        # 使用共享变量，避免重复调用
        variables = self._get_shared_project_variables(context)
        variables.update({
            "previous_catalog": previous_catalog,
            "previous_catalog_issues": previous_catalog_issues,
        })
        return variables
    
    def _build_document_variables(self, context: GenerationContext,
                                catalogue_data: Dict[str, Any],
                                document_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建文档生成的统一变量
        
        Args:
            context: 生成上下文
            catalogue_data: 目录结构数据
            document_item: 当前文档项
            
        Returns:
            文档生成变量字典
        """
        # 使用共享项目变量，避免重复调用 get_project_info()
        
        # 使用共享变量，避免重复调用
        variables = self._get_shared_project_variables(context)
        
        def related_files(related_files: List[str]) -> str:
            if not related_files: return ''
            return '\n'.join([' - "{0}"'.format(f) for f in related_files])
            
        related_files_text = related_files(document_item.get("relatedFilenames", []))
        
        # 从 extra_context 中获取用户批注
        user_annotation = context.extra_context.get('user_annotation', '') or ""
        
        update_dict = {
            "document_title": document_item.get("title", ""),
            "document_prompt": document_item.get("prompt", ""),
            "document_related_files": related_files_text,
            "catalogue_structure": json.dumps(catalogue_data, ensure_ascii=False, indent=2),
            "user_annotation": user_annotation,
        }
        
        variables.update(update_dict)
        
        return variables
    
    def _build_overview_variables(self, context: GenerationContext) -> Dict[str, Any]:
        """
        构建概览生成的统一变量
        
        Args:
            context: 生成上下文
            
        Returns:
            概览生成变量字典
        """
        # 使用共享项目变量，避免重复调用 get_project_info()
        
        # 使用共享变量，避免重复调用
        variables = self._get_shared_project_variables(context)
        variables.update({
            "catalogue": getattr(context, 'catalogue', ''),
        })
        return variables
    
    
    def _validate_project_path(self, project_path: str) -> Optional[str]:
        """
        验证项目路径，包含日志记录
        
        Args:
            project_path: 项目路径
            
        Returns:
            错误信息，如果路径有效则返回None
        """
        error = StrategyUtils.validate_project_path(project_path)
        if error:
            self.logger.error(error)
        return error
    
    def _save_content_to_file(self, context: GenerationContext, content: str, path_name: str) -> str:
        """
        保存内容到文件
        
        Args:
            context: 生成上下文信息
            content: 要保存的内容
            path_name: 文件路径名
            
        Returns:
            保存的文件路径
            
        Raises:
            RuntimeError: 当文件保存失败时
            ValueError: 当必需参数缺失时
        """
        try:
            # 参数验证：确保必需的参数存在且有效
            if not path_name or not path_name.strip():
                raise ValueError("文件路径名不能为空")
            
            if content is None:
                raise ValueError("文件内容不能为 None")
            
            # 验证 GenerationContext 的必需属性
            if not hasattr(context, 'repo_group') or not context.repo_group:
                raise ValueError("GenerationContext 缺少必需的 repo_group 属性或其值为空")
            
            if not hasattr(context, 'repo_name') or not context.repo_name:
                raise ValueError("GenerationContext 缺少必需的 repo_name 属性或其值为空")
            
            # 获取版本信息
            version = getattr(context, 'prompt_version', None)
            
            # 记录关键信息用于调试
            self.logger.info(f"保存文件: {path_name} (repo: {context.repo_group}/{context.repo_name}, 版本: {version})")
            
            # 创建IO实例并保存文件
            file_path = create_io(context.repo_group, context.repo_name, version).write(path_name, content)
            
            self.logger.info(f"文件保存成功: {file_path}")
            return file_path
            
        except ValueError as e:
            # 参数验证错误，记录详细信息
            self.logger.error(f"参数验证失败: {e}")
            self.logger.error(f"上下文信息 - repo_group: {getattr(context, 'repo_group', 'MISSING')}, "
                            f"repo_name: {getattr(context, 'repo_name', 'MISSING')}, "
                            f"path_name: '{path_name}', content类型: {type(content)}")
            raise RuntimeError(f"文件保存参数验证失败: {e}") from e
            
        except Exception as e:
            # 其他异常，记录详细错误信息
            self.logger.error(f"保存文件时发生异常: {e}")
            self.logger.error(f"异常类型: {type(e)}")
            self.logger.error(f"文件路径: {path_name}")
            import traceback
            self.logger.error(f"完整堆栈:\n{traceback.format_exc()}")
            raise RuntimeError(f"保存文件失败: {path_name}") from e
        
    def _create_child_directory(self, parent_path: Path, child_name: str) -> Path:
        """
        创建子目录
        
        Args:
            parent_path: 父目录路径
            child_name: 子目录名称
            
        Returns:
            子目录路径
        """
        from ...utils.path_utils import sanitize_filename
        
        safe_dirname = sanitize_filename(child_name)
        child_path = parent_path / safe_dirname
        child_path.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"创建子目录: {child_path}")
        return child_path
    
    def _init_llm_with_defaults(self, llm_options: Optional[Dict[str, Any]] = None):
        """
        初始化LLM，提供默认配置
        
        Args:
            llm_options: LLM配置选项
            
        Returns:
            初始化的LLM实例
        """
        from ...tasks.llm import init_llm
        
        if llm_options is None:
            llm_options = {"model": "gpt-4-turbo-preview", "temperature": 0}
        
        return init_llm(llm_options)
    
    def _load_prompt_with_strategy_mode(self, prompt_name: str, project_type: str, 
                                      strategy_mode: str,
                                      prompt_version: Optional[str] = None):
        """
        加载指定策略模式的提示词
        
        Args:
            prompt_name: 提示词名称
            project_type: 项目类型
            strategy_mode: 策略模式 ("prompt" 或 "agent")
            prompt_version: 提示词版本
            
        Returns:
            加载的提示词模板
        """
        from ...utils.prompt_loader import load_prompt
        
        return load_prompt(prompt_name, project_type, prompt_version, strategy_mode=strategy_mode)
    
    def estimate_cost(self, context: GenerationContext) -> Dict[str, Any]:
        """
        估算生成成本（可选实现）
        
        Args:
            context: 生成上下文
            
        Returns:
            成本估算信息
        """
        return {
            "estimated": False, 
            "reason": f"{self.get_strategy_name()} does not support cost estimation"
        }
    
    def cleanup(self, context: GenerationContext) -> None:
        """
        清理策略相关资源（可选实现）
        
        Args:
            context: 生成上下文
        """
        pass
    
    def _load_file_cache(self, context: GenerationContext, file_path: str) -> Optional[str]:
        """
        从缓存文件中加载内容
        
        Args:
            file_path: 缓存文件路径
            
        Returns:
            Optional[str]: 如果缓存文件存在则返回内容，否则返回None
        """
        try:
            _io = create_io(context.repo_group, context.repo_name, context.prompt_version)
            if _io.exists(file_path):
                cached_content = _io.read(file_path)
                self.logger.info(f"从缓存文件读取项目摘要: {file_path}")
                return cached_content
            else:
                self.logger.debug(f"缓存文件不存在: {file_path}")
                return None
        except Exception as cache_error:
            self.logger.warning(f"读取缓存摘要文件失败，继续正常流程: {str(cache_error)} {str(file_path)}")
            return None
    
    def _set_file_cache(self, context: GenerationContext,  file_path: Path, content: str) -> None:
        """
        设置文件缓存
        
        Args:
            file_path: 缓存文件路径
            content: 要缓存的内容
        """
        # 保存文件
        self._save_content_to_file(context, content, file_path)

    
    def _collect_document_tasks(self, 
                               items: List[Dict[str, Any]], 
                               parent_path: str = "") -> List[Dict[str, Any]]:
        """
        收集所有需要生成的文档任务
        
        Args:
            items: 文档项列表
            parent_path: 父路径
            
        Returns:
            文档任务列表，每个任务包含文档路径和文档项信息
        """
        tasks = []
        
        for item in items:
            # 构建当前文档的路径
            current_path = f"{parent_path}/{item['name']}" if parent_path else item['name']
            
            # 添加当前文档任务
            tasks.append({
                'document_path': current_path,
                'document_item': item,
                'parent_path': parent_path
            })
            
            # 递归处理子项
            if "children" in item and isinstance(item["children"], list) and len(item["children"]) > 0:
                child_tasks = self._collect_document_tasks(item["children"], current_path)
                tasks.extend(child_tasks)
        
        return tasks
    
    def _execute_parallel_generation(self,
                                   tasks: List[Dict[str, Any]],
                                   catalogue_data: Dict[str, Any],
                                   context: GenerationContext,
                                   max_workers: Optional[int] = None) -> Dict[str, Any]:
        """
        并行执行文档生成任务
        
        Args:
            tasks: 文档生成任务列表
            catalogue_data: 文档目录结构数据
            context: 生成上下文
            max_workers: 最大工作线程数
            
        Returns:
            生成统计信息
        """
        stats = StrategyUtils.create_generation_stats()
        stats["total_items"] = len(tasks)
        
        # 确定工作线程数
        if max_workers is None:
            max_workers = min(len(tasks), 4)  # 默认最多4个线程
        
        self.logger.info(f"开始并行生成 {len(tasks)} 个文档，使用 {max_workers} 个工作线程")
        max_workers = min(max_workers, os.cpu_count() * 4) if max_workers else os.cpu_count() * 4
        with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix='document-gen-worker-') as executor:
            # 提交所有任务
            future_to_task = {}
            for task in tasks:
                future = executor.submit(
                    self._generate_single_document_task,
                    task,
                    catalogue_data,
                    context
                )
                future_to_task[future] = task
            
            # 收集结果
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    if result:
                        stats["successful_generations"] += 1
                        stats["generated_files"].append(result)
                        self.logger.info(f"文档生成成功: {task['document_path']}")
                        
                        # 更新进度回调
                        if context.tracker:
                            context.tracker.update_document_progress(stats["successful_generations"])
                    else:
                        stats["failed_generations"] += 1
                        self.logger.error(f"文档生成失败: {task['document_path']}")
                except Exception as e:
                    stats["failed_generations"] += 1
                    self.logger.error(f"文档生成异常: {task['document_path']}, 错误: {e}", exc_info=True)
        
        return stats
    
    def _generate_single_document_task(self,
                                     task: Dict[str, Any],
                                     catalogue_data: Dict[str, Any],
                                     context: GenerationContext) -> Optional[str]:
        """
        生成单个文档任务
        
        Args:
            task: 文档任务信息
            catalogue_data: 文档目录结构数据
            context: 生成上下文
            
        Returns:
            生成的文件路径，如果生成失败则返回None
            
        Raises:
            Exception: 当任务执行过程中发生错误时抛出异常
        """
        # 调用子类实现的_generate_document方法
        content = self._generate_document(
            task['document_path'],
            catalogue_data,
            context
        )
        
        if content:
            # 构建输出路径
            parent_path = '' if 'parent_path' not in task.keys() else task['parent_path']
            full_path = parent_path + '/' + task['document_item']['name'] + '.md'
            saved_path = self._save_content_to_file(context, content, full_path)
            
            # 生成文档后更新 catalogue_data, 根据当前任务的path: task['document_path'] 找到对应目录项， 添加 saved_path 属性
            set_catalogue_saved_path(task['document_path'], catalogue_data, saved_path)
            
            return saved_path
        
        return None
    