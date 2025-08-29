"""
Chat服务核心实现
"""

import os
import json
import logging
import uuid
from typing import Dict, Any, Optional, List, Iterator

from ..rag import RAGService, build_rag_service
from ..config.application_config import get_application_config
from ..tasks.llm import init_llm
from ..utils.prompt_loader import load_custom_prompt
from ..utils.git_utils import source_to_git_repo_url


from .models import (
    ChatMessage, MessageRole, ConversationContext, 
    ChatRequest, ChatResponse, StreamChunk
)

from .conversion import ConversationManager
from .ask_chat_service import AskChatService

logger = logging.getLogger(__name__)


class ChatService:
    """聊天服务核心类"""
    
    def __init__(self, conversation_manager: Optional[ConversationManager] = None, verbose: bool = False):
        self.app_config = get_application_config()
        self.conversation_manager = conversation_manager or ConversationManager()
        self.rag_services: Dict[str, RAGService] = {}  # repo_name -> RAG服务
        self.agent_service = AskChatService()
        self.verbose = verbose
        
        if self.verbose:
            logger.info("🔊 ChatService initialized in verbose mode")
        else:
            logger.info("🔇 ChatService initialized in normal mode")
        
    def stream_chat(self, request: ChatRequest) -> Iterator[StreamChunk]:
        """流式聊天接口"""
        logger.info("使用Agent模式进行聊天")
        yield from self.agent_service.stream_chat(request)
            
    
    def get_conversation_history(self, conversation_id: str) -> Optional[ConversationContext]:
        """获取对话历史"""
        return self.conversation_manager.get_conversation(conversation_id)
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """清空对话历史"""
        context = self.conversation_manager.get_conversation(conversation_id)
        if context:
            context.clear_history()
            self.conversation_manager._save_conversation(context)
            
            # 同时清空Agent服务的对话
            self.agent_service.clear_conversation(conversation_id)
            
            return True
        return False
    
    def get_available_tools(self, conversation_id: str) -> List[Dict[str, Any]]:
        """获取对话可用的工具列表"""
        return self.agent_service.get_available_tools(conversation_id)
    