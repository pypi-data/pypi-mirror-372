"""
Chat HTTP服务器实现
"""

import json
import logging
from typing import Any, Dict, Optional
from flask import Flask, request, Response, jsonify
from flask_cors import CORS

from kengine.chat.base_agent_chat_service import BaseAgentChatService
from kengine.chat.prd_review_service import PRDReviewService

from .ask_chat_service import AskChatService
from .models import ChatRequest, StreamChunk

logger = logging.getLogger(__name__)


class ChatServer:
    """Chat HTTP服务器"""
    
    def __init__(self, chat_services: Optional[Dict[str, BaseAgentChatService]] = None, port: int = 8080, verbose: bool = True):
        self.app = Flask(__name__)
        CORS(self.app)  # 启用CORS支持
        
        # 初始化chat services映射
        self.chat_services = chat_services or {}
        
        # 设置默认的chat service
        if not self.chat_services:
            self.chat_services = {
                "ask_chat": AskChatService(),
                "default": AskChatService(),  # 默认使用AskChatService
                "prd_review": PRDReviewService()
            }
        
        self.port = port
        self.verbose = verbose
        
        self._setup_routes()
    
    def _get_chat_service(self, agent_type: Optional[str] = None) -> BaseAgentChatService:
        """根据agent_type获取对应的chat service"""
        if not agent_type:
            return self.chat_services.get("default", self.chat_services.get("ask_chat"))
        
        # 尝试获取指定类型的service
        service = self.chat_services.get(agent_type)
        if service:
            return service
        
        # 如果找不到指定类型，使用默认service
        logger.warning(f"未找到agent_type '{agent_type}'对应的chat service，使用默认service")
        return self.chat_services.get("default", self.chat_services.get("ask_chat"))
    
    def _setup_routes(self):
        """设置路由"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """健康检查"""
            return jsonify({"status": "healthy", "service": "chat"})
        
        @self.app.route('/api/chat', methods=['POST'])
        def chat():
            """聊天接口"""
            try:
                # 解析请求
                data = request.get_json()
                if not data:
                    return jsonify({"error": "请求体不能为空"}), 400
                
                chat_request = ChatRequest.from_dict(data)
                
                # 验证必要参数
                if not chat_request.message:
                    return jsonify({"error": "消息内容不能为空"}), 400
                
                # 获取agent_type参数
                agent_type = data.get("agent_type")
                
                # 根据agent_type获取对应的chat service
                chat_service = self._get_chat_service(agent_type)
                
                # 只支持流式响应模式
                return self._handle_stream_chat(chat_request, chat_service)
                    
            except ValueError as e:
                logger.error(f"请求参数错误: {e}")
                return jsonify({"error": f"参数错误: {str(e)}"}), 400
            except Exception as e:
                logger.error(f"聊天处理失败: {e}")
                return jsonify({"error": f"服务器错误: {str(e)}"}), 500
        
        @self.app.route('/api/conversations/<conversation_id>', methods=['GET'])
        def get_conversation(conversation_id: str):
            """获取对话历史"""
            try:
                # 从查询参数获取agent_type
                agent_type = request.args.get("agent_type")
                chat_service = self._get_chat_service(agent_type)
                
                context = chat_service.get_conversation_history(conversation_id)
                if not context:
                    return jsonify({"error": "对话不存在"}), 404
                
                return jsonify(context.to_dict())
                
            except Exception as e:
                logger.error(f"获取对话历史失败: {e}")
                return jsonify({"error": f"服务器错误: {str(e)}"}), 500
        
        @self.app.route('/api/conversations/<conversation_id>', methods=['DELETE'])
        def clear_conversation(conversation_id: str):
            """清空对话历史"""
            try:
                # 从查询参数获取agent_type
                agent_type = request.args.get("agent_type")
                chat_service = self._get_chat_service(agent_type)
                
                success = chat_service.clear_conversation(conversation_id)
                if success:
                    return jsonify({"message": "对话历史已清空"})
                else:
                    return jsonify({"error": "对话不存在"}), 404
                    
            except Exception as e:
                logger.error(f"清空对话历史失败: {e}")
                return jsonify({"error": f"服务器错误: {str(e)}"}), 500
        
        @self.app.route('/api/agent-types', methods=['GET'])
        def get_agent_types():
            """获取支持的agent类型列表"""
            try:
                agent_types = list(self.chat_services.keys())
                return jsonify({
                    "agent_types": agent_types,
                    "default": "default" if "default" in self.chat_services else agent_types[0] if agent_types else None
                })
            except Exception as e:
                logger.error(f"获取agent类型列表失败: {e}")
                return jsonify({"error": f"服务器错误: {str(e)}"}), 500
    
    def _handle_stream_chat(self, chat_request: ChatRequest, chat_service: BaseAgentChatService) -> Response:
        """处理流式聊天 - 优化的SSE实现"""
        def generate():
            try:
                # Send initial connection established event
                yield f"data: {json.dumps({'type': 'connection', 'status': 'established'})}\n\n"
                
                chunk_count = 0
                for chunk in chat_service.stream_chat(chat_request):
                    chunk_count += 1
                    
                    # Ensure proper SSE formatting
                    chunk_data = chunk.to_json_string()
                    
                    # Add chunk sequence number for debugging
                    if hasattr(chunk, 'metadata'):
                        chunk.metadata['sequence'] = chunk_count
                        chunk_data = chunk.to_json_string()
                    
                    # Send the chunk with proper SSE format
                    yield f"data: {chunk_data}\n\n"
                    
                    # Flush the buffer to ensure immediate transmission
                    import sys
                    if hasattr(sys.stdout, 'flush'):
                        sys.stdout.flush()
                    
            except ValueError as e:
                logger.error(f"流式聊天参数错误: {e}")
                error_chunk = StreamChunk(type="error", data=f"参数错误: {str(e)}")
                yield f"data: {error_chunk.to_json_string()}\n\n"
            except Exception as e:
                logger.error(f"流式聊天失败: {e}")
                error_chunk = StreamChunk(type="error", data=f"错误: {str(e)}")
                yield f"data: {error_chunk.to_json_string()}\n\n"
            finally:
                # Send connection close event
                yield f"data: {json.dumps({'type': 'connection', 'status': 'closed'})}\n\n"
        
        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Cache-Control',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'X-Accel-Buffering': 'no',  # Disable nginx buffering
            }
        )
    
    def run(self, host: str = '0.0.0.0', debug: bool = False):
        """启动服务器"""
        logger.info(f"启动Chat服务器: http://{host}:{self.port}")
        logger.info(f"支持的agent类型: {list(self.chat_services.keys())}")
        self.app.run(host=host, port=self.port, debug=debug, threaded=True)


def create_chat_server(port: int = 8080, chat_services: Optional[Dict[str, BaseAgentChatService]] = None, verbose: bool = True) -> ChatServer:
    """创建Chat服务器的便捷函数"""
    return ChatServer(chat_services=chat_services, port=port, verbose=verbose)


if __name__ == "__main__":
    # 直接运行时启动服务器
    import sys
    
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("端口号必须是整数")
            sys.exit(1)
    
    server = create_chat_server(port=port)
    server.run(debug=True)