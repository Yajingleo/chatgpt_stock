"""yfinance-backed market data adapter."""

from agent.config import settings


class YFinanceMarketProvider:
    def __init__(self, runtime=None):
        # Local import avoids a cycle through the market package exports.
        from agent.runtime import AgentRuntime
        self.runtime = runtime if runtime is not None else AgentRuntime()

    def momentum_tickers(self, lookback_days=None):
        return self.runtime.momentum_tickers(lookback_days or settings.analysis.lookback_days)
