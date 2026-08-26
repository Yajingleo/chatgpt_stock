"""OpenAI chat-completions adapter."""

import asyncio
import json
from typing import Any, Dict, List, Optional

from agent.domain.model_io import ModelResponse, ProviderConfigurationError, ProviderError, ToolCall


def _to_openai_messages(messages):
    """Translate provider-neutral tool history to OpenAI chat-completion messages."""
    translated = []
    for message in messages:
        item = dict(message)
        if item.get("role") == "assistant" and item.get("tool_calls"):
            tool_calls = []
            for call in item["tool_calls"]:
                if call.get("type") == "function" and "function" in call:
                    tool_calls.append(call)
                    continue
                arguments = call.get("arguments", {})
                tool_calls.append({
                    "id": call["id"],
                    "type": "function",
                    "function": {
                        "name": call["name"],
                        "arguments": json.dumps(arguments),
                    },
                })
            item["tool_calls"] = tool_calls
        translated.append(item)
    return translated


class OpenAIModelProvider:
    def __init__(self, api_key: Optional[str] = None, client: Any = None, base_url: Optional[str] = None):
        if client is not None:
            self.client = client
            return
        try:
            from openai import OpenAI
        except ImportError as error:
            raise ProviderConfigurationError("The openai package is not installed") from error
        if not api_key:
            raise ProviderConfigurationError("OPENAI_API_KEY is required")
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = OpenAI(**kwargs)

    async def complete(self, messages, tools, model, temperature) -> ModelResponse:
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=model,
                messages=_to_openai_messages(messages),
                tools=tools,
                tool_choice="auto",
                temperature=temperature,
            )
            message = response.choices[0].message
            calls = []
            for call in message.tool_calls or []:
                calls.append(ToolCall(call.id, call.function.name, json.loads(call.function.arguments or "{}")))
            usage = None
            if getattr(response, "usage", None):
                usage = {
                    "input_tokens": getattr(response.usage, "prompt_tokens", 0),
                    "output_tokens": getattr(response.usage, "completion_tokens", 0),
                }
            return ModelResponse(message.content or "", calls, usage)
        except ProviderConfigurationError:
            raise
        except Exception as error:
            raise ProviderError(f"OpenAI request failed: {error}") from error
