"""
File-Based Caching with TTL Support

Provides persistent caching for expensive operations like S&P 500 data fetching.
Uses JSON files for storage (stdlib only, no external dependencies).

Usage:
    from stock_agent.utils import get_cache

    cache = get_cache()
    value = cache.get('my_key')
    cache.set('my_key', {'data': 'value'}, ttl=1800)

    # Or with decorator
    @cache.cached(ttl=3600)
    def expensive_operation():
        ...
"""

import json
import hashlib
import time
from pathlib import Path
from typing import Any, Optional, Callable, TypeVar
from functools import wraps
from dataclasses import dataclass
import threading

from .logging_config import get_logger

logger = get_logger('stock_agent.cache')

T = TypeVar('T')


@dataclass
class CacheEntry:
    """Represents a cached value with metadata."""
    value: Any
    created_at: float
    ttl: int
    key: str

    @property
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        return time.time() - self.created_at > self.ttl

    @property
    def age_seconds(self) -> float:
        """Get the age of the cache entry in seconds."""
        return time.time() - self.created_at


class FileCache:
    """
    File-based cache with TTL support.

    Thread-safe implementation using locks.

    Usage:
        cache = FileCache(cache_dir='.cache', default_ttl=3600)

        # Get or set
        value = cache.get('my_key')
        cache.set('my_key', {'data': 'value'}, ttl=1800)

        # With decorator
        @cache.cached(ttl=3600)
        def expensive_operation():
            ...
    """

    def __init__(self, cache_dir: str = '.cache', default_ttl: int = 3600):
        """
        Initialize the file cache.

        Args:
            cache_dir: Directory for cache files
            default_ttl: Default time-to-live in seconds
        """
        self.cache_dir = Path(cache_dir)
        self.default_ttl = default_ttl
        self._lock = threading.Lock()
        self._memory_cache: dict[str, CacheEntry] = {}

        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"FileCache initialized at {self.cache_dir}")

    def _get_cache_path(self, key: str) -> Path:
        """Generate file path for a cache key."""
        # Hash the key to create a safe filename
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        # Check memory cache first
        if key in self._memory_cache:
            entry = self._memory_cache[key]
            if not entry.is_expired:
                logger.debug(f"Cache hit (memory): {key}")
                return entry.value
            else:
                del self._memory_cache[key]

        # Check file cache
        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            logger.debug(f"Cache miss: {key}")
            return None

        try:
            with self._lock:
                with open(cache_path, 'r') as f:
                    data = json.load(f)

            entry = CacheEntry(
                value=data['value'],
                created_at=data['created_at'],
                ttl=data['ttl'],
                key=key
            )

            if entry.is_expired:
                logger.debug(f"Cache expired: {key} (age: {entry.age_seconds:.0f}s)")
                self._delete_file(cache_path)
                return None

            # Store in memory cache for faster subsequent access
            self._memory_cache[key] = entry
            logger.debug(f"Cache hit (file): {key}")
            return entry.value

        except (json.JSONDecodeError, KeyError, IOError) as e:
            logger.warning(f"Cache read error for {key}: {e}")
            self._delete_file(cache_path)
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in cache.

        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time-to-live in seconds (uses default if not specified)
        """
        ttl = ttl if ttl is not None else self.default_ttl

        entry = CacheEntry(
            value=value,
            created_at=time.time(),
            ttl=ttl,
            key=key
        )

        # Store in memory cache
        self._memory_cache[key] = entry

        # Store in file cache
        cache_path = self._get_cache_path(key)
        try:
            with self._lock:
                with open(cache_path, 'w') as f:
                    json.dump({
                        'value': value,
                        'created_at': entry.created_at,
                        'ttl': ttl,
                        'key': key
                    }, f)
            logger.debug(f"Cache set: {key} (ttl: {ttl}s)")
        except (IOError, TypeError) as e:
            logger.warning(f"Cache write error for {key}: {e}")

    def delete(self, key: str) -> bool:
        """
        Delete a cache entry.

        Args:
            key: Cache key

        Returns:
            True if entry was deleted, False if not found
        """
        # Remove from memory cache
        if key in self._memory_cache:
            del self._memory_cache[key]

        # Remove file
        cache_path = self._get_cache_path(key)
        return self._delete_file(cache_path)

    def _delete_file(self, path: Path) -> bool:
        """Safely delete a cache file."""
        try:
            if path.exists():
                path.unlink()
                return True
        except IOError as e:
            logger.warning(f"Failed to delete cache file {path}: {e}")
        return False

    def clear(self) -> int:
        """
        Clear all cache entries.

        Returns:
            Number of entries cleared
        """
        count = 0
        self._memory_cache.clear()

        for cache_file in self.cache_dir.glob('*.json'):
            if self._delete_file(cache_file):
                count += 1

        logger.info(f"Cache cleared: {count} entries removed")
        return count

    def cached(self, ttl: Optional[int] = None, key_prefix: str = ''):
        """
        Decorator for caching function results.

        Args:
            ttl: Time-to-live in seconds
            key_prefix: Optional prefix for cache key

        Usage:
            @cache.cached(ttl=3600)
            def expensive_function(arg1, arg2):
                ...
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            def wrapper(*args, **kwargs) -> T:
                # Generate cache key from function name and arguments
                key_parts = [key_prefix, func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = ':'.join(filter(None, key_parts))

                # Try to get from cache
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value

                # Execute function and cache result
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                return result

            return wrapper
        return decorator


# Global cache instance (lazy initialization)
_cache: Optional[FileCache] = None


def get_cache() -> FileCache:
    """
    Get the global cache instance.

    Returns:
        FileCache instance configured from settings
    """
    global _cache
    if _cache is None:
        from stock_agent.config import settings
        _cache = FileCache(
            cache_dir=str(settings.cache.cache_dir),
            default_ttl=settings.cache.sp500_ttl
        )
    return _cache


def clear_cache() -> int:
    """Clear all cached data and return count of entries removed."""
    return get_cache().clear()
