"""
Default component implementations for agent chat services

This module provides default implementations of the protocols defined in protocols.py.
"""

import logging
from typing import Dict, Any, List, Iterator

from langchain.agents import AgentExecutor

from .protocols import MetadataProvider, StreamProcessor, MessageHandler
from .models import ChatMessage, ConversationContext, StreamChunk, MessageRole
from .conversion import ConversationManager
from kengine.rag.interface import DocumentInfo

logger = logging.getLogger(__name__)


class DefaultMetadataProvider(MetadataProvider):
    """
    Default implementation of metadata provider.
    
    This class provides a basic implementation of the MetadataProvider protocol,
    generating standard metadata for all stages of the agent chat workflow.
    It serves as a fallback implementation when no custom metadata provider
    is specified.
    
    The default implementation provides minimal but functional metadata
    that works for most agent types without customization.
    """
    
    def get_conversation_start_metadata(self, context: ConversationContext) -> Dict[str, Any]:
        """
        Get conversation start metadata.
        
        Args:
            context: Conversation context containing conversation information.
        
        Returns:
            Dict containing basic conversation start metadata.
        """
        return {
            "conversation_id": context.conversation_id,
            "repo_name": context.repo_name,
            "status": "starting"
        }
    
    def get_documents_metadata(self, relevant_docs: List[DocumentInfo]) -> Dict[str, Any]:
        """
        Get documents metadata.
        
        Args:
            relevant_docs: List of relevant documents retrieved from RAG.
        
        Returns:
            Dict containing basic document metadata.
        """
        return {
            "documents_retrieved": len(relevant_docs),
            "status": "documents_ready"
        }
    
    def get_agent_status_metadata(self, context: ConversationContext, agent_executor: AgentExecutor) -> Dict[str, Any]:
        """
        Get agent status metadata.
        
        Args:
            context: Conversation context containing conversation information.
            agent_executor: Agent executor instance with available tools.
        
        Returns:
            Dict containing basic agent status metadata.
        """
        return {"status": "agent_ready"}


class DefaultStreamProcessor(StreamProcessor):
    """
    Default implementation of stream processor.
    
    This class provides a basic implementation of the StreamProcessor protocol,
    handling the standard flow of agent execution responses. It processes
    agent actions and outputs, yielding appropriate stream chunks for
    real-time response delivery.
    
    The default implementation handles common agent execution patterns
    and serves as a fallback when no custom stream processor is specified.
    """
    
    def process_agent_stream(self, agent_executor: AgentExecutor, agent_input: Dict[str, Any]) -> Iterator[StreamChunk]:
        """
        Default agent stream processing.
        
        This method processes the agent execution stream, handling both actions
        (tool calls) and outputs (responses). It yields appropriate stream chunks
        for real-time delivery to clients.
        
        Args:
            agent_executor: Agent executor instance to run.
            agent_input: Input data for the agent.
        
        Yields:
            StreamChunk: Stream chunks for real-time response delivery.
        """
        for step in agent_executor.stream(agent_input):

            logger.info(f"step: {step}")
            
            # Handle actions (tool calls)
            if isinstance(step, dict) and 'actions' in step and step['actions']:
                for action in step['actions']:
                    if hasattr(action, 'tool') and hasattr(action, 'tool_input'):
                        yield StreamChunk(
                            type="thinking", 
                            data=f"🔧工具调用: {action.tool}, 参数: {action.tool_input}"
                        )
            
            # Handle output (responses)
            if isinstance(step, dict) and 'output' in step and step['output']:
                response = step['output']
                yield StreamChunk(type="content", data=response)


class DefaultMessageHandler(MessageHandler):
    """
    Default implementation of message handler.
    
    This class provides a basic implementation of the MessageHandler protocol,
    handling the standard flow of adding user and assistant messages to
    conversation history. It serves as a fallback implementation when no
    custom message handler is specified.
    
    The default implementation provides straightforward message handling
    that works for most agent types without customization.
    """
    
    def __init__(self, conversation_manager: ConversationManager):
        """
        Initialize the default message handler.
        
        Args:
            conversation_manager: Conversation manager instance for message storage.
        """
        self.conversation_manager = conversation_manager
    
    def add_user_message(self, context: ConversationContext, message: str) -> None:
        """
        Add user message to conversation.
        
        Args:
            context: Conversation context containing conversation information.
            message: User message content to add.
        """
        user_message = ChatMessage(role=MessageRole.USER, content=message)
        self.conversation_manager.add_message(context.conversation_id, user_message)
    
    def add_assistant_message(self, context: ConversationContext, message: str) -> None:
        """
        Add assistant message to conversation.
        
        Args:
            context: Conversation context containing conversation information.
            message: Assistant message content to add.
        """
        assistant_message = ChatMessage(role=MessageRole.ASSISTANT, content=message)
        self.conversation_manager.add_message(context.conversation_id, assistant_message)
