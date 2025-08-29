"""
MCP 服务器请求处理模块

包含处理不同类型 MCP 请求的函数，如初始化、工具列表、工具调用等
"""

import logging

# 获取日志记录器
logger = logging.getLogger("kengine_mcp_server")

# 导入各个处理函数
from .echo_handler import handle_echo_tool
from .business_context_handler import handle_business_context_tool
from .initialize_handler import handle_initialize
from .tools_list_handler import handle_tools_list
from .tools_call_handler import handle_tools_call
from .heartbeat_handler import handle_heartbeat
from .version_handler import handle_version

# 请求处理函数映射
REQUEST_HANDLERS = {
    "initialize": handle_initialize,
    "tools/list": handle_tools_list,
    "tools/call": handle_tools_call,
    "heartbeat": handle_heartbeat,
    "version": handle_version
}