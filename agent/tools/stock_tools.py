"""Service-backed tools available to the single orchestrator."""

from typing import Any, Dict, Mapping

from agent.domain import AnalysisRun, NewsArticle, Recommendation, SentimentAnalysis
from agent.orchestration.context import AgentRunContext
from agent.tools.registry import ToolDefinition, ToolRegistry


def create_stock_tool_registry(stock_service, memory_service) -> ToolRegistry:
    def momentum(args: Mapping[str, Any], context: AgentRunContext) -> Dict[str, Any]:
        result = stock_service.momentum(args.get("lookback_days"))
        if result.get("success"):
            context.tickers = list(result.get("tickers", []))
        return result

    def news(args: Mapping[str, Any], context: AgentRunContext) -> Dict[str, Any]:
        context.tickers = [str(item).upper() for item in args["tickers"]]
        result = stock_service.news(context.tickers, args.get("limit"))
        if result.get("success"):
            context.news_data = result.get("news_data", [])
        return result

    def sentiment(args: Mapping[str, Any], context: AgentRunContext) -> Dict[str, Any]:
        if not context.news_data:
            return {"success": False, "error": "Fetch news before sentiment analysis"}
        result = stock_service.sentiment(context.news_data)
        if result.get("success"):
            context.sentiment_data = result.get("sentiment_analysis", {})
            _remember(context, memory_service)
        return result

    def recommendations(args: Mapping[str, Any], context: AgentRunContext) -> Dict[str, Any]:
        if not context.sentiment_data:
            return {"success": False, "error": "Analyze sentiment before generating recommendations"}
        result = stock_service.recommendations(context.sentiment_data)
        if result.get("success"):
            context.recommendations = result.get("recommendations", [])
            result["run_id"] = _remember(context, memory_service)
        return result

    def search_memory(args: Mapping[str, Any], context: AgentRunContext) -> Dict[str, Any]:
        items = memory_service.search(args.get("ticker"), args.get("limit"))
        return {"success": True, "memories": items, "count": len(items)}

    def get_memory(args: Mapping[str, Any], context: AgentRunContext) -> Dict[str, Any]:
        item = memory_service.get(args["run_id"])
        return {"success": bool(item), "memory": item, **({} if item else {"error": "Memory not found"})}

    empty = {"type": "object", "properties": {}, "additionalProperties": False}
    return ToolRegistry([
        ToolDefinition("get_sp500_recommendations", "Get top S&P 500 momentum stocks.",
                       {"type": "object", "properties": {"lookback_days": {"type": "integer", "minimum": 1}}, "additionalProperties": False}, momentum),
        ToolDefinition("fetch_stock_news", "Fetch recent news for stock tickers.",
                       {"type": "object", "properties": {"tickers": {"type": "array", "items": {"type": "string"}, "minItems": 1}, "limit": {"type": "integer", "minimum": 1}}, "required": ["tickers"], "additionalProperties": False}, news, _present_news),
        ToolDefinition("analyze_sentiment", "Analyze news fetched during this run.", empty, sentiment, _present_sentiment),
        ToolDefinition("generate_recommendations", "Generate research signals from analyzed sentiment.", empty, recommendations, _present_recommendations),
        ToolDefinition("search_analysis_memory", "Search prior analysis by ticker.",
                       {"type": "object", "properties": {"ticker": {"type": "string"}, "limit": {"type": "integer", "minimum": 1}}, "additionalProperties": False}, search_memory),
        ToolDefinition("get_analysis_memory", "Retrieve one prior analysis by run ID.",
                       {"type": "object", "properties": {"run_id": {"type": "string"}}, "required": ["run_id"], "additionalProperties": False}, get_memory),
    ])


def _remember(context, memory_service):
    run = AnalysisRun(
        run_id=context.run_id,
        query=context.query,
        tickers=context.tickers,
        articles=[NewsArticle.from_dict(item) for item in context.news_data or []],
        sentiment=[SentimentAnalysis.from_pair(ticker, item) for ticker, item in (context.sentiment_data or {}).items()],
        recommendations=[Recommendation.from_dict(item) for item in context.recommendations or []],
    )
    return memory_service.remember(run)


def _present_news(result):
    if not result.get("success"):
        return result
    articles = result.get("news_data", [])
    return {"success": True, "news_count": result.get("news_count", len(articles)),
            "news_data": [{"ticker": a.get("ticker", ""), "title": a.get("title", "")[:200],
                           "summary": a.get("summary", "")[:500], "url": a.get("url", ""),
                           "published": a.get("published", "")} for a in articles[:50]]}


def _present_sentiment(result):
    if not result.get("success"):
        return result
    values = result.get("sentiment_analysis", {})
    return {"success": True, "sentiment_analysis": {
        ticker: {"sentiment_score": data.get("sentiment_score", 0), "news_count": data.get("news_count", 0),
                 "confidence": data.get("confidence", "low"), "key_phrases": data.get("key_phrases", [])[:3]}
        for ticker, data in list(values.items())[:30]}}


def _present_recommendations(result):
    if not result.get("success"):
        return result
    return {"success": True, "run_id": result.get("run_id"),
            "recommendations": result.get("recommendations", [])[:20],
            "total_analyzed": result.get("total_analyzed", len(result.get("recommendations", [])))}
