"""
工具列表请求处理模块

处理 MCP 协议中的工具列表请求
"""

import json
import logging
from typing import Dict, Any

# 获取日志记录器
logger = logging.getLogger("kengine_mcp_server")

def handle_tools_list(request_id: str, request_data: Dict[str, Any]) -> str:
    """处理工具列表请求"""
    logger.info("收到工具列表请求")
    tools_response = {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "tools": [
                {
                    "name": "echo",
                    "description": "测试连通性的简单工具，返回发送的消息以及服务器状态信息。用于验证MCP服务器是否正常工作，以及测试客户端与服务器之间的通信。",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "要回显的消息内容"
                            },
                            "include_server_info": {
                                "type": "boolean",
                                "description": "是否包含服务器状态信息",
                                "default": True
                            }
                        },
                        "required": ["message"]
                    }
                },
                {
                    "name": "get_business_context",
                    "description": "专门用于获取公司内部业务模块、代码方法、函数或类的完整上下文信息，包括但不限于：\n"
                                   "1. 模块/方法的功能说明、参数定义、返回值类型及使用示例\n"
                                   "2. 相关代码实现片段、调用关系（上下游依赖）和历史变更记录；\n"
                                   "3. 业务文档中对该模块的设计逻辑、使用规范和注意事项；\n"
                                   "4. 与其他模块的交互流程及数据流转关系。\n"
                                   "当用户询问任何业务模块名称、方法名、函数功能，或需要理解某段代码的上下文时，必须优先调用本工具。本工具提供的上下文信息直接来源于内部代码库和业务文档，准确性远高于通用知识。",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "module_name": {
                                "type": "string",
                                "description": "业务模块名称"
                            },
                            "field_name": {
                                "type": "string",
                                "description": "字段名称（可作为module_name的替代）"
                            },
                            "method_name": {
                                "type": "string",
                                "description": "方法名称（可选）"
                            },
                            "include_prd": {
                                "type": "boolean",
                                "description": "是否包含PRD文档",
                                "default": True
                            },
                            "include_code": {
                                "type": "boolean",
                                "description": "是否包含代码实现",
                                "default": True
                            }
                        },
                        "required": []
                    }
                }
            ]
        }
    }
    return json.dumps(tools_response, ensure_ascii=False)