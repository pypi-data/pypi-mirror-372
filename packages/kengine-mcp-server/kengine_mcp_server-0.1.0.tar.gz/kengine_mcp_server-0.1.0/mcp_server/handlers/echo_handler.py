"""
Echo 工具处理模块

处理 MCP 协议中的 echo 工具调用
"""

import json
import logging
import time
from typing import Dict, Any

# 获取日志记录器
logger = logging.getLogger("kengine_mcp_server")

def handle_echo_tool(request_id: str, tool_arguments: Dict[str, Any]) -> str:
    """处理 echo 工具调用"""
    message = tool_arguments.get("message", "")
    include_server_info = tool_arguments.get("include_server_info", True)
    
    # 参数验证
    if not message:
        error_response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32602,
                "message": "参数错误: 必须提供 message 参数"
            }
        }
        return json.dumps(error_response, ensure_ascii=False)
    
    # 记录日志
    logger.info(f"处理 echo 工具调用: message={message}, include_server_info={include_server_info}")
    
    # 构建响应数据
    echo_result = {
        "echo": message,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 构建工具响应
    tool_response = {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(echo_result, ensure_ascii=False, indent=2)
                }
            ]
        }
    }
    return json.dumps(tool_response, ensure_ascii=False)