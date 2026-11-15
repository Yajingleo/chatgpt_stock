"""Model-callable sentiment tools: schemas, handlers, and result presentation."""

from typing import Any, Dict, Mapping

from agent.orchestration.context import AgentRunContext
from agent.tools.registry import ToolDefinition
from agent.tools.memory import remember_analysis


def create_sentiment_tools(stock_service, memory_service):
    def sentiment(args: Mapping[str, Any], context: AgentRunContext) -> Dict[str, Any]:
        context.sentiment_data = None
        context.recommendations = None
        if not context.news_data:
            return {"success": False, "error": "Fetch news before sentiment analysis"}
        result = stock_service.sentiment(context.news_data)
        if result.get("success"):
            context.sentiment_data = result.get("sentiment_analysis", {})
            remember_analysis(context, memory_service)
        return result

    empty = {"type": "object", "properties": {}, "additionalProperties": False}
    return [
        ToolDefinition("analyze_sentiment", "Analyze news fetched during this run.", empty, sentiment, _present_sentiment),
    ]


def _present_sentiment(result):
    if not result.get("success"):
        return result
    values = result.get("sentiment_analysis", {})
    return {"success": True, "sentiment_analysis": {
        ticker: {"sentiment_score": data.get("sentiment_score", 0), "news_count": data.get("news_count", 0),
                 "confidence": data.get("confidence", "low"), "key_phrases": data.get("key_phrases", [])[:3]}
        for ticker, data in list(values.items())[:30]}}
