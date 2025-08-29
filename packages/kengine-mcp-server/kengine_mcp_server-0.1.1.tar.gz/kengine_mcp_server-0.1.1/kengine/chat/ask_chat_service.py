"""
Refactored Ask Chat Service

This module provides an agent-based chat service using the improved base class
with better abstraction and extensibility.
"""

import logging
from typing import Iterator, Dict, Any, List

from kengine.rag.interface import DocumentInfo

from .base_agent_chat_service import BaseAgentChatService
from .models import StreamChunk, ConversationContext
from langchain.agents import AgentExecutor

logger = logging.getLogger(__name__)


class AskChatService(BaseAgentChatService):
    """
    Refactored AskChat service using the improved base class.

    This service provides a chat interface for the AskChat agent, including:
    1. Custom metadata provider
    2. Custom stream processor
    3. Custom agent preparation
    4. Custom chat finalization
    """
    
    def __init__(self, **kwargs):
        """
        Initialize AskChat service with custom components.
        
        This constructor creates custom metadata provider and stream processor
        instances specific to the AskChat service, then initializes the base
        class with these components using dependency injection.
        
        Args:
            **kwargs: Additional keyword arguments passed to the base class.
        
        Note:
            This demonstrates the Strategy pattern where different components
            are injected to provide specific behaviors for the AskChat service.
        """
        # Initialize base class with custom components via dependency injection
        super().__init__(
            agent_prompt_name='AskChatPrompt',
            **kwargs
        )
        
        logger.info("AskChatService initialized with custom components")
    
    
    def _prepare_agent(self, context: ConversationContext, agent_executor: AgentExecutor, repo_status: Dict[str, Any]) -> Iterator[StreamChunk]:
        """
        Custom agent preparation for AskChat service.
        
        This method customizes the agent preparation phase by adding repository
        status metadata before the standard agent status metadata. This provides
        additional context about the repository availability to the client.
        
        Args:
            context: Conversation context containing conversation information.
            agent_executor: Agent executor instance ready for execution.
            repo_status: Repository availability status information.
        
        Yields:
            StreamChunk: Metadata chunks for agent preparation phase.
        
        Note:
            This demonstrates how subclasses can customize hook methods to add
            service-specific behavior while maintaining the overall flow structure.
        """
        # Add custom repository status metadata
        yield from self._stream_metadata({
            "repository_status": repo_status,
            "status": "repository_checked",
            "service_type": "ask_chat"
        })
        
        # Use the default agent status metadata
        yield from self._stream_metadata(self.metadata_provider.get_agent_status_metadata(context, agent_executor))
    
    def _finalize_chat(self, context: ConversationContext, relevant_docs: List[DocumentInfo], full_response: str) -> Iterator[StreamChunk]:
        """
        Custom chat finalization for AskChat service.
        
        This method customizes the chat finalization phase by adding service type
        identification to the end metadata. This helps clients identify the specific
        service that processed the request.
        
        Args:
            context: Conversation context containing conversation information.
            relevant_docs: List of relevant documents used in the conversation.
            full_response: Complete response from the agent.
        
        Yields:
            StreamChunk: Final chunks for chat completion with service identification.
        
        Note:
            This demonstrates how subclasses can customize finalization to add
            service-specific metadata while maintaining compatibility with the base flow.
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
                "status": "completed",
                "service_type": "ask_chat"
            }
        )
    

    
