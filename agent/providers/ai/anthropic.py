"""Anthropic messages adapter."""

import asyncio
import json
from typing import Any, Optional

from agent.domain.model_io import ModelResponse, ProviderConfigurationError, ProviderError, ToolCall


class AnthropicModelProvider:
    def __init__(self, api_key: Optional[str] = None, client: Any = None):
        if client is not None:
            self.client = client
            return
        try:
            from anthropic import Anthropic
        except ImportError as error:
            raise ProviderConfigurationError("The anthropic package is not installed") from error
        if not api_key:
            raise ProviderConfigurationError("ANTHROPIC_API_KEY is required")
        self.client = Anthropic(api_key=api_key)

    async def complete(self, messages, tools, model, temperature) -> ModelResponse:
        system = "\n".join(message.get("content", "") for message in messages if message["role"] == "system")
        conversation = [message for message in messages if message["role"] != "system"]
        anthropic_tools = [
            {
                "name": item["function"]["name"],
                "description": item["function"]["description"],
                "input_schema": item["function"]["parameters"],
            }
            for item in tools
        ]
        try:
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=model,
                system=system,
                messages=conversation,
                tools=anthropic_tools,
                temperature=temperature,
                max_tokens=2048,
            )
            text = "".join(block.text for block in response.content if getattr(block, "type", None) == "text")
            calls = [
                ToolCall(block.id, block.name, dict(block.input))
                for block in response.content
                if getattr(block, "type", None) == "tool_use"
            ]
            usage = {
                "input_tokens": getattr(response.usage, "input_tokens", 0),
                "output_tokens": getattr(response.usage, "output_tokens", 0),
            }
            return ModelResponse(text, calls, usage)
        except Exception as error:
            raise ProviderError(f"Anthropic request failed: {error}") from error
