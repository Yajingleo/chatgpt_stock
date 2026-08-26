"""Google ADK/Gemini model adapter with normalized tool calls."""

import asyncio
from typing import Any, Optional

from agent.domain.model_io import ModelResponse, ProviderConfigurationError, ProviderError, ToolCall


class GoogleADKModelProvider:
    """Use the Gemini client installed with Google ADK as a model backend."""

    def __init__(self, api_key: Optional[str] = None, client: Any = None):
        if client is not None:
            self.client = client
            return
        try:
            import google.adk  # noqa: F401 - verifies the requested runtime
            from google import genai
        except ImportError as error:
            raise ProviderConfigurationError("google-adk and google-genai are required") from error
        if not api_key:
            raise ProviderConfigurationError("GOOGLE_API_KEY is required")
        self.client = genai.Client(api_key=api_key)

    async def complete(self, messages, tools, model, temperature) -> ModelResponse:
        system = "\n".join(message.get("content", "") for message in messages if message["role"] == "system")
        contents = [message for message in messages if message["role"] != "system"]
        declarations = [item["function"] for item in tools]
        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=model,
                contents=contents,
                config={
                    "system_instruction": system,
                    "temperature": temperature,
                    "tools": [{"function_declarations": declarations}],
                },
            )
            calls = []
            for index, call in enumerate(getattr(response, "function_calls", None) or []):
                calls.append(ToolCall(f"google-{index}", call.name, dict(call.args or {})))
            return ModelResponse(getattr(response, "text", "") or "", calls)
        except Exception as error:
            raise ProviderError(f"Google ADK request failed: {error}") from error
