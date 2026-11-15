"""Provider-neutral model/tool execution loop."""

import asyncio
import json
from typing import Any, Callable, Dict, List, Optional

from agent.orchestration.context import AgentRunContext
from agent.tools.registry import ToolRegistry

ProgressCallback = Callable[[str, str, Optional[str]], None]


class ToolCallingRunner:
    def __init__(self, provider, model: str, registry: ToolRegistry, logger, temperature: float = 0.1):
        self.provider = provider
        self.model = model
        self.registry = registry
        self.logger = logger
        self.temperature = temperature

    async def run(self, query: str, system_prompt: str, max_iterations: int = 10,
                  progress_callback: Optional[ProgressCallback] = None, history=None) -> Dict[str, Any]:
        if isinstance(max_iterations, bool) or not isinstance(max_iterations, int) or max_iterations < 1:
            return {"success": False, "error": "max_iterations must be a positive integer", "query": query}
        context = AgentRunContext(query=query)
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
        ]
        # Only prior conversation text is accepted: callers cannot inject system
        # instructions or incomplete tool exchanges through conversation history.
        for message in list(history or [])[-20:]:
            if (isinstance(message, dict) and message.get("role") in ("user", "assistant")
                    and isinstance(message.get("content"), str)):
                messages.append({"role": message["role"], "content": message["content"]})
        messages.append({"role": "user", "content": query})
        for iteration in range(1, max_iterations + 1):
            try:
                response = await self.provider.complete(messages, self.registry.schemas, self.model, self.temperature)
            except Exception as error:
                self.logger.error("Model request failed: %s", error, exc_info=True)
                return {"success": False, "error": str(error), "query": query}

            messages.append({
                "role": "assistant",
                "content": response.content,
                "tool_calls": [{"id": call.id, "name": call.name, "arguments": call.arguments}
                               for call in response.tool_calls],
            })
            if not response.tool_calls:
                if progress_callback:
                    progress_callback("complete", "Analysis complete", "Orchestrator finished")
                result = {"success": True, "answer": response.content, "iterations": iteration, "query": query}
                if context.sentiment_data or context.recommendations:
                    result["run_id"] = context.run_id
                return result

            for call in response.tool_calls:
                if progress_callback:
                    progress_callback(call.name, f"Executing {call.name}...", f"Arguments: {call.arguments}")
                try:
                    result = await asyncio.to_thread(self.registry.invoke, call.name, call.arguments, context)
                except Exception as error:
                    self.logger.error("Tool %s failed: %s", call.name, error, exc_info=True)
                    result = {"success": False, "error": str(error)}
                if progress_callback and result.get("success") and result.get("tables"):
                    for name, table in result["tables"].items():
                        progress_callback("dataframe", name, table)
                messages.append({"role": "tool", "tool_call_id": call.id, "name": call.name,
                                 "content": json.dumps(self.registry.present(call.name, result), default=str)})

        return {"success": False, "error": f"Orchestrator exceeded maximum iterations ({max_iterations})",
                "query": query, "partial_answer": messages[-1].get("content")}
