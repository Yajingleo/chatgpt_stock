"""Cache integration test for SEC CIK lookups."""

from types import SimpleNamespace
import unittest
from unittest.mock import patch


class InMemoryCache:
    def __init__(self): self.values = {}
    def get(self, key): return self.values.get(repr(sorted(key.items())))
    def set(self, key, value, ttl=None): self.values[repr(sorted(key.items()))] = value


class SECFilingsCacheTest(unittest.TestCase):
    def test_cik_lookup_reuses_cached_result(self):
        from agent.providers.sec import edgar as sec_filings
        cache, calls = InMemoryCache(), []
        settings = SimpleNamespace(cache=SimpleNamespace(enabled=True, sec_filings_ttl=60, fundamentals_ttl=60))
        response = lambda *args, **kwargs: calls.append(args[0]) or SimpleNamespace(json=lambda: {'0': {'ticker': 'ABC', 'cik_str': 123}})
        with patch.object(sec_filings, 'get_session_cache', lambda *args: cache), \
             patch.object(sec_filings, 'settings', settings), \
             patch.object(sec_filings.requests, 'get', response):
            analyzer = sec_filings.SECFilingsAnalyzer()
            self.assertEqual(analyzer.get_company_cik('ABC'), '0000000123')
            self.assertEqual(analyzer.get_company_cik('ABC'), '0000000123')
        self.assertEqual(len(calls), 1)


if __name__ == '__main__': unittest.main()
