"""
工具调用请求处理模块

处理 MCP 协议中的工具调用请求
"""

import json
import logging
from typing import Dict, Any

# 获取日志记录器
logger = logging.getLogger("kengine_mcp_server")

# 导入工具处理函数
from .echo_handler import handle_echo_tool
from .business_context_handler import handle_business_context_tool

def handle_tools_call(request_id: str, request_data: Dict[str, Any]) -> str:
    """处理工具调用请求"""
    logger.info(f"收到工具调用请求: {request_data.get('params', {})}")
    tool_params = request_data.get("params", {})
    tool_name = tool_params.get("name")
    tool_arguments = tool_params.get("arguments", {})
    
    # 工具处理函数映射
    tool_handlers = {
        "echo": lambda: handle_echo_tool(request_id, tool_arguments),
        "get_business_context": lambda: handle_business_context_tool(request_id, tool_arguments)
    }
    
    # 检查工具是否存在
    if tool_name in tool_handlers:
        logger.info(f"开始执行 {tool_name} 工具调用")
        return tool_handlers[tool_name]()
    else:
        # 未知工具
        error_response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"未知工具: {tool_name}"
            }
        }
        return json.dumps(error_response, ensure_ascii=False)