"""
Resilience Utilities

Provides retry logic with exponential backoff and rate limiting
for handling API failures gracefully.

Usage:
    from agent.utils import retry, get_rate_limiter

    @retry(max_attempts=3, base_delay=1.0)
    def call_external_api():
        ...

    limiter = get_rate_limiter('openai')
    limiter.acquire()
    make_api_call()
"""

import time
import random
import threading
from typing import Callable, TypeVar, Optional, Tuple, Type
from functools import wraps

from .logging_config import get_logger

logger = get_logger('agent.resilience')

T = TypeVar('T')


class RetryError(Exception):
    """Raised when all retry attempts have been exhausted."""

    def __init__(self, message: str, last_exception: Optional[Exception] = None):
        super().__init__(message)
        self.last_exception = last_exception


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for retry logic with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts (including initial)
        base_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential backoff (2.0 = double each time)
        jitter: Add random jitter to prevent thundering herd
        retryable_exceptions: Tuple of exception types to retry on
        on_retry: Optional callback called on each retry with (exception, attempt)

    Usage:
        @retry(max_attempts=3, base_delay=1.0)
        def call_external_api():
            ...

        @retry(retryable_exceptions=(ConnectionError, TimeoutError))
        def fetch_data():
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception: Optional[Exception] = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e

                    if attempt == max_attempts:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}: {e}"
                        )
                        raise RetryError(
                            f"Failed after {max_attempts} attempts: {e}",
                            last_exception=e
                        ) from e

                    # Calculate delay with exponential backoff
                    delay = min(
                        base_delay * (exponential_base ** (attempt - 1)),
                        max_delay
                    )

                    # Add jitter (0-25% of delay)
                    if jitter:
                        delay = delay * (1 + random.uniform(0, 0.25))

                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )

                    # Call retry callback if provided
                    if on_retry:
                        on_retry(e, attempt)

                    time.sleep(delay)

            # Should never reach here, but just in case
            raise RetryError(
                f"Unexpected: all attempts exhausted for {func.__name__}",
                last_exception=last_exception
            )

        return wrapper
    return decorator


def retry_with_config(
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Retry decorator that reads settings from configuration.

    Usage:
        @retry_with_config(retryable_exceptions=(RequestException,))
        def make_api_call():
            ...
    """
    from agent.config import settings

    return retry(
        max_attempts=settings.rate_limit.max_retries,
        base_delay=settings.rate_limit.retry_base_delay,
        max_delay=settings.rate_limit.retry_max_delay,
        retryable_exceptions=retryable_exceptions,
        on_retry=on_retry
    )


class RateLimiter:
    """
    Token bucket rate limiter for controlling API request rates.

    Thread-safe implementation that limits requests per time window.

    Usage:
        limiter = RateLimiter(requests_per_second=2.0)

        for item in items:
            limiter.acquire()  # Blocks until allowed
            make_api_call(item)
    """

    def __init__(
        self,
        requests_per_second: float = 1.0,
        burst_size: int = 1
    ):
        """
        Initialize rate limiter.

        Args:
            requests_per_second: Maximum sustained request rate
            burst_size: Maximum burst of requests allowed
        """
        self.requests_per_second = requests_per_second
        self.burst_size = burst_size
        self.tokens = float(burst_size)
        self.last_update = time.monotonic()
        self._lock = threading.Lock()

        logger.debug(
            f"RateLimiter initialized: {requests_per_second} req/s, burst={burst_size}"
        )

    def acquire(self, tokens: int = 1) -> float:
        """
        Acquire tokens, blocking if necessary.

        Args:
            tokens: Number of tokens to acquire (default: 1)

        Returns:
            Time waited in seconds
        """
        with self._lock:
            waited = 0.0

            while True:
                self._refill_tokens()

                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return waited

                # Calculate wait time
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.requests_per_second

                # Release lock while sleeping
                self._lock.release()
                try:
                    time.sleep(wait_time)
                    waited += wait_time
                finally:
                    self._lock.acquire()

    def _refill_tokens(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self.last_update
        self.last_update = now

        # Add tokens for elapsed time
        self.tokens = min(
            self.burst_size,
            self.tokens + elapsed * self.requests_per_second
        )

    def try_acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens without blocking.

        Args:
            tokens: Number of tokens to acquire

        Returns:
            True if tokens acquired, False otherwise
        """
        with self._lock:
            self._refill_tokens()

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False


class AdaptiveRateLimiter(RateLimiter):
    """
    Rate limiter that adapts based on response times and errors.

    Automatically slows down when errors occur and speeds up on success.
    """

    def __init__(
        self,
        initial_rate: float = 1.0,
        min_rate: float = 0.1,
        max_rate: float = 10.0,
        burst_size: int = 1,
        backoff_factor: float = 0.5,
        recovery_factor: float = 1.1
    ):
        super().__init__(requests_per_second=initial_rate, burst_size=burst_size)
        self.initial_rate = initial_rate
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.backoff_factor = backoff_factor
        self.recovery_factor = recovery_factor
        self._error_count = 0
        self._success_count = 0

    def report_success(self) -> None:
        """Report a successful request - may increase rate."""
        with self._lock:
            self._success_count += 1
            self._error_count = 0

            # Gradually increase rate after consecutive successes
            if self._success_count >= 5:
                new_rate = min(
                    self.requests_per_second * self.recovery_factor,
                    self.max_rate
                )
                if new_rate != self.requests_per_second:
                    logger.debug(f"Rate limiter: increasing rate to {new_rate:.2f} req/s")
                    self.requests_per_second = new_rate
                self._success_count = 0

    def report_error(self) -> None:
        """Report a failed request - decreases rate."""
        with self._lock:
            self._error_count += 1
            self._success_count = 0

            # Immediately decrease rate on error
            new_rate = max(
                self.requests_per_second * self.backoff_factor,
                self.min_rate
            )
            if new_rate != self.requests_per_second:
                logger.warning(f"Rate limiter: decreasing rate to {new_rate:.2f} req/s")
                self.requests_per_second = new_rate


# Global rate limiters for different services
_rate_limiters: dict[str, RateLimiter] = {}
_limiter_lock = threading.Lock()


def get_rate_limiter(
    name: str,
    requests_per_second: Optional[float] = None
) -> RateLimiter:
    """
    Get or create a named rate limiter.

    Args:
        name: Limiter name (e.g., 'openai', 'news', 'yfinance')
        requests_per_second: Rate limit (uses config defaults if not specified)

    Returns:
        RateLimiter instance
    """
    with _limiter_lock:
        if name not in _rate_limiters:
            from agent.config import settings

            # Use configured rate or default
            if requests_per_second is None:
                if name == 'news':
                    requests_per_second = 1.0 / settings.rate_limit.news_rate_limit_delay
                elif name == 'api':
                    requests_per_second = 1.0 / settings.rate_limit.api_rate_limit_delay
                elif name == 'openai':
                    # Use configurable OpenAI rate limit
                    requests_per_second = settings.rate_limit.openai_rate_limit
                else:
                    requests_per_second = 2.0  # Default: 2 requests/second

            _rate_limiters[name] = RateLimiter(
                requests_per_second=requests_per_second,
                burst_size=3
            )
            logger.debug(f"Created rate limiter '{name}': {requests_per_second} req/s")

        return _rate_limiters[name]


def reset_rate_limiters() -> None:
    """Reset all rate limiters (useful for testing)."""
    with _limiter_lock:
        _rate_limiters.clear()
