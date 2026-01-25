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
├── stock_agent/              # Main package
│   ├── agents/               # Agent orchestration
│   │   └── main_agent.py    # Main orchestrator
│   ├── data/                 # Data fetching modules
│   │   ├── news_crawler.py  # News fetching
│   │   ├── fundamentals.py  # Stock fundamentals
│   │   ├── sp500_analyzer.py # S&P 500 analysis
│   │   └── sec_filings.py   # SEC & insider trading
│   ├── analysis/             # Analysis engines
│   │   ├── sentiment.py     # Sentiment analysis
│   │   └── recommender.py   # Recommendation engine
│   ├── utils/                # Utilities
│   │   ├── logging_config.py
│   │   └── validators.py
│   └── config/               # Configuration (Phase 2)
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
python3 -c "from stock_agent.agents.main_agent import StockNewsADKAgent; print('✅ Setup complete')"
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
from stock_agent.agents.main_agent import StockNewsADKAgent

# Create agent
agent = StockNewsADKAgent()

# Run analysis
results = asyncio.run(agent.run_analysis())

# Display results
agent.display_results(results)
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

- `OPENAI_API_KEY`: OpenAI API key for sentiment analysis (optional, has fallback)
- `LOOKBACK_DAYS`: Days of historical data (default: 30)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

See `.env.example` for full configuration options.

## Development

### Phase 1 (Completed) ✅
- Code duplication eliminated
- Logging infrastructure implemented
- Input validation added
- Requirements consolidated

### Phase 2 (In Progress)
- Configuration management
- Caching layer for S&P 500 data
- Retry logic and rate limiting

### Phase 3 (Planned)
- Enhanced error handling
- Graceful degradation
- Circuit breakers

### Phase 4 (Planned)
- Comprehensive test suite
- Complete documentation
- Developer tools (Makefile, pre-commit hooks)

## Requirements

- Python 3.9+
- Internet connection for stock data
- OpenAI API key (optional, falls back to simulation)

## License

Copyright © 2026 Stock Agent Team