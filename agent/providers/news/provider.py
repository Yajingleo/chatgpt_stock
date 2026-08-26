"""HTTP/yfinance-backed news adapter."""

from agent.providers.news.http_news import fetch_stock_news_tool


class HttpNewsProvider:
    def fetch(self, tickers, limit=None):
        return fetch_stock_news_tool(tickers, limit=limit)
