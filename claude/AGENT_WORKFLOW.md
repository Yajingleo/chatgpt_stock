# 🚀 Stock Analysis Agent Workflow

A comprehensive visual guide to the AI-powered stock analysis system that combines market data, news intelligence, and advanced AI analysis into actionable investment insights.

## 🎯 Complete Workflow Overview

```
🚀 STOCK ANALYSIS AGENT WORKFLOW
═══════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────┐
│                            🎯 START ANALYSIS                            │
└─────────────────────┬───────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   📊 STEP 1: STOCK SELECTION                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  • SP500StockAnalyzer analyzes 500+ stocks                     │   │
│  │  • Technical indicators: volume, price movement, momentum      │   │
│  │  • Lookback period: 30 days                                    │   │
│  │  • Output: Top 46 recommended tickers                          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    📰 STEP 2: NEWS FETCHING                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  • Select top 5 tickers for analysis                           │   │
│  │  • StockNewsCrawler fetches 10 articles per ticker             │   │
│  │  • Sources: Yahoo Finance, major financial sites               │   │
│  │  • NewsContentEnhancer reads full article text                 │   │
│  │  • Output: 50 articles with enhanced content                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  💭 STEP 3: SENTIMENT ANALYSIS                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   🤖 OpenAI GPT-3.5 Analysis                   │   │
│  │  ┌─────────────────────────────────────────────────────────┐   │   │
│  │  │  For Each Article:                                      │   │   │
│  │  │  • Send structured prompt to OpenAI API                │   │   │
│  │  │  • Get sentiment score (-100 to +100)                  │   │   │
│  │  │  • Extract key factors & market catalysts              │   │   │
│  │  │  • Assess confidence level (high/medium/low)           │   │   │
│  │  │  • Determine investment impact                          │   │   │
│  │  └─────────────────────────────────────────────────────────┘   │   │
│  │                                                             │   │
│  │  📊 Aggregation Engine                                      │   │
│  │  • Sum sentiment scores per ticker                          │   │
│  │  • Track analysis depth (full article vs summary)          │   │
│  │  • Generate confidence metrics                              │   │
│  │                                                             │   │
│  │  💾 CSV Export                                              │   │
│  │  • Save raw OpenAI responses with timestamps                │   │
│  │  • Include all analysis details for transparency            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                 🎯 STEP 4: RECOMMENDATION ENGINE                        │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Decision Logic:                                               │   │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │   │
│  │  │ Score ≥ 3 AND   │    │ Score ≤ -3 AND  │    │   Other     │ │   │
│  │  │ News ≥ 2        │    │ News ≥ 2        │    │ Conditions  │ │   │
│  │  │        │        │    │        │        │    │     │       │ │   │
│  │  │        ▼        │    │        ▼        │    │     ▼       │ │   │
│  │  │   🟢 BUY        │    │   🔴 SELL       │    │  🟡 HOLD    │ │   │
│  │  │   HIGH/MED      │    │   HIGH/MED      │    │   LOW       │ │   │
│  │  │   CONFIDENCE    │    │   CONFIDENCE    │    │ CONFIDENCE  │ │   │
│  │  └─────────────────┘    └─────────────────┘    └─────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      📁 OUTPUT GENERATION                              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  🗂️ Multiple Output Formats:                                    │   │
│  │                                                                 │   │
│  │  📄 JSON Report (output/modular_stock_analysis.json)           │   │
│  │  ├── Executive summary with recommendations                     │   │
│  │  ├── Complete workflow steps and data                          │   │
│  │  └── Analysis quality metrics                                  │   │
│  │                                                                 │   │
│  │  📊 CSV Analysis (report/openai_sentiment_analysis_YYYYMMDD.csv) │   │
│  │  ├── Individual OpenAI API responses                           │   │
│  │  ├── Timestamps, sentiment scores, reasoning                   │   │
│  │  └── Complete audit trail for transparency                     │   │
│  │                                                                 │   │
│  │  🎨 Console Display                                            │   │
│  │  ├── Color-coded recommendations with emojis                   │   │
│  │  ├── Confidence indicators and key signals                     │   │
│  │  └── Professional formatting for readability                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        ✅ ANALYSIS COMPLETE                             │
│                                                                         │
│  📊 Example Results (from live demo):                                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  🟢📈 AMD: BUY (Sentiment: 630, Confidence: HIGH)              │   │
│  │      ├─ KeyBanc upgrade with $270 price target                 │   │
│  │      ├─ Hyperscaler demand acceleration                        │   │
│  │      └─ Server CPU sold out for 2026                          │   │
│  │                                                                 │   │
│  │  🟡➡️ LMT: HOLD (Sentiment: 0, Confidence: LOW)               │   │
│  │      └─ Mixed defense sector signals                           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

## 🔧 Technical Architecture

### 📁 Modular Components

```
├── 🏗️ adk_stock_agent_main.py     ← Main orchestrator
├── 📊 stock_recommender.py        ← SP500 analysis & recommendations  
├── 📰 news_crawler_agent.py       ← News fetching & content enhancement
├── 🤖 sentiment_analyzer.py       ← OpenAI integration & CSV export
└── 🎯 WORKFLOW COORDINATION       ← Sequential execution with error handling
```

### 🔄 Data Flow

**Stock Tickers** → **News Articles** → **AI Analysis** → **Investment Decisions** → **Reports**

### ⚡ Performance Metrics (from live run)

| Metric | Value |
|--------|--------|
| Total Runtime | ~2 minutes |
| API Calls | 14 OpenAI requests |
| Data Points | 50 articles analyzed |
| Output Files | 2 (JSON + CSV) |
| Recommendations | 2 actionable insights |

## 🎯 Key Features

- 🤖 **Real AI analysis** (not just keywords)
- 📊 **Professional-grade output formats**  
- 💾 **Complete transparency** with audit trails
- 🎨 **User-friendly visualization**
- 📈 **Actionable investment recommendations**

## 📊 Step-by-Step Breakdown

### Step 1: Stock Selection
- **Input**: S&P 500 universe (500+ stocks)
- **Processing**: Technical analysis with volume, price movement, momentum indicators
- **Parameters**: 30-day lookback period
- **Output**: Top 46 recommended tickers ranked by technical signals

### Step 2: News Intelligence
- **Input**: Top 5 highest-momentum tickers
- **Processing**: Web scraping from Yahoo Finance and financial news sources
- **Enhancement**: Full article content extraction for deeper analysis
- **Output**: 50 recent news articles with rich content

### Step 3: AI-Powered Sentiment Analysis
- **Input**: News articles with full text content
- **Processing**: 
  - Structured prompts sent to OpenAI GPT-3.5
  - Sentiment scoring (-100 to +100 scale)
  - Key factor extraction and confidence assessment
- **Output**: 
  - Aggregated sentiment scores per ticker
  - Individual analysis details saved to CSV
  - Confidence levels and analysis depth tracking

### Step 4: Investment Recommendations
- **Input**: Aggregated sentiment data with confidence metrics
- **Processing**: Rule-based decision engine with thresholds
- **Logic**:
  - **BUY**: Sentiment ≥ 3 AND News ≥ 2 articles
  - **SELL**: Sentiment ≤ -3 AND News ≥ 2 articles  
  - **HOLD**: All other conditions
- **Output**: Actionable recommendations with confidence levels

### Step 5: Multi-Format Output
- **JSON Report**: Structured data for programmatic access
- **CSV Export**: Individual AI responses for transparency
- **Console Display**: Human-readable recommendations with visual indicators

## 🏃‍♂️ How to Run

### Quick Start
```bash
cd stock_selection/agent
python adk_stock_agent_main.py
```

### Prerequisites
- Python 3.8+
- OpenAI API key in `.env` file
- Required packages: `openai`, `yfinance`, `beautifulsoup4`, `pandas`

### Expected Output Files
- `output/modular_stock_analysis.json` - Main analysis results
- `stock_selection/report/openai_sentiment_analysis_YYYYMMDD_HHMMSS.csv` - Raw AI responses

## 🎨 Sample Output

### Console Display
```
🎯 STOCK NEWS ANALYSIS RESULTS
════════════════════════════════════════════════
📊 Tickers analyzed: 2
📰 News items processed: 15
🎯 Recommendations generated: 2

💡 ENHANCED INVESTMENT RECOMMENDATIONS:
──────────────────────────────────────────────────
🟢📈 AMD: BUY
   🔥 Confidence: HIGH | 📚 Analysis: full_article
   📊 Sentiment Score: 630 | 📰 Articles: 10
   💭 Reason: Strong positive sentiment (score: 630, 10 news items)
   🏷️ Key Signals: Hyperscaler demand acceleration, Server CPU and AI GPU growth
```

## 🔍 Advanced Features

### Transparency & Auditability
- Every OpenAI API call is logged with timestamp
- Complete reasoning chain preserved in CSV format
- Analysis confidence levels tracked per article
- Content depth indicators (full article vs summary)

### Quality Assurance
- Fallback analysis when API calls fail
- Content enhancement for better analysis accuracy
- Multi-source news aggregation
- Error handling with graceful degradation

### Extensibility
- Modular architecture for easy component updates
- Pluggable sentiment analysis backends
- Configurable stock selection criteria
- Flexible output format support

---

*This system demonstrates a complete AI-powered investment research platform that combines market data, news intelligence, and advanced AI analysis into actionable investment insights.*