"""
Refactored Base Agent Chat Service

This module provides the base functionality for agent-based chat services with improved
abstraction and extensibility using strategy pattern and template method pattern.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Iterator

from langchain.tools import Tool
from langchain.agents import AgentExecutor
from langchain_core.callbacks import BaseCallbackHandler

from kengine.agent.shared.callbacks import ReactAgentLoggingHandler
from kengine.rag.interface import DocumentInfo

from ..rag import RAGService, build_rag_service
from ..config.application_config import get_application_config
from ..tasks.llm import init_llm
from ..utils.prompt_loader import load_custom_prompt
from ..utils.git_utils import source_to_git_repo_url

from .models import (
    MessageRole, ConversationContext, 
    ChatRequest, StreamChunk
)
from .conversion import ConversationManager
from .protocols import MetadataProvider, StreamProcessor, MessageHandler
from .components import DefaultMetadataProvider, DefaultStreamProcessor, DefaultMessageHandler

from ..agent.shared import (
    AgentToolFactory,
    create_agent_executor
)

logger = logging.getLogger(__name__)


class BaseAgentChatService(ABC):
    """
    Refactored base agent chat service with better separation of concerns.
    
    This abstract base class provides a foundation for agent-based chat services
    using modern design patterns including strategy pattern, template method pattern,
    and dependency injection. It separates infrastructure management from business logic
    and provides multiple extension points for customization.
    
    Key Features:
        1. Infrastructure Management: RAG services, agent tools, executors
        2. Pluggable Components: Metadata providers, stream processors, message handlers
        3. Template Method Pattern: Defines chat flow algorithm with customizable hooks
        4. Dependency Injection: Supports custom component injection with defaults
    
    Design Patterns:
        - Strategy Pattern: Pluggable components via Protocol interfaces
        - Template Method Pattern: Chat flow with customizable hook methods
        - Dependency Injection: Component injection with default implementations
        - Abstract Base Class: Enforces interface implementation
    
    Subclasses must implement:
        - _build_agent_input(): Build agent input from request and context
    
    Subclasses can override:
        - _prepare_agent(): Customize agent preparation phase
        - _execute_agent_with_stream(): Customize agent execution
        - _finalize_chat(): Customize chat finalization
    """
    
    def __init__(self, 
                 conversation_manager: Optional[ConversationManager] = None, 
                 verbose: bool = True,
                 agent_prompt_name: str = 'ChatAgent',
                 metadata_provider: Optional[MetadataProvider] = None,
                 stream_processor: Optional[StreamProcessor] = None,
                 message_handler: Optional[MessageHandler] = None):
        """
        Initialize the base agent chat service.
        
        Args:
            conversation_manager: Optional conversation manager instance.
                If None, creates a new ConversationManager.
            verbose: Enable verbose logging mode.
            agent_prompt_name: Name of the agent prompt template to use.
            metadata_provider: Custom metadata provider implementation.
                If None, uses DefaultMetadataProvider.
            stream_processor: Custom stream processor implementation.
                If None, uses DefaultStreamProcessor.
            message_handler: Custom message handler implementation.
                If None, uses DefaultMessageHandler.
        
        Note:
            This constructor demonstrates dependency injection pattern,
            allowing custom components to be injected while providing
            sensible defaults for all optional components.
        """
        # Infrastructure components
        self.app_config = get_application_config()
        self.conversation_manager = conversation_manager or ConversationManager()
        self.rag_services: Dict[str, RAGService] = {}
        self.agent_executors: Dict[str, AgentExecutor] = {}
        self.verbose = verbose
        self.agent_prompt_name = agent_prompt_name
        self.agent_callbacks: List[BaseCallbackHandler] = []
        
        # Pluggable components with dependency injection
        self.metadata_provider = metadata_provider or DefaultMetadataProvider()
        self.stream_processor = stream_processor or DefaultStreamProcessor()
        self.message_handler = message_handler or DefaultMessageHandler(self.conversation_manager)
        
        logger.info(f"BaseAgentChatService initialized with prompt: {agent_prompt_name}")
    
    def _get_or_create_rag_service(self, repo_path: str) -> RAGService:
        """Get or create RAG service for the repository"""
        if repo_path not in self.rag_services:
            group_name, repo_name = repo_path.strip().split('/')
            self.rag_services[repo_path] = build_rag_service(group_name, repo_name)
        return self.rag_services[repo_path]
    
    def _get_project_path(self, repo_name: str) -> str:
        """Get the project path for the repository"""
        # Extract group and repo from repo_name (format: group/repo)
        group_name, repo_name_only = repo_name.strip().split('/')
        
        # Construct the project path based on the RAG service structure
        # This should match the path used in RAG service (.cloned-repo/{group_name}/{repo_name})
        project_path = f".cloned-repo/{group_name}/{repo_name_only}"
        return project_path
    
    def _check_repository_availability(self, repo_name: str) -> Dict[str, Any]:
        """Check if the repository is available for agent tools"""
        project_path = self._get_project_path(repo_name)
        import os
        
        result = {
            "available": False,
            "project_path": project_path,
            "exists": False,
            "message": ""
        }
        
        if os.path.exists(project_path):
            result["exists"] = True
            result["available"] = True
            result["message"] = f"Repository available at: {project_path}"
        else:
            result["message"] = f"Repository not cloned. Expected path: {project_path}"
            logger.warning(f"Repository not available for local file access: {project_path}")
        
        return result
    
    def _create_agent_tools(self, repo_name: str, rag_service: RAGService) -> List[Tool]:
        """Create agent tools for the conversation"""
        project_path = self._get_project_path(repo_name)
        
        # Check if the project directory exists
        import os
        if not os.path.exists(project_path):
            logger.warning(f"Project directory does not exist: {project_path}")
            # Create tools without local file access when directory doesn't exist
            tools = AgentToolFactory.create_tools(
                base_dir=".",  # Use current directory as fallback
                rag_service=rag_service
            )
        else:
            # Create tools using the existing AgentToolFactory
            tools = AgentToolFactory.create_tools(
                base_dir=project_path,
                rag_service=rag_service
            )
        
        logger.info(f"Created {len(tools)} tools for repository: {repo_name}")
        return tools
    
    def _create_agent_executor(self, 
                              tools: List[Tool], 
                              conversation_id: str,
                              repo_name: str) -> AgentExecutor:
        """Create an agent executor for the conversation"""
        
        logger.info(f"Creating agent executor for conversation: {conversation_id}")
        
        # Load agent chat prompt template using configurable prompt name
        prompt_template = load_custom_prompt('agent', self.agent_prompt_name)
        
        # Get LLM configuration
        chat_config = self.app_config.get('chat', {}).get('model_options', {})
        default_config = self.app_config.get_default_model_config()
        
        # 合并配置，确保streaming参数正确设置
        model_config = {**default_config, **chat_config}
        
        # 对于Agent执行，建议使用streaming=False以获得更好的稳定性
        # 因为Agent需要完整的响应来进行工具调用决策
        model_config['streaming'] = False
        
        # 优化超时设置
        model_config['timeout'] = 200  # 减少超时时间到2分钟
        
        logger.info(f"LLM配置: model={model_config.get('model')}, streaming={model_config.get('streaming')}, timeout={model_config.get('timeout')}")
        
        # 初始化LLM
        llm_instance = init_llm(model_config)
        
      
        
        # Create agent executor with merged callback
        executor = create_agent_executor(
            tools=tools,
            llm_instance=llm_instance,
            prompt_template=prompt_template,
            max_iterations=20,  # 合理的迭代次数限制
            session_name=f"ChatAgent_{conversation_id}",
            logger=logger,
            callbacks=self.agent_callbacks  # Add merged callback
        )

        # Set verbose mode if enabled
        if self.verbose:
            executor.verbose = True
        
        logger.info(f"Agent executor created successfully for conversation: {conversation_id}")
        return executor
    
    def _build_agent_input(self, 
                          request: ChatRequest, 
                          context: ConversationContext,
                          relevant_docs: List[DocumentInfo]) -> Dict[str, Any]:
        """Build input for the agent"""
        
        # Format conversation history
        recent_messages = context.get_recent_messages(request.context_limit)
        conversation_history = []
        for msg in recent_messages:
            if msg.role != MessageRole.THINKING:
                role_name = {"user": "用户", "assistant": "助手", "system": "系统"}.get(msg.role.value, msg.role.value)
                conversation_history.append(f"{role_name}: {msg.content}")
        
        # Format relevant documents
        formatted_docs = []
        for i, doc in enumerate(relevant_docs, 1):
            file_path = doc.source
            file_name = doc.filename
            formatted_docs.append(
                f"文档 {i} (filePath: {file_path}, fileName: {file_name}):\n{doc.content}"
            )
        
        
        # Build agent input
        project_path = self._get_project_path(context.repo_name)
        agent_input = {
            "human_input": request.message,  # Required by agent executor memory
            "chat_history": "\n".join(conversation_history) if conversation_history else "无对话历史",  # Required by agent executor memory
            "user_message": request.message,
            "conversation_history": "\n".join(conversation_history) if conversation_history else "无对话历史",
            "relevant_documents": "\n\n".join(formatted_docs) if formatted_docs else "无相关文档",
            "repository_name": context.repo_name,
            "project_path": project_path,
            "working_directory": project_path,  # 明确指定工作目录
            "path_instruction": f"所有文件操作都基于项目路径 '{project_path}'，请使用相对路径（如 'src/main.py'）而不是绝对路径"
        }

        return agent_input
    
    
    
    def _get_conversation_context(self, request: ChatRequest) -> ConversationContext:
        """Get or create conversation context"""
        if request.conversation_id:
            context = self.conversation_manager.get_conversation(request.conversation_id)
            if not context:
                raise ValueError(f"对话不存在: {request.conversation_id}")
        else:
            if not request.repo_name:
                raise ValueError("新对话必须指定仓库名称")
            conversation_id = self.conversation_manager.create_conversation(request.repo_name)
            context = self.conversation_manager.get_conversation(conversation_id)
            logger.info(f"Created new conversation: {conversation_id}")
        
        return context
    
    def _get_relevant_documents(self, request: ChatRequest, context: ConversationContext) -> List[DocumentInfo]:
        """Get relevant documents from RAG service"""
        rag_service = self._get_or_create_rag_service(context.repo_name)
        relevant_docs = rag_service.similarity_search(request.message)
        logger.debug(f"Retrieved {len(relevant_docs)} relevant documents from RAG")
        
        return relevant_docs
    
    def _ensure_agent_executor(self, context: ConversationContext, rag_service: RAGService) -> AgentExecutor:
        """Ensure agent executor exists for the conversation"""
        if context.conversation_id not in self.agent_executors:
            tools = self._create_agent_tools(context.repo_name, rag_service)
            self.agent_executors[context.conversation_id] = self._create_agent_executor(
                tools, context.conversation_id, context.repo_name
            )
            logger.info(f"New agent executor created for conversation: {context.conversation_id}")
        
        return self.agent_executors[context.conversation_id]
    
    
    def _stream_response_chunks(self, response: str) -> Iterator[StreamChunk]:
        """Stream response in chunks for better UX"""
        # Send thinking/processing indicator
        yield StreamChunk(type="thinking", data="正在生成回答...")
        
        # Stream the final response in smaller chunks
        chunk_size = 50  # characters per chunk
        for i in range(0, len(response), chunk_size):
            chunk = response[i:i + chunk_size]
            yield StreamChunk(type="content", data=chunk)

        yield StreamChunk(type="thinking", data="回答完成")
    
    def _stream_sources(self, relevant_docs: List[DocumentInfo]) -> Iterator[StreamChunk]:
        """Stream source documents"""
        if relevant_docs:
            source_docs = [
                {
                    "source": source_to_git_repo_url(doc.source),
                    "filename": doc.filename,
                }
                for doc in relevant_docs
            ]
            yield StreamChunk(
                type="sources", 
                data=json.dumps(source_docs, ensure_ascii=False)
            )
    
    def stream_chat(self, request: ChatRequest) -> Iterator[StreamChunk]:
        """
        Template method for chat flow - defines the algorithm structure.
        
        This method implements the Template Method pattern, defining a fixed algorithm
        structure while allowing subclasses to customize specific steps through hook methods.
        The flow follows a clear sequence of operations for processing chat requests.
        
        Algorithm Steps:
            1. Initialize conversation context
            2. Retrieve relevant documents
            3. Add user message to history
            4. Check repository availability and prepare agent
            5. Customizable agent preparation (hook method)
            6. Build agent input
            7. Execute agent with customizable processing
            8. Stream source documents
            9. Add assistant message to history
            10. Customizable finalization (hook method)
        
        Args:
            request: Chat request containing user message and context.
        
        Yields:
            StreamChunk: Stream chunks for real-time response delivery.
        
        Raises:
            Exception: Any exception during processing is caught and yielded as error chunk.
        
        Note:
            This method demonstrates the Template Method pattern, where the algorithm
            structure is fixed but specific steps can be customized by subclasses.
        """
        logger.info(f"Starting agent chat stream for request: {request.message[:50]}{'...' if len(request.message) > 50 else ''}")
        
        try:
            # Step 1: Initialize conversation
            context = self._get_conversation_context(request)
            yield from self._stream_metadata(self.metadata_provider.get_conversation_start_metadata(context))
            
            # Step 2: Get relevant documents
            relevant_docs = self._get_relevant_documents(request, context)
            yield from self._stream_metadata(self.metadata_provider.get_documents_metadata(relevant_docs))
            
            # Step 3: Add user message
            self.message_handler.add_user_message(context, request.message)
            
            # Step 4: Check repository and prepare agent
            repo_status = self._check_repository_availability(context.repo_name)
            rag_service = self._get_or_create_rag_service(context.repo_name)
            agent_executor = self._ensure_agent_executor(context, rag_service)
            
            # Step 5: Customizable agent preparation (hook method)
            yield from self._prepare_agent(context, agent_executor, repo_status)
            
            # Step 6: Build agent input
            agent_input = self.build_agent_input(request, context, relevant_docs)
            
            # Step 7: Execute agent with customizable processing
            full_response = ""
            for chunk in self._execute_agent_with_stream(agent_executor, agent_input):
                yield chunk
                if chunk.type == "content":
                    full_response += chunk.data
            
            # Step 8: Stream sources
            yield from self._stream_sources(relevant_docs)
            
            # Step 9: Add assistant message
            self.message_handler.add_assistant_message(context, full_response)
            
            # Step 10: Finalize (hook method)
            yield from self._finalize_chat(context, relevant_docs, full_response)
            
        except Exception as e:
            logger.error(f"Agent chat failed: {e}", exc_info=True)
            yield StreamChunk(type="error", data=f"错误: {str(e)}")
    
    def _prepare_agent(self, context: ConversationContext, agent_executor: AgentExecutor, repo_status: Dict[str, Any]) -> Iterator[StreamChunk]:
        """
        Hook method for agent preparation - can be overridden by subclasses.
        
        This hook method allows subclasses to customize the agent preparation phase.
        The default implementation streams agent status metadata.
        
        Args:
            context: Conversation context containing conversation information.
            agent_executor: Agent executor instance ready for execution.
            repo_status: Repository availability status information.
        
        Yields:
            StreamChunk: Metadata chunks for agent preparation phase.
        
        Note:
            This is a hook method in the Template Method pattern, allowing
            subclasses to customize agent preparation without changing the
            overall algorithm structure.
        """
        yield from self._stream_metadata(self.metadata_provider.get_agent_status_metadata(context, agent_executor))
    
    def _execute_agent_with_stream(self, agent_executor: AgentExecutor, agent_input: Dict[str, Any]) -> Iterator[StreamChunk]:
        """
        Hook method for agent execution - can be overridden by subclasses.
        
        This hook method delegates agent execution to the configured stream processor.
        Subclasses can override this to provide custom execution logic.
        
        Args:
            agent_executor: Agent executor instance to run.
            agent_input: Input data for the agent.
        
        Yields:
            StreamChunk: Stream chunks from agent execution.
        
        Note:
            This hook method demonstrates the Strategy pattern, where different
            stream processors can be injected to provide different execution behaviors.
        """
        return self.stream_processor.process_agent_stream(agent_executor, agent_input)
    
    def _finalize_chat(self, context: ConversationContext, relevant_docs: List[DocumentInfo], full_response: str) -> Iterator[StreamChunk]:
        """
        Hook method for chat finalization - can be overridden by subclasses.
        
        This hook method allows subclasses to customize the chat finalization phase.
        The default implementation yields an end chunk with comprehensive metadata.
        
        Args:
            context: Conversation context containing conversation information.
            relevant_docs: List of relevant documents used in the conversation.
            full_response: Complete response from the agent.
        
        Yields:
            StreamChunk: Final chunks for chat completion.
        
        Note:
            This hook method allows subclasses to add custom finalization logic,
            such as additional metadata, cleanup operations, or custom end markers.
        """
        yield StreamChunk(
            type="end", 
            data="",
            metadata={
                "conversation_id": context.conversation_id,
                "num_sources": len(relevant_docs),
                "agent_mode": True,
                "response_length": len(full_response),
                "tools_used": self.get_tool_usage_data(context.conversation_id),
                "status": "completed"
            }
        )
    
    def build_agent_input(self, request: ChatRequest, context: ConversationContext, relevant_docs: List[DocumentInfo]) -> Dict[str, Any]:
        """
        Build input for the agent - must be implemented by subclasses.
        
        This abstract method enforces that all subclasses must implement their own
        agent input building logic. This allows each agent type to customize how
        it processes and formats input data for the underlying LLM.
        
        Args:
            request: Chat request containing user message and context.
            context: Conversation context with history and metadata.
            relevant_docs: List of relevant documents retrieved from RAG.
        
        Returns:
            Dict[str, Any]: Formatted input dictionary for the agent executor.
        
        Note:
            This method is abstract to ensure that each agent type implements
            its own input processing logic, which is essential for different
            agent behaviors and capabilities.
        """
        return self._build_agent_input(request, context, relevant_docs)
    
    def _stream_metadata(self, metadata: Dict[str, Any]) -> Iterator[StreamChunk]:
        """
        Stream metadata chunk.
        
        Utility method to convert metadata dictionary to stream chunk format.
        
        Args:
            metadata: Dictionary containing metadata information.
        
        Yields:
            StreamChunk: Metadata chunk in stream format.
        """
        yield StreamChunk(type="metadata", data=json.dumps(metadata))
    
    def get_conversation_history(self, conversation_id: str) -> Optional[ConversationContext]:
        """Get conversation history"""
        return self.conversation_manager.get_conversation(conversation_id)
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """Clear conversation history and remove agent executor"""
        context = self.conversation_manager.get_conversation(conversation_id)
        if context:
            context.clear_history()
            self.conversation_manager._save_conversation(context)
            
            # Remove agent executor for this conversation
            if conversation_id in self.agent_executors:
                del self.agent_executors[conversation_id]
            
            return True
        return False
    
    def get_available_tools(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get available tools for a conversation"""
        if conversation_id not in self.agent_executors:
            return []
        
        executor = self.agent_executors[conversation_id]
        tools = []
        
        for tool in executor.tools:
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "type": type(tool).__name__
            })
        
        return tools
    
    def get_repository_status(self, repo_name: str) -> Dict[str, Any]:
        """Get repository status and availability information"""
        return self._check_repository_availability(repo_name)

    def get_tool_usage_data(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get tool usage data for a conversation"""
        for callback in self.agent_callbacks:
            if isinstance(callback, ReactAgentLoggingHandler):
                return callback.get_tools_used()
        return None
    
  

