"""
Centralized Configuration Management

Loads configuration from environment variables with sensible defaults.
Uses dataclasses for type safety and immutability.

Usage:
    from stock_agent.config import settings

    model = settings.openai.model
    timeout = settings.rate_limit.request_timeout
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _get_env_int(key: str, default: int) -> int:
    """Get integer from environment with default."""
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _get_env_float(key: str, default: float) -> float:
    """Get float from environment with default."""
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _get_env_bool(key: str, default: bool) -> bool:
    """Get boolean from environment with default."""
    value = os.getenv(key)
    if value is None:
        return default
    return value.lower() in ('true', '1', 'yes', 'on')


@dataclass(frozen=True)
class OpenAISettings:
    """OpenAI API configuration."""
    api_key: Optional[str] = field(default_factory=lambda: os.getenv('OPENAI_API_KEY'))
    model: str = field(default_factory=lambda: os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'))
    max_tokens: int = field(default_factory=lambda: _get_env_int('OPENAI_MAX_TOKENS', 500))
    temperature: float = field(default_factory=lambda: _get_env_float('OPENAI_TEMPERATURE', 0.1))


@dataclass(frozen=True)
class AnalysisSettings:
    """Stock analysis configuration."""
    lookback_days: int = field(default_factory=lambda: _get_env_int('LOOKBACK_DAYS', 30))
    top_n_results: int = field(default_factory=lambda: _get_env_int('TOP_N_RESULTS', 30))
    years_lookback: int = field(default_factory=lambda: _get_env_int('YEARS_LOOKBACK', 1))

    # Recommendation thresholds
    buy_threshold: int = field(default_factory=lambda: _get_env_int('BUY_THRESHOLD', 3))
    sell_threshold: int = field(default_factory=lambda: _get_env_int('SELL_THRESHOLD', -3))
    high_confidence_buy: int = field(default_factory=lambda: _get_env_int('HIGH_CONFIDENCE_BUY', 5))
    high_confidence_sell: int = field(default_factory=lambda: _get_env_int('HIGH_CONFIDENCE_SELL', -5))
    min_news_count: int = field(default_factory=lambda: _get_env_int('MIN_NEWS_COUNT', 2))


@dataclass(frozen=True)
class ProcessingSettings:
    """Parallel processing configuration."""
    num_processes: int = field(default_factory=lambda: _get_env_int('NUM_PROCESSES', 10))
    max_workers: int = field(default_factory=lambda: _get_env_int('MAX_WORKERS', 5))
    news_limit: int = field(default_factory=lambda: _get_env_int('NEWS_LIMIT', 5))
    max_articles_to_enhance: int = field(default_factory=lambda: _get_env_int('MAX_ARTICLES_TO_ENHANCE', 15))


@dataclass(frozen=True)
class RateLimitSettings:
    """Rate limiting and timeout configuration."""
    request_timeout: int = field(default_factory=lambda: _get_env_int('API_REQUEST_TIMEOUT', 10))
    news_rate_limit_delay: float = field(default_factory=lambda: _get_env_float('NEWS_RATE_LIMIT_DELAY', 0.5))
    api_rate_limit_delay: float = field(default_factory=lambda: _get_env_float('API_RATE_LIMIT_DELAY', 0.1))

    # Retry settings
    max_retries: int = field(default_factory=lambda: _get_env_int('MAX_RETRIES', 3))
    retry_base_delay: float = field(default_factory=lambda: _get_env_float('RETRY_BASE_DELAY', 1.0))
    retry_max_delay: float = field(default_factory=lambda: _get_env_float('RETRY_MAX_DELAY', 60.0))


@dataclass(frozen=True)
class CacheSettings:
    """Caching configuration."""
    enabled: bool = field(default_factory=lambda: _get_env_bool('ENABLE_CACHING', True))
    sp500_ttl: int = field(default_factory=lambda: _get_env_int('SP500_CACHE_TTL', 3600))
    stock_data_ttl: int = field(default_factory=lambda: _get_env_int('STOCK_DATA_CACHE_TTL', 1800))
    cache_dir: Path = field(default_factory=lambda: Path(os.getenv('CACHE_DIR', '.cache')))


@dataclass(frozen=True)
class ServerSettings:
    """Web server configuration."""
    host: str = field(default_factory=lambda: os.getenv('SERVER_HOST', 'localhost'))
    port: int = field(default_factory=lambda: _get_env_int('SERVER_PORT', 8080))


@dataclass(frozen=True)
class LoggingSettings:
    """Logging configuration."""
    level: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))
    log_dir: str = field(default_factory=lambda: os.getenv('LOG_DIR', 'logs'))
    backup_count: int = field(default_factory=lambda: _get_env_int('LOG_BACKUP_COUNT', 30))


@dataclass(frozen=True)
class ContentSettings:
    """Content length thresholds for text processing."""
    min_full_content_length: int = field(default_factory=lambda: _get_env_int('MIN_FULL_CONTENT_LENGTH', 500))
    max_article_text_length: int = field(default_factory=lambda: _get_env_int('MAX_ARTICLE_TEXT_LENGTH', 3000))
    max_llm_content_length: int = field(default_factory=lambda: _get_env_int('MAX_LLM_CONTENT_LENGTH', 2000))
    max_chat_history: int = field(default_factory=lambda: _get_env_int('MAX_CHAT_HISTORY', 20))


class Settings:
    """
    Main settings container - singleton pattern.

    Usage:
        from stock_agent.config import settings

        # Access nested settings
        model = settings.openai.model
        timeout = settings.rate_limit.request_timeout
    """
    _instance: Optional['Settings'] = None

    def __new__(cls) -> 'Settings':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize all settings groups."""
        self.openai = OpenAISettings()
        self.analysis = AnalysisSettings()
        self.processing = ProcessingSettings()
        self.rate_limit = RateLimitSettings()
        self.cache = CacheSettings()
        self.server = ServerSettings()
        self.logging = LoggingSettings()
        self.content = ContentSettings()

    def reload(self) -> None:
        """Reload settings from environment (useful for testing)."""
        try:
            from dotenv import load_dotenv
            load_dotenv(override=True)
        except ImportError:
            pass
        self._initialize()


# Global settings instance
settings = Settings()
