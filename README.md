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

### Programmatic Usage

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
