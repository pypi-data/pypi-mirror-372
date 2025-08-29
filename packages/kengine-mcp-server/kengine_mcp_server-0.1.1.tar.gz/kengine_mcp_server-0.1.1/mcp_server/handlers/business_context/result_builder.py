"""
结果构建模块

构建业务上下文工具的响应结果
"""

import json
import logging
import time
from typing import Dict, Any

# 获取日志记录器
logger = logging.getLogger("kengine_mcp_server")

def build_success_result(request_id: str, params: Dict[str, Any], prd_info: Dict[str, Any], code_info: Dict[str, Any]) -> str:
    """
    构建成功响应结果
    
    Args:
        request_id: 请求ID
        params: 处理后的参数字典
        prd_info: PRD信息字典
        code_info: 代码信息字典
        
    Returns:
        str: JSON格式的响应结果
    """
    # 构建最终结果
    result = {
        "module_name": params.get("module_name", ""),
        "field_name": params.get("field_name", ""),
        "method_name": params.get("method_name", ""),
        "business_context": {
            "prd_info": prd_info,
            "code_info": code_info
        },
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
                    "text": json.dumps(result, ensure_ascii=False, indent=2)
                }
            ]
        }
    }
    
    logger.info(f"构建成功响应结果: request_id={request_id}")
    return json.dumps(tool_response, ensure_ascii=False)

def build_error_result(request_id: str, params: Dict[str, Any], error: Exception) -> str:
    """
    构建错误响应结果
    
    Args:
        request_id: 请求ID
        params: 处理后的参数字典
        error: 异常对象
        
    Returns:
        str: JSON格式的响应结果
    """
    # 获取主关键词
    primary_keyword = params.get("primary_keyword", "")
    module_name = params.get("module_name", "")
    field_name = params.get("field_name", "")
    method_name = params.get("method_name", "")
    include_prd = params.get("include_prd", True)
    include_code = params.get("include_code", True)
    
    # 构建错误结果
    result = {
        "module_name": module_name,
        "field_name": field_name,
        "method_name": method_name,
        "business_context": {
            "prd_info": {
                "title": f"{primary_keyword}模块PRD",
                "description": "",
                "requirements": [],
                "business_rules": [],
                "search_status": "查询过程中发生错误，未找到相关PRD文档"
            } if include_prd else None,
            "code_info": {
                "file_paths": [],
                "main_classes": [],
                "key_methods": [method_name] if method_name else [],
                "dependencies": [],
                "search_status": "查询过程中发生错误，未找到相关代码信息"
            } if include_code else None
        },
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "error": str(error),
        "status": "error",
        "message": "获取业务上下文失败，请检查日志获取详细信息"
    }
    
    # 构建工具响应
    tool_response = {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False, indent=2)
                }
            ]
        }
    }
    
    logger.error(f"构建错误响应结果: request_id={request_id}, error={str(error)}")
    return json.dumps(tool_response, ensure_ascii=False)