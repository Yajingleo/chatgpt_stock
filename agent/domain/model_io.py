"""Provider-neutral model request and response types."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass(frozen=True)
class ModelResponse:
    content: str = ""
    tool_calls: List[ToolCall] = field(default_factory=list)
    usage: Optional[Dict[str, int]] = None


class ProviderError(RuntimeError):
    """A selected model provider could not complete the request."""


class ProviderConfigurationError(ProviderError):
    """A selected provider is missing credentials or dependencies."""
