"""
Configuration Management

Provides centralized configuration for the Stock Agent system.

Usage:
    from agent.config import settings

    # Access configuration
    timeout = settings.rate_limit.request_timeout
    model = settings.openai.model

    # Access constants
    from agent.config import SP500_WIKIPEDIA_URL, POSITIVE_KEYWORDS
"""

from .settings import (
    settings,
    Settings,
    OpenAISettings,
    AnalysisSettings,
    ProcessingSettings,
    RateLimitSettings,
    CacheSettings,
    ServerSettings,
    LoggingSettings,
    ContentSettings,
)

from .constants import (
    SP500_WIKIPEDIA_URL,
    DEFAULT_USER_AGENT,
    LIQUIDITY_HORIZONS,
    ARTICLE_SELECTORS,
    POSITIVE_KEYWORDS,
    NEGATIVE_KEYWORDS,
    RISK_KEYWORDS,
    THEME_KEYWORDS,
    EXTRA_TICKERS,
    DEFAULT_DEMO_TICKERS,
    CONFIDENCE_THRESHOLDS,
    IMPACT_THRESHOLDS,
    SENTIMENT_SCALE_FACTOR,
    RISK_WEIGHT_MULTIPLIER,
    MAX_CONFIDENCE_MULTIPLIER,
    MARKET_CAP_TRILLION,
    MARKET_CAP_BILLION,
    MARKET_CAP_MILLION,
    MAX_KEY_FACTORS,
    MAX_KEY_PHRASES,
    MAX_THEMES_PER_GROUP,
    MAX_INSIGHTS,
    MAX_DISPLAY_TICKERS,
    HTTP_INTERNAL_ERROR,
    PORT_SEARCH_RANGE,
    MAX_CHAT_INPUT_LENGTH,
    NLP_CONFIDENCE,
    MIN_TICKER_LENGTH,
    EXCLUDED_WORDS,
)

__all__ = [
    # Settings
    'settings',
    'Settings',
    'OpenAISettings',
    'AnalysisSettings',
    'ProcessingSettings',
    'RateLimitSettings',
    'CacheSettings',
    'ServerSettings',
    'LoggingSettings',
    'ContentSettings',
    # Constants
    'SP500_WIKIPEDIA_URL',
    'DEFAULT_USER_AGENT',
    'LIQUIDITY_HORIZONS',
    'ARTICLE_SELECTORS',
    'POSITIVE_KEYWORDS',
    'NEGATIVE_KEYWORDS',
    'RISK_KEYWORDS',
    'THEME_KEYWORDS',
    'EXTRA_TICKERS',
    'DEFAULT_DEMO_TICKERS',
    'CONFIDENCE_THRESHOLDS',
    'IMPACT_THRESHOLDS',
    'SENTIMENT_SCALE_FACTOR',
    'RISK_WEIGHT_MULTIPLIER',
    'MAX_CONFIDENCE_MULTIPLIER',
    'MARKET_CAP_TRILLION',
    'MARKET_CAP_BILLION',
    'MARKET_CAP_MILLION',
    'MAX_KEY_FACTORS',
    'MAX_KEY_PHRASES',
    'MAX_THEMES_PER_GROUP',
    'MAX_INSIGHTS',
    'MAX_DISPLAY_TICKERS',
    'HTTP_INTERNAL_ERROR',
    'PORT_SEARCH_RANGE',
    'MAX_CHAT_INPUT_LENGTH',
    'NLP_CONFIDENCE',
    'MIN_TICKER_LENGTH',
    'EXCLUDED_WORDS',
]
