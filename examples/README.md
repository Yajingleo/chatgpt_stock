# Stock Agent Examples

The project exposes one provider-neutral `Orchestrator`. It chooses registered
market-data, news, sentiment, recommendation, and memory tools based on the
user's query.

```python
from agent import Orchestrator

agent = Orchestrator.from_settings()
result = await agent.run("Compare recent sentiment for AAPL and MSFT")

if result["success"]:
    print(result["answer"])
else:
    print(result["error"])
```

Select the model backend with `MODEL_PROVIDER` and `MODEL_NAME`, and configure
the matching API key. Supported providers are Google ADK/Gemini, OpenAI,
Anthropic, and DeepSeek.

Run the interactive example from the repository root:

```bash
python examples/general_agent_demo.py
```
