"""Unit tests for S&P 500 historical-data caching."""

from types import SimpleNamespace
import unittest
import tempfile
from pathlib import Path
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

    def test_recommended_tickers_preserve_rank_order_without_duplicates(self):
        from agent.providers.market.sp500 import SP500StockAnalyzer
        result = object.__new__(SP500StockAnalyzer)
        result.top_energy = result.bottom_energy = None
        result.top_return = result.bottom_return = None
        result._get_n_days_energy = lambda days: pd.DataFrame({
            'Ticker': ['AAA', 'BBB', 'CCC'],
            f'{days}D_Energy': [3, 2, 1],
        })
        result._get_n_days_return = lambda days: pd.DataFrame({
            'Ticker': ['BBB', 'DDD', 'AAA'],
            f'{days}D_Return': [0.3, 0.2, 0.1],
        })

        result.analyze_stocks(lookback_days=30, top_n=3)

        self.assertEqual(['AAA', 'BBB', 'CCC', 'DDD'], result.get_recommanded_tickers())


class AgentRuntimeTest(unittest.TestCase):
    def test_analysis_and_plotting_share_one_lazy_object(self):
        from unittest.mock import Mock
        from agent.runtime import AgentRuntime
        from agent.providers.market.yfinance_provider import YFinanceMarketProvider
        data = Mock(all_data=pd.DataFrame())
        data.get_recommanded_tickers.return_value = ['AAA']
        factory, plotter = Mock(return_value=data), Mock()
        runtime = AgentRuntime(analyzer_factory=factory, plotter=plotter)
        factory.assert_not_called()
        self.assertEqual(YFinanceMarketProvider(runtime).momentum_tickers(30), ['AAA'])
        runtime.plot_kline('AAA', days=10)
        self.assertIs(runtime.sp500, data)
        factory.assert_called_once_with()
        plotter.plot.assert_called_once_with(data.all_data, 'AAA', days=10, output_path=None)

    def test_runtime_reloads_after_ttl_or_date_change(self):
        from unittest.mock import Mock
        from agent.runtime import AgentRuntime
        runtime = AgentRuntime(analyzer_factory=Mock(side_effect=[object(), object(), object()]))
        first = runtime.sp500
        runtime._loaded_at = float('-inf')
        second = runtime.sp500
        self.assertIsNot(first, second)
        runtime._loaded_date = None
        self.assertIsNot(second, runtime.sp500)

    def test_new_runtime_restores_prices_from_file_without_download(self):
        from agent.runtime import AgentRuntime
        from agent.utils.cache import SessionDataCache
        from agent.providers.market import sp500
        columns = pd.MultiIndex.from_product([['Open', 'High', 'Low', 'Close', 'Volume'], ['AAA']])
        prices = pd.DataFrame([[10, 12, 9, 11, 100]],
                              index=pd.date_range('2026-08-20', periods=1), columns=columns)
        with tempfile.TemporaryDirectory() as directory:
            def factory():
                # Separate cache instances force the second load to read disk.
                result = analyzer(SessionDataCache(Path(directory), 'prices', 3600))
                result._load_stock_data()
                return result
            with patch.object(sp500, 'settings', SimpleNamespace(cache=SimpleNamespace(enabled=True))), \
                    patch.object(sp500.yf, 'download', return_value=prices) as download:
                first = AgentRuntime(analyzer_factory=factory).sp500
                second = AgentRuntime(analyzer_factory=factory).sp500
            download.assert_called_once()
            pd.testing.assert_frame_equal(first.all_data, second.all_data)


class SP500KlineTest(unittest.TestCase):
    def setUp(self):
        from agent.plotting import KlinePlotter
        self.plotter = KlinePlotter()
        self.subject = analyzer(InMemoryCache())
        columns = pd.MultiIndex.from_product([['Open', 'High', 'Low', 'Close'], ['AAA']])
        self.subject.all_data = pd.DataFrame(
            [[10, 13, 9, 12], [12, 14, 10, 11], [11, 12, 10, 11],
             [float('nan'), 12, 10, 11]],
            index=pd.date_range('2026-08-20', periods=4), columns=columns,
        )

    def test_candles_use_ohlc_and_skip_incomplete_sessions(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'charts' / 'AAA.png'
            figure = self.plotter.plot(self.subject.all_data, 'aaa', days=3, output_path=path)
            self.assertTrue(path.read_bytes().startswith(b'\x89PNG'))
        ax = figure.axes[0]
        self.assertEqual(len(ax.patches), 2)  # The doji is a horizontal line.
        self.assertEqual([p.get_height() for p in ax.patches], [2, 1])
        self.assertEqual([p.get_y() for p in ax.patches], [10, 11])
        self.assertEqual(list(ax.collections[0].get_segments()[0][:, 1]), [9, 13])
        self.assertIn('2026-08-22', [label.get_text() for label in ax.get_xticklabels()])
        self.assertNotIn('2026-08-23', [label.get_text() for label in ax.get_xticklabels()])
        recent = self.plotter.plot(self.subject.all_data, 'AAA', days=1)
        self.assertEqual(len(recent.axes[0].patches), 0)
        self.assertIn('1 trading sessions', recent.axes[0].get_title())

    def test_invalid_input_has_clear_errors(self):
        for days in (0, -1):
            with self.assertRaisesRegex(ValueError, 'positive integer'):
                self.plotter.plot(self.subject.all_data, 'AAA', days=days)
        with self.assertRaisesRegex(ValueError, 'No loaded price data'):
            self.plotter.plot(self.subject.all_data, 'UNKNOWN')
        self.subject.all_data = self.subject.all_data.astype(float) * float('nan')
        with self.assertRaisesRegex(ValueError, 'No complete OHLC'):
            self.plotter.plot(self.subject.all_data, 'AAA')


if __name__ == '__main__': unittest.main()
