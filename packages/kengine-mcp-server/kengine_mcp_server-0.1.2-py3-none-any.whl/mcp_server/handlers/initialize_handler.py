"""
初始化请求处理模块

处理 MCP 协议中的初始化请求
"""

import json
import logging
from typing import Dict, Any

# 获取日志记录器
logger = logging.getLogger("kengine_mcp_server")

def handle_initialize(request_id: str, request_data: Dict[str, Any]) -> str:
    """处理初始化请求"""
    logger.info("收到初始化请求")
    # 直接构建符合MCP协议的响应
    response = {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": "2024-11-05",
            "serverInfo": {
                "name": "kengine_mcp_server",  # 使用常量定义的服务器名称
                "version": "1.0.0"
            },
            "capabilities": {
                "tools": {
                    "listChanged": True
                },
                "resources": {}
            }
        }
    }
    return json.dumps(response, ensure_ascii=False)