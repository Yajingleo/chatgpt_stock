"""Render K-line charts from an in-memory OHLC DataFrame."""

import os

import pandas as pd

FIELDS = ['Open', 'High', 'Low', 'Close']
VOLUME = 'Volume'


class KlinePlotter:
    """Plot field/ticker MultiIndex data without fetching or caching prices."""

    def _validate(self, data: pd.DataFrame, ticker: str, days: int) -> None:
        """Raise ValueError unless ``data`` can be plotted for ``ticker``."""
        if not isinstance(days, int) or isinstance(days, bool) or days <= 0:
            raise ValueError('days must be a positive integer')
        if data is None or ticker not in data.columns.get_level_values(1):
            raise ValueError(f'No loaded price data for {ticker}')
        if any((field, ticker) not in data.columns for field in FIELDS):
            raise ValueError(f'Missing OHLC columns for {ticker}')

    def plot(self, data: pd.DataFrame, ticker: str, days: int = 60, output_path=None):
        """Return a matplotlib Figure of adjusted daily OHLC candlesticks.

        Uses already loaded data, omits incomplete OHLC rows, and plots the
        latest ``days`` trading sessions. Optionally saves to ``output_path``.
        Green candles close at or above open; red candles close below open.
        """
        import numpy as np
        from matplotlib.figure import Figure
        from matplotlib.patches import Rectangle

        ticker = ticker.strip().upper()
        self._validate(data, ticker, days)
        prices = data.loc[:, [(field, ticker) for field in FIELDS]].copy()
        prices.columns = FIELDS
        prices = prices.replace([np.inf, -np.inf], np.nan).dropna().sort_index().tail(days)
        if prices.empty:
            raise ValueError(f'No complete OHLC rows for {ticker}')

        volume = None
        if (VOLUME, ticker) in data.columns:
            volume = data[(VOLUME, ticker)].reindex(prices.index).fillna(0)

        figure = Figure(figsize=(12, 6), constrained_layout=True)
        if volume is None:
            ax = bottom = figure.subplots()
        else:
            ax, volume_ax = figure.subplots(2, 1, sharex=True, height_ratios=[3, 1])
            bottom = volume_ax
        colors = []
        for x, (opening, high, low, close) in enumerate(prices.itertuples(index=False, name=None)):
            color = '#16803c' if close >= opening else '#dc2626'
            colors.append(color)
            ax.vlines(x, low, high, color=color, linewidth=1)
            if close == opening:
                ax.hlines(close, x - 0.3, x + 0.3, color=color, linewidth=1.5)
            else:
                ax.add_patch(Rectangle((x - 0.3, min(opening, close)), 0.6,
                                       abs(close - opening), facecolor=color, edgecolor=color))
        ticks = np.unique(np.linspace(0, len(prices) - 1, min(8, len(prices)), dtype=int))
        if volume is not None:
            volume_ax.bar(range(len(prices)), volume, width=0.6, color=colors)
            volume_ax.set_ylabel('Volume')
            volume_ax.grid(axis='y', alpha=0.2)
        bottom.set_xticks(ticks)
        bottom.set_xticklabels(prices.index[ticks].strftime('%Y-%m-%d'), rotation=30, ha='right')
        ax.set_xlim(-1, len(prices))
        ax.autoscale_view(scalex=False)
        ax.set_title(f'{ticker} — Daily K-line ({len(prices)} trading sessions)')
        ax.set_ylabel('Adjusted price')
        bottom.set_xlabel('Trading date · Green: close ≥ open · Red: close < open')
        ax.grid(axis='y', alpha=0.2)
        if output_path is not None:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            figure.savefig(output_path, dpi=150)
        return figure

