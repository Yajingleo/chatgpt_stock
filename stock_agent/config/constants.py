"""
Static Constants

Values that do not change based on environment configuration.
These are fixed values used throughout the application.
"""

# S&P 500 data source
SP500_WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

# User agent for web requests
DEFAULT_USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
)

# Liquidity analysis horizons (days)
LIQUIDITY_HORIZONS = [5, 10, 20, 30, 40, 60, 120]

# Article content CSS selectors for web scraping
ARTICLE_SELECTORS = [
    'article',
    '.article-body',
    '.story-content',
    '.article-content',
    '.post-content',
    '.entry-content',
    'main .content',
    '[data-module="ArticleBody"]',
    '.caas-body',
]

# Sentiment analysis keywords
POSITIVE_KEYWORDS = [
    'growth', 'profit', 'increase', 'strong', 'beat', 'up', 'bullish', 'surge',
    'gain', 'record', 'breakthrough', 'success', 'expansion', 'rising', 'higher',
    'boost', 'upgrade', 'outperform', 'rally', 'momentum', 'strength', 'improve',
    'revenue', 'earnings', 'buyback', 'dividend', 'acquisition', 'partnership',
    'innovation', 'competitive', 'market share', 'efficiency', 'productivity',
    'optimistic',
]

NEGATIVE_KEYWORDS = [
    'loss', 'decline', 'fall', 'weak', 'miss', 'down', 'bearish', 'drop', 'crash',
    'fail', 'concern', 'risk', 'warning', 'cut', 'reduce', 'lower', 'downgrade',
    'underperform', 'slowdown', 'pressure', 'challenge', 'struggle', 'uncertain',
    'volatile', 'debt', 'lawsuit', 'investigation', 'regulatory', 'competition',
    'market share loss', 'headwinds', 'recession', 'inflation', 'costs',
]

# Risk-related keywords (weighted higher in sentiment analysis)
RISK_KEYWORDS = [
    'risk', 'warning', 'concern', 'volatile', 'uncertainty', 'regulatory',
    'investigation', 'lawsuit', 'debt', 'recession', 'inflation',
]

# Sector/theme keywords for classification
THEME_KEYWORDS = {
    'growth': ['growth', 'expansion', 'increase', 'rising', 'momentum'],
    'value': ['dividend', 'buyback', 'undervalued', 'value', 'yield'],
    'risk': ['risk', 'volatile', 'uncertainty', 'warning', 'concern'],
    'earnings': ['earnings', 'revenue', 'profit', 'quarterly', 'guidance'],
    'market': ['market', 'sector', 'industry', 'competition', 'share'],
    'innovation': ['innovation', 'technology', 'product', 'launch', 'patent'],
}

# Extra tickers beyond S&P 500
EXTRA_TICKERS = {
    "ARM": "Arm Holdings",
    "TSM": "Taiwan SemiConductor Manufacturing Company",
    "NUKZ": "Range Nuclear Renaissance Index ETF",
    "NLR": "VanEck Uranium and Nuclear ETF",
}

# Default demo tickers
DEFAULT_DEMO_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META"]

# Confidence thresholds for sentiment analysis
CONFIDENCE_THRESHOLDS = {
    'high_signals': 10,
    'high_diversity': 4,
    'medium_signals': 6,
    'medium_diversity': 3,
}

# Investment impact thresholds
IMPACT_THRESHOLDS = {
    'strong_positive': 30,
    'positive': 15,
    'strong_negative': -30,
    'negative': -15,
}

# Sentiment score scaling factor
SENTIMENT_SCALE_FACTOR = 8

# Risk signals weight multiplier
RISK_WEIGHT_MULTIPLIER = 1.5

# Confidence multiplier cap
MAX_CONFIDENCE_MULTIPLIER = 2.0

# Market cap formatting thresholds
MARKET_CAP_TRILLION = 1e12
MARKET_CAP_BILLION = 1e9
MARKET_CAP_MILLION = 1e6

# Display limits
MAX_KEY_FACTORS = 5
MAX_KEY_PHRASES = 3
MAX_THEMES_PER_GROUP = 2
MAX_INSIGHTS = 3
MAX_DISPLAY_TICKERS = 5

# HTTP status codes
HTTP_INTERNAL_ERROR = 500

# Web server
PORT_SEARCH_RANGE = 100

# Chat input
MAX_CHAT_INPUT_LENGTH = 500

# NLP confidence levels
NLP_CONFIDENCE = {
    'default': 0.5,
    'pattern_match': 0.8,
    'conversational': 0.9,
}

# Ticker validation
MIN_TICKER_LENGTH = 3

# Common words to exclude from ticker matching
EXCLUDED_WORDS = {
    'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
    'her', 'was', 'one', 'our', 'out', 'has', 'have', 'been', 'would',
    'could', 'will', 'their', 'what', 'this', 'from', 'they', 'some',
    'with', 'that', 'news', 'stock', 'stocks', 'market', 'price', 'share',
    'shares', 'buy', 'sell', 'hold', 'good', 'bad', 'high', 'low', 'how',
    'why', 'when', 'where', 'which', 'who', 'about', 'today', 'yesterday',
    'week', 'month', 'year', 'more', 'less', 'most', 'best', 'worst',
}
