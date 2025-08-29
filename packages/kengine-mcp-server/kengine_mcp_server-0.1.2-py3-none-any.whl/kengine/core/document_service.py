"""
文档生成服务

提供高级生成功能，处理完整的生成流程
"""
from typing import Dict, Any, Union, Optional
import logging
import json
import os
from datetime import datetime

from .strategy_factory import StrategyFactory
from .types import GenerationContext, StepGenerationResult
from ..utils.safe_file import safe_file_operation
from .enums import GenerationStrategy, ExecuteStep, ProgressStage
from .strategies.base_strategy import GenerationMode
from ..utils.project_metadata import ProjectMetadataManager
from ..config.application_config import get_application_config
from .progress import ProgressTracker
from .utils.safe_tracker import SafeTrackerOperations
from .utils.catalogue_data_utils import filter_catalogue_by_path
from ..io import create_doc_file_io

class DocumentGenerationService:
    """文档生成服务 - 提供高级生成功能"""
    
    def __init__(self):
        """
        初始化服务
        
        Args:
            factory: 文档生成工厂实例
        """
        self.factory = StrategyFactory()
        self.metadata_manager = ProjectMetadataManager()
        self.logger = logging.getLogger(__name__)
        self.app_config  = get_application_config()
        self.config = self.app_config.get('generate-settings', {})
        self.tracker: Optional[ProgressTracker] = None
    
    def _get_parallel_generation_config(self):
        """
        获取并行生成配置
        
        Returns:
            tuple: (mode, max_workers) - 生成模式和最大工作线程数
        """
        # 读取配置中的并发数设置
        concurrent_count = self.config.get('document-concurrent', 1)
        
        # 如果并发数大于1，使用并行模式，否则使用串行模式
        if concurrent_count > 1:
            mode = GenerationMode.PARALLEL
            max_workers = concurrent_count
            self.logger.info(f"Using parallel generation mode with {max_workers} workers")
        else:
            mode = GenerationMode.SERIAL
            max_workers = None
            self.logger.info("Using serial generation mode")
            
        return mode, max_workers
    
    def generate_catalogue(self, context: GenerationContext) -> StepGenerationResult:
        """
        生成文档目录结构
        
        Args:
            context: 生成上下文
            
        Returns:
            生成结果
        """
        try:
            # 开始目录生成阶段
            SafeTrackerOperations.safe_tracker_start_stage(self.tracker,ProgressStage.CATALOGUE_GENERATION, "开始生成文档目录结构")
            generator = self._initialize_strategy_generator(context)            
            self.logger.info(
                f"Generating catalogue using {generator.get_strategy_name()} "
                f"for project type '{context.project_type}'"
            )
            
            result = generator.generate_catalogue(context)
            
            if result.success:
                self.logger.info("Catalogue generation completed successfully")
                context.catalogue = result.data
                # 将文档目录保存 output_path / __catalogue__.json 中
                self._save_catalogue_to_json(result.data, context)
                
                # 完成目录生成阶段
                SafeTrackerOperations.safe_tracker_complete_stage(self.tracker,ProgressStage.CATALOGUE_GENERATION, "文档目录结构生成完成")
                
            else:
                self.logger.error(f"Catalogue generation failed: {result.error}")
                # 标记目录生成失败
                SafeTrackerOperations.safe_tracker_fail_stage(self.tracker,ProgressStage.CATALOGUE_GENERATION, f"目录生成失败: {result.error}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Catalogue generation error: {e}")
            # 标记目录生成失败
            SafeTrackerOperations.safe_tracker_fail_stage(self.tracker,ProgressStage.CATALOGUE_GENERATION, f"目录生成异常: {str(e)}")
            return StepGenerationResult(
                success=False,
                error=str(e),
                strategy_used=context.strategy
            )
    
    def generate_documents(self,
        catalogue_data: Dict[str, Any],
        context: GenerationContext,
        execute_step = 'full',
        specify_document_path = None
    ) -> StepGenerationResult:
        """
        生成文档内容
        
        Args:
            catalogue_data: 目录结构数据
            context: 生成上下文（包含输出路径信息）
            execute_step: 此次请求所要求执行步骤, 默认值full为全部生成
            specify_document_path： 要求生产的文档路径, 该路径必须是 catalogue中的路径，默认值为None
        Returns:
            生成结果
        """
        try:
            # 开始文档生成阶段
            SafeTrackerOperations.safe_tracker_start_stage(self.tracker,ProgressStage.DOCUMENT_GENERATION, "开始生成文档内容")
            generator = self._initialize_strategy_generator(context)     
            # 如果指定了 execute_step == 'document' and  specify_document_path is not None
            # 从文档路径中过滤需要执行的目录去生成
            result = None
            if execute_step == ExecuteStep.DOCUMENT and specify_document_path is not None and specify_document_path:
                self.logger.info(f'generate document specify {specify_document_path}')
                # 需要将 catalogue_data 转换为 filter_catalogue_by_path 期望的格式
                catalogue_items = catalogue_data.get('catalogue', catalogue_data)
                filtered_catalogue_data = filter_catalogue_by_path(catalogue_items, specify_document_path)
                if not filtered_catalogue_data['items']:
                    raise RuntimeError(f"'{specify_document_path}' error can not parse valid catalogues")
                # 指定文档采用默认执行模式
                result = generator.generate_documents(filtered_catalogue_data, context)
            else:
                # 直接调用策略的 generate_documents 方法，输出路径已包含在 context 中
                # 获取并行生成配置
                mode, max_workers = self._get_parallel_generation_config()
                result = generator.generate_documents(catalogue_data,
                                                      context,
                                                      mode=mode,
                                                      max_workers=max_workers)
            result.strategy_used = context.strategy
            if result.success:
                self.logger.info("Document generation completed successfully")
                # 完成文档生成阶段
                SafeTrackerOperations.safe_tracker_complete_stage(self.tracker,ProgressStage.DOCUMENT_GENERATION, "文档内容生成完成")
            else:
                self.logger.error(f"Document generation failed: {result.error}")
                # 标记文档生成失败
                SafeTrackerOperations.safe_tracker_fail_stage(self.tracker,ProgressStage.DOCUMENT_GENERATION, f"文档生成失败: {result.error}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Document generation error: {e}")
            # 标记文档生成失败
            SafeTrackerOperations.safe_tracker_fail_stage(self.tracker,ProgressStage.DOCUMENT_GENERATION, f"文档生成异常: {str(e)}")
            return StepGenerationResult(
                success=False,
                error=str(e),
                strategy_used=context.strategy
            )
        
    
    def generate_overview(self, context: GenerationContext) -> StepGenerationResult:
        """
        生成项目概览文档
        
        Args:
            context: 生成上下文，包含所有必要信息
            
        Returns:
            概览生成结果
        """
        try:
            # 开始概览生成阶段
            SafeTrackerOperations.safe_tracker_start_stage(self.tracker,ProgressStage.OVERVIEW_GENERATION, "开始生成项目概览文档")
            
            generator = self.factory.create_generator(context.strategy)
            
            self.logger.info(
                f"Generating overview using {generator.get_strategy_name()} "
                f"for project type '{context.project_type}'"
            )
            
            result = generator.generate_overview(context)
            
            if result.success:
                self.logger.info("Overview generation completed successfully")
                # 完成概览生成阶段
                SafeTrackerOperations.safe_tracker_complete_stage(self.tracker,ProgressStage.OVERVIEW_GENERATION, "项目概览文档生成完成")
            else:
                self.logger.error(f"Overview generation failed: {result.error}")
                # 标记概览生成失败
                SafeTrackerOperations.safe_tracker_fail_stage(self.tracker,ProgressStage.OVERVIEW_GENERATION, f"概览生成失败: {result.error}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Overview generation error: {e}")
            # 标记概览生成失败
            SafeTrackerOperations.safe_tracker_fail_stage(self.tracker,ProgressStage.OVERVIEW_GENERATION, f"概览生成异常: {str(e)}")
            return StepGenerationResult(
                success=False,
                error=str(e),
                strategy_used=context.strategy
            )
    
    
    @safe_file_operation("保存目录文件")
    def _save_catalogue_to_json(self, catalogue_data: Dict[str, Any], context: GenerationContext) -> None:
        """
        将文档目录保存到 __catalogue__.json 文件中
        
        Args:
            catalogue_data: 目录结构数据
            context: 生成上下文，包含输出路径信息
        """
        # 构建目录文件路径
        catalogue_file =  "__catalogue__.json"
        
        # 添加元数据信息
        catalogue_with_metadata = {
            "generated_at": datetime.now().isoformat(),
            "project_type": context.project_type,
            "strategy": context.strategy.value,
            "prompt_version": context.prompt_version,
            "catalogue": catalogue_data
        }
        
        # 保存到JSON文件
        with create_doc_file_io(context.repo_group, context.repo_name, context.prompt_version) as f:
            data = json.dumps(catalogue_with_metadata, ensure_ascii=False, indent=2)
            f.write(path=catalogue_file, content=data)
        
        self.logger.info(f"目录文件已保存: {catalogue_file}")
        
    
    def _initialize_strategy_generator(self, context: GenerationContext):
        if not context.strategy:
            strategy_name = self.app_config.get_classification_generation_strategy(context.project_type)
            if not strategy_name:
                error_msg = f"项目分类 '{context.project_type}' 未配置生成策略，请检查 config/application_config.json"
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)
            strategy = GenerationStrategy(strategy_name)
            self.logger.info(f"根据项目分类 '{context.project_type}' 自动选择策略: {strategy}")
            context.strategy = strategy
        generator = self.factory.create_generator(context.strategy)
        self.logger.info(
            f"Generating documents using {generator.get_strategy_name()} "
            f"for project type '{context.project_type}'"
        )
        return generator

    def generate_docs(self,
        context: GenerationContext,
        execute_step: Union[ExecuteStep] = ExecuteStep.FULL,
        specify_document_path: Optional[str] = None) -> Dict[str, StepGenerationResult]:
        """
        一键生成完整文档（概览+目录+内容）或仅生成概览
        
        Args:
            context: 生成上下文对象，包含所有必要的生成参数
            execute_step: 执行步骤，可以是ExecuteStep枚举或字符串 ("full", "overview", "catalogue", "document")
            specify_document_path: 指定要生成的文档路径
            
        Returns:
            包含概览、目录和文档生成结果的字典
        """
        # 使用上下文中的tracker
        self.tracker = context.tracker
        if self.tracker:
            self.logger.info(f"Using progress tracker from context for task: {context.task_id}")
        
        # 更新上下文中的执行步骤和指定文档路径
        context.execute_step = execute_step
        context.specify_document_path = specify_document_path
        self._initialize_strategy_generator(context)     

        
        if execute_step == ExecuteStep.OVERVIEW:
            self.logger.info(f"Starting overview generation for '{context.project_type}' ")
        else:
            self.logger.info(f"Starting full documentation generation for '{context.project_type}' ")
        
        results = {}
        
        
        # 1. 生成目录
        catalogue_result = None
        should_execute_catalogue = execute_step == ExecuteStep.FULL or execute_step == ExecuteStep.CATALOGUE
        if not should_execute_catalogue:
            catalogue_path =  '/__catalogue__.json'
            _io = create_doc_file_io(context.repo_group, context.repo_name, context.prompt_version)
            if _io.exists(catalogue_path):
                self.logger.info(f'load catalogue from file {catalogue_path}')
                should_execute_catalogue = False
                catalogue_result = json.loads(_io.read(catalogue_path))
                catalogue_result = StepGenerationResult(
                    success=True,
                    data=catalogue_result['catalogue']
                )
                results['catalogue'] = catalogue_result
                # 设置上下文， 以方便后续使用
                context.catalogue = catalogue_result.data
            else:
                self.logger.warning(f'execute_step = {execute_step} but file {catalogue_path} not exists, load catalogue will execute')
                should_execute_catalogue = True
        
        if should_execute_catalogue:
            catalogue_result = self.generate_catalogue(context)
            results["catalogue"] = catalogue_result
        
            if not catalogue_result.success:
                self.logger.error("Catalogue generation failed, will skip document generation later")
        
        if execute_step == ExecuteStep.CATALOGUE:
            self.logger.info("catalogue generation completed, step exit")
            return results
        
        # 2. 生成项目概览（使用上下文缓存） 当step 为 full 或者 overview 时生成概览
        # 其他情况不生成
        overview_result = None
        if execute_step in (ExecuteStep.FULL, ExecuteStep.OVERVIEW):
            overview_result = self.generate_overview(context)
            results["overview"] = overview_result
            
            if not overview_result.success:
                self.logger.warning("Overview generation failed")
                self.logger.warning("Continuing with documentation generation")
        else:
            overview_result = StepGenerationResult(False, {}, error=f"execute step ignore overview")
        
        # 如果只需要生成概览，在此处返回
        if execute_step == ExecuteStep.OVERVIEW:
            self.logger.info("Overview generation completed, step exit")
            return results
        
        # 3. 生成文档 - 只有在目录生成成功时才执行
        if catalogue_result and catalogue_result.success:
            documents_result = self.generate_documents(
                catalogue_result.data,
                context,
                execute_step=execute_step,
                specify_document_path=specify_document_path
            )
            results["documents"] = documents_result
        else:
            self.logger.info("Skipping document generation due to catalogue failure")
        
        return results
