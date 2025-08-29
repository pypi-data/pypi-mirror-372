"""
MCP 服务器请求处理模块

包含处理不同类型 MCP 请求的函数，如初始化、工具列表、工具调用等
"""

import logging
from typing import Dict, Any

from .handlers.heartbeat_handler import handle_heartbeat
from .handlers.tools_call_handler import handle_tools_call
# 导入子模块中的处理函数
from .handlers.tools_list_handler import handle_tools_list
from .handlers.version_handler import handle_version

# 获取日志记录器
logger = logging.getLogger("kengine_mcp_server")

# --------------------------
# 请求处理函数
# --------------------------

def handle_initialize(request_id: str, request_data: Dict[str, Any]) -> str:
    """处理初始化请求"""
    import json
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

# 请求处理函数映射
REQUEST_HANDLERS = {
    "initialize": handle_initialize,
    "tools/list": handle_tools_list,
    "tools/call": handle_tools_call,
    "heartbeat": handle_heartbeat,
    "version": handle_version
}