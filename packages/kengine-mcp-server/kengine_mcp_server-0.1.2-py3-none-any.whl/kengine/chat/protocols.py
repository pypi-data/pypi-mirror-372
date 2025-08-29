"""
Protocol definitions for agent chat services

This module defines the interfaces that different components of agent chat services
must implement, enabling better abstraction and extensibility.
"""

from typing import Dict, Any, List, Iterator, Protocol
from langchain.agents import AgentExecutor

from .models import ConversationContext, StreamChunk


class MetadataProvider(Protocol):
    """
    Protocol for metadata providers.

    This interface defines methods for generating metadata at various stages of the agent chat workflow.
    Implementations should provide context-specific metadata for conversation start, document retrieval,
    and agent status reporting.

    Methods:
        get_conversation_start_metadata(context): 
            Returns metadata when a conversation starts.
        get_documents_metadata(relevant_docs): 
            Returns metadata about the relevant documents retrieved.
        get_agent_status_metadata(context, agent_executor): 
            Returns metadata about the agent's current status.
    """
    
    def get_conversation_start_metadata(self, context: ConversationContext) -> Dict[str, Any]:
        """Get conversation start metadata"""
        ...
    
    def get_documents_metadata(self, relevant_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get documents metadata"""
        ...
    
    def get_agent_status_metadata(self, context: ConversationContext, agent_executor: AgentExecutor) -> Dict[str, Any]:
        """Get agent status metadata"""
        ...

class StreamProcessor(Protocol):
    """
    Protocol for stream processors.

    This interface defines methods for processing agent stream responses.
    Implementations should handle the stream of responses from the agent and yield appropriate chunks.

    Methods:
        process_agent_stream(agent_executor, agent_input): 
            Processes the agent stream and yields chunks.
    """
    
    def process_agent_stream(self, agent_executor: AgentExecutor, agent_input: Dict[str, Any]) -> Iterator[StreamChunk]:
        """Process agent stream and yield chunks"""
        ...


class MessageHandler(Protocol):
    """
    Protocol for message handlers.

    This interface defines methods for handling messages in the conversation.
    Implementations should handle user and assistant messages appropriately.

    Methods:
        add_user_message(context, message): 
            Adds a user message to the conversation.
        add_assistant_message(context, message): 
            Adds an assistant message to the conversation.
    """
    
    def add_user_message(self, context: ConversationContext, message: str) -> None:
        """Add user message to conversation"""
        ...
    
    def add_assistant_message(self, context: ConversationContext, message: str) -> None:
        """Add assistant message to conversation"""
        ...
