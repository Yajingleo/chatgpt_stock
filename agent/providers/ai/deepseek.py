"""DeepSeek adapter using its OpenAI-compatible API."""

from typing import Any, Optional

from agent.domain.model_io import ProviderConfigurationError
from agent.providers.ai.openai import OpenAIModelProvider


class DeepSeekModelProvider(OpenAIModelProvider):
    def __init__(self, api_key: Optional[str] = None, client: Any = None, base_url: str = "https://api.deepseek.com"):
        if client is None and not api_key:
            raise ProviderConfigurationError("DEEPSEEK_API_KEY is required")
        super().__init__(api_key=api_key, client=client, base_url=base_url)
