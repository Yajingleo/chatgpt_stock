"""Long-lived market data shared by an agent's analysis and plotting calls."""

from datetime import date
from threading import RLock
from time import monotonic

from agent.config import settings
from agent.plotting import KlinePlotter
from agent.providers.market.sp500 import SP500StockAnalyzer


class AgentRuntime:
    """Lazily retain an S&P 500 data/analyzer object backed by its file cache.

    Memory is reused for ``stock_data_ttl`` seconds or until the date changes.
    Reloading consults the analyzer's existing disk cache before downloading.
    """

    def __init__(self, *, analyzer_factory=None, plotter=None):
        self._analyzer_factory = analyzer_factory or SP500StockAnalyzer
        self.plotter = plotter or KlinePlotter()
        self._sp500 = None
        self._loaded_at = None
        self._loaded_date = None
        self._lock = RLock()

    @property
    def sp500(self):
        with self._lock:
            if (self._sp500 is None or self._loaded_date != date.today()
                    or monotonic() - self._loaded_at >= settings.cache.stock_data_ttl):
                loaded = self._analyzer_factory()
                self._sp500 = loaded
                self._loaded_at = monotonic()
                self._loaded_date = date.today()
            return self._sp500

    def momentum_tickers(self, lookback_days=None):
        with self._lock:
            data = self.sp500
            data.analyze_stocks(lookback_days=lookback_days)
            return list(data.get_recommanded_tickers())

    def plot_kline(self, ticker, days=60, output_path=None):
        return self.plotter.plot(self.sp500.all_data, ticker, days=days,
                                 output_path=output_path)
