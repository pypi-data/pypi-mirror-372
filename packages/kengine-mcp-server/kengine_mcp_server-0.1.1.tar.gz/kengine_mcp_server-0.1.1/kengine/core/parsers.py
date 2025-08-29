"""
文档生成输出解析器模块

提供通用的LLM输出解析器，供所有策略模块使用
"""

import json
import logging
from typing import Dict, Any

from langchain_core.output_parsers import BaseOutputParser
from langchain_core.exceptions import OutputParserException
from kengine.markdown import fix_markdown


class CatalogueOutputParser(BaseOutputParser[Dict[str, Any]]):
    """
    文档目录结构输出解析器
    解析格式: <documentation_structure>JSON内容</documentation_structure>
    """
    
    def parse(self, text: str) -> Dict[str, Any]:
        """解析LLM输出的文档目录结构"""
        try:
            # 查找 <documentation_structure> 标签之间的内容
            start_tag = "<documentation_structure>"
            end_tag = "</documentation_structure>"
            
            start_idx = text.find(start_tag)
            end_idx = text.find(end_tag)
            
            if start_idx == -1 or end_idx == -1:
                # 尝试直接解析整个响应作为JSON
                return self._parse_json_content(text.strip())
            
            # 提取标签之间的内容
            json_content = text[start_idx + len(start_tag):end_idx].strip()
            return self._parse_json_content(json_content)
            
        except Exception as e:
            raise OutputParserException(f"解析文档目录结构失败: {e}")
    
    def _parse_json_content(self, json_content: str) -> Dict[str, Any]:
        """解析并验证JSON内容"""
        try:
            catalogue_data = extract_json_from_markdown(json_content)
            
            # 验证JSON结构
            if not isinstance(catalogue_data, dict):
                raise OutputParserException(f"JSON结构无效：根节点必须是对象 , json 内容 '{json_content}'")
            
            if "items" not in catalogue_data:
                if "children" in catalogue_data:
                    catalogue_data["items"] = catalogue_data.pop("children")
                else:
                    raise OutputParserException(f"JSON结构无效：缺少'items'字段, json 内容 '{json_content}'")
            
            if not isinstance(catalogue_data["items"], list):
                raise OutputParserException(f"JSON结构无效：'items'字段必须是数组, json 内容 '{json_content}'")
            
            # 验证items结构
            self._validate_items_structure(catalogue_data["items"])
            return catalogue_data
            
        except json.JSONDecodeError as e:
            raise OutputParserException(f"无法解析JSON格式: {e}, JSON内容: '{json_content}'")
    
    def _validate_items_structure(self, items: list) -> None:
        """验证items数组的结构"""
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                raise OutputParserException(f"第{i+1}个item必须是对象")
            
            # 检查必需字段
            required_fields = ["title", "name", "prompt"]
            for field in required_fields:
                if field not in item:
                    raise OutputParserException(f"第{i+1}个item缺少必需字段: {field}")
                if not isinstance(item[field], str) or not item[field].strip():
                    raise OutputParserException(f"第{i+1}个item的{field}字段必须是非空字符串")
            
            # 如果有children，递归验证
            if "children" in item:
                if not isinstance(item["children"], list):
                    raise OutputParserException(f"第{i+1}个item的children字段必须是数组")
                self._validate_items_structure(item["children"])
    
    @property  
    def _type(self) -> str:
        return "catalogue_output_parser"


class TaggedContentOutputParser(BaseOutputParser[str]):
    """
    通用标签内容输出解析器
    支持解析任意标签格式: <tag>内容</tag>
    """
    
    # Pydantic v2 字段定义
    tag_name: str
    allow_fallback: bool = True
    start_tag: str = ""
    end_tag: str = ""
    is_markdown: bool = False
    
    def __init__(self, tag_name: str,
                 allow_fallback: bool = True, 
                 is_markdown: bool = False):
        """
        初始化解析器
        
        Args:
            tag_name: 标签名称（如 "document", "overview" 等）
            allow_fallback: 如果找不到标签，是否返回原始内容
            is_markdown: 是否为markdown格式
        """
        # 使用 Pydantic v2 兼容的初始化方式
        super().__init__(
            tag_name=tag_name,
            allow_fallback=allow_fallback,
            is_markdown=is_markdown,
            start_tag=f"<{tag_name}>",
            end_tag=f"</{tag_name}>"
        )
    
    def parse(self, text: str) -> str:
        """解析LLM输出的标签内容"""
        try:
            start_idx = text.find(self.start_tag)
            end_idx = text.find(self.end_tag)
            
            if start_idx == -1 or end_idx == -1:
                if self.allow_fallback:
                    # 如果没有找到标签，返回原始内容
                    return text.strip()
                else:
                    raise OutputParserException(f"未找到{self.tag_name}标签, 原始文本: '{text}'")
            
            # 提取标签之间的内容
            content = text[start_idx + len(self.start_tag):end_idx].strip()
            
            if not content:
                raise OutputParserException(f"{self.tag_name}标签内容为空, 原始文本: '{text}'")
            
            if self.is_markdown:
                content = fix_markdown(content)
            
            return content
            
        except Exception as e:
            raise OutputParserException(f"解析{self.tag_name}内容失败: {e}, 原始文本: '{text}'") from e
    
    @property
    def _type(self) -> str:
        return f"tagged_content_output_parser_{self.tag_name}"


# 为了向后兼容，提供常用的别名
class DocumentOutputParser(TaggedContentOutputParser):
    """文档内容输出解析器 - 兼容性别名"""
    
    def __init__(self):
        super().__init__(tag_name="document", allow_fallback=True, is_markdown=True)


class OverviewOutputParser(TaggedContentOutputParser):
    """概览内容输出解析器 - 便捷别名"""
    
    def __init__(self):
        super().__init__(tag_name="overview", allow_fallback=True, is_markdown=True)


def extract_json_from_markdown(content: str) -> Dict[str, Any]:
    """
    从markdown格式的内容中提取JSON数据
    支持以下格式：
    1. ```json ... ```
    2. 纯JSON格式 {...}
    3. 其他包含JSON的文本
    
    Args:
        content: 包含JSON的文本内容
        
    Returns:
        Dict[str, Any]: 解析后的JSON数据
        
    Raises:
        ValueError: 当无法提取有效JSON时抛出异常
    """
    import re
    
    if not content or not content.strip():
        raise ValueError("输入内容不能为空")
    
    # 首先尝试提取markdown代码块中的JSON
    # 匹配 ```json ... ``` 或 ``` ... ``` 格式
    markdown_patterns = [
        r'```json\s*\n(.*?)\n```',  # ```json ... ```
        r'```\s*\n(\{.*?\})\s*\n```',  # ``` {...} ```
    ]
    
    for pattern in markdown_patterns:
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        for match in matches:
            json_content = match.strip()
            if json_content:
                try:
                    return json.loads(json_content)
                except json.JSONDecodeError:
                    continue
    
    # 如果没有找到markdown格式，尝试直接提取JSON对象
    # 匹配最外层的JSON对象
    json_patterns = [
        r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # 简单的嵌套JSON匹配
        r'\{.*\}',  # 最宽泛的匹配
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, content, re.DOTALL)
        for match in matches:
            json_content = match.strip()
            if json_content:
                try:
                    return json.loads(json_content)
                except json.JSONDecodeError:
                    continue
    
    # 如果所有方法都失败，抛出详细的错误信息
    raise ValueError(f"无法从Agent输出中提取有效的JSON结构。输入内容前200字符: {content}")



class JsonOutputParser(BaseOutputParser[Dict[str, Any]]):
    """
    JSON 提取，兼容 markdown格式提取， 和纯 json提取
    """
    
    def parse(self, text: str) -> Dict[str, Any]:
        return extract_json_from_markdown(text)