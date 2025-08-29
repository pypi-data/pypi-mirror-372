"""
版本请求处理模块

处理 MCP 协议中的版本请求
"""

import json
import logging
from typing import Dict, Any

# 获取日志记录器
logger = logging.getLogger("kengine_mcp_server")

def handle_version(request_id: str, request_data: Dict[str, Any]) -> str:
    """处理版本请求"""
    response = {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "status": "success",
            "code": 200,
            "message": "版本查询成功",
            "data": {
                "kengine_mcp_server_version": "1.0.0",
                "business_logic_version": "1.0.0"
            }
        }
    }
    return json.dumps(response, ensure_ascii=False)