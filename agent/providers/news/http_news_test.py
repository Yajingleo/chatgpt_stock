"""Cache integration test for news retrieval."""

from types import SimpleNamespace
import unittest
from unittest.mock import patch

import pandas as pd


class InMemoryCache:
    def __init__(self): self.values = {}
    def get(self, key): return self.values.get(repr(sorted(key.items())))
    def set(self, key, value, ttl=None): self.values[repr(sorted(key.items()))] = value


class NewsCrawlerCacheTest(unittest.TestCase):
    def test_reuses_cached_result(self):
        from agent.providers.news import http_news as news_crawler
        cache, calls = InMemoryCache(), []
        class FakeCrawler:
            def __init__(self, tickers):
                calls.append(tickers)
                self.news_df = pd.DataFrame([{'Ticker': tickers[0], 'Title': 'Cached news'}])
            def get_stock_news(self): pass
        settings = SimpleNamespace(cache=SimpleNamespace(enabled=True, news_ttl=60), processing=SimpleNamespace(news_limit=5, max_articles_to_enhance=1))
        with patch.object(news_crawler, 'get_session_cache', lambda *args: cache), \
             patch.object(news_crawler, 'settings', settings), \
             patch.object(news_crawler, 'StockNewsCrawler', FakeCrawler):
            self.assertEqual(news_crawler.fetch_stock_news_tool(['ABC'], fetch_full_content=False)['news_count'], 1)
            self.assertEqual(news_crawler.fetch_stock_news_tool(['ABC'], fetch_full_content=False)['news_count'], 1)
        self.assertEqual(calls, [['ABC']])


if __name__ == '__main__': unittest.main()
