from typing import Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.language_models.base import LanguageModelInput

from kengine.utils.retryable_llm import ChatOpenAIWithRetry

class ChatOpenAI4Anthropic(ChatOpenAIWithRetry):
    
    def _get_request_payload(
        self,
        input_: LanguageModelInput,
        *,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> dict:
        payload = super()._get_request_payload(input_, stop=stop, **kwargs)
        # reset for anthropic claude api
        if "max_tokens" not in payload and "max_completion_tokens" in payload:
            payload["max_tokens"] = payload.pop("max_completion_tokens")
        return payload