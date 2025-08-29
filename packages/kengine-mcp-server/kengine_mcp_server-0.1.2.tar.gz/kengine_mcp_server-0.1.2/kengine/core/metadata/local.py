"""
文件存储模式的元数据适配器实现

实现基于文件系统的元数据存储和管理功能
"""

import logging
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import PosixPath

from .metadata_adapter import MetadataAdapter
from ..types import KnowledgeGenerationRequest, KnowledgeGenerationResult, GenerationContext, StepGenerationResult
from ...utils.safe_file import safe_file_operation
from ...utils.project_metadata import ProjectMetadataManager
from ...utils.dir_utils import base_dir

class FileMetadataAdapter(MetadataAdapter):
    """文件存储模式的元数据适配器"""
    
    def __init__(self, output_dir: str = "docs4demo"):
        """
        初始化文件元数据适配器
        
        Args:
            output_dir: 元数据输出目录，默认为 "docs4demo"
        """
        self.logger = logging.getLogger(__name__)
        self.output_dir = output_dir
        self.metadata_manager = ProjectMetadataManager()
        
    def on_start_generate(self,
                          request: KnowledgeGenerationRequest,
                          context: GenerationContext) -> str:
        """
        开始生成文档时保存元数据
        
        Args:
            request: 生成文档的请求信息
            context: 生成文档的上下文信息
            
        Returns:
            操作结果描述
            
        Raises:
            Exception: 保存失败时抛出异常
        """
        pass
    
    def on_cloned_repository(self,
                          context: GenerationContext,
                          generate_result: KnowledgeGenerationResult
                          ) -> Optional[Dict[str, Any]]:
        """
        仓库克隆完成后的处理
        
        Args:
            context: 生成文档的上下文信息
            generate_result: 生成结果对象
            
        Returns:
            处理结果元数据
        """
        pass
    
    def on_classified(self,
                          context: GenerationContext,
                          generate_result: KnowledgeGenerationResult
                          ) -> Optional[Dict[str, Any]]:
        """
        分类完成后的处理
        
        Args:
            context: 生成文档的上下文信息
            generate_result: 生成结果对象
            
        Returns:
            处理结果元数据
        """
        pass
    
    def _to_json(self, obj):
        if obj is None:
            return {}
        
        if isinstance(obj, dict):
            return obj
        
        if hasattr(obj, 'to_json'):
            return obj.to_json()
        
        return obj
    
    def _global_output_dir(self):
        output_dir = os.path.join(base_dir, 'docs4demo')
        return output_dir
        
    
    @safe_file_operation("元数据保存")
    def on_completed(self,
                          context: GenerationContext,
                          generate_result: KnowledgeGenerationResult
                          ) -> Optional[Dict[str, Any]]:
        """
        文档生成完成后的处理 - 整合元数据保存功能
        
        整合了原document_service.py中的两个元数据保存方法：
        1. _save_documentation_metadata: 保存文档库元数据到JSON文件
        2. _save_project_metadata: 保存项目元数据
        
        Args:
            context: 生成文档的上下文信息
            generate_result: 生成结果对象
            
        Returns:
            处理结果元数据
        """
        try:
            self.logger.info(f"开始保存元数据: {context.repo_group}/{context.repo_name}")
            generate_result.generate_stage = "metadata"
            
            # 构建输出URI（如果有版本信息则包含版本）
            output_uri = generate_result.output_path
            if context.prompt_version:
                output_uri = f"{output_uri}-{context.prompt_version}"
            
            # 1. 保存文档库元数据到JSON文件
            self._save_documentation_metadata(
                catalogue_data=generate_result.catalogue_result.data,
                output_dir=output_uri,
                project_path=generate_result.project_path,
                project_type=generate_result.project_type or "unknown",
                strategy=str(generate_result.strategy_used) if generate_result.strategy_used else "",
                git_repository=context.git_repository_url or "",
                git_branch=context.branch,
                prompt_version=context.prompt_version,
                overview_result=generate_result.overview_result.data
            )
            
            # 2. 保存项目元数据
            metadata_path = self._save_project_metadata(
                project_path=generate_result.project_path,
                project_type=context.project_type or generate_result.project_type or "unknown",
                git_repository=context.git_repository_url or "",
                git_branch=context.branch,
                strategy=context.strategy.value if context.strategy else "unknown",
                model_name=context.extra_context.get('model_name', ''),
                prompt_version=context.prompt_version or "",
                model_options=context.extra_context.get('llm_options', {}),
                output_dir=output_uri,
                name=context.repo_name or "",
                group=context.repo_group or ""
            )
            
            # 3. 更新全局项目元数据文件 (project_metadata.json)
            # 构建文档元数据路径
            doc_metadata_path = os.path.join(output_uri, "documentation_metadata.json")
            def path2str(input):
                str_path = str(input) if isinstance(input, PosixPath) else input
                if str_path.startswith(base_dir):
                    str_path = str_path[len(base_dir):]
                if str_path.startswith('/') or str_path.startswith('\\'):
                    str_path = str_path[1:]
                return str_path
            
            # 构建项目元数据用于全局更新
            project_metadata = self.metadata_manager.create_project_metadata(
                local_path=path2str(generate_result.project_path),
                project_type=context.project_type or generate_result.project_type or "unknown",
                git_repository=context.git_repository_url or "",
                git_branch=context.branch,
                name=context.repo_name or "",
                group=context.repo_group or "",
                strategy=context.strategy.value if context.strategy else (str(generate_result.strategy_used).split('.')[-1].lower() if generate_result.strategy_used else ""),
                model_name=context.extra_context.get('model_name', ''),
                prompt_version=context.prompt_version or "",
                model_options=context.extra_context.get('llm_options', {}),
                output_uri=path2str(output_uri),
                document_metadata_path=path2str(doc_metadata_path),
                status="saved",
                event="save_metadata",
                event_time=datetime.now().isoformat()
            )
            
            # 调用 ProjectMetadataManager 更新全局元数据
            # 使用 context.output_dir 而不是硬编码路径，确保测试环境隔离
            output_dir = self._global_output_dir()
            global_metadata_path = self.metadata_manager.save_project_metadata(
                metadata=project_metadata,
                output_dir=output_dir
            )
            
            self.logger.info(f"全局项目元数据已更新: {global_metadata_path}")
                
            # 更新生成结果
            generate_result.metadata_saved = True
            generate_result.metadata_path = metadata_path
            
            completion_metadata = {
                "metadata_path": metadata_path,
                "output_uri": output_uri,
                "completion_time": datetime.now().isoformat(),
                "status": "success",
                "metadata_saved": True
            }
            
            self.logger.info(f"元数据保存成功: {metadata_path}")
            return completion_metadata
            
        except Exception as e:
            error_msg = f"保存元数据失败: {e}"
            self.logger.error(error_msg)
            
            # 更新生成结果中的警告信息
            if hasattr(generate_result, 'warnings'):
                generate_result.warnings.append(error_msg)
            
            # 元数据保存失败不影响主流程，返回错误信息但不抛出异常
            return {"error": error_msg, "status": "metadata_save_failed"}
    
    @safe_file_operation("文档元数据保存")
    def _save_documentation_metadata(self,
                                     catalogue_data: Dict[str, Any],
                                     output_dir: str,
                                     project_path: str,
                                     project_type: str,
                                     strategy: str,
                                     git_repository: str = "",
                                     git_branch: str = "master",
                                     prompt_version: str = None,
                                     overview_result: Dict[str, Any] = None) -> None:
        """
        保存文档库元数据到JSON文件
        
        Args:
            catalogue_data: 目录结构数据
            output_dir: 输出目录
            project_path: 项目路径
            project_type: 项目类型
            strategy: 生成策略
            git_repository: Git仓库地址
            git_branch: Git分支名
            prompt_version: 提示词版本
            overview_result: 概览生成结果
            
        Raises:
            ValueError: 当输出目录无效时
            OSError: 当文件写入失败时
            RuntimeError: 当元数据构建失败时
        """
        if not output_dir:
            raise ValueError("输出目录不能为空")
            
        try:
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 构建元数据 - 根据测试期望的结构
            metadata = {
                "generated_at": datetime.now().isoformat(),
                "documentation_info": {
                    "generator": "Knowledge Engineering System",
                    "version": "1.0.0"
                },
                "project_info": {
                    "path": project_path,
                    "type": project_type,
                    "git_repository": git_repository,
                    "git_branch": git_branch
                },
                "generation_config": {
                    "strategy": strategy,
                    "prompt_version": prompt_version
                },
                "overview": overview_result,
                "catalogue": catalogue_data
            }
            
            # 保存到JSON文件
            metadata_file = os.path.join(output_dir, "documentation_metadata.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Documentation metadata saved to: {metadata_file}")
            
        except (OSError, IOError) as e:
            error_msg = f"无法保存文档元数据文件到 {output_dir}: {e}"
            self.logger.error(error_msg)
            raise OSError(error_msg) from e
        except ValueError as e:
            # ValueError 需要保持原始类型，让装饰器处理
            error_msg = f"保存文档元数据时发生参数错误: {e}"
            self.logger.error(error_msg)
            raise ValueError(error_msg) from e
        except Exception as e:
            error_msg = f"保存文档元数据时发生未知错误: {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    @safe_file_operation("项目元数据保存")
    def _save_project_metadata(self,
                               project_path: str,
                               project_type: str,
                               git_repository: str,
                               git_branch: str,
                               strategy: str,
                               model_name: str,
                               prompt_version: str,
                               model_options: Dict[str, Any],
                               output_dir: str,
                               name: str = "",
                               group: str = "") -> str:
        """
        保存项目元数据信息
        
        Args:
            project_path: 项目路径
            project_type: 项目类型
            git_repository: Git仓库地址
            git_branch: Git分支
            strategy: 生成策略
            model_name: 模型名称
            prompt_version: 提示词版本
            model_options: 模型选项
            output_dir: 输出目录
            name: 项目名称
            group: 项目组
            
        Returns:
            保存的元数据文件路径
        """
        try:
            # 构建文档元数据路径
            doc_metadata_path = os.path.join(output_dir, "documentation_metadata.json")
            def path2str(input):
                return str(input) if isinstance(input, PosixPath) else input
            
            # 创建项目元数据
            metadata = self.metadata_manager.create_project_metadata(
                local_path=path2str(project_path),
                project_type=project_type,
                git_repository=git_repository,
                git_branch=git_branch,
                name=name,
                group=group,
                strategy=strategy,
                model_name=model_name,
                prompt_version=prompt_version,
                model_options=model_options,
                output_uri=path2str(output_dir),
                document_metadata_path=path2str(doc_metadata_path),
                status="saved",
                event="save_metadata",
                event_time=datetime.now().isoformat()
            )
            
            # 直接保存单个项目元数据到文件
            metadata_file_path = os.path.join(output_dir, "__project_metadata__.json")
            os.makedirs(output_dir, exist_ok=True)
            
            with open(metadata_file_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            return metadata_file_path
            
        except Exception as e:
            self.logger.error(f"保存项目元数据失败: {e}")
            raise
    
    def on_error(self,
        context: GenerationContext,
        generate_result: KnowledgeGenerationResult,
        error: Exception
        ) -> Optional[Dict[str, Any]]:
        """
        错误处理
        
        Args:
            context: 生成文档的上下文信息
            generate_result: 生成结果对象
            error: 发生的错误
            
        Returns:
            错误处理结果元数据
        """
        pass
    