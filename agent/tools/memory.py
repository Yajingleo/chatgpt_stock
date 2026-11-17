"""Model-callable memory tools: schemas, handlers, and result presentation."""

from typing import Any, Dict, Mapping

from agent.orchestration.context import AgentRunContext
from agent.tools.registry import ToolDefinition
from agent.domain import AnalysisRun, NewsArticle, Recommendation, SentimentAnalysis


def create_memory_tools(memory_service):
    def search_memory(args: Mapping[str, Any], context: AgentRunContext) -> Dict[str, Any]:
        items = memory_service.search(args.get("ticker"), args.get("limit"))
        return {"success": True, "memories": items, "count": len(items)}

    def get_memory(args: Mapping[str, Any], context: AgentRunContext) -> Dict[str, Any]:
        item = memory_service.get(args["run_id"])
        return {"success": bool(item), "memory": item, **({} if item else {"error": "Memory not found"})}

    return [
        ToolDefinition("search_analysis_memory", "Search prior analysis by ticker.",
                       {"type": "object", "properties": {"ticker": {"type": "string"}, "limit": {"type": "integer", "minimum": 1}}, "additionalProperties": False}, search_memory),
        ToolDefinition("get_analysis_memory", "Retrieve one prior analysis by run ID.",
                       {"type": "object", "properties": {"run_id": {"type": "string"}}, "required": ["run_id"], "additionalProperties": False}, get_memory),
    ]


def remember_analysis(context, memory_service):
    run = AnalysisRun(
        run_id=context.run_id,
        query=context.query,
        tickers=context.tickers,
        articles=[NewsArticle.from_dict(item) for item in context.news_data or []],
        sentiment=[SentimentAnalysis.from_pair(ticker, item) for ticker, item in (context.sentiment_data or {}).items()],
        recommendations=[Recommendation.from_dict(item) for item in context.recommendations or []],
    )
    return memory_service.remember(run)
