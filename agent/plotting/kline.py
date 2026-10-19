"""Render K-line charts from an in-memory OHLC DataFrame."""

import os

import pandas as pd


class KlinePlotter:
    """Plot field/ticker MultiIndex data without fetching or caching prices."""

    def plot(self, data: pd.DataFrame, ticker: str, days: int = 60, output_path=None):
        """Return a matplotlib Figure of adjusted daily OHLC candlesticks.

        Uses already loaded data, omits incomplete OHLC rows, and plots the
        latest ``days`` trading sessions. Optionally saves to ``output_path``.
        Green candles close at or above open; red candles close below open.
        """
        import numpy as np
        from matplotlib.figure import Figure
        from matplotlib.patches import Rectangle

        if not isinstance(days, int) or isinstance(days, bool) or days <= 0:
            raise ValueError('days must be a positive integer')
        ticker = ticker.strip().upper()
        if data is None or ticker not in data.columns.get_level_values(1):
            raise ValueError(f'No loaded price data for {ticker}')
        fields = ['Open', 'High', 'Low', 'Close']
        if any((field, ticker) not in data.columns for field in fields):
            raise ValueError(f'Missing OHLC columns for {ticker}')
        prices = data.loc[:, [(field, ticker) for field in fields]].copy()
        prices.columns = fields
        prices = prices.replace([np.inf, -np.inf], np.nan).dropna().sort_index().tail(days)
        if prices.empty:
            raise ValueError(f'No complete OHLC rows for {ticker}')

        figure = Figure(figsize=(12, 6), constrained_layout=True)
        ax = figure.subplots()
        for x, (opening, high, low, close) in enumerate(prices.itertuples(index=False, name=None)):
            color = '#16803c' if close >= opening else '#dc2626'
            ax.vlines(x, low, high, color=color, linewidth=1)
            if close == opening:
                ax.hlines(close, x - 0.3, x + 0.3, color=color, linewidth=1.5)
            else:
                ax.add_patch(Rectangle((x - 0.3, min(opening, close)), 0.6,
                                       abs(close - opening), facecolor=color, edgecolor=color))
        ticks = np.unique(np.linspace(0, len(prices) - 1, min(8, len(prices)), dtype=int))
        ax.set_xticks(ticks)
        ax.set_xticklabels(prices.index[ticks].strftime('%Y-%m-%d'), rotation=30, ha='right')
        ax.set_xlim(-1, len(prices))
        ax.autoscale_view(scalex=False)
        ax.set_title(f'{ticker} — Daily K-line ({len(prices)} trading sessions)')
        ax.set_ylabel('Adjusted price')
        ax.set_xlabel('Trading date · Green: close ≥ open · Red: close < open')
        ax.grid(axis='y', alpha=0.2)
        if output_path is not None:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            figure.savefig(output_path, dpi=150)
        return figure

