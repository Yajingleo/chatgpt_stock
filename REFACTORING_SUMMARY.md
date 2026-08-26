# Refactoring Summary

## Status

The application now uses a single provider-neutral `Orchestrator` as its public
agent API. The legacy `agent.agents`, `agent.analysis`, and `agent.data`
packages have been replaced and removed.

## Architecture

- `agent/domain`: provider-neutral request, response, and tool-call models
- `agent/orchestration`: per-run state and the model/tool execution loop
- `agent/providers`: AI, market, news, SEC, and memory adapters
- `agent/services`: stock analysis, sentiment, recommendations, and memory logic
- `agent/tools`: shared schemas, dispatch, and presentation boundaries
- `web`: chat UI and HTTP integration using the public orchestrator

The model backend is selected with `MODEL_PROVIDER` and `MODEL_NAME`. Supported
adapters are Google ADK/Gemini, OpenAI, Anthropic, and DeepSeek.

## Public API

```python
from agent import Orchestrator

agent = Orchestrator.from_settings()
result = await agent.run("Analyze AAPL using recent market data and news")
```

## Verification

Bazel builds the core library, web server, launcher, and examples. Bazel tests
cover the provider-neutral orchestration loop and persistent-cache behavior for
market fundamentals, S&P 500 data, HTTP news, and SEC CIK lookup.

Last updated: 2026-08-25
