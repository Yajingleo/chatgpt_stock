"""Unit tests for provider-independent agent orchestration."""

import asyncio
import json
import logging
import unittest
from types import SimpleNamespace
from agent.orchestration.context import AgentRunContext
from agent.domain.model_io import ModelResponse, ToolCall
from agent.orchestration.runner import ToolCallingRunner
from agent.providers.ai.openai import OpenAIModelProvider
from agent.tools.registry import ToolDefinition, ToolRegistry


class FakeProvider:
    def __init__(self, responses):
        self._responses = iter(responses)
        self.requests = []

    async def complete(self, messages, tools, model, temperature):
        self.requests.append({"messages": list(messages), "tools": tools, "model": model})
        return next(self._responses)


class FakeOpenAICompletions:
    def __init__(self):
        self.request = None

    def create(self, **kwargs):
        self.request = kwargs
        message = SimpleNamespace(content="News fetched", tool_calls=[])
        return SimpleNamespace(choices=[SimpleNamespace(message=message)], usage=None)


class ToolRegistryTest(unittest.TestCase):
    def test_schema_and_dispatch_come_from_same_definition(self):
        definition = ToolDefinition(
            name="echo",
            description="Echo a value",
            parameters={"type": "object", "properties": {"value": {"type": "string"}}},
            handler=lambda args, context: {"success": True, "message": args["value"]},
        )
        registry = ToolRegistry([definition])
        context = AgentRunContext(query="hello")

        result = registry.invoke("echo", {"value": "hello"}, context)

        self.assertEqual("echo", registry.schemas[0]["function"]["name"])
        self.assertEqual("hello", result["message"])
        self.assertIs(result, context.tool_results["echo"])

    def test_unknown_tool_is_a_structured_error(self):
        registry = ToolRegistry([
            ToolDefinition("known", "Known", {"type": "object"}, lambda args, ctx: {})
        ])
        result = registry.invoke("missing", {}, AgentRunContext(query="test"))
        self.assertFalse(result["success"])


class ToolCallingRunnerTest(unittest.TestCase):
    def test_executes_tool_then_returns_final_answer(self):
        seen_contexts = []

        def handler(args, context):
            seen_contexts.append(context)
            return {"success": True, "message": args["value"]}

        registry = ToolRegistry([
            ToolDefinition(
                "echo",
                "Echo",
                {"type": "object", "properties": {"value": {"type": "string"}}},
                handler,
            )
        ])
        provider = FakeProvider([
            ModelResponse(tool_calls=[ToolCall("call-1", "echo", {"value": "AAPL"})]),
            ModelResponse(content="AAPL complete"),
        ])
        runner = ToolCallingRunner(provider, "test-model", registry, logging.getLogger("test"))

        result = asyncio.run(runner.run("analyze AAPL", "system"))

        self.assertTrue(result["success"])
        self.assertEqual("AAPL complete", result["answer"])
        self.assertEqual(2, result["iterations"])
        tool_message = next(
            message
            for message in provider.requests[1]["messages"]
            if message["role"] == "tool"
        )
        self.assertEqual("tool", tool_message["role"])
        self.assertEqual("AAPL", json.loads(tool_message["content"])["message"])
        self.assertEqual("analyze AAPL", seen_contexts[0].query)

    def test_each_run_receives_a_new_context(self):
        contexts = []
        registry = ToolRegistry([
            ToolDefinition(
                "record",
                "Record",
                {"type": "object", "properties": {}},
                lambda args, context: contexts.append(context) or {"success": True},
            )
        ])

        for query in ("first", "second"):
            provider = FakeProvider([
                ModelResponse(tool_calls=[ToolCall("call", "record", {})]),
                ModelResponse(content="done"),
            ])
            runner = ToolCallingRunner(provider, "model", registry, logging.getLogger("test"))
            asyncio.run(runner.run(query, "system"))

        self.assertIsNot(contexts[0], contexts[1])
        self.assertEqual(["first", "second"], [context.query for context in contexts])


class OpenAIModelProviderTest(unittest.TestCase):
    def test_serializes_provider_neutral_tool_calls_for_openai(self):
        completions = FakeOpenAICompletions()
        client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
        provider = OpenAIModelProvider(client=client)
        messages = [
            {"role": "user", "content": "Crawl news for AAPL"},
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [{"id": "call-1", "name": "fetch_news", "arguments": {"tickers": ["AAPL"]}}],
            },
            {"role": "tool", "tool_call_id": "call-1", "name": "fetch_news", "content": "{}"},
        ]

        result = asyncio.run(provider.complete(messages, [], "test-model", 0.1))

        serialized = completions.request["messages"][1]["tool_calls"][0]
        self.assertEqual("function", serialized["type"])
        self.assertEqual("fetch_news", serialized["function"]["name"])
        self.assertEqual({"tickers": ["AAPL"]}, json.loads(serialized["function"]["arguments"]))
        self.assertEqual("News fetched", result.content)


if __name__ == "__main__":
    unittest.main()
