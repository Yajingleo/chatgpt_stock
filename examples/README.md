# Stock Agent Examples

This directory contains examples showing different ways to use the stock analysis agents.

## Available Agents

### 1. StockNewsADKAgent (Workflow-based)

**Location:** `stock_agent/agents/workflow_agent.py`

**How it works:**
- Runs a **fixed workflow** regardless of user input
- Always executes: SP500 analysis → News fetching → Sentiment analysis → Recommendations
- Designed for batch processing and scheduled runs

**When to use:**
- Daily/scheduled analysis
- Consistent reporting
- When you want the full pipeline every time

**Example:**
```python
from stock_agent.agents import StockNewsADKAgent

agent = StockNewsADKAgent()
result = await agent.run_analysis("Any query here")  # Always runs full workflow
```

---

### 2. GeneralStockAgent (Function calling)

**Location:** `stock_agent/agents/general_agent.py`

**How it works:**
- Uses **OpenAI function calling** to dynamically decide which tools to use
- GPT-4 interprets the query and calls appropriate tools in the right order
- Different queries trigger different tool combinations

**When to use:**
- Interactive chat/Q&A
- Ad-hoc analysis
- When users ask varied questions

**Example:**
```python
from stock_agent.agents import GeneralStockAgent

agent = GeneralStockAgent()

# Different queries trigger different tools:
await agent.run("What's the sentiment on AAPL?")
# → Calls: fetch_stock_news(["AAPL"]) → analyze_sentiment()

await agent.run("Give me stock recommendations")
# → Calls: get_sp500_recommendations() → fetch_stock_news() → analyze_sentiment() → generate_recommendations()

await agent.run("Show me news for Tesla")
# → Calls: fetch_stock_news(["TSLA"]) only
```

---

## Comparison

| Feature | StockNewsADKAgent | GeneralStockAgent |
|---------|-------------------|-------------------|
| **Query handling** | Ignores query, fixed workflow | Interprets query dynamically |
| **Tools called** | Always all 4 tools | Only what's needed |
| **Speed** | Slower (always full pipeline) | Faster (minimal tools) |
| **Predictability** | Always same output format | Varies by query |
| **Best for** | Batch/scheduled runs | Interactive chat |
| **Requires** | Just your tools | OpenAI API key |

---

## Running the Demo

```bash
# Set OpenAI API key
export OPENAI_API_KEY='your-api-key'

# Run the demo
python examples/general_agent_demo.py
```

---

## Query Examples for GeneralStockAgent

### Simple Queries
- "What's the sentiment on AAPL?"
- "Show me news for Microsoft"
- "Is Tesla stock bullish or bearish?"

### Comparison Queries
- "Compare AAPL and MSFT sentiment"
- "Which has better news, Google or Amazon?"

### Recommendation Queries
- "Give me stock recommendations"
- "What should I buy today?"
- "Top stocks to invest in"

### The agent figures out what tools to call for each query!

---

## Implementation Details

### How GeneralStockAgent Works

```
User: "What's the sentiment on AAPL?"
         ↓
    [Send to GPT-4]
         ↓
GPT decides: "I need news for AAPL first"
         ↓
Calls: fetch_stock_news(["AAPL"])
         ↓
    [Execute function]
         ↓
    [Send result back]
         ↓
GPT decides: "Now I can analyze sentiment"
         ↓
Calls: analyze_sentiment(news_data)
         ↓
    [Execute function]
         ↓
    [Send result back]
         ↓
GPT answers: "AAPL has positive sentiment (+45)..."
         ↓
    [Return to user]
```

### Tool Definitions

The agent provides GPT-4 with clear descriptions of each tool:

```python
{
    "name": "fetch_stock_news",
    "description": "Fetch recent news articles for specific stock ticker symbols...",
    "parameters": {
        "tickers": ["AAPL", "MSFT"],
        "limit": 10
    }
}
```

GPT-4 reads these descriptions and decides when and how to use each tool.
