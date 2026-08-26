"""A single source of truth for model schemas and Python tool dispatch."""

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Mapping

from agent.orchestration.context import AgentRunContext

ToolHandler = Callable[[Mapping[str, Any], AgentRunContext], Dict[str, Any]]
ResultPresenter = Callable[[Dict[str, Any]], Dict[str, Any]]


def _identity(result: Dict[str, Any]) -> Dict[str, Any]:
    return result


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: ToolHandler
    present_result: ResultPresenter = _identity

    def model_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolRegistry:
    """Immutable-by-convention registry used by both the model and dispatcher."""

    def __init__(self, definitions: Iterable[ToolDefinition]):
        self._definitions = {definition.name: definition for definition in definitions}
        if not self._definitions:
            raise ValueError("At least one tool definition is required")

    @property
    def schemas(self) -> List[Dict[str, Any]]:
        return [definition.model_schema() for definition in self._definitions.values()]

    def invoke(
        self,
        name: str,
        arguments: Mapping[str, Any],
        context: AgentRunContext,
    ) -> Dict[str, Any]:
        definition = self._definitions.get(name)
        if definition is None:
            return {"success": False, "error": f"Unknown function: {name}"}
        result = definition.handler(arguments, context)
        context.remember(name, result)
        return result

    def present(self, name: str, result: Dict[str, Any]) -> Dict[str, Any]:
        definition = self._definitions.get(name)
        return definition.present_result(result) if definition else result
