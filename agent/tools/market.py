"""Model-callable market tools: schemas, handlers, and result presentation."""

from typing import Any, Dict, Mapping

from agent.orchestration.context import AgentRunContext
from agent.tools.registry import ToolDefinition


def create_market_tools(stock_service):
    def momentum(args: Mapping[str, Any], context: AgentRunContext) -> Dict[str, Any]:
        result = stock_service.momentum(args.get("lookback_days"))
        if result.get("success"):
            context.tickers = list(result.get("tickers", []))
        return result

    def fundamentals(args: Mapping[str, Any], context: AgentRunContext) -> Dict[str, Any]:
        return stock_service.fundamentals([str(item).upper() for item in args["tickers"]])

    return [
        ToolDefinition("get_stock_fundamentals",
                       "Fetch company fundamentals for specified tickers: valuation, revenue, margins, sector, debt, and business summary. Independent of news and momentum screening. Values may be cached; missing fields are unavailable, not zero.",
                       {"type": "object", "properties": {"tickers": {"type": "array", "items": {"type": "string"}, "minItems": 1}}, "required": ["tickers"], "additionalProperties": False}, fundamentals),
        ToolDefinition("get_sp500_recommendations", "Run S&P 500 analysis and return top/bottom energy and return dataframes plus selected tickers.",
                       {"type": "object", "properties": {"lookback_days": {"type": "integer", "minimum": 1}}, "additionalProperties": False}, momentum),
    ]
