"""
LLM 初始化模块
提供统一的 LLM 初始化接口，支持 OpenAI 和 Anthropic 两个主要提供商
包含 504 错误重试机制
"""

import logging
from typing import Optional
from langchain_core.language_models.chat_models import BaseChatModel
from kengine.utils import ChatOpenAI4Anthropic
from kengine.utils.retryable_llm import ChatOpenAIWithRetry, LLMRetryError
from kengine.config.application_config import get_application_config

# 配置日志
logger = logging.getLogger(__name__)


def init_llm(options: Optional[dict] = None) -> BaseChatModel:
    """
    初始化大模型，应用的其他地方不做大模型初始化，统一在此处初始化大模型，便于切换模型和修改参数
    
    Args:
        options: LLM 配置选项字典，可选。如果不提供，将使用默认配置。包含以下字段:
            - model (str): 模型名称，默认 "gpt-3.5-turbo"
            - temperature (float, optional): 温度参数，默认 0.7
            - max_tokens (int, optional): 最大令牌数
            - streaming (bool, optional): 是否启用流式响应，默认 False
            - provider_specific (dict, optional): 提供商特定参数
            - retry_config (dict, optional): 重试配置
                - max_retries (int): 最大重试次数，默认 3
                - base_delay (float): 基础延迟时间，默认 1.0 秒
    
    Returns:
        BaseChatModel: 带重试机制的 LLM 实例
        
    Raises:
        LLMInitializationError: 初始化失败
        APIKeyMissingError: API 密钥缺失
        
    Examples:
        >>> # 使用默认配置初始化
        >>> llm = init_llm()
        
        >>> # 初始化 OpenAI GPT-4
        >>> llm = init_llm({
        ...     "provider": "openai",
        ...     "model": "gpt-4",
        ...     "temperature": 0.7
        ... })
        
        >>> # 初始化 Anthropic Claude
        >>> llm = init_llm({
        ...     "provider": "anthropic", 
        ...     "model": "claude-3-sonnet-20240229",
        ...     "temperature": 0.5,
        ...     "max_tokens": 4000
        ... })
        
        >>> # 自定义重试配置
        >>> llm = init_llm({
        ...     "provider": "openai",
        ...     "model": "gpt-3.5-turbo",
        ...     "retry_config": {
        ...         "max_retries": 5,
        ...         "base_delay": 2.0
        ...     }
        ... })
    """
    # 如果没有提供选项，使用默认配置
    if options is None:
        options = {}
    
    # 设置默认值
    default_options =  get_application_config().get_default_model_config()
    # 合并用户选项和默认选项
    merged_options = {**default_options, **options}
    model = merged_options["model"]

    # 处理重试配置 - 支持向后兼容性
    retry_config = merged_options.pop('retry_config', {})
    
    # 优先从 retry_config 中获取，然后从 merged_options 中获取（向后兼容）
    max_retries = retry_config.get('max_retries', merged_options.pop('max_retries', 3))
    base_delay = retry_config.get('base_delay', merged_options.pop('base_delay', 1.0))

    # 创建带重试机制的 ChatModel 实例
    if 'claude-sonnet-4' in model or 'claude-3-5-sonnet' in model:
        return ChatOpenAI4Anthropic(**merged_options)
    else:
        return ChatOpenAIWithRetry(max_retries=max_retries, base_delay=base_delay, **merged_options)


# 使用示例
if __name__ == "__main__":
    # 示例：初始化带重试机制的 LLM
    try:
        llm = init_llm()
        answer = llm.invoke('什么是土鸡蛋')
        print(answer.content)
    except LLMRetryError as e:
        print(f"LLM 重试失败: {e}")
    except Exception as e:
        print(f"LLM 调用失败: {e}")