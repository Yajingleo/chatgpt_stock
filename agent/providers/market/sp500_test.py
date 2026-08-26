"""Unit tests for S&P 500 historical-data caching."""

from types import SimpleNamespace
import unittest
from unittest.mock import patch

import pandas as pd


class InMemoryCache:
    cache_dir = 'in-memory-test-cache'
    def __init__(self): self.values = {}
    def get(self, key): return self.values.get(repr(sorted(key.items())))
    def set(self, key, value, ttl=None): self.values[repr(sorted(key.items()))] = value


def analyzer(cache):
    from agent.providers.market.sp500 import SP500StockAnalyzer
    result = object.__new__(SP500StockAnalyzer)
    result.tickers, result._requested_tickers = ['AAA'], ('AAA',)
    result.start_date, result.end_date = '2025-08-24', '2026-08-24'
    result._stock_data_cache, result.all_data = cache, None
    return result


class SP500AnalyzerCacheTest(unittest.TestCase):
    def test_download_is_reused_from_session_cache(self):
        from agent.providers.market import sp500 as sp500_analyzer
        cache, calls = InMemoryCache(), []
        columns = pd.MultiIndex.from_tuples([('Close', 'AAA'), ('Volume', 'AAA')])
        downloaded = pd.DataFrame([[10.0, 100], [11.0, 150]], index=pd.date_range('2026-08-20', periods=2), columns=columns)
        with patch.object(sp500_analyzer, 'settings', SimpleNamespace(cache=SimpleNamespace(enabled=True))), \
             patch.object(sp500_analyzer.yf, 'download', lambda *args, **kwargs: calls.append(args) or downloaded.copy()):
            first, second = analyzer(cache), analyzer(cache)
            first._load_stock_data()
            second._load_stock_data()
        self.assertEqual(len(calls), 1)
        pd.testing.assert_frame_equal(second.all_data, first.all_data)
        self.assertIn(('Energy', 'AAA'), second.all_data.columns)


if __name__ == '__main__': unittest.main()
