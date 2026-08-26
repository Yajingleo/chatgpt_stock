"""Stock-analysis application use cases."""

from typing import Any, Dict, List, Optional

from agent.config import settings
from agent.services.recommendations import generate_recommendations_tool
from agent.services.sentiment import analyze_sentiment_tool


class StockAnalysisService:
    def __init__(self, market_provider, news_provider):
        self.market_provider = market_provider
        self.news_provider = news_provider

    def momentum(self, lookback_days: Optional[int] = None) -> Dict[str, Any]:
        try:
            tickers = self.market_provider.momentum_tickers(lookback_days or settings.analysis.lookback_days)
            return {"success": True, "tickers": tickers, "count": len(tickers)}
        except Exception as error:
            return {"success": False, "error": str(error)}

    def news(self, tickers: List[str], limit: Optional[int] = None) -> Dict[str, Any]:
        return self.news_provider.fetch(tickers, limit or settings.processing.news_limit)

    def sentiment(self, news_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        return analyze_sentiment_tool(news_data)

    def recommendations(self, sentiment_data: Dict[str, Any]) -> Dict[str, Any]:
        return generate_recommendations_tool(sentiment_data)
