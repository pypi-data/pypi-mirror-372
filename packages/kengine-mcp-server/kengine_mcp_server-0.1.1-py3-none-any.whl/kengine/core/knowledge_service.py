import os
import logging
from typing import Dict, Any, Optional, Union
from kengine.core.utils.catalogue_data_utils import count_documents_in_catalogue
from kengine.utils.dir_utils import base_dir

from ..tasks.clone import clone_repository
from ..tasks.classification import classify_repository
from ..rag import build_rag_service
from ..config.application_config import get_application_config
from .document_service import DocumentGenerationService
from .types import GenerationContext, KnowledgeGenerationRequest, KnowledgeGenerationResult
from .enums import GenerationStrategy, ValidationLevel
from .enums import ExecuteStep, ProgressStage, ProgressStatus
from .progress import ProgressTracker, progress_manager
from .metadata import MetadataAdapter, create_meta_adapter
from .utils.safe_tracker import SafeTrackerOperations



class KnowledgeService:
    """知识工程服务"""
    
    def __init__(self):
        """初始化知识工程服务"""
        self.logger = logging.getLogger(__name__)
        self.app_config = get_application_config()
        self.doc_service = DocumentGenerationService()
        # self.metadata_manager = ProjectMetadataManager()
        self.metadata_adapter = create_meta_adapter()
    
    def create_context(self,
                      project_path: str,
                      project_type: str,
                      strategy: Union[GenerationStrategy, str],
                      llm_options: Optional[Dict[str, Any]] = None,
                      rag_service: Optional[Any] = None,
                      git_repository_url: Optional[str] = None,
                      branch: str = "master",
                      validation_level: ValidationLevel = ValidationLevel.BASIC,
                      custom_config: Optional[Dict[str, Any]] = None,
                      prompt_version: Optional[str] = None,
                      doc_output_base_path: Optional[str] = None,
                      extra_context: Dict[str, Any] = None,
                      catalogue: Optional[Dict[str, Any]] = None,
                      task_id: Optional[str] = None,
                      tracker: Optional[Any] = None,
                      repo_name: str = None,
                      repo_group: str = None) -> GenerationContext:
        """
        创建生成上下文
        
        Args:
            project_path: 项目路径
            project_type: 项目类型
            strategy: 生成策略，AUTO表示自动选择
            llm_options: 大模型选项配置
            rag_service: RAG服务实例
            git_repository_url: Git仓库URL
            branch: Git分支
            validation_level: 验证级别
            custom_config: 自定义配置
            prompt_version: 提示词版本
            doc_output_base_path: 输出路径
            extra_context: 额外上下文信息
            catalogue: 文档目录信息
            task_id: 任务ID
            tracker: 进度跟踪器
            repo_name: 仓库名称
            repo_group: 仓库组名
            
        Returns:
            生成上下文对象
        """
        # 处理策略选择
        if isinstance(strategy, str):
            strategy = GenerationStrategy(strategy.lower())
        
        # 处理 extra_context 默认值
        if extra_context is None:
            extra_context = {}
        
        return GenerationContext(
            project_path=project_path,
            project_type=project_type,
            strategy=strategy,
            llm_options=llm_options,
            rag_service=rag_service,
            git_repository_url=git_repository_url,
            branch=branch,
            validation_level=validation_level,
            custom_config=custom_config,
            prompt_version=prompt_version,
            doc_output_base_path=doc_output_base_path,
            extra_context=extra_context,
            catalogue=catalogue,
            task_id=task_id,
            tracker=tracker,
            repo_name=repo_name,
            repo_group=repo_group
        )
        
    
    def generate_knowledge(self,
                                 request: KnowledgeGenerationRequest,
                                 task_id: Optional[int] = None) -> KnowledgeGenerationResult:
        """
        执行完整的知识生成流程 - 重构版本
        
        重构内容：
        1. 移除任务管理逻辑，专注知识生成核心功能
        2. KnowledgeService 直接管理 tracker 创建
        3. 简化代码逻辑，提高可维护性
        4. 实现职责分离：任务管理由 KnowledgeScheduler 负责
        
        Args:
            request: 知识生成请求参数
            task_id: 任务ID（可选，用于进度跟踪）
            
        Returns:
            知识生成结果
        """
        result = KnowledgeGenerationResult(
            success=False,
            project_path="",
            output_path=""
        )
        
        # 创建进度跟踪器
        tracker = None
        if task_id:
            tracker = progress_manager.create_tracker(
                task_id=task_id,
                enable_database=True,
                auto_detect_websocket=True
            )
            self.logger.info(f"已创建进度跟踪器，自动配置callbacks - 任务ID: {task_id}")
        
        
        try:
            # 1. 根据请求计算内部路径和配置
            paths = self._calculate_paths(request)
            configs = self._prepare_configs(request)
            
            # 2. 创建生成上下文对象（在克隆前创建，项目类型稍后更新）
            context = self.create_context(
                project_path=paths["clone_dir"],
                project_type="unknown",  # 项目类型将在分类后更新
                strategy=None,
                llm_options=configs["model_config"],
                git_repository_url=paths["repo_url"],
                branch=request.branch,
                prompt_version=request.prompt_version,
                doc_output_base_path=paths["output_dir"],
                task_id=str(task_id),
                tracker=tracker,
                repo_name=request.repo_name,
                repo_group=request.repo_group,
                extra_context={
                    'model_name': request.model_name,
                    'specify_document_path': request.specify_document_path,
                    'user_annotation': request.user_annotation
                }
            )
            self.logger.info(f"已创建生成上下文对象")
            # 保存开始元数据
            self.metadata_adapter.on_start_generate(request=request, context=context)
            
            # 3. 克隆代码库
            SafeTrackerOperations.safe_tracker_start_stage(tracker, ProgressStage.CLONE, "开始克隆代码库...")
            self._clone_repository(request, paths, result)
            self.metadata_adapter.on_cloned_repository(context=context, generate_result=result)
            SafeTrackerOperations.safe_tracker_complete_stage(tracker, ProgressStage.CLONE, "代码库克隆完成")
            
            # 4. 分类项目类型 总是执行
            SafeTrackerOperations.safe_tracker_start_stage(tracker, ProgressStage.CLASSIFICATION, "开始项目分类...")
            self._classify_project(request, configs, result)
            # 5. 更新上下文中的项目类型
            context.project_type = result.project_type
            self.logger.info(f"已更新上下文中的项目类型: {result.project_type}")
            self.metadata_adapter.on_classified(context=context, generate_result=result)
            SafeTrackerOperations.safe_tracker_complete_stage(tracker, ProgressStage.CLASSIFICATION, f"项目分类完成: {result.project_type}")
            
            # execute step
            # CLASSIFICATION = "classification"
            # OVERVIEW = "overview"
            # CATALOGUE = "catalogue"
            # DOCUMENT = "document"
            # FULL = "full"
            if request.execute_step not in (ExecuteStep.CLASSIFICATION,):
                # 4. 构建RAG知识库， 如果不是 classification 执行
                SafeTrackerOperations.safe_tracker_start_stage(tracker, ProgressStage.RAG_BUILD, "开始构建RAG知识库...")
                self._build_rag_knowledge_base(request, paths, configs, result)
                SafeTrackerOperations.safe_tracker_complete_stage(tracker, ProgressStage.RAG_BUILD, "RAG知识库构建完成")
                # 更新上下文中的 RAG 服务
                context.rag_service = result.rag_service
                # 5. 生成文档 - 优化：统一由 DocumentService 处理执行步骤
                # 是 overview， catalogue， document都要执行
                self._generate_documents(context, request, result, tracker)
            
            result.success = True
            self.metadata_adapter.on_completed(context=context, generate_result=result)
            self.logger.info(f"知识生成流程完成 - 执行步骤: {request.execute_step.value}")
            
        except Exception as e:
            result.error = str(e)
            result.success = False
            self.logger.error(f"知识生成失败: {e}", exc_info=True)
            # 标记任务失败
            SafeTrackerOperations.safe_tracker_report_error(tracker, ProgressStage.CLASSIFICATION, str(e))
            self.metadata_adapter.on_error(context=context, generate_result=result, error=e)
        
        finally:
            SafeTrackerOperations.safe_progress_manager_remove_tracker(progress_manager, task_id)
        
        return result
    
    def _calculate_paths(self, request: KnowledgeGenerationRequest) -> Dict[str, str]:
        """根据请求计算所有内部路径"""
        return {
            "repo_url": f"git@coding.jd.com:{request.repo_group}/{request.repo_name}.git",
            "clone_dir": os.path.join(base_dir, ".cloned-repo", request.repo_group, request.repo_name),
            "output_dir": os.path.join(base_dir, "docs4demo", request.repo_group, request.repo_name),
            "knowledge_base_dir": os.path.join(base_dir, ".kb", request.repo_group, request.repo_name)
        }
    
    def _prepare_configs(self, request: KnowledgeGenerationRequest) -> Dict[str, Any]:
        """准备内部配置"""
        # 验证模型配置
        model_config = self.app_config.get_model_config(request.model_name)
        self.logger.info(f"使用模型: {model_config.get('model')}")
        
        return {
            "model_config": model_config,
        }
    
    def _clone_repository(self, request: KnowledgeGenerationRequest, paths: Dict[str, str], result: KnowledgeGenerationResult):
        """克隆代码库"""
        result.generate_stage = "clone"
        result.project_path = paths["clone_dir"]
        result.output_path = paths["output_dir"]
        
        # 确保目录存在
        os.makedirs(paths["clone_dir"], exist_ok=True)
        
        self.logger.info(f"开始克隆仓库: {paths['repo_url']} -> {paths['clone_dir']}")
        
        try:
            clone_repository(paths["repo_url"], paths["clone_dir"], force=True)
            self.logger.info("仓库克隆完成")
        except Exception as e:
            error_msg = f"克隆仓库失败: {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def _classify_project(self, request: KnowledgeGenerationRequest, configs: Dict[str, Any], result: KnowledgeGenerationResult):
        """分类项目类型"""
        result.generate_stage = "classification"
        
        self.logger.info(f"开始分析仓库类型与功能: {result.project_path}")
        
        if request.force_project_type:
            # 强制使用指定类型
            result.project_type = request.force_project_type
            result.classification_result = {
                "classification": request.force_project_type,
                "confidence": 1.0,
                "analysis_summary": f"强制指定项目类型: {request.force_project_type}",
                "forced": True
            }
            self.logger.info(f"强制使用项目类型: {request.force_project_type}")
        else:
            # 自动分类
            try:
                classification_result = classify_repository(result.project_path, request.model_name)
                result.classification_result = classification_result
                result.project_type = classification_result.get("classification", "Applications")
                
                self.logger.info("分析结果:")
                self.logger.info(f"- 分类: {result.project_type}")
                self.logger.info(f"- 置信度: {classification_result.get('confidence')}")
                self.logger.info(f"- 摘要: {classification_result.get('analysis_summary')}")
                
            except Exception as e:
                error_msg = f"项目分类失败: {e}"
                self.logger.error(error_msg)
                raise RuntimeError(f"classification error {error_msg}") from e
        
    
    def _build_rag_knowledge_base(self,
                                  request: KnowledgeGenerationRequest, 
                                  paths: Dict[str, str],
                                  configs: Dict[str, Any],
                                  result: KnowledgeGenerationResult):
        """构建RAG知识库"""
        result.generate_stage = "rag"
        
        self.logger.info(f"开始构建RAG知识库: {result.project_path}")
        
        try:
            # 构建RAG知识库
            rag_service = build_rag_service(request.repo_group, request.repo_name)
            # 将rag_service赋值给结果对象
            result.rag_service = rag_service
            result.rag_built = True
            self.logger.info("RAG知识库构建成功")
        except Exception as e:
            error_msg = f"构建RAG知识库失败: {e}"
            self.logger.error(error_msg, exc_info=True)
            raise RuntimeError(f"rag build error {error_msg}") from e
    
    def _generate_documents(self,
                                 context: GenerationContext,
                                 request: KnowledgeGenerationRequest,
                                 result: KnowledgeGenerationResult,
                                 progress_tracker: ProgressTracker = None):
        """
        生成文档 - 优化版本
        
        优化内容：
        1. 移除重复的 ExecuteStep 分支判断
        2. 统一由 DocumentService 处理所有执行步骤
        3. 简化代码逻辑，提高可维护性
        4. 集成进度跟踪
        """
        result.generate_stage = "documentation"
        
        self.logger.info(f"开始生成文档 - 项目路径: {result.project_path} 执行步骤: {request.execute_step.value}")
        
        try:
            # 目录生成阶段
            if request.execute_step in (ExecuteStep.FULL, ExecuteStep.CATALOGUE, ExecuteStep.DOCUMENT):
                SafeTrackerOperations.safe_tracker_start_stage(progress_tracker, ProgressStage.CATALOGUE_GENERATION, "开始生成文档目录...")
            
            # 优化：直接调用 DocumentService，传递上下文对象
            generation_results = self.doc_service.generate_docs(
                context=context,
                execute_step=request.execute_step,  # 传递执行步骤给 DocumentService
                specify_document_path=request.specify_document_path,
            )
            
            # 处理生成结果并更新进度
            self._process_generation_results(generation_results, 
                                                   result, 
                                                   request.execute_step, 
                                                   progress_tracker)
            
        except Exception as e:
            error_msg = f"生成文档失败: {e}"
            self.logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e
    
    def _process_generation_results(self, 
                                          generation_results: Dict[str, Any], 
                                          result: KnowledgeGenerationResult, 
                                          execute_step: ExecuteStep, 
                                          progress_tracker: ProgressTracker = None):
        """
        处理文档生成结果 - 优化版本
        
        根据执行步骤处理不同的生成结果，并更新进度
        """
        # 处理概览生成结果（所有步骤都可能包含概览）
        overview_result = generation_results.get("overview")
        result.overview_result = overview_result
        
        if overview_result:
            if overview_result.success:
                self.logger.info("项目概览生成完成")
                SafeTrackerOperations.safe_tracker_update_progress(progress_tracker, 
                                                  ProgressStage.OVERVIEW_GENERATION,
                                                  ProgressStatus.COMPLETED, 
                                                  100, 
                                                  "项目概览生成完成")
            else:
                self.logger.warning(f"项目概览生成失败: {overview_result.error}")
                SafeTrackerOperations.safe_tracker_update_progress(progress_tracker, 
                                                  ProgressStage.OVERVIEW_GENERATION,
                                                  ProgressStatus.FAILED, 
                                                  0,
                                                  f"项目概览生成失败: {overview_result.error}")
        
        # 如果只是概览步骤，在此返回
        if execute_step == ExecuteStep.OVERVIEW:
            self.logger.info("概览生成流程完成")
            return
        
        # 处理目录生成结果
        catalogue_result = generation_results.get("catalogue")
        result.catalogue_result = catalogue_result
        
        if catalogue_result and catalogue_result.success:
            # 计算文档数量并更新权重
            doc_count = count_documents_in_catalogue(catalogue_result.data)
            self.logger.info(f"文档目录生成完成， 共 {doc_count} 个文件")
            # 设置总文档数用于进度跟踪
            SafeTrackerOperations.safe_tracker_set_document_count(progress_tracker, doc_count)
            SafeTrackerOperations.safe_tracker_update_progress(progress_tracker, 
                                              ProgressStage.CATALOGUE_GENERATION,
                                              ProgressStatus.COMPLETED, 
                                              100, 
                                              f"文档目录生成完成，共{doc_count}个文档")
                
        elif catalogue_result:
            error_msg = f"文档目录生成失败: {catalogue_result.error}"
            self.logger.error(error_msg)
            SafeTrackerOperations.safe_tracker_update_progress(progress_tracker, 
                                              ProgressStage.CATALOGUE_GENERATION,
                                              ProgressStatus.FAILED, 
                                              0, 
                                              error_msg)
            raise RuntimeError(error_msg)
        
        # 如果只是目录步骤，在此返回
        if execute_step == ExecuteStep.CATALOGUE:
            return
        
        # 处理文档生成结果
        documents_result = generation_results.get("documents")
        result.documents_result = documents_result
        
        if documents_result and documents_result.success:
            stats = documents_result.data
            self.logger.info(f"文档生成完成, 总计项目: {stats['total_items']} 成功生成: {stats['successful_generations']} 生成失败: {stats['failed_generations']}")
            
            SafeTrackerOperations.safe_tracker_update_progress(progress_tracker, 
                                              ProgressStage.DOCUMENT_GENERATION,
                                              ProgressStatus.COMPLETED, 
                                              100,
                                              f"文档生成完成: {stats['successful_generations']}/{stats['total_items']}")
            
            if stats['generated_files']:
                self.logger.info("生成的文档文件:")
                for file_path in stats['generated_files']:
                    self.logger.info(f"  - {file_path}")
            
            if stats['failed_items']:
                self.logger.warning("生成失败的项目:")
                for failed_item in stats['failed_items']:
                    self.logger.warning(f"  - {failed_item['title']}: {failed_item['error']}")
        elif documents_result:
            error_msg = f"文档生成失败: {documents_result.error}"
            self.logger.error(error_msg)
            SafeTrackerOperations.safe_tracker_update_progress(progress_tracker, 
                                              ProgressStage.DOCUMENT_GENERATION,
                                              ProgressStatus.FAILED, 
                                              0, 
                                              error_msg)
            raise RuntimeError(error_msg)
    
    