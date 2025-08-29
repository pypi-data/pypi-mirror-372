"""
Agent执行器工厂模块

提供Agent执行器的创建和带重试机制的执行功能，供其他模块共享使用。
支持两种执行器类型：
- single: 单Action模式，使用标准输出解析器
- multi: 多Action模式（默认），支持选择单Action或多Action解析器

默认使用多Action模式和多Action解析器。
"""

import logging
from typing import Dict, Any, List, Callable, Optional, Union

from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

from .outputparser import EnhancedAgentOutputParser
from .callbacks import ReactAgentLoggingHandler
from .multi_action_parser import EnhancedMultiActionOutputParser


class AgentExecutorFactory:
    """Agent执行器工厂类，提供创建和执行Agent的通用方法"""
    
    @staticmethod
    def create_agent_executor(
        tools: List[Tool],
        llm_instance,
        prompt_template: str,
        max_iterations: int,
        session_name: str,
        logger: Optional[logging.Logger] = None,
        # 执行器配置参数
        executor_type: str = "multi",
        callbacks: Optional[List] = None
    ) -> AgentExecutor:
        """创建Agent执行器的通用方法，默认使用多Action模式
        
        Args:
            tools: Agent工具列表
            llm_instance: LLM实例
            prompt_template: 提示模板字符串
            max_iterations: 最大迭代次数
            session_name: 会话名称，用于日志记录
            logger: 日志记录器，可选
            executor_type: 执行器类型，"single" 或 "multi"（默认）
            callbacks: 自定义回调处理器列表，可选
            
        Returns:
            AgentExecutor: 配置好的Agent执行器
            
        Raises:
            RuntimeError: Agent执行器创建失败时抛出
        """
        try:
            # 根据执行器类型创建相应的执行器
            if executor_type == "single":
                return AgentExecutorFactory._create_single_executor(
                    tools, llm_instance, prompt_template, max_iterations,
                    session_name, logger, callbacks
                )
            else:  # multi (默认)
                return AgentExecutorFactory._create_multi_executor(
                    tools, llm_instance, prompt_template, max_iterations,
                    session_name, logger, callbacks
                )
                
        except Exception as e:
            raise RuntimeError(f"Agent执行器创建失败: {str(e)}") from e
    
    @staticmethod
    def _create_single_executor(
        tools: List[Tool],
        llm_instance,
        prompt_template: str,
        max_iterations: int,
        session_name: str,
        logger: Optional[logging.Logger] = None,
        callbacks: Optional[List] = None
    ) -> AgentExecutor:
        """创建单Action的Agent执行器"""
        prompt = PromptTemplate.from_template(prompt_template)
        agent = create_react_agent(
            tools=tools,
            llm=llm_instance,
            output_parser=EnhancedAgentOutputParser(),
            prompt=prompt
        )
        
        # 准备回调处理器列表
        callback_list = []
        
        # 添加默认的React Agent日志回调处理器
        agent_callback = ReactAgentLoggingHandler(
            logger=logger,
            session_name=session_name
        )
        callback_list.append(agent_callback)
        
        # 添加自定义回调处理器
        if callbacks:
            callback_list.extend(callbacks)
        
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            input_key="human_input"
        )

        return AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            max_iterations=max_iterations,
            verbose=False,
            handle_parsing_errors=True,
            callbacks=callback_list
        )
    
    @staticmethod
    def _create_multi_executor(
        tools: List[Tool],
        llm_instance,
        prompt_template: str,
        max_iterations: int,
        session_name: str,
        logger: Optional[logging.Logger] = None,
        callbacks: Optional[List] = None
    ) -> AgentExecutor:
        """创建多Action的Agent执行器（默认模式）
        
        Args:
            tools: Agent工具列表
            llm_instance: LLM实例
            prompt_template: 提示模板字符串
            max_iterations: 最大迭代次数
            session_name: 会话名称，用于日志记录
            logger: 日志记录器，可选
            callbacks: 自定义回调处理器列表，可选
        """
        prompt = PromptTemplate.from_template(prompt_template)
        
        # 使用多Action输出解析器
        output_parser = EnhancedMultiActionOutputParser()
        if logger:
            logger.info("使用多Action输出解析器")
        
        agent = create_react_agent(
            tools=tools,
            llm=llm_instance,
            output_parser=output_parser,
            prompt=prompt
        )
        
        # 准备回调处理器列表
        callback_list = []
        
        # 添加默认的React Agent日志回调处理器
        agent_callback = ReactAgentLoggingHandler(
            logger=logger,
            session_name=session_name
        )
        callback_list.append(agent_callback)
        
        # 添加自定义回调处理器
        if callbacks:
            callback_list.extend(callbacks)
        
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            input_key="human_input"
        )

        if logger:
            logger.info("创建多Action执行器成功")

        return AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            max_iterations=max_iterations,
            verbose=False,
            handle_parsing_errors=True,
            callbacks=callback_list
        )


class AgentExecutorRunner:
    """Agent执行器运行器，提供带重试机制的执行功能"""
    
    def __init__(self, max_retries: int = 3, logger: Optional[logging.Logger] = None):
        """初始化执行器运行器
        
        Args:
            max_retries: 最大重试次数
            logger: 日志记录器，可选
        """
        self.max_retries = max_retries
        self.logger = logger or logging.getLogger(__name__)
    
    def execute_with_retry(self, 
                          executor_factory: Callable[[], AgentExecutor], 
                          output_parser,
                          input_data: Dict[str, Any],
                          operation_name: str) -> str:
        """带重试机制的Agent执行
        
        Args:
            executor_factory: 创建AgentExecutor的方法，每次重试时会调用此方法创建新的executor
            output_parser: 输出解析器
            input_data: 输入数据
            operation_name: 操作名称，用于日志记录
        
        Returns:
            str: 执行结果
            
        Raises:
            RuntimeError: 在最大重试次数后仍然失败时抛出
        """
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                self.logger.info(f"执行{operation_name}，尝试次数: {attempt + 1}/{self.max_retries + 1}")
                
                # 每次重试时创建新的AgentExecutor
                executor = executor_factory()
                
                # 确保输入数据包含必要的键
                if 'human_input' not in input_data.keys():
                    input_data['human_input'] = ''
                
                # 执行Agent
                agent_output = executor.invoke(input_data)
                agent_output = agent_output.get('output', None) if isinstance(agent_output, dict) and 'output' in agent_output.keys() else agent_output
                
                # 解析输出
                result = output_parser.invoke(agent_output)
                if not result:
                    raise ValueError(f"{operation_name}生成的内容为空")
                
                return result
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"{operation_name}第{attempt + 1}次尝试失败: {e}", exc_info=True)
                
                if attempt < self.max_retries:
                    self.logger.info(f"将进行第{attempt + 2}次重试...")
                    continue
                else:
                    break
        
        raise RuntimeError(f"{operation_name}在{self.max_retries + 1}次尝试后仍然失败，最后错误: {last_error}")


# 便利函数，提供简化的接口
def create_agent_executor(
    tools: List[Tool],
    llm_instance,
    prompt_template: str,
    max_iterations: int,
    session_name: str,
    logger: logging.Logger,
    # 执行器配置参数
    executor_type: str = "multi",
    callbacks: Optional[List] = None
) -> AgentExecutor:
    """创建Agent执行器的便利函数，默认使用多Action模式
    
    这是AgentExecutorFactory.create_agent_executor的简化接口
    
    Args:
        tools: Agent工具列表
        llm_instance: LLM实例
        prompt_template: 提示模板字符串
        max_iterations: 最大迭代次数
        session_name: 会话名称，用于日志记录
        logger: 日志记录器，可选
        executor_type: 执行器类型，"single" 或 "multi"（默认）
        callbacks: 自定义回调处理器列表，可选
        
    Returns:
        AgentExecutor: 配置好的Agent执行器
    """
    return AgentExecutorFactory.create_agent_executor(
        tools=tools,
        llm_instance=llm_instance,
        prompt_template=prompt_template,
        max_iterations=max_iterations,
        session_name=session_name,
        logger=logger,
        executor_type=executor_type,
        callbacks=callbacks
    )


def execute_agent_with_retry(
    executor_factory: Callable[[], AgentExecutor], 
    logger: logging.Logger,
    output_parser=None,
    input_data: Dict[str, Any] = None,
    operation_name: str = "Agent执行",
    max_retries: int = 3
) -> Union[str, Dict[str, Any]]:
    """带重试机制执行Agent的便利函数
    
    Args:
        executor_factory: 创建执行器的工厂函数
        output_parser: 输出解析器
        input_data: 输入数据
        operation_name: 操作名称，用于日志记录
        max_retries: 最大重试次数
        logger: 日志记录器
        
    Returns:
        Union[str, Dict[str, Any]]: 执行结果
    """
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            logger.info(f"执行{operation_name}，尝试次数: {attempt + 1}/{max_retries + 1}")
            
            # 每次重试时创建新的执行器
            executor = executor_factory()
            
            # 确保输入数据包含必要的键
            if input_data and 'human_input' not in input_data.keys():
                input_data['human_input'] = ''
            
            # 执行Agent
            result = executor.invoke(input_data or {})
            
            if not result or not result.get('output'):
                raise RuntimeError(f"{operation_name}生成的内容为空")
            
            # 如果提供了output_parser，使用它解析结果
            if output_parser and result and result.get('output'):
                try:
                    parsed_result = output_parser.parse(result['output'])
                    # 更新result中的output
                    result['output'] = parsed_result
                except Exception as e:
                    logger.warning(f"输出解析失败: {e}")
                    # 解析失败时保持原始输出
            
            return result['output']
                
        except Exception as e:
            last_error = e
            logger.warning(f"{operation_name}第{attempt + 1}次尝试失败: {e}", exc_info=True)
            
            if attempt < max_retries:
                logger.info(f"将进行第{attempt + 2}次重试...")
                continue
            else:
                break
    
    raise RuntimeError(f"{operation_name}在{max_retries + 1}次尝试后仍然失败，最后错误: {last_error}")
