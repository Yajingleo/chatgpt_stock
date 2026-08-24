"""Cache integration test for fundamental-data lookups."""

from types import SimpleNamespace
import unittest
from unittest.mock import patch


class InMemoryCache:
    def __init__(self): self.values = {}
    def get(self, key): return self.values.get(repr(sorted(key.items())))
    def set(self, key, value, ttl=None): self.values[repr(sorted(key.items()))] = value


class FundamentalsCacheTest(unittest.TestCase):
    def test_reuses_persistent_cache(self):
        from agent.data import fundamentals
        cache, calls = InMemoryCache(), []
        with patch.object(fundamentals, 'get_session_cache', lambda *args: cache), \
             patch.object(fundamentals, 'get_rate_limiter', lambda *args, **kwargs: SimpleNamespace(acquire=lambda: None)), \
             patch.object(fundamentals, 'settings', SimpleNamespace(cache=SimpleNamespace(enabled=True, fundamentals_ttl=60))), \
             patch.object(fundamentals.yf, 'Ticker', lambda ticker: calls.append(ticker) or SimpleNamespace(info={'longName': 'Example Corp'})):
            self.assertEqual(fundamentals.StockFundamentalData().get_stock_info('ABC')['full_name'], 'Example Corp')
            self.assertEqual(fundamentals.StockFundamentalData().get_stock_info('ABC')['full_name'], 'Example Corp')
        self.assertEqual(calls, ['ABC'])


if __name__ == '__main__': unittest.main()
