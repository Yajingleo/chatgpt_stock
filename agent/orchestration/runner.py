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
                  progress_callback: Optional[ProgressCallback] = None) -> Dict[str, Any]:
        context = AgentRunContext(query=query)
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]
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
                messages.append({"role": "tool", "tool_call_id": call.id, "name": call.name,
                                 "content": json.dumps(self.registry.present(call.name, result), default=str)})

        return {"success": False, "error": f"Orchestrator exceeded maximum iterations ({max_iterations})",
                "query": query, "partial_answer": messages[-1].get("content")}
