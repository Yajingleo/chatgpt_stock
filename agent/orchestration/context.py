"""State owned by one agent invocation."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import uuid4


@dataclass
class AgentRunContext:
    """Intermediate data for one run; never shared between users or requests."""

    query: str
    run_id: str = field(default_factory=lambda: uuid4().hex)
    tickers: List[str] = field(default_factory=list)
    news_data: Optional[List[Dict[str, Any]]] = None
    sentiment_data: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    tool_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def remember(self, tool_name: str, result: Dict[str, Any]) -> None:
        self.tool_results[tool_name] = result
