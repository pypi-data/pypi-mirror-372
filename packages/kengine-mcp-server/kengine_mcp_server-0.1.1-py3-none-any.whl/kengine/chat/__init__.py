"""
Chat模块 - 提供基于RAG的对话服务

该模块提供：
1. 流式对话HTTP服务
2. 对话上下文记忆
3. 思考模式支持
4. 基于代码库的RAG问答
"""

from .models import ChatRequest, ChatResponse, ChatMessage, ConversationContext

# Lazy imports to avoid dependency issues
def _import_service():
    from .service import ChatService
    return ChatService

def _import_server():
    from .server import ChatServer
    return ChatServer

def _import_ask_chat_service():
    from .ask_chat_service import AskChatService
    return AskChatService

__all__ = [
    'ChatService',
    'ChatRequest', 
    'ChatResponse',
    'ChatMessage',
    'ConversationContext',
    'ChatServer',
    'AskChatService'
]

# Lazy import handlers
def __getattr__(name):
    if name == 'ChatService':
        return _import_service()
    elif name == 'ChatServer':
        return _import_server()
    elif name == 'AskChatService':
        return _import_ask_chat_service()

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")