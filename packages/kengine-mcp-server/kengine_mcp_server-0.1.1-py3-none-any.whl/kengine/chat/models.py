"""
Chat数据模型定义
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """消息角色枚举"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    THINKING = "thinking"


@dataclass
class ChatMessage:
    """聊天消息模型"""
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """从字典创建实例"""
        return cls(
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {})
        )


@dataclass
class ConversationContext:
    """对话上下文"""
    conversation_id: str
    repo_name: str  # 更改为repo_name
    messages: List[ChatMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, message: ChatMessage) -> None:
        """添加消息"""
        self.messages.append(message)
        self.updated_at = datetime.now()
    
    def get_recent_messages(self, limit: int = 10) -> List[ChatMessage]:
        """获取最近的消息"""
        return self.messages[-limit:]
    
    def clear_history(self) -> None:
        """清空对话历史"""
        self.messages.clear()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "conversation_id": self.conversation_id,
            "repo_name": self.repo_name,  # 更改为repo_name
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class ChatRequest:
    """聊天请求模型"""
    message: str
    conversation_id: Optional[str] = None
    repo_name: Optional[str] = None  # 更改为repo_name
    enable_deep_thinking: bool = False
    enable_agent_mode: bool = False  # 启用Agent模式
    agent_type: Optional[str] = None  # Agent类型
    stream: bool = True
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    context_limit: int = 10
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "message": self.message,
            "conversation_id": self.conversation_id,
            "repo_name": self.repo_name,  # 更改为repo_name
            "enable_deep_thinking": self.enable_deep_thinking,
            "enable_agent_mode": self.enable_agent_mode,
            "agent_type": self.agent_type,
            "stream": self.stream,
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "context_limit": self.context_limit
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatRequest':
        """从字典创建实例"""
        return cls(
            message=data["message"],
            conversation_id=data.get("conversation_id"),
            repo_name=data.get("repo_name"),  # 更改为repo_name
            enable_deep_thinking=data.get("enable_deep_thinking", False),
            enable_agent_mode=data.get("enable_agent_mode", False),
            agent_type=data.get("agent_type"),
            stream=data.get("stream", True),
            model_name=data.get("model_name"),
            temperature=data.get("temperature"),
            max_tokens=data.get("max_tokens"),
            context_limit=data.get("context_limit", 10)
        )


@dataclass
class ChatResponse:
    """聊天响应模型"""
    conversation_id: str
    message: ChatMessage
    thinking_content: Optional[str] = None
    source_documents: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "conversation_id": self.conversation_id,
            "message": self.message.to_dict(),
            "thinking_content": self.thinking_content,
            "source_documents": self.source_documents,
            "metadata": self.metadata
        }


@dataclass
class StreamChunk:
    """流式响应块"""
    type: Literal["thinking", "content", "sources", "end", "error", "metadata"]
    data: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "type": self.type,
            "data": self.data,
            "metadata": self.metadata
        }
    
    def to_json_string(self) -> str:
        """转换为JSON字符串"""
        import json
        return json.dumps(self.to_dict(), ensure_ascii=False)