"""The single public stock-analysis orchestrator."""

from typing import Any, Optional

from agent.config import settings
from agent.domain.model_io import ProviderConfigurationError
from agent.orchestration.runner import ToolCallingRunner
from agent.providers.ai import create_model_provider
from agent.providers.market import YFinanceMarketProvider
from agent.providers.memory import FileSystemMemoryStore
from agent.providers.news import HttpNewsProvider
from agent.services import AnalysisMemoryService, StockAnalysisService
from agent.tools.stock_tools import create_stock_tool_registry
from agent.utils import get_logger


SYSTEM_PROMPT = """You are a stock research orchestrator with tools for current market data,
news, sentiment, research signals, and prior analysis memory. Use tools instead
of inventing current facts. For a complete analysis, select momentum stocks,
fetch news, analyze sentiment, then generate recommendations. Clearly separate
observed data from interpretation and never present research as personalized
financial advice. Recall prior memory only when the user asks or it is directly
relevant, and label historical results with their date.
"""


class Orchestrator:
    """Coordinate model-selected stock-analysis services and memory."""

    def __init__(self, model_provider, stock_service, memory_service, *, model: str,
                 temperature: float = 0.1, registry=None, configuration_error: Optional[str] = None):
        self.logger = get_logger("agent.orchestrator")
        self.model_provider = model_provider
        self.stock_service = stock_service
        self.memory_service = memory_service
        self.model = model
        self.temperature = temperature
        self.configuration_error = configuration_error
        self.registry = registry or create_stock_tool_registry(stock_service, memory_service)

    @classmethod
    def from_settings(cls) -> "Orchestrator":
        stock_service = StockAnalysisService(YFinanceMarketProvider(), HttpNewsProvider())
        memory_service = AnalysisMemoryService(
            FileSystemMemoryStore(settings.memory.directory),
            enabled=settings.memory.enabled,
            default_limit=settings.memory.search_limit,
        )
        try:
            provider = create_model_provider(settings.model)
            error = None
        except ProviderConfigurationError as exc:
            provider = None
            error = str(exc)
        return cls(provider, stock_service, memory_service, model=settings.model.name,
                   temperature=settings.model.temperature, configuration_error=error)

    async def run(self, query: str, max_iterations: int = 10, progress_callback=None) -> dict:
        if self.configuration_error or self.model_provider is None:
            return {"success": False, "error": self.configuration_error or "Model provider unavailable",
                    "query": query}
        if not isinstance(query, str) or not query.strip():
            return {"success": False, "error": "A non-empty query is required", "query": query}
        runner = ToolCallingRunner(self.model_provider, self.model, self.registry, self.logger, self.temperature)
        return await runner.run(query.strip(), SYSTEM_PROMPT, max_iterations, progress_callback)
