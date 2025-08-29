"""
策略公用工具模块

提供文档生成策略的公用辅助方法和验证逻辑
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..types import GenerationContext, StepGenerationResult
from ..parsers import TaggedContentOutputParser


class StrategyUtils:
    """策略公用工具类"""
    
    @staticmethod
    def validate_project_path(project_path: str) -> Optional[str]:
        """
        验证项目路径是否有效
        
        Args:
            project_path: 项目路径
            
        Returns:
            错误信息，如果路径有效则返回None
        """
        path = Path(project_path)
        if not path.exists():
            return f"项目路径不存在: {project_path}"
        if not path.is_dir():
            return f"路径不是目录: {project_path}"
        return None
    
    @staticmethod
    def validate_catalogue_data(catalogue_data: Dict[str, Any]) -> None:
        """
        验证目录数据格式
        
        Args:
            catalogue_data: 目录数据
            
        Raises:
            ValueError: 如果数据格式无效
        """
        if not isinstance(catalogue_data, dict):
            raise ValueError(f"catalogue_data参数必须是字典类型,  而当前内容[{catalogue_data}] 类型 [{type(catalogue_data)}]")
        if "items" not in catalogue_data:
            raise ValueError(f"catalogue_data缺少'items'字段 [{catalogue_data}]")
        if not isinstance(catalogue_data["items"], list):
            raise ValueError("catalogue_data的'items'字段必须是数组")
    
    @staticmethod
    def create_generation_stats() -> Dict[str, Any]:
        """
        创建文档生成统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "total_items": 0,
            "successful_generations": 0,
            "failed_generations": 0,
            "generated_files": [],
            "failed_items": []
        }
    
    @staticmethod
    def process_git_repository_url(context: GenerationContext) -> Optional[str]:
        """
        处理Git仓库URL转换
        
        Args:
            context: 生成上下文
            
        Returns:
            转换后的HTTP URL，如果没有仓库URL则返回None
        """
        if not context.git_repository_url:
            return None
        
        from ...utils.git_utils import convert_git_url_to_http
        return convert_git_url_to_http(context.git_repository_url, context.branch)
    
    @staticmethod
    def create_result_data(content: str, file_path: str, context: GenerationContext) -> Dict[str, Any]:
        """
        创建结果数据字典
        
        Args:
            content: 生成的内容
            file_path: 文件路径
            context: 生成上下文
            
        Returns:
            结果数据字典
        """
        return {
            "content": content,
            "file_path": file_path,
            "project_type": context.project_type,
            "git_repository": context.git_repository_url or "",
            "git_branch": context.branch or "master"
        }
    
    @staticmethod
    def parse_content_with_fallback(content: str, tag_name: str = "document") -> str:
        """
        解析内容，如果解析失败则使用原始内容
        
        Args:
            content: 要解析的内容
            tag_name: 标签名称
            
        Returns:
            解析后的内容
        """
        output_parser = TaggedContentOutputParser(tag_name=tag_name, allow_fallback=True)
        try:
            return output_parser.parse(content)
        except Exception:
            # 如果解析失败，使用原始内容
            return content
    
    
    @staticmethod
    def create_safe_filename_and_path(item_name: str, output_path: Path) -> tuple[str, Path]:
        """
        创建安全的文件名和路径
        
        Args:
            item_name: 原始项目名称
            output_path: 输出目录路径
            
        Returns:
            (安全文件名, 完整文件路径) 的元组
        """
        from ...utils.path_utils import sanitize_filename
        
        safe_filename = sanitize_filename(item_name)
        filename = f"{safe_filename}.md"
        file_path = output_path / filename
        return filename, file_path
    