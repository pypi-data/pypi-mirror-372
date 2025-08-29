"""
心跳请求处理模块

处理 MCP 协议中的心跳请求
"""

import json
import logging
import time
from typing import Dict, Any

# 获取日志记录器
logger = logging.getLogger("kengine_mcp_server")

def handle_heartbeat(request_id: str, request_data: Dict[str, Any]) -> str:
    """处理心跳请求"""
    logger.debug("收到心跳请求")
    response = {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "status": "success",
            "code": 200,
            "message": "MCP Server 存活",
            "data": {"timestamp": time.time()}
        }
    }
    return json.dumps(response, ensure_ascii=False)