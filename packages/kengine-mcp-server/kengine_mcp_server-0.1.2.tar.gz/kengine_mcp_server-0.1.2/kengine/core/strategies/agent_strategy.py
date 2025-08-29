"""
基于Agent的文档生成策略 - 重构版本

使用Agent包中的工具和组件，实现清晰的分层架构
支持动态配置参数，包括最大迭代次数、超时和重试机制
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from langchain.tools import Tool
from langchain.agents import AgentExecutor

from kengine.agent.shared.outputparser import EnhancedAgentOutputParser
from kengine.core.parsers import OverviewOutputParser, \
    DocumentOutputParser,  CatalogueOutputParser, \
        JsonOutputParser

from .base_strategy import DocumentGenerationStrategy, GenerationMode
from .strategy_utils import StrategyUtils
from ..types import GenerationContext, StepGenerationResult
from ..enums import GenerationStrategy
from ...agent.shared import (
    AgentToolFactory, 
    ReactAgentLoggingHandler,
    create_agent_executor,
    execute_agent_with_retry
)
from kengine.core.utils.catalogue_data_utils import find_document_item_in_catalogue, set_catalogue_saved_path


class AgentBasedStrategy(DocumentGenerationStrategy):
    """基于Agent的文档生成策略 - 使用Agent包实现，支持动态配置"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化策略，加载配置"""
        super().__init__(config)
        self._load_agent_config(config)
    
    def _load_agent_config(self, app_config) -> None:
        """加载Agent配置参数"""
        self.agent_config = app_config or {}
        
        # 设置默认值以防配置缺失
        self.overview_max_iterations = self.agent_config.get('overview_max_iterations', 25)
        self.catalog_max_iterations = self.agent_config.get('catalog_max_iterations', 30)
        self.catalog_verify_max_iterations = self.agent_config.get('catalog_verify_max_iterations', 30)
        self.document_max_iterations = self.agent_config.get('document_max_iterations', 20)
        self.max_retries = self.agent_config.get('max_retries', 3)
        self.timeout = self.agent_config.get('timeout', 600)
        self.tools_timeout = self.agent_config.get('tools_timeout', 60)
        self.max_verify_times = self.agent_config.get('max_verify_times', 3)
        
        self.logger.info(f"Agent配置加载成功: overview_max_iterations={self.overview_max_iterations}, "
                        f"catalog_max_iterations={self.catalog_max_iterations}, "
                        f"document_max_iterations={self.document_max_iterations}")
        
    
    def get_strategy_name(self) -> str:
        return "AgentBased"
    
    def _create_tools(self, base_dir: str, rag_service=None) -> List[Tool]:
        """创建Agent工具列表"""
        return AgentToolFactory.create_tools(base_dir, rag_service)
    
    def _create_agent_executor(self,
                               tools: List[Tool],
                               llm_instance,
                               prompt_template: str,
                              max_iterations: int,
                              session_name: str
                              ) -> AgentExecutor:
        """创建Agent执行器的通用方法 - 使用共享模块实现"""
        return create_agent_executor(
            tools=tools,
            llm_instance=llm_instance,
            prompt_template=prompt_template,
            max_iterations=max_iterations,
            session_name=session_name,
            logger=self.logger
        )
    
    def _execute_with_retry(self, 
                            executor_factory, 
                            outputParser,
                            input_data: Dict[str, Any],
                           operation_name: str) -> str:
        """带重试机制的Agent执行 - 使用共享模块实现
        
        Args:
            executor_factory: 创建AgentExecutor的方法，每次重试时会调用此方法创建新的executor
            outputParser: 输出解析器
            input_data: 输入数据
            operation_name: 操作名称，用于日志记录
        
        Returns:
            str: 执行结果
        """
        return execute_agent_with_retry(
            executor_factory=executor_factory,
            logger=self.logger,
            output_parser=outputParser,
            input_data=input_data,
            operation_name=operation_name,
            max_retries=self.max_retries
        )
    
    def _verify_catalog(self, catalog: str, tools, context: GenerationContext) -> Dict[str, Any]:
        """验证文档目录是否符合要求"""
        if not isinstance(catalog, str):
            raise ValueError("catalog参数必须是字符串类型")

        if isinstance(catalog, str) and not catalog.strip():
            return {"pass": False, "issues": ["目录内容不能为空"]}
        
        try:
            from ...utils.prompt_loader import load_prompt
            
            # 使用相同的提示词模板进行验证（可能包含验证逻辑）
            verify_prompt = load_prompt('VerifyCatalog', context.project_type, context.prompt_version, strategy_mode="agent")
            
            # 创建executor工厂方法
            def create_verify_executor():
                llm_instance = self._init_llm_with_defaults(context.llm_options)
                return self._create_agent_executor(
                    tools,
                    llm_instance,
                    verify_prompt,
                    self.catalog_verify_max_iterations,
                    "CatalogGeneration-Verify"
                )
            
            self.logger.info(f"开始验证目录，长度: {len(catalog)} 字符")
            # 使用基类统一变量管理构建验证输入
            input_vars = self._build_catalogue_variables(context)
            # 添加验证特有的变量
            input_vars.update({
                "catalog": catalog,
                "max_iterations": self.catalog_verify_max_iterations
            })
            output_parser = JsonOutputParser()
            verify_result = self._execute_with_retry(create_verify_executor, output_parser, input_vars, "目录验证")
            return verify_result
        except Exception as e:
            raise RuntimeError(f"验证失败: {catalog}") from e
        
    def _format_verification_issues(self, verdict: Dict[str, Any]) -> str:
        """格式化验证问题反馈，提供结构化的问题描述"""
        feedback_parts = []
        
        # 添加评分信息
        if verdict.get("score") is not None:
            feedback_parts.append(f"评分: {verdict['score']}/100")
        if verdict.get("grade"):
            feedback_parts.append(f"等级: {verdict['grade']}")
        
        # 添加总结
        if verdict.get("summary"):
            feedback_parts.append(f"总结: {verdict['summary']}")
        
        # 处理结构化问题列表
        issues = verdict.get("issues", [])
        if issues:
            if isinstance(issues[0], dict):
                # 新格式：结构化问题对象
                categorized_issues = {"A": [], "B": [], "C": []}
                for issue in issues:
                    category = issue.get("category", "C")
                    description = issue.get("description", "")
                    suggestion = issue.get("suggestion", "")
                    location = issue.get("location", "")
                    
                    issue_text = f"{description}"
                    if suggestion:
                        issue_text += f" (建议: {suggestion})"
                    if location:
                        issue_text += f" [位置: {location}]"
                    
                    categorized_issues[category].append(issue_text)
                
                # 按优先级组织问题
                for category, label in [("A", "严重问题"), ("B", "重要问题"), ("C", "一般问题")]:
                    if categorized_issues[category]:
                        feedback_parts.append(f"{label}: " + "; ".join(categorized_issues[category]))
            else:
                # 旧格式：简单字符串列表
                feedback_parts.append("问题: " + "; ".join(issues))
        
        # 添加详细评分
        if verdict.get("detailed_scores"):
            scores_text = ", ".join([f"{k}: {v}" for k, v in verdict["detailed_scores"].items()])
            feedback_parts.append(f"详细评分: {scores_text}")
        
        return " | ".join(feedback_parts) if feedback_parts else "验证未通过，但未提供具体问题信息"
    
    def generate_catalogue(self, context: GenerationContext) -> StepGenerationResult:
        """使用Agent生成文档目录结构，包含验证和自修复"""
        try:
            # 验证项目路径
            error = self._validate_project_path(context.project_path)
            if error:
                raise ValueError(error)
            
            project_path = Path(context.project_path)
            
            # 创建Agent执行器工厂方法
            prompt_template = self._load_prompt_with_strategy_mode('AnalyzeCatalog', context.project_type, "agent", context.prompt_version)
        
            # 创建工具和LLM实例
            tools = self._create_tools(str(project_path), context.rag_service)
            if context.rag_service:
                self.logger.info("RAG搜索工具已启用，Agent可以进行语义搜索")
            else:
                self.logger.info("RAG服务未可用，Agent将使用基础文件操作工具")
            def create_catalog_executor():
                llm_instance = self._init_llm_with_defaults(context.llm_options)
                return self._create_agent_executor(
                    tools,
                    llm_instance,
                    prompt_template,
                    self.catalog_max_iterations,
                    "CatalogGeneration"
                )
                        
            # 第一轮：让Agent生成目录 - 使用基类统一变量管理
            initial_input = self._build_catalogue_variables(
                context,
                previous_catalog='',
                previous_catalog_issues=''
            )
            # 添加agent策略特有的max_iterations
            initial_input["max_iterations"] = self.catalog_max_iterations
            output_parser = CatalogueOutputParser()
            first_catalog = self._execute_with_retry(create_catalog_executor, output_parser, initial_input, "目录生成")
            
            # 验证和自修复循环
            catalog = first_catalog
            if self.max_verify_times > 0:
                for r in range(self.max_verify_times):
                    str_catalog = json.dumps(catalog) if isinstance(catalog, dict) else catalog
                    verdict = self._verify_catalog(str_catalog, tools, context)
                    is_valid_verify_result = isinstance(verdict, dict) \
                        and "score" in verdict.keys() \
                        and "pass" in verdict.keys()
                        
                    if not is_valid_verify_result:
                        continue
                    
                    # 记录详细的验证结果
                    if isinstance(verdict, dict) and "score" in verdict and verdict.get("score"):
                        self.logger.info(f"目录验证得分: {verdict.get('score')}/100, 等级: {verdict.get('grade', '未知')}")
                    
                    if verdict.get("pass"):
                        if verdict.get("strengths"):
                            self.logger.info(f"目录优点: {', '.join(verdict.get('strengths', []))}")
                        break
                    
                    # 构建更详细的问题反馈
                    issues_feedback = self._format_verification_issues(verdict)
                    self.logger.warning(f"目录验证未通过(第{r+1}轮)，问题反馈: {issues_feedback}")
                    
                    # 使用基类统一变量管理
                    fix_input = self._build_catalogue_variables(
                        context,
                        previous_catalog=str_catalog,
                        previous_catalog_issues=issues_feedback
                    )
                    # 添加agent策略特有的max_iterations
                    fix_input["max_iterations"] = self.catalog_max_iterations
                    
                    catalog = self._execute_with_retry(create_catalog_executor, output_parser, fix_input, f"目录修复(第{r+1}轮)")
            self.logger.info(f"Agent文档目录结构生成完成 {catalog}")
            return StepGenerationResult(
                success=True,
                data=catalog,
                strategy_used=GenerationStrategy.AGENT
            )
            
        except Exception as e:
            self.logger.error(f"Agent catalogue generation failed, project_type='{context.project_type}', project_path='{context.project_path}': {e}", exc_info=True)
            return StepGenerationResult(
                success=False,
                error=str(e),
                strategy_used=GenerationStrategy.AGENT
            )
    
    def generate_documents(self,
                          catalogue_data: Dict[str, Any],
                          context: GenerationContext,
                          mode: GenerationMode = GenerationMode.SERIAL,
                          max_workers: Optional[int] = None) -> StepGenerationResult:
        """使用Agent生成文档内容，支持串行和并行模式"""
        try:
            # 调用基类的预处理逻辑
            self._on_generate_documents(catalogue_data, context)
            
            StrategyUtils.validate_catalogue_data(catalogue_data)
                        
            # 创建Agent工具和LLM实例
            project_path = Path(context.project_path)
            tools = self._create_tools(str(project_path), context.rag_service)
            # llm_instance = self._init_llm_with_defaults(context.llm_options)
            
            # 处理Git仓库URL
            git_repository_root_url = StrategyUtils.process_git_repository_url(context)
            
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
                # 递归处理所有文档项，使用Agent生成内容
                self._generate_documents(
                    catalogue_data["items"],
                    # relative root
                    '/',
                    stats,
                    tools,
                    context,
                    catalogue_data,
                    git_repository_root_url
                )
            
            self.logger.info(f"Agent文档生成完成，成功: {stats['successful_generations']}, 失败: {stats['failed_generations']}")
            return StepGenerationResult(
                success=True,
                data=stats,
                strategy_used=GenerationStrategy.AGENT
            )
            
        except Exception as e:
            self.logger.error(f"Agent document generation failed, project_type='{context.project_type}', project_path='{context.project_path}': {e}", exc_info=True)
            return StepGenerationResult(
                success=False,
                error=str(e),
                strategy_used=GenerationStrategy.AGENT
            )
    
    def _generate_documents(self, 
                                 items: List[Dict[str, Any]], 
                                 output_path: str, 
                                 stats: Dict[str, Any],
                                 tools: List[Tool],
                                 context: GenerationContext,
                                 catalogue_data: Dict[str, Any],
                                 git_repository_root_url: str) -> None:
        """使用Agent和工具递归处理文档项列表"""
        # 创建文档生成Agent工厂方法
        # 加载文档生成的prompt模板（使用agent模式）
        prompt_template = self._load_prompt_with_strategy_mode('GenerateDocs', context.project_type, "agent", context.prompt_version)
        
        def create_document_executor():
            llm_instance = self._init_llm_with_defaults(context.llm_options)
            return self._create_agent_executor(
                tools,
                llm_instance,
                prompt_template,
                self.document_max_iterations,
                "DocumentGeneration"
            )
        document_output_parser = DocumentOutputParser()
        for item in items:
            stats["total_items"] += 1
            
            try:
                # 使用基类统一变量管理构建Agent输入
                agent_input = self._build_document_variables(context, catalogue_data, item)
                
                # 添加agent策略特有的变量
                agent_input["max_iterations"] = self.document_max_iterations
                
                # 让Agent生成文档内容（带重试机制）
                content = self._execute_with_retry(
                    create_document_executor,
                    document_output_parser, 
                    agent_input, 
                    f"文档生成({item.get('name', 'unnamed')})")
                if content is None:
                    self.logger.warning(f"Agent生成文档失败，{context.repo_group}-{context.repo_name} 项目名称='{item.get('name', 'unnamed')}'")
                    continue
                
                # 清理文件名并保存
                catalog_path = child_output_path + '/' + f'{item['name']}'
                file_output_path = f'{catalog_path}.md'
                saved_path = self._save_content_to_file(context, content, file_output_path)
                # 生成文档后更新 catalogue_data, 根据当前任务的path: task['document_path'] 找到对应目录项， 添加 saved_path 属性
                set_catalogue_saved_path(catalog_path, catalogue_data, saved_path)
                # todo saved path
                stats["successful_generations"] += 1
                stats["generated_files"].append(str(saved_path))
                
            except Exception as e:
                self.logger.error(f"generate doc {item['name']} error ", exc_info=True)
                # Agent模式下不使用降级方案，继续处理下一个文档
            
            # 递归处理子项
            if "children" in item and isinstance(item["children"], list) and len(item["children"]) > 0:
                child_output_path = output_path + '/' + item.get('name', 'unnamed')
                
                try:
                    self._generate_documents(
                        item["children"], 
                        child_output_path, 
                        stats,
                        tools,
                        context,
                        catalogue_data,
                        git_repository_root_url
                    )
                    
                except Exception as e:
                    self.logger.error(f"递归处理子项失败，项目名称='{item.get('name', 'unnamed')}', 子项数量={len(item['children'])}: {e}")
                    # 如果处理失败，仍然尝试在当前目录处理子项
                    self._generate_documents(
                        item["children"], 
                        child_output_path, 
                        stats,
                        tools,
                        context,
                        catalogue_data,
                        git_repository_root_url
                    )
    
    def generate_overview(self, context: GenerationContext) -> StepGenerationResult:
        """使用Agent生成项目概览文档"""
        try:
            # 验证项目路径
            error = self._validate_project_path(context.project_path)
            if error:
                return StepGenerationResult(
                    success=False,
                    error=error,
                    strategy_used=GenerationStrategy.AGENT
                )
            
            project_path = Path(context.project_path)
            
            # 创建工具和LLM实例
            tools = self._create_tools(str(project_path), context.rag_service)
            if context.rag_service:
                self.logger.info("RAG搜索工具已启用，Agent可以进行语义搜索")
            else:
                self.logger.info("RAG服务未可用，Agent将使用基础文件操作工具")
            
            # 创建Agent执行器工厂方法
            prompt_template = self._load_prompt_with_strategy_mode('Overview', context.project_type, "agent", context.prompt_version)
            
            def create_overview_executor():
                llm_instance = self._init_llm_with_defaults(context.llm_options)
                return self._create_agent_executor(
                    tools,
                    llm_instance,
                    prompt_template,
                    self.overview_max_iterations,
                    "OverviewGeneration"
                )
            
            # 使用基类统一变量管理构建Agent输入
            agent_input = self._build_overview_variables(context)
            
            # 添加agent策略特有的变量
            agent_input["max_iterations"] = self.overview_max_iterations
            
            # 让Agent生成概览内容（带重试机制）
            try:
                output_parser = OverviewOutputParser()
                overview_content = self._execute_with_retry(create_overview_executor, output_parser, agent_input, "项目概览生成")
            except Exception as e:
                raise RuntimeError(f"Agent生成概览失败: {str(e)}") from e
            
            if overview_content is None:
                raise RuntimeError(f"生成概览为None {context.repo_group}-{context.repo_name}")
            # 保存文件到输出路径
            saved_path = self._save_content_to_file(context, overview_content,  "overview.md")
            # todo save saved path
            
            # 构建结果数据
            result_data = StrategyUtils.create_result_data(overview_content, saved_path, context)
            
            self.logger.info("Agent项目概览生成完成")
            return StepGenerationResult(
                success=True,
                data=result_data,
                strategy_used=GenerationStrategy.AGENT
            )
            
        except Exception as e:
            error_msg = f"Agent生成项目概览失败，项目类型='{context.project_type}', 项目路径='{context.project_path}': {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return StepGenerationResult(
                success=False,
                error=error_msg,
                strategy_used=GenerationStrategy.AGENT
            )
            
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
            生成的文档内容
        """
        # 使用基类的公共方法验证参数并查找文档项
        document_item = find_document_item_in_catalogue(document_path, catalogue_data)
        
        # 创建Agent工具
        project_path = Path(context.project_path)
        tools = self._create_tools(str(project_path), context.rag_service)
        
        # 加载文档生成的prompt模板
        prompt_template = self._load_prompt_with_strategy_mode('GenerateDocs', context.project_type, "agent", context.prompt_version)
        
        # 创建文档生成Agent工厂方法
        def create_document_executor():
            llm_instance = self._init_llm_with_defaults(context.llm_options)
            return self._create_agent_executor(
                tools,
                llm_instance,
                prompt_template,
                self.document_max_iterations,
                f"DocumentGeneration-{document_path}"
            )
        
        # 使用基类统一变量管理构建Agent输入
        agent_input = self._build_document_variables(context, catalogue_data, document_item)
        
        # 添加agent策略特有的变量
        agent_input["max_iterations"] = self.document_max_iterations
        
        # 让Agent生成文档内容（带重试机制）
        document_output_parser = DocumentOutputParser()
        content = self._execute_with_retry(
            create_document_executor,
            document_output_parser,
            agent_input,
            f"文档生成({document_item.get('name', 'unnamed')})"
        )
        
        return content
    