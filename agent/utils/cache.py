"""
File-Based Caching with TTL Support

Provides persistent caching for expensive operations like S&P 500 data fetching.
Uses JSON files for storage (stdlib only, no external dependencies).

Usage:
    from agent.utils import get_cache

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
import copy
from pathlib import Path
from typing import Any, Optional, Callable, TypeVar
from functools import wraps
from dataclasses import dataclass
import threading
import pickle
import tempfile

from .logging_config import get_logger

logger = get_logger('agent.cache')

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
        from agent.config import settings
        _cache = FileCache(
            cache_dir=str(settings.cache.cache_dir),
            default_ttl=settings.cache.sp500_ttl
        )
    return _cache


def clear_cache() -> int:
    """Clear all cached data and return count of entries removed."""
    return get_cache().clear()


class SessionDataCache:
    """Cache arbitrary trusted Python data for one date-based session.

    Unlike :class:`FileCache`, this cache stores pickle files, allowing callers
    to cache pandas DataFrames as well as regular Python dictionaries and lists.
    Cache files must be treated as trusted local data and should never be copied
    from an untrusted source.
    """

    def __init__(self, cache_dir: Path, namespace: str, default_ttl: int):
        self.cache_dir = Path(cache_dir) / namespace / time.strftime('%Y-%m-%d')
        self.default_ttl = default_ttl
        self._memory_cache: dict[str, CacheEntry] = {}
        self._lock = threading.Lock()

    @staticmethod
    def _key_text(key: Any) -> str:
        """Convert JSON-compatible keys into a deterministic identifier."""
        try:
            return json.dumps(key, sort_keys=True, separators=(',', ':'), default=str)
        except (TypeError, ValueError):
            return repr(key)

    def _cache_path(self, key: Any) -> Path:
        key_hash = hashlib.sha256(self._key_text(key).encode()).hexdigest()
        return self.cache_dir / f'{key_hash}.pkl'

    def get(self, key: Any) -> Optional[Any]:
        """Return a non-expired cached value, or ``None`` on a cache miss."""
        key_text = self._key_text(key)
        entry = self._memory_cache.get(key_text)
        if entry is not None:
            if not entry.is_expired:
                logger.debug('Session cache hit (memory): %s', key_text)
                return copy.deepcopy(entry.value)
            del self._memory_cache[key_text]

        cache_path = self._cache_path(key)
        if not cache_path.exists():
            return None

        try:
            with self._lock:
                with cache_path.open('rb') as cache_file:
                    entry = pickle.load(cache_file)
            if not isinstance(entry, CacheEntry) or entry.is_expired:
                return None
            self._memory_cache[key_text] = entry
            logger.debug('Session cache hit (file): %s', key_text)
            return copy.deepcopy(entry.value)
        except (EOFError, OSError, pickle.UnpicklingError, AttributeError) as exc:
            logger.warning('Ignoring invalid session cache %s: %s', cache_path, exc)
            return None

    def set(self, key: Any, value: Any, ttl: Optional[int] = None) -> None:
        """Store a value atomically for the remainder of its TTL."""
        key_text = self._key_text(key)
        entry = CacheEntry(
            value=copy.deepcopy(value),
            created_at=time.time(),
            ttl=ttl if ttl is not None else self.default_ttl,
            key=key_text,
        )
        cache_path = self._cache_path(key)
        temporary_path = None
        try:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode='wb', dir=cache_path.parent, prefix=f'.{cache_path.stem}-', delete=False
            ) as cache_file:
                temporary_path = Path(cache_file.name)
                pickle.dump(entry, cache_file, protocol=pickle.HIGHEST_PROTOCOL)
            temporary_path.replace(cache_path)
            self._memory_cache[key_text] = entry
            logger.debug('Session cache set: %s', key_text)
        except (OSError, pickle.PicklingError, TypeError) as exc:
            logger.warning('Unable to write session cache %s: %s', cache_path, exc)
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    def clear(self) -> int:
        """Clear this namespace's current session files."""
        self._memory_cache.clear()
        if not self.cache_dir.exists():
            return 0
        count = 0
        for cache_path in self.cache_dir.glob('*.pkl'):
            try:
                cache_path.unlink()
                count += 1
            except OSError as exc:
                logger.warning('Unable to clear session cache %s: %s', cache_path, exc)
        return count


_session_caches: dict[tuple[str, int], SessionDataCache] = {}


def get_session_cache(namespace: str, default_ttl: int) -> SessionDataCache:
    """Get a shared date-scoped cache for a data-source namespace."""
    from agent.config import settings

    cache_key = (namespace, default_ttl)
    if cache_key not in _session_caches:
        _session_caches[cache_key] = SessionDataCache(
            cache_dir=settings.cache.cache_dir,
            namespace=namespace,
            default_ttl=default_ttl,
        )
    return _session_caches[cache_key]
