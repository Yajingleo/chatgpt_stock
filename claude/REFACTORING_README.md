# Stock News Agent - Modular Refactoring

This project has been refactored from a single large file (`adk_stock_agent.py`) into a clean modular architecture with focused components.

## 🏗️ New Modular Structure

### Core Files

1. **[adk_stock_agent_main.py](adk_stock_agent_main.py)** - Main orchestrator (RECOMMENDED)
   - Clean main entry point
   - Coordinates all modular components
   - Implements ADK workflow logic

2. **[news_crawler_agent.py](news_crawler_agent.py)** - News fetching & scraping
   - Stock news fetching from multiple sources
   - Full article content scraping
   - Content enhancement and quality metrics
   - Rate limiting and error handling

3. **[sentiment_analyzer.py](sentiment_analyzer.py)** - LLM sentiment analysis
   - OpenAI GPT integration
   - Google ADK/Gemini LLM support
   - Sophisticated sentiment scoring
   - Financial keyword analysis
   - Theme detection and scoring

4. **[stock_recommender.py](stock_recommender.py)** - Investment recommendations
   - S&P 500 analysis integration
   - Buy/Sell/Hold recommendation generation
   - Risk tolerance adjustments
   - Confidence level assessment
   - Advanced recommendation logic

5. **[adk_stock_agent.py](adk_stock_agent.py)** - Legacy version (backwards compatibility)
   - Original monolithic file updated to use modules
   - Kept for backwards compatibility only
   - **Use `adk_stock_agent_main.py` for new development**

## 🚀 Usage

### Recommended Usage (New Modular Version)
```bash
python adk_stock_agent_main.py
```

### Legacy Usage (Backwards Compatibility)
```bash
python adk_stock_agent.py
```

## 🧩 Benefits of Modular Architecture

### Before Refactoring
- ❌ Single 800-line file
- ❌ Mixed concerns (news, sentiment, recommendations)
- ❌ Hard to test individual components
- ❌ Difficult to maintain and extend
- ❌ Code duplication and tight coupling

### After Refactoring
- ✅ Clean separation of concerns
- ✅ Easy to test individual modules
- ✅ Reusable components
- ✅ Better maintainability
- ✅ Easier to extend and modify
- ✅ Clear interfaces between components

## 📋 Module Responsibilities

### News Crawler Agent (`news_crawler_agent.py`)
- **Primary Function**: Fetch and enhance stock news content
- **Key Features**:
  - Multi-source news fetching
  - Full article content scraping
  - Content quality assessment
  - Rate-limited requests
  - Error handling and fallbacks

### Sentiment Analyzer (`sentiment_analyzer.py`)
- **Primary Function**: Analyze news sentiment using LLM
- **Key Features**:
  - OpenAI GPT-3.5 integration
  - Google ADK/Gemini support
  - Financial keyword analysis
  - Theme-based scoring
  - Confidence assessment

### Stock Recommender (`stock_recommender.py`)
- **Primary Function**: Generate investment recommendations
- **Key Features**:
  - S&P 500 technical analysis
  - Sentiment-based recommendations
  - Risk tolerance adjustments
  - Confidence levels
  - Advanced recommendation logic

### Main Orchestrator (`adk_stock_agent_main.py`)
- **Primary Function**: Coordinate workflow and display results
- **Key Features**:
  - Clean ADK integration
  - Modular component coordination
  - Result formatting and display
  - Error handling and fallbacks

## 🔧 Development

### Adding New Features

1. **News Sources**: Extend `news_crawler_agent.py`
2. **Analysis Models**: Extend `sentiment_analyzer.py`
3. **Recommendation Logic**: Extend `stock_recommender.py`
4. **Workflow Changes**: Modify `adk_stock_agent_main.py`

### Testing Individual Components

Each module can be imported and tested independently:

```python
from news_crawler_agent import fetch_stock_news_tool
from sentiment_analyzer import analyze_sentiment_tool
from stock_recommender import generate_recommendations_tool

# Test individual components
news_result = fetch_stock_news_tool(['AAPL', 'GOOGL'])
sentiment_result = analyze_sentiment_tool(news_result['news_data'])
recommendations = generate_recommendations_tool(sentiment_result['sentiment_analysis'])
```

## 🏃‍♂️ Migration Guide

### For Existing Code
- Replace imports from `adk_stock_agent` to specific modules
- Use `adk_stock_agent_main.py` as the new entry point
- Update function calls to use modular imports

### For New Development
- Start with `adk_stock_agent_main.py`
- Import specific functions from modules as needed
- Follow the modular architecture patterns

## 📁 File Dependencies

```
adk_stock_agent_main.py
├── news_crawler_agent.py
│   └── stock_selection/stock_news_crawler.py
├── sentiment_analyzer.py
│   ├── openai (optional)
│   └── google.adk (optional)
└── stock_recommender.py
    └── stock_selection/sp_500_energy.py
```

## ✨ Future Enhancements

With the modular architecture, it's now easy to:
- Add new LLM providers (Claude, Llama, etc.)
- Integrate additional news sources
- Implement different recommendation algorithms  
- Add real-time data feeds
- Create specialized analysis modules
- Build API endpoints for each component

The modular design makes the codebase more maintainable, testable, and extensible! 🎉