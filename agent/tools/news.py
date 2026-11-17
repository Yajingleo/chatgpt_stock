"""Model-callable news tools: schemas, handlers, and result presentation."""

from typing import Any, Dict, Mapping

from agent.orchestration.context import AgentRunContext
from agent.tools.registry import ToolDefinition


def create_news_tools(stock_service):
    def news(args: Mapping[str, Any], context: AgentRunContext) -> Dict[str, Any]:
        # A new fetch invalidates derived state, even if the fetch fails.
        context.news_data = None
        context.sentiment_data = None
        context.recommendations = None
        context.tickers = [str(item).upper() for item in args["tickers"]]
        result = stock_service.news(context.tickers, args.get("limit"))
        if result.get("success"):
            context.news_data = result.get("news_data", [])
        return result

    return [
        ToolDefinition("fetch_stock_news", "Fetch recent news for stock tickers.",
                       {"type": "object", "properties": {"tickers": {"type": "array", "items": {"type": "string"}, "minItems": 1}, "limit": {"type": "integer", "minimum": 1}}, "required": ["tickers"], "additionalProperties": False}, news, _present_news),
    ]


def _present_news(result):
    if not result.get("success"):
        return result
    articles = result.get("news_data", [])
    return {"success": True, "news_count": result.get("news_count", len(articles)),
            "news_data": [{"ticker": a.get("ticker", ""), "title": a.get("title", "")[:200],
                           "summary": a.get("summary", "")[:500], "url": a.get("url", ""),
                           "published": a.get("published", "")} for a in articles[:50]]}
