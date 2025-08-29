import os
import json
import logging
import uuid
from typing import Dict, Optional
from datetime import datetime

from .models import (
    ChatMessage, ConversationContext, 
)

logger = logging.getLogger(__name__)


class ConversationManager:
    """对话管理器"""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or self._get_default_storage_path()
        self.conversations: Dict[str, ConversationContext] = {}
        self._ensure_storage_dir()
    
    def _get_default_storage_path(self) -> str:
        """获取默认存储路径"""
        return os.path.join(os.getcwd(), ".chat_history")
    
    def _ensure_storage_dir(self) -> None:
        """确保存储目录存在"""
        os.makedirs(self.storage_path, exist_ok=True)
    
    def create_conversation(self, repo_name: str, conversation_id: Optional[str] = None) -> str:
        """创建新对话"""
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        context = ConversationContext(
            conversation_id=conversation_id,
            repo_name=repo_name  # 更改为repo_name
        )
        
        self.conversations[conversation_id] = context
        self._save_conversation(context)
        
        logger.info(f"创建新对话: {conversation_id}, 仓库名称: {repo_name}")
        return conversation_id
    
    def get_conversation(self, conversation_id: str) -> Optional[ConversationContext]:
        """获取对话上下文"""
        if conversation_id in self.conversations:
            return self.conversations[conversation_id]
        
        # 尝试从磁盘加载
        return self._load_conversation(conversation_id)
    
    def add_message(self, conversation_id: str, message: ChatMessage) -> None:
        """添加消息到对话"""
        context = self.get_conversation(conversation_id)
        if context:
            context.add_message(message)
            self._save_conversation(context)
    
    def _save_conversation(self, context: ConversationContext) -> None:
        """保存对话到磁盘"""
        try:
            file_path = os.path.join(self.storage_path, f"{context.conversation_id}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(context.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存对话失败 {context.conversation_id}: {e}")
    
    def _load_conversation(self, conversation_id: str) -> Optional[ConversationContext]:
        """从磁盘加载对话"""
        try:
            file_path = os.path.join(self.storage_path, f"{conversation_id}.json")
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            context = ConversationContext(
                conversation_id=data["conversation_id"],
                repo_name=data.get("repo_name", data.get("project_path", "")),  # 兼容旧数据
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
                metadata=data.get("metadata", {})
            )
            
            # 加载消息
            for msg_data in data.get("messages", []):
                message = ChatMessage.from_dict(msg_data)
                context.messages.append(message)
            
            self.conversations[conversation_id] = context
            return context
            
        except Exception as e:
            logger.error(f"加载对话失败 {conversation_id}: {e}")
            return None