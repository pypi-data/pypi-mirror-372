import logging
import time
import json
from typing import Optional, Any, List

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.language_models.base import LanguageModelInput
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI


logger = logging.getLogger(__name__)

class LLMRetryError(Exception):
    """LLM 重试相关异常"""
    pass


class ChatOpenAIWithRetry(ChatOpenAI):
    """
    带有 504 错误重试机制的 ChatOpenAI
    
    该类继承自 ChatOpenAI，为其 invoke 方法添加重试功能：
    - 检测 504 Gateway Timeout 错误
    - 最多重试 3 次
    - 指数退避重试间隔
    - 完全兼容 ChatOpenAI 接口
    - 添加性能监控
    """
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, **kwargs):
        """
        初始化带重试机制的 ChatOpenAI
        
        Args:
            max_retries: 最大重试次数，默认 3 次
            base_delay: 基础延迟时间（秒），默认 1.0 秒
            **kwargs: ChatOpenAI 的其他参数
        """
        super().__init__(**kwargs)
        self._max_retries = max_retries
        self._base_delay = base_delay
    
    def _is_504_error(self, exception: Exception) -> bool:
        """
        检测是否为 504 Gateway Timeout 错误
        
        Args:
            exception: 捕获的异常
            
        Returns:
            bool: 如果是 504 错误返回 True，否则返回 False
        """
        # 首先检查 HTTP 状态码（如果异常有 response 属性）
        if hasattr(exception, 'response') and hasattr(exception.response, 'status_code'):
            return exception.response.status_code == 504
        
        # 检查其他可能的 504 错误属性
        if hasattr(exception, 'status_code'):
            return exception.status_code == 504
        
        # 检查异常消息中是否包含 504 相关信息
        error_message = str(exception).lower()
        
        # 常见的 504 错误标识（更精确的匹配）
        if '504' in error_message:
            return True
        
        # 只有在明确包含 gateway timeout 相关词汇时才认为是 504 错误
        gateway_timeout_indicators = [
            'gateway timeout',
            'gateway time-out',
            'gateway timed out'
        ]
        
        if any(indicator in error_message for indicator in gateway_timeout_indicators):
            return True
            
        return False
    
    def _is_902_error(self, result: BaseMessage) -> bool:
        """
        当返回response信息为 如下信息时
         {'code': '9002', 'message': '{"message":"The system encountered an unexpected error during processing. Try your request again."}'}
        """
        content = result.content
        if content and (content.strip().startswith('{\'code\':') or content.strip().startswith('{"code":')):
            try:
                # 尝试直接解析JSON格式
                result_json = json.loads(content.strip())
                if result_json.get('code', None) == '9002':
                    return True
            except json.JSONDecodeError:
                try:
                    # 如果JSON解析失败，尝试使用ast.literal_eval解析Python字典格式
                    import ast
                    result_dict = ast.literal_eval(content.strip())
                    if result_dict.get('code', None) == '9002':
                        return True
                except:
                    logger.warning(f'llm invoke return unexpected content {content}')
                    return False
            except:
                logger.warning(f'llm invoke return unexpected content {content}')
                return False
        return False
        
    
    def _calculate_delay(self, attempt: int) -> float:
        """
        计算重试延迟时间（指数退避）
        
        Args:
            attempt: 当前重试次数（从 1 开始）
            
        Returns:
            float: 延迟时间（秒）
        """
        return self._base_delay * (2 ** (attempt - 1))
    
    def invoke(
        self,
        input: LanguageModelInput,
        config: Optional[RunnableConfig] = None,
        *,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> BaseMessage:
        """
        带重试机制的 invoke 方法
        
        Args:
            input: 输入消息
            config: 运行配置
            stop: 停止词列表
            **kwargs: 其他参数
            
        Returns:
            BaseMessage: LLM 响应消息
            
        Raises:
            LLMRetryError: 重试次数耗尽后仍然失败
            Exception: 非 504 错误直接抛出
        """
        last_exception = None
        
        for attempt in range(1, self._max_retries + 2):  # +2 因为包含初始尝试
            try:
                start_time = time.time()
                logger.debug(f"LLM invoke 尝试 {attempt}/{self._max_retries + 1}")
                
                # 调用父类的 invoke 方法
                result = super().invoke(
                    input=input,
                    config=config,
                    stop=stop,
                    **kwargs
                )
                
                # 记录性能指标
                elapsed_time = time.time() - start_time
                logger.info(f"LLM调用完成，耗时: {elapsed_time:.2f}秒")
                
                if elapsed_time > 30:  # 超过30秒的调用记录警告
                    logger.warning(f"LLM调用耗时过长: {elapsed_time:.2f}秒")
                
                if self._is_902_error(result):
                    logger.warning(f'LLM invoke response 902 error {result} retry again')
                    if attempt > self._max_retries:
                        logger.error(f"LLM invoke 重试 {self._max_retries} 次后仍然失败: {result}")
                        raise LLMRetryError(
                            f"LLM invoke 在重试 {self._max_retries} 次后仍然遇到 902 错误: {result}"
                        ) 
                    
                    delay = self._calculate_delay(attempt)
                    time.sleep(delay)
                    continue
                    
                
                # 成功则返回结果
                if attempt > 1:
                    logger.info(f"LLM invoke 在第 {attempt} 次尝试后成功")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                # 如果不是 504 错误，直接抛出
                if not self._is_504_error(e):
                    logger.error(f"LLM invoke 遇到非 504 错误: {e}")
                    raise e
                
                # 如果是最后一次尝试，不再重试
                if attempt > self._max_retries:
                    logger.error(f"LLM invoke 重试 {self._max_retries} 次后仍然失败: {e}")
                    raise LLMRetryError(
                        f"LLM invoke 在重试 {self._max_retries} 次后仍然遇到 504 错误: {e}"
                    ) from e
                
                # 计算延迟时间并等待
                delay = self._calculate_delay(attempt)
                logger.warning(f"LLM invoke 遇到 504 错误，{delay:.1f}秒后进行第 {attempt + 1} 次重试: {e}")
                time.sleep(delay)
        
        # 理论上不会到达这里，但为了安全起见
        raise LLMRetryError(f"LLM invoke 重试失败: {last_exception}") from last_exception
