"""yfinance-backed market data adapter."""

from agent.config import settings
from agent.providers.market.sp500 import SP500StockAnalyzer


class YFinanceMarketProvider:
    def momentum_tickers(self, lookback_days=None):
        analyzer = SP500StockAnalyzer()
        analyzer.analyze_stocks(lookback_days=lookback_days or settings.analysis.lookback_days)
        tickers = analyzer.get_recommanded_tickers()
        return list(tickers)
