"""Protocols implemented by external adapters."""

from typing import Any, Dict, List, Protocol

from agent.domain.model_io import ModelResponse


class ModelProvider(Protocol):
    async def complete(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        model: str,
        temperature: float,
    ) -> ModelResponse:
        ...
