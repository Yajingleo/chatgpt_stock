"""Configured model-provider construction."""

from agent.config import settings
from agent.domain.model_io import ProviderConfigurationError


def create_model_provider(model_settings=None):
    config = model_settings or settings.model
    provider = config.provider.strip().lower()
    if provider in {"google", "google_adk", "adk"}:
        from agent.providers.ai.google_adk import GoogleADKModelProvider
        return GoogleADKModelProvider(api_key=config.google_api_key)
    if provider == "openai":
        from agent.providers.ai.openai import OpenAIModelProvider
        return OpenAIModelProvider(api_key=settings.openai.api_key)
    if provider == "anthropic":
        from agent.providers.ai.anthropic import AnthropicModelProvider
        return AnthropicModelProvider(api_key=config.anthropic_api_key)
    if provider == "deepseek":
        from agent.providers.ai.deepseek import DeepSeekModelProvider
        return DeepSeekModelProvider(config.deepseek_api_key, base_url=config.deepseek_base_url)
    raise ProviderConfigurationError(f"Unsupported MODEL_PROVIDER: {config.provider}")
