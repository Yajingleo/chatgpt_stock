# Stock Agent - Professional Stock Analysis System

A comprehensive AI-powered stock analysis system with sentiment analysis, news crawling, fundamental data fetching, and investment recommendations.

## Features

- 📊 **Stock Selection**: Momentum-based selection from S&P 500, major ADRs, and sector ETFs
- 📰 **News Crawler**: Automated news fetching with full article content extraction
- 💭 **Sentiment Analysis**: LLM-powered (OpenAI GPT) sentiment scoring with fallback simulation
- 🎯 **Recommendations**: BUY/SELL/HOLD signals with confidence levels
- 🌐 **Web Interface**: Modern chat-based UI for natural language queries
- 📈 **Fundamentals**: Stock fundamental data and S&P 500 analysis
- 📋 **SEC Filings**: SEC filing and insider trading data integration

## Project Structure

```
chatgpt_stock/
├── agent/                    # Main package
│   ├── orchestration/        # Public orchestrator and model/tool loop
│   ├── providers/            # AI, market, news, SEC, and memory adapters
│   ├── services/             # Stock analysis and recommendation logic
│   ├── tools/                # Tool registry, schemas, and adapters
│   ├── domain/               # Provider-neutral boundary models
│   ├── utils/                # Utilities
│   │   ├── logging_config.py
│   │   └── validators.py
│   └── config/               # Environment-backed configuration
├── web/                      # Web interface
│   └── server.py            # Chat server
├── scripts/                  # Launch scripts
│   ├── launch_server.py     # Server launcher
│   └── examples/
├── tests/                    # Test suite (Phase 4)
├── logs/                     # Generated logs
├── requirements.txt          # Dependencies
└── .env.example             # Environment template
```

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

3. **Verify installation:**
```bash
python3 -c "from agent import Orchestrator; print('✅ Setup complete')"
```

## Usage

### Launch Web Interface

**Quick Start:**
```bash
python scripts/launch_server.py
```

**Direct launch:**
```bash
python -m web.server
```

### S&P 500 Command Line

Run these commands from the repository root after installing dependencies.

Run analysis with the configured defaults:

```bash
python -m agent.providers.market.sp500
```

Analyze a 30-day window and save the top/bottom 20 results as CSVs:

```bash
python -m agent.providers.market.sp500 \
  --lookback_days 30 \
  --top_n 20 \
  --output_dir results/sp500
```

The output directory contains `top_energy.csv`, `bottom_energy.csv`,
`top_return.csv`, and `bottom_return.csv`.

Run S&P 500 analysis and save daily candlestick (K-line) charts:

```bash
python -m agent.providers.market.sp500 \
  --lookback_days 30 \
  --top_n 20 \
  --output_dir results/sp500 \
  --plot_tickers AAPL MSFT \
  --plot_days 60
```

This saves analysis CSVs and `AAPL_kline.png` / `MSFT_kline.png`. Charts use
adjusted open, high, low, and close prices for the latest 60 available trading
sessions. Green means close ≥ open; red means close < open.

List all command-line options:

```bash
python -m agent.providers.market.sp500 --help
```

### Programmatic Usage

The agent runtime keeps one lazily loaded S&P 500 object in memory. Momentum
analysis and plotting reuse this object; its existing file cache avoids repeat
downloads across restarts while entries remain valid. Memory reloads after
`STOCK_DATA_CACHE_TTL` seconds (default 1800) or a date change. File caching is
controlled by the existing cache settings.

```python
from agent import Orchestrator

agent = Orchestrator.from_settings()
figure = agent.runtime.plot_kline("AAPL", days=60, output_path="results/AAPL_kline.png")
```

For standalone use without configuring a model:

```python
from agent.runtime import AgentRuntime
from agent.plotting import KlinePlotter

runtime = AgentRuntime()
data = runtime.sp500  # Loads once, using the file cache when available.
figure = KlinePlotter().plot(data.all_data, "AAPL", days=60,
                            output_path="results/AAPL_kline.png")
```

`KlinePlotter` only renders the supplied OHLC DataFrame; it does not fetch data
or manage caches. Omit `output_path` to return the figure without saving it.
The runtime's plotting method is a Python API, not a registered model tool.

```python
import asyncio
from agent import Orchestrator

# Create agent
agent = Orchestrator.from_settings()

# Run analysis
results = asyncio.run(agent.run("Analyze AAPL using recent news and market data"))
print(results["answer"] if results["success"] else results["error"])
```

### Natural Language Queries (Web UI)

- "Give me stock recommendations"
- "Analyze AAPL stock"
- "What's the sentiment on Tesla?"
- "How is the market doing today?"

## Workflow

1. **Stock Selection**: Traditional momentum-based selection from candidate pools
2. **News Crawling**: Automated web crawler for top performers
3. **Sentiment Analysis**: LLM-powered analysis with keyword fallback
4. **Recommendations**: BUY/SELL/HOLD with confidence levels and reasoning
5. **Report Generation**: Stock, Action, Sentiment Score, Confidence, Reasoning

## Configuration

All configuration is managed through environment variables (`.env` file):

- `MODEL_PROVIDER`: `google_adk`, `openai`, `anthropic`, or `deepseek`
- `MODEL_NAME`: Model identifier for the selected provider
- Provider API key, such as `GOOGLE_API_KEY` or `OPENAI_API_KEY`

The default provider is OpenAI because it is included in `requirements.txt`.
Google ADK, Anthropic, and DeepSeek support is optional and must be configured
explicitly with the matching package and API key.
- `LOOKBACK_DAYS`: Days of historical data (default: 30)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

See `.env.example` for full configuration options.

## Requirements

- Python 3.9+
- Internet connection for stock data
- OpenAI API key (optional, falls back to simulation)

## License

Copyright © 2026 Stock Agent Team
