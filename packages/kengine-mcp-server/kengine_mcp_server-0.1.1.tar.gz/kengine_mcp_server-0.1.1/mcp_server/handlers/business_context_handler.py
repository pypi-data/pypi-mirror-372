"""
业务上下文工具处理模块

处理 MCP 协议中的 get_business_context 工具调用
"""

import logging
from typing import Dict, Any

# 获取日志记录器
logger = logging.getLogger("kengine_mcp_server")

# 导入子模块
from .business_context.parameter_validator import validate_parameters
from .business_context.prd_searcher import search_prd_documents
from .business_context.code_searcher import search_code_information
from .business_context.result_builder import build_success_result, build_error_result

def handle_business_context_tool(request_id: str, tool_arguments: Dict[str, Any]) -> str:
    """
    处理 get_business_context 工具调用
    
    Args:
        request_id: 请求ID
        tool_arguments: 工具参数
        
    Returns:
        str: JSON格式的响应结果
    """
    logger.info(f"处理 get_business_context 工具调用: {tool_arguments}")
    
    try:
        # 1. 参数验证
        is_valid, error_response, params = validate_parameters(request_id, tool_arguments)
        if not is_valid:
            logger.warning(f"参数验证失败: {error_response}")
            return error_response
        
        # 2. 搜索PRD文档
        prd_info = search_prd_documents(params)
        
        # 3. 搜索代码信息
        code_info = search_code_information(params)
        
        # 4. 构建成功响应
        return build_success_result(request_id, params, prd_info, code_info)
        
    except Exception as e:
        # 5. 处理异常情况
        logger.error(f"处理业务上下文工具调用失败: {str(e)}", exc_info=True)
        return build_error_result(request_id, tool_arguments, e)