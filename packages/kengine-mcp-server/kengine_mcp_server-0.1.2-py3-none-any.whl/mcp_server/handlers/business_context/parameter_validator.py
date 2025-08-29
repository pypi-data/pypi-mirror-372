"""
参数验证模块

验证业务上下文工具的输入参数
"""

import json
import logging
from typing import Dict, Any, Tuple, Optional

# 获取日志记录器
logger = logging.getLogger("kengine_mcp_server")

def validate_parameters(request_id: str, tool_arguments: Dict[str, Any]) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """
    验证业务上下文工具的输入参数
    
    Args:
        request_id: 请求ID
        tool_arguments: 工具参数
        
    Returns:
        Tuple[bool, Optional[str], Dict[str, Any]]:
            - 验证是否通过
            - 如果验证失败，返回错误响应JSON字符串；如果验证通过，返回None
            - 处理后的参数字典
    """
    # 获取业务模块或方法的上下文
    module_name = tool_arguments.get("module_name", "")
    field_name = tool_arguments.get("field_name", "")
    method_name = tool_arguments.get("method_name", "")
    include_prd = tool_arguments.get("include_prd", True)
    include_code = tool_arguments.get("include_code", True)
    
    # 参数验证：确保至少有一个参数非空
    if not module_name and not field_name and not method_name:
        error_response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32602,
                "message": "参数错误: module_name、field_name、method_name 至少需要提供一个"
            }
        }
        return False, json.dumps(error_response, ensure_ascii=False), {}
    
    # 记录日志
    logger.info(f"验证参数: module_name={module_name}, field_name={field_name}, method_name={method_name}")
    
    # 构建搜索关键词组合
    search_keywords = []
    if module_name:
        search_keywords.append(module_name)
    if field_name:
        search_keywords.append(field_name)
    if method_name:
        search_keywords.append(method_name)
    
    # 主搜索关键词（用于标题等）
    primary_keyword = module_name or field_name or method_name
    
    # 构建处理后的参数字典
    processed_params = {
        "module_name": module_name,
        "field_name": field_name,
        "method_name": method_name,
        "include_prd": include_prd,
        "include_code": include_code,
        "search_keywords": search_keywords,
        "primary_keyword": primary_keyword
    }
    
    return True, None, processed_params