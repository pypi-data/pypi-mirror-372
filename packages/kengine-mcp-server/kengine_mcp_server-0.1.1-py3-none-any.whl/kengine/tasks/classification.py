"""
LangChain代码库分类Chain节点
用于从输入的本地目录路径分析该代码库属于哪个分类
支持动态配置分类类别和提示词
"""

import re
import os
import logging
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.exceptions import OutputParserException

from ..utils.prompt_loader import load_classification_prompt
from ..utils.project_utils import get_project_info_text
from .llm import init_llm
from ..config.application_config import get_application_config

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClassificationOutputParser(BaseOutputParser[Dict[str, Any]]):
    """
    自定义输出解析器，解析分类结果
    解析格式: <classify>classifyName:分类</classify>
    支持动态分类验证
    """
    
    def __init__(self):
        """初始化解析器"""
        super().__init__()
        object.__setattr__(self, 'config', get_application_config())
    
    def parse(self, text: str) -> Dict[str, Any]:
        """
        解析LLM输出的分类结果
        
        Args:
            text: LLM输出的原始文本
            
        Returns:
            解析后的分类结果字典
            
        Raises:
            OutputParserException: 解析失败
        """
        try:
            # 使用正则表达式提取分类结果
            pattern = r'<classify>\s*classifyName:([^<]+)\s*</classify>'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            
            if not match:
                raise OutputParserException("未找到有效的分类标签")
            
            classification = match.group(1).strip()
            
            # 动态验证分类是否有效
            if not self.config.validate_classfication(classification):
                # 尝试模糊匹配
                available_classifications = self.config.get_enabled_classifications()
                classification_lower = classification.lower()
                matched_category = None
                
                # 1. 精确匹配（大小写不敏感）
                for category in available_classifications:
                    if category.lower() == classification_lower:
                        matched_category = category
                        break
                
                # 2. 部分匹配（分类名称包含在输入中）
                if not matched_category:
                    for category in available_classifications:
                        if category.lower() in classification_lower:
                            matched_category = category
                            logger.info(f"通过部分匹配找到分类: {category}")
                            break
                
                if matched_category:
                    classification = matched_category
                else:
                    raise OutputParserException(
                        f"无效的分类结果: {classification}，可用分类: {available_classifications}"
                    )
            
            # 提取分析摘要（可选）
            analysis_summary = self._extract_analysis_summary(text)
            
            # 获取分类详细信息
            category_info = self.config.get_classification_info(classification)
            confidence = "high" if category_info else "medium"
            
            return {
                "classification": classification,
                "confidence": confidence,
                "analysis_summary": analysis_summary,
                "category_info": category_info,
                "raw_output": text
            }
            
        except Exception as e:
            logger.error(f"解析分类结果失败: {e}")
            raise OutputParserException(f"解析分类结果失败: {e}")
    
    def _extract_analysis_summary(self, text: str) -> str:
        """
        从输出文本中提取分析摘要
        
        Args:
            text: LLM输出的原始文本
            
        Returns:
            分析摘要文本
        """
        # 简单提取前几句作为摘要
        lines = text.split('\n')
        summary_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('<') and len(line) > 10:
                summary_lines.append(line)
                if len(summary_lines) >= 3:  # 最多3行摘要
                    break
        
        return ' '.join(summary_lines) if summary_lines else "自动分类完成"
    
    @property
    def _type(self) -> str:
        return "classification_output_parser"


class RepositoryClassificationChain:
    """
    代码库分类Chain节点
    组合LLM、prompt、parser为完整的分类链
    支持动态配置和提示词
    """
    
    def __init__(self, model_name: str = "gpt-4"):
        """
        初始化分类Chain
        
        Args:
            model_name: 使用的LLM模型名称
            config_file: 分类配置文件路径
        """
        # 如果指定了配置文件，重新加载配置
        self.config = get_application_config()
        model_config = self.config.get_model_config(model_name)

        self.llm = init_llm(model_config)
        self.output_parser = ClassificationOutputParser()
        
        # 动态加载prompt模板
        self._load_prompt_template()
        
        # 构建完整的chain
        self.chain = (
            {
                "projectInfo": lambda x: get_project_info_text(x["local_directory_path"]),
                "categories": lambda x: self._get_categories_info()
            }
            | self.prompt
            | self.llm
            | self.output_parser
        )
        
    def _load_prompt_template(self):
        """动态加载提示词模板"""
        try:
            prompt_template = load_classification_prompt()
            
            # 动态注入分类信息到提示词中
            categories_info = self._get_categories_description()
            
            # 如果提示词中包含占位符，则替换
            if "{categories}" in prompt_template:
                prompt_template = prompt_template.replace("{categories}", categories_info)
            
            self.prompt = ChatPromptTemplate.from_template(prompt_template)
            logger.info("成功加载动态分类提示词模板")
            
        except Exception as e:
            logger.error(f"加载提示词模板失败: {e}")
            # 使用默认模板
            self.prompt = ChatPromptTemplate.from_template(
                "请分析以下项目信息并进行分类：\n\n{projectInfo}\n\n"
                "可用分类：{categories}\n\n"
                "请使用<classify>classifyName:分类名</classify>格式输出结果。"
            )
    
    def _get_categories_description(self) -> str:
        """获取分类描述信息"""
        enabled_classifications = self.config.get_enabled_classifications()
        descriptions = []
        
        for category in enabled_classifications:
            info = self.config.get_classification_info(category)
            if info:
                desc = f"- {category}: {info.get('description', '')}"
                keywords = info.get('keywords', [])
                if keywords:
                    desc += f" (关键词: {', '.join(keywords)})"
                descriptions.append(desc)
        
        return "\n".join(descriptions)
    
    def _get_categories_info(self) -> str:
        """获取分类信息（用于prompt中的占位符）"""
        return self._get_categories_description()
    
    def classify_repository(self, local_directory_path: str) -> Dict[str, Any]:
        """
        对本地代码库进行分类
        
        Args:
            local_directory_path: 本地目录路径
            
        Returns:
            分类结果字典，包含:
            - local_directory_path: 本地目录路径
            - classification: 分类结果
            - confidence: 置信度
            - analysis_summary: 分析摘要
            - category_info: 分类详细信息
            
        Raises:
            ValueError: 目录路径无效
            FileNotFoundError: 目录不存在
            Exception: 分类过程中的其他错误
        """
        try:
            logger.info(f"开始分类本地代码库: {local_directory_path}")
            
            # 检查目录是否存在
            if not os.path.exists(local_directory_path):
                raise FileNotFoundError(f"目录不存在: {local_directory_path}")
            
            # 执行分类chain
            result = self.chain.invoke({
                "local_directory_path": local_directory_path,
            })
            
            # 构建最终结果
            final_result = {
                "local_directory_path": local_directory_path,
                "classification": result["classification"],
                "confidence": result["confidence"],
                "analysis_summary": result["analysis_summary"],
                "category_info": result.get("category_info"),
                "available_classifications": self.config.get_enabled_classifications()
            }
            
            logger.info(f"分类完成: {result['classification']} (置信度: {result['confidence']})")
            return final_result
            
        except Exception as e:
            logger.error(f"分类本地代码库失败，目录路径='{local_directory_path}': {e}")
            raise
    
    
    def get_available_categories(self) -> list:
        """获取可用分类列表"""
        return self.config.get_enabled_classifications()



def classify_repository(local_directory_path: str, model_name: str = "gpt-4", 
                       config_file: str = None) -> Dict[str, Any]:
    """
    便捷的本地代码库分类函数
    
    Args:
        local_directory_path: 本地目录路径
        model_name: 使用的LLM模型名称
        config_file: 分类配置文件路径
        
    Returns:
        分类结果字典
    """
    chain = RepositoryClassificationChain(model_name=model_name)
    return chain.classify_repository(local_directory_path)


def get_available_categories() -> list:
    """
    获取可用分类列表
    
    Args:
        config_file: 分类配置文件路径
        
    Returns:
        分类列表
    """
    config = get_application_config()
    return config.get_enabled_classifications()

