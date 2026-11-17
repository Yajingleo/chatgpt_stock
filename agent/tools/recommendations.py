"""Model-callable recommendations tools: schemas, handlers, and result presentation."""

from typing import Any, Dict, Mapping

from agent.orchestration.context import AgentRunContext
from agent.tools.registry import ToolDefinition
from agent.tools.memory import remember_analysis


def create_recommendations_tools(stock_service, memory_service):
    def recommendations(args: Mapping[str, Any], context: AgentRunContext) -> Dict[str, Any]:
        if not context.sentiment_data:
            return {"success": False, "error": "Analyze sentiment before generating recommendations"}
        result = stock_service.recommendations(context.sentiment_data)
        if result.get("success"):
            context.recommendations = result.get("recommendations", [])
            result["run_id"] = remember_analysis(context, memory_service)
        return result

    empty = {"type": "object", "properties": {}, "additionalProperties": False}
    return [
        ToolDefinition("generate_recommendations", "Generate research signals from analyzed sentiment.", empty, recommendations, _present_recommendations),
    ]


def _present_recommendations(result):
    if not result.get("success"):
        return result
    return {"success": True, "run_id": result.get("run_id"),
            "recommendations": result.get("recommendations", [])[:20],
            "total_analyzed": result.get("total_analyzed", len(result.get("recommendations", [])))}
