"""
RAG语义搜索工具模块 - 重构版本

包含 RAGSearchTool 类，提供强大的语义搜索能力，使用统一的错误处理机制。
"""

import json
import logging
from typing import List, Dict, Any, Optional, Union

from kengine.rag.interface import DocumentInfo

from .base import BasePathTool
from .exceptions import ServiceUnavailableError, SearchError
from .error_handler import ErrorHandler, handle_tool_errors, safe_execute
from ..decorators import prevent_duplicate_calls


class RAGSearchTool:
    """RAG语义搜索工具
     
    这个工具为Agent提供强大的语义搜索能力，可以：
    1. 在整个项目知识库中进行语义搜索
    2. 查找与特定概念、功能或技术相关的代码和文档
    3. 帮助Agent更好地理解项目结构和实现细节
    
    使用统一的错误处理机制，返回结构化的响应。
    """
    
    def __init__(self, rag_service=None):
        """
        初始化RAG搜索工具
        
        Args:
            rag_service: RAG服务实例，提供向量搜索功能
            base_dir: 基础目录路径
        """
        self.rag_service = rag_service
        self.logger = logging.getLogger(__name__)
        self.default_k = 5
        self.max_k = 20
        self.max_content_length = 400
        self.error_handler = ErrorHandler()
    
    def search(self, query: str, k: int = None, include_metadata: bool = True) -> Dict[str, Any]:
        """
        执行RAG语义搜索并返回结构化结果（新的推荐接口）- 返回结构化响应
        
        Args:
            query: 搜索查询，可以是：
                   - 功能描述："用户认证逻辑"
                   - 技术关键词："数据库连接"
                   - 类或函数名："UserService"
                   - 代码片段："@RequestMapping"
            k: 返回结果数量，默认5个，最大20个
            include_metadata: 是否包含元数据信息
            
        Returns:
            包含搜索结果或错误信息的字典
        """
        return safe_execute(
            self._search_internal,
            tool_name="RAGSearchTool",
            operation="search",
            query=query,
            k=k,
            include_metadata=include_metadata
        )
    
    def _search_internal(self, query: str, k: int = None, include_metadata: bool = True) -> Dict[str, Any]:
        """
        内部搜索方法
        
        Args:
            query: 搜索查询
            k: 返回结果数量
            include_metadata: 是否包含元数据信息
            
        Returns:
            包含搜索结果的字典
            
        Raises:
            SearchError: 搜索参数无效
            ServiceUnavailableError: RAG服务不可用
        """
        # 输入验证
        if not query or not query.strip():
            raise SearchError(
                "搜索查询不能为空",
                pattern=query,
                tool_name=self.__class__.__name__
            )
        
        if not self.rag_service:
            raise ServiceUnavailableError(
                "RAG服务未初始化",
                service_name="rag_service",
                tool_name=self.__class__.__name__
            )
        
        # 参数处理
        k = k or self.default_k
        try:
            if isinstance(k, str):
                k = int(k)
            k = max(1, min(k, self.max_k))  # 限制在1-20之间
        except (ValueError, TypeError):
            k = self.default_k
        
        # 执行搜索
        results = self.rag_service.similarity_search(query, k=k)
        
        if not results:
            return {
                "query": query,
                "results": [],
                "total_results": 0,
                "message": "未找到相关内容",
                "suggestions": [
                    "尝试使用更通用的关键词", 
                    "使用FileSearch工具搜索特定文件",
                    "检查拼写和术语是否正确"
                ]
            }
        
        # 格式化结果
        formatted_results = []
        for i, result in enumerate(results):
            formatted_result = self._format_search_result(result, include_metadata)
            formatted_results.append(formatted_result)
        
        return {
            "query": query,
            "results": formatted_results,
            "total_results": len(results),
            "requested_k": k,
            "message": f"找到 {len(results)} 个相关结果"
        }
    
    @BasePathTool.json_compatible_input({'query': 'query', 'k': 'k'})
    @prevent_duplicate_calls(ttl=180)
    @handle_tool_errors(tool_name="RAGSearchTool", operation="search", return_format="json")
    def run(self, query: str, k: int = 5) -> Union[str, Dict[str, Any]]:
        """
        执行RAG语义搜索并返回JSON格式结果（保持向后兼容的接口）- 可返回JSON格式错误
        
        Args:
            query: 搜索查询，支持JSON格式参数
            k: 返回结果数量，默认5个，最大20个
            
        Returns:
            JSON字符串格式的搜索结果或错误信息
        """
        query = query.strip()
        
        # 执行内部搜索并转换为JSON
        result = self._search_internal(query, k, include_metadata=True)
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    def _format_search_result(self, result: DocumentInfo, include_metadata: bool = True) -> Dict[str, Any]:
        """
        格式化单个搜索结果
        
        Args:
            result: 原始搜索结果 (DocumentInfo对象或字典)
            include_metadata: 是否包含元数据
            
        Returns:
            格式化后的搜索结果
        """
        content = result.content
        source = result.source
        metadata = result.metadata
        
        # 智能截断内容
        content_preview = self._truncate_content(content, self.max_content_length)
        
        formatted_result = {
            "source": source,
            "content": content_preview
        }
        
        if include_metadata and metadata:
            formatted_result["metadata"] = metadata
        
        return formatted_result
    
    def _truncate_content(self, content: str, max_length: int = 400) -> str:
        """
        智能截断内容，保留关键信息
        
        Args:
            content: 原始内容
            max_length: 最大长度
            
        Returns:
            截断后的内容
        """
        if len(content) <= max_length:
            return content
        
        # 尝试在句号或换行符处截断
        truncate_pos = max_length
        for pos in [content.rfind('.', 0, max_length), content.rfind('\n', 0, max_length)]:
            if pos > max_length * 0.75:  # 确保截断位置不太靠前
                truncate_pos = pos + 1
                break
        
        return content[:truncate_pos] + "..."
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        获取RAG服务状态信息 - 返回结构化响应
        
        Returns:
            包含服务状态的字典
        """
        return {
            "success": True,
            "data": {
                "service_available": self.rag_service is not None,
                "service_type": type(self.rag_service).__name__ if self.rag_service else None,
                "default_k": self.default_k,
                "max_k": self.max_k,
                "max_content_length": self.max_content_length
            },
            "message": "服务状态获取成功",
            "tool_name": "RAGSearchTool",
            "operation": "get_service_status"
        }
    
    def set_search_parameters(self, default_k: Optional[int] = None, 
                            max_k: Optional[int] = None, 
                            max_content_length: Optional[int] = None) -> Dict[str, Any]:
        """
        设置搜索参数 - 返回结构化响应
        
        Args:
            default_k: 默认返回结果数量
            max_k: 最大返回结果数量
            max_content_length: 内容最大长度
            
        Returns:
            操作结果字典
        """
        try:
            old_params = {
                "default_k": self.default_k,
                "max_k": self.max_k,
                "max_content_length": self.max_content_length
            }
            
            changes = []
            
            if default_k is not None and default_k > 0:
                self.default_k = default_k
                changes.append(f"default_k: {old_params['default_k']} -> {default_k}")
            
            if max_k is not None and max_k > 0:
                self.max_k = max_k
                changes.append(f"max_k: {old_params['max_k']} -> {max_k}")
            
            if max_content_length is not None and max_content_length > 0:
                self.max_content_length = max_content_length
                changes.append(f"max_content_length: {old_params['max_content_length']} -> {max_content_length}")
            
            new_params = {
                "default_k": self.default_k,
                "max_k": self.max_k,
                "max_content_length": self.max_content_length
            }
            
            return self.error_handler.format_success_response(
                data={
                    "old_parameters": old_params,
                    "new_parameters": new_params,
                    "changes": changes
                },
                message=f"搜索参数已更新，共 {len(changes)} 项变更",
                tool_name="RAGSearchTool",
                operation="set_search_parameters"
            )
        except Exception as e:
            return self.error_handler.format_error_response(
                e,
                tool_name="RAGSearchTool",
                operation="set_search_parameters"
            )
    
    def get_search_suggestions(self, query: str) -> Dict[str, Any]:
        """
        根据查询内容提供搜索建议 - 返回结构化响应
        
        Args:
            query: 搜索查询
            
        Returns:
            包含搜索建议的字典
        """
        try:
            suggestions = []
            
            # 基于查询内容的智能建议
            if not query or len(query.strip()) < 3:
                suggestions.extend([
                    "请提供更具体的搜索关键词",
                    "尝试使用技术术语或功能描述",
                    "可以搜索类名、方法名或注解"
                ])
            elif query.strip().lower() in ['test', 'tests', '测试']:
                suggestions.extend([
                    "尝试搜索具体的测试类名",
                    "搜索测试方法或断言相关内容",
                    "使用'单元测试'或'集成测试'等更具体的词汇"
                ])
            elif any(keyword in query.lower() for keyword in ['config', 'configuration', '配置']):
                suggestions.extend([
                    "搜索配置文件名如'application.yml'",
                    "尝试搜索配置类或配置注解",
                    "搜索环境相关的配置信息"
                ])
            else:
                suggestions.extend([
                    "尝试使用同义词或相关术语",
                    "可以搜索相关的技术栈或框架名称",
                    "尝试更通用或更具体的关键词"
                ])
            
            return self.error_handler.format_success_response(
                data={
                    "query": query,
                    "suggestions": suggestions,
                    "suggestion_count": len(suggestions)
                },
                message="搜索建议生成成功",
                tool_name="RAGSearchTool",
                operation="get_search_suggestions"
            )
        except Exception as e:
            return self.error_handler.format_error_response(
                e,
                tool_name="RAGSearchTool",
                operation="get_search_suggestions"
            )
    
    def validate_query(self, query: str) -> Dict[str, Any]:
        """
        验证搜索查询的有效性 - 返回结构化响应
        
        Args:
            query: 搜索查询
            
        Returns:
            包含验证结果的字典
        """
        try:
            validation_result = {
                "query": query,
                "is_valid": True,
                "issues": [],
                "recommendations": []
            }
            
            # 检查查询长度
            if not query or not query.strip():
                validation_result["is_valid"] = False
                validation_result["issues"].append("查询不能为空")
                validation_result["recommendations"].append("请提供有意义的搜索关键词")
            elif len(query.strip()) < 2:
                validation_result["is_valid"] = False
                validation_result["issues"].append("查询过短")
                validation_result["recommendations"].append("请使用至少2个字符的搜索词")
            elif len(query) > 200:
                validation_result["issues"].append("查询过长，可能影响搜索效果")
                validation_result["recommendations"].append("考虑使用更简洁的关键词")
            
            # 检查特殊字符
            special_chars = ['<', '>', '&', '"', "'"]
            found_special = [char for char in special_chars if char in query]
            if found_special:
                validation_result["issues"].append(f"包含特殊字符: {', '.join(found_special)}")
                validation_result["recommendations"].append("避免使用HTML标签或特殊符号")
            
            # 检查是否全为数字或符号
            if query.strip().isdigit():
                validation_result["issues"].append("查询全为数字")
                validation_result["recommendations"].append("尝试添加描述性文字")
            
            return self.error_handler.format_success_response(
                data=validation_result,
                message="查询验证完成",
                tool_name="RAGSearchTool",
                operation="validate_query"
            )
        except Exception as e:
            return self.error_handler.format_error_response(
                e,
                tool_name="RAGSearchTool",
                operation="validate_query"
            )
    