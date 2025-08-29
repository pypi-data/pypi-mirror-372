"""
基于提示词的文档生成策略 - 重构版本

使用简化的基类变量管理，添加prompt策略特有的功能
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from langchain_core.prompts import ChatPromptTemplate

from .base_strategy import DocumentGenerationStrategy, GenerationMode
from .strategy_utils import StrategyUtils
from ..types import GenerationContext, StepGenerationResult
from ..enums import GenerationStrategy
from ..parsers import CatalogueOutputParser, DocumentOutputParser, TaggedContentOutputParser
from ...repo.extractor import extract_repo_endpoint_skeletons
from ..utils.summerize import summerize_chunks
from ...utils.prompt_loader import extract_variables_from_prompt
from kengine.core.utils.catalogue_data_utils import find_document_item_in_catalogue, set_catalogue_saved_path


class PromptBasedStrategy(DocumentGenerationStrategy):
    """基于提示词的文档生成策略 - 使用简化的基类变量管理"""
    
    def get_strategy_name(self) -> str:
        return "PromptBased"
    
    def generate_catalogue(self, context: GenerationContext) -> StepGenerationResult:
        """生成文档目录结构"""
        llm_response = None
        try:
            
            self.logger.info(f"Generating catalogue for project type: {context.project_type}")
            
            # 验证项目路径
            error = self._validate_project_path(context.project_path)
            if error:
                raise FileNotFoundError(error)
            
            # 初始化LLM和解析器
            llm = self._init_llm_with_defaults(context.llm_options)
            output_parser = CatalogueOutputParser()
            
            # 加载prompt模板（指定prompt模式）
            prompt_template = self._load_prompt_with_strategy_mode('AnalyzeCatalogue', context.project_type, "prompt", context.prompt_version)
            prompt = ChatPromptTemplate.from_template(prompt_template)
            
            # 使用基类的统一变量构建方法
            chain_input = self._build_catalogue_variables(context)
            
            # 如果模板内容中包含 endpoint_definitions 变量， 从 项目中找到所有的入口服务， 并提取定义信息添加到 chain_input
            # 在项目目录中找到所有的入口服务：
            # Controller， Service
            # 将入口服务的定义作为上下文信息传递给prompt
            if self._should_extract_endpoint_definitions(prompt_template):
                self.logger.info("检测到模板包含 endpoint_definitions 变量，开始提取端点定义")
                endpoint_skeletons = self._extract_endpoint_skeletons(context) or ''
                chain_input["endpoint_definitions"] = endpoint_skeletons 
                self.logger.info(f"成功提取端点定义，内容长度: {len(endpoint_skeletons)} 个字符")
            
            # 执行生成链
            response = prompt.format(**chain_input)
            llm_response = llm.invoke(response)
            result_data = output_parser.parse(llm_response.content)
            
            self.logger.info("文档目录结构生成完成")
            return StepGenerationResult(
                success=True,
                data=result_data,
                strategy_used=GenerationStrategy.PROMPT
            )
            
        except Exception as e:
            self.logger.error(f"Catalogue generation failed, project_type='{context.project_type}', project_path='{context.project_path}': {e}", exc_info=True)
            self.logger.error(f'LLM Response: {llm_response.content if llm_response else "No response"}')
            return StepGenerationResult(
                success=False,
                error=str(e),
                strategy_used=GenerationStrategy.PROMPT
            )
    
    def generate_documents(self,
                          catalogue_data: Dict[str, Any],
                          context: GenerationContext,
                          mode: GenerationMode = GenerationMode.SERIAL,
                          max_workers: Optional[int] = None) -> StepGenerationResult:
        """生成文档内容，支持串行和并行模式"""
        try:
            self.logger.info(f"Generating documents for project type: {context.project_type}")
            
            # 调用基类的预处理逻辑
            self._on_generate_documents(catalogue_data, context)
            
            # 验证输入参数
            StrategyUtils.validate_catalogue_data(catalogue_data)
            
            # 初始化LLM和相关组件
            llm = self._init_llm_with_defaults(context.llm_options)
            output_parser = DocumentOutputParser()
            
            # 加载prompt模板（指定prompt模式）
            prompt_template = self._load_prompt_with_strategy_mode('GenerateDocs', context.project_type, "prompt", context.prompt_version)
            prompt = ChatPromptTemplate.from_template(prompt_template)
            
            # 生成统计信息
            stats = StrategyUtils.create_generation_stats()
            
            # 根据模式选择生成方式
            if mode == GenerationMode.PARALLEL:
                self.logger.info("使用并行模式生成文档")
                # 收集所有文档任务
                tasks = self._collect_document_tasks(catalogue_data["items"])
                # 并行执行
                stats = self._execute_parallel_generation(tasks, catalogue_data, context, max_workers)
            else:
                self.logger.info("使用串行模式生成文档")
                # 递归处理所有文档项
                self._generate_documents(
                    catalogue_data["items"],
                    stats,
                    llm,
                    prompt,
                    output_parser,
                    context,
                    catalogue_data,
                    current_level_output_path=''
                )
            
            self.logger.info(f"文档生成完成，成功: {stats['successful_generations']}, 失败: {stats['failed_generations']}")
            return StepGenerationResult(
                success=True,
                data=stats,
                strategy_used=GenerationStrategy.PROMPT
            )
            
        except Exception as e:
            error_msg = f"Document generation failed, project_type='{context.project_type}', project_path='{context.project_path}': {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return StepGenerationResult(
                success=False,
                error=str(e),
                strategy_used=GenerationStrategy.PROMPT
            )
    
    def _generate_documents(self,
                      items: List[Dict[str, Any]],
                      stats: Dict[str, Any],
                      llm,
                      prompt,
                      output_parser,
                      context: GenerationContext,
                      catalogue_data: Dict[str, Any],
                      current_level_output_path: Optional[str] = None) -> None:
        """递归处理文档项列表"""
        # 从 context 中获取 RAG 服务
        rag_service = context.rag_service
        
        for item in items:
            stats["total_items"] += 1
            
            try:
                # 准备RAG上下文信息（prompt策略特有）
                context_info = ""
                if item.get("name") and rag_service:
                    try:
                        rag_results = rag_service.similarity_search(
                            item["prompt"], 
                            k=20
                        )
                        related_docs = [
                            f"文件: {doc['filename']}\n路径: {doc['source']}\n内容:\n{doc['content'][:500]}..."
                            for doc in rag_results
                        ]
                        context_info = "\n\n".join(related_docs) if related_docs else "未找到相关文档"
                    except Exception as e:
                        self.logger.warning(f"RAG检索失败，项目名称='{item.get('name', 'unknown')}', 查询='{item.get('prompt', 'unknown')}': {e}")
                        context_info = "未找到相关文档"
                
                # 使用基类的统一变量构建方法
                chain_input = self._build_document_variables(context, catalogue_data, item)
                
                # 添加prompt策略特有的context_info
                chain_input["context_info"] = context_info
                
                # 生成文档内容
                formatted_prompt = prompt.format(**chain_input)
                llm_response = llm.invoke(formatted_prompt)
                content = output_parser.parse(llm_response.content)
                if content is None:
                    raise RuntimeError(f"生成文档内容为None ，{context.repo_group}-{context.repo_name} 项目名称='{item.get('name', 'unknown')}', 查询='{item.get('prompt', 'unknown')}'")
                # 清理文件名并保存
                catalog_path = f"{current_level_output_path}/{item['name']}"
                file_path = f"{catalog_path}.md"
                saved_path = self._save_content_to_file(context, content, file_path)
                # 生成文档后更新 catalogue_data, 根据当前任务的path: task['document_path'] 找到对应目录项， 添加 saved_path 属性
                set_catalogue_saved_path(catalog_path, catalogue_data, saved_path)
                # todo save saved_path to db
                stats["successful_generations"] += 1
                stats["generated_files"].append(str(saved_path))
                
                # 更新进度回调
                if context.tracker:
                    context.tracker.update_document_progress(stats["successful_generations"])
                
            except Exception as e:
                self.logger.error(f"generate doc {json.dumps(item)} error ", exc_info=True)
                # Agent模式下不使用降级方案，继续处理下一个文档
            
            # 递归处理子项
            if "children" in item and isinstance(item["children"], list) and len(item["children"]) > 0:
                child_output_path = f"{current_level_output_path}/{item['name']}"
                self._generate_documents(
                    item["children"],
                    stats,
                    llm,
                    prompt,
                    output_parser,
                    context,
                    catalogue_data,
                    current_level_output_path=child_output_path
                )
                    
    
    def generate_overview(self, context: GenerationContext) -> StepGenerationResult:
        """生成项目概览文档"""
        try:
            self.logger.info(f"Generating overview for project type: {context.project_type}")
            
            # 验证项目路径
            error = self._validate_project_path(context.project_path)
            if error:
                return StepGenerationResult(
                    success=False,
                    error=error,
                    strategy_used=GenerationStrategy.PROMPT
                )
            
            # 初始化LLM和解析器（使用overview标签解析器）
            llm = self._init_llm_with_defaults(context.llm_options)
            output_parser = TaggedContentOutputParser(tag_name="document", allow_fallback=True)
            
            # 加载overview模板
            prompt_template = self._load_prompt_with_strategy_mode('Overview', context.project_type, "prompt", context.prompt_version)
            prompt = ChatPromptTemplate.from_template(prompt_template)
            
            # 使用基类的统一变量构建方法
            chain_input = self._build_overview_variables(context)
            
            # 执行生成链
            chain = prompt | llm | output_parser
            overview_content = chain.invoke(chain_input)
            
            # 保存文件到输出路径
            overview_file_path =  "overview.md"
            
            saved_path = self._save_content_to_file(context, overview_content, overview_file_path)
            # todo save saved_path
            
            # 构建结果数据
            result_data = StrategyUtils.create_result_data(overview_content, saved_path, context)
            
            self.logger.info("项目概览生成完成")
            return StepGenerationResult(
                success=True,
                data=result_data,
                strategy_used=GenerationStrategy.PROMPT
            )
            
        except Exception as e:
            error_msg = f"生成项目概览失败，项目类型='{context.project_type}', 项目路径='{context.project_path}': {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return StepGenerationResult(
                success=False,
                error=error_msg,
                strategy_used=GenerationStrategy.PROMPT
            )
    
    def _should_extract_endpoint_definitions(self, prompt_content: str) -> bool:
        """
        检测模板是否包含 endpoint_definitions 变量
        
        Args:
            prompt_content: 模板内容
            
        Returns:
            bool: 如果模板包含 endpoint_definitions 变量则返回 True
        """
        # 使用 prompt_loader 中的函数提取变量
        variables = extract_variables_from_prompt(prompt_content)
        
        # 检查是否包含 endpoint_definitions 变量
        return "endpoint_definitions" in variables
    
    # 定义大模型输入限制常量
    MAX_LLM_INPUT_LENGTH = 5000
    SUMMARY_TARGET_LENGTH = 250
    
    def _extract_endpoint_skeletons(self, context: GenerationContext) -> str:
        """
        从项目中提取端点骨架信息，使用 summarize_chunks 函数进行总结
        
        Args:
            context: 生成上下文对象
            
        Returns:
            str: 格式化的端点骨架信息
        """
        try:
            # 查看 output_path / __abstract__.md 是否存在， 如果存在， 直接从文件中读取内容返回
            cached_content = self._load_cached_abstract(context)
            if cached_content:
                return cached_content
            
            # 使用 repo_extractor 提取端点骨架
            endpoint_data = extract_repo_endpoint_skeletons(context.project_path)
            
            # 如果提取失败或没有候选文件，返回提示信息
            if 'error' in endpoint_data:
                self.logger.warning(f"端点骨架提取失败: {endpoint_data['error']} for {context.project_path}")
                return None
            
            candidates = endpoint_data.get('candidates', [])
            if not candidates:
                self.logger.warning(f"未找到端点文件 for {context.project_path}")
                return None
            
            self.logger.info(f"开始处理 {len(candidates)} 个候选端点文件")
            
            # 提取所有候选文件的骨架作为 chunks
            skeleton_chunks = []
            for i, candidate in enumerate(candidates):
                skeleton = candidate.get('skeleton', None)
                if skeleton and skeleton.strip():
                    skeleton_chunks.append(skeleton)
                    self.logger.debug(f"添加第 {i+1}/{len(candidates)} 个候选文件骨架，长度: {len(skeleton)} 字符")
            
            if not skeleton_chunks:
                self.logger.warning("所有候选文件都没有有效的骨架内容")
                return None
            
            self.logger.info(f"共收集到 {len(skeleton_chunks)} 个有效的骨架文件")
            
            # 检查合并后的内容长度是否需要总结
            combined_skeletons = "\n".join(skeleton_chunks)
            if len(combined_skeletons) <= self.MAX_LLM_INPUT_LENGTH:
                # 内容较短，直接返回原始内容
                self.logger.info(f"内容长度 {len(combined_skeletons)} 字符，无需总结，直接返回")
                self._save_abstract_to_file(combined_skeletons, context)
                return combined_skeletons
            
            # 内容较长，需要进行总结
            # 使用 summarize_chunks 函数进行两阶段总结
            # 第一阶段：对每个骨架进行总结，目标长度为 SUMMARY_TARGET_LENGTH
            # 第二阶段：对所有总结进行最终合并，目标长度为 MAX_LLM_INPUT_LENGTH
            self.logger.info("开始使用 summarize_chunks 进行两阶段总结")
            
            final_summary = summerize_chunks(
                chunks=skeleton_chunks,
                chunk_prompt_name="CodeSkeleton",  # 使用现有的代码骨架总结提示词
                chunk_max_length=self.SUMMARY_TARGET_LENGTH,  # 单个骨架总结的目标长度
                summarize_chunk_prompt="CodeSkeletonSummary",  # 使用现有的默认总结提示词
                final_max_length=self.MAX_LLM_INPUT_LENGTH  # 最终总结的目标长度
            )
            
            if final_summary and final_summary.strip():
                self.logger.info(f"端点骨架总结完成，最终内容长度: {len(final_summary)} 字符")
                # 此处添加将项目的摘要信息存储到文件的逻辑
                # 存储到 文档生成的目标， 以 __abstract__.md 来命名
                try:
                    self._save_abstract_to_file(final_summary, context)
                except Exception as save_error:
                    self.logger.warning(f"保存摘要文件失败，但继续返回总结内容: {str(save_error)}")
                
                return final_summary
            else:
                self.logger.warning("summarize_chunks 返回了空的总结结果, 截断部分内容返回")
                # 如果总结失败，返回截断的原始内容并添加标记
                combined_skeletons = "\n".join(skeleton_chunks)
                suffix = "...[总结失败已截断]"
                max_content_length = self.MAX_LLM_INPUT_LENGTH - len(suffix)
                truncated_content = combined_skeletons[:max_content_length] + suffix
                return truncated_content
                
        except Exception as e:
            self.logger.error(f"端点骨架提取过程中发生异常: {str(e)}", exc_info=True)
            # 如果已经生成了总结内容，优先返回总结内容
            if 'final_summary' in locals() and final_summary and final_summary.strip():
                self.logger.info("虽然发生异常，但已生成总结内容，返回总结结果")
                return final_summary
            # 如果没有总结内容，尝试返回截断的原始内容
            try:
                if 'skeleton_chunks' in locals() and skeleton_chunks:
                    combined_skeletons = "\n".join(skeleton_chunks)
                    suffix = "...[处理异常已截断]"
                    max_content_length = self.MAX_LLM_INPUT_LENGTH - len(suffix)
                    truncated_content = combined_skeletons[:max_content_length] + suffix
                    return truncated_content
                else:
                    return None
            except:
                return None
    
    def _save_abstract_to_file(self, abstract_content: str, context: GenerationContext) -> None:
        """
        将项目摘要信息保存到 __abstract__.md 文件
        
        Args:
            abstract_content: 项目摘要内容
            context: 生成上下文，包含输出路径信息
            
        Raises:
            Exception: 当文件保存失败时抛出异常
        """
        # 获取输出路径
        # 构建摘要文件路径
        abstract_file_path_name = "__abstract__.md"
        
        self._set_file_cache(context, abstract_file_path_name, abstract_content)
        
    def _load_cached_abstract(self, context: GenerationContext) -> Optional[str]:
            """
            从缓存文件中加载项目摘要内容
            
            Args:
                context: 生成上下文，包含输出路径信息
                
            Returns:
                Optional[str]: 如果缓存文件存在则返回内容，否则返回None
            """
            abstract_file_path = "__abstract__.md"
            return self._load_file_cache(context, abstract_file_path)

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
        # 验证并查找文档项
        document_item = find_document_item_in_catalogue(document_path, catalogue_data)
        
        # 初始化LLM和解析器
        llm = self._init_llm_with_defaults(context.llm_options)
        output_parser = DocumentOutputParser()
        
        # 加载prompt模板（指定prompt模式）
        prompt_template = self._load_prompt_with_strategy_mode('GenerateDocs', context.project_type, "prompt", context.prompt_version)
        prompt = ChatPromptTemplate.from_template(prompt_template)
        
        # 准备RAG上下文信息（prompt策略特有）
        context_info = ""
        if document_item.get("name") and context.rag_service:
            try:
                rag_results = context.rag_service.similarity_search(
                    document_item["prompt"], 
                    k=20
                )
                related_docs = [
                    f"文件: {doc['filename']}\n路径: {doc['source']}\n内容:\n{doc['content'][:500]}..."
                    for doc in rag_results
                ]
                context_info = "\n\n".join(related_docs) if related_docs else "未找到相关文档"
            except Exception as e:
                self.logger.warning(f"RAG检索失败，项目名称='{document_item.get('name', 'unknown')}', 查询='{document_item.get('prompt', 'unknown')}': {e}")
                context_info = "未找到相关文档"
        
        # 使用基类的统一变量构建方法
        chain_input = self._build_document_variables(context, catalogue_data, document_item)
        
        # 添加prompt策略特有的context_info
        chain_input["context_info"] = context_info
        
        # 生成文档内容
        formatted_prompt = prompt.format(**chain_input)
        llm_response = llm.invoke(formatted_prompt)
        content = output_parser.parse(llm_response.content)
        
        return content
    
