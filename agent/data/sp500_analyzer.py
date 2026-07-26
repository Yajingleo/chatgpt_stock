"""
S&P 500 Stock Analyzer

Analyzes S&P 500 stocks based on energy (price movement * volume) and returns.
Uses caching to avoid repeated API calls for ticker list.
"""
import argparse
from datetime import datetime, timedelta
import logging
import os
import urllib
import time
from typing import Optional

# Suppress yfinance internal error messages
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

import pandas as pd
import yfinance as yf

from agent.config import (
    settings,
    SP500_WIKIPEDIA_URL,
    EXTRA_TICKERS,
    LIQUIDITY_HORIZONS,
)
from agent.utils import get_logger, get_cache

logger = get_logger('agent.sp500_analyzer')


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='S&P 500 Stock Energy Analysis with customizable parameters',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        '--lookback_days', type=int,
        default=settings.analysis.lookback_days,
        help=f'Number of days to look back for analysis (default: {settings.analysis.lookback_days})'
    )

    parser.add_argument(
        '--num_processes', type=int,
        default=settings.processing.num_processes,
        help=f'Number of parallel processes for data fetching (default: {settings.processing.num_processes})'
    )

    parser.add_argument(
        '--top_n', type=int,
        default=settings.analysis.top_n_results,
        help=f'Number of top/bottom results to display (default: {settings.analysis.top_n_results})'
    )

    parser.add_argument(
        '--years_lookback', type=int,
        default=settings.analysis.years_lookback,
        help=f'Number of years of historical data to fetch (default: {settings.analysis.years_lookback})'
    )

    parser.add_argument(
        '--output_dir', type=str, default=None,
        help='Output directory for CSV files (optional)'
    )

    parser.add_argument(
        '--num_stocks_to_test', type=int, default=None,
        help='Limit number of stocks to test (for debugging)'
    )

    return parser.parse_args()


class SP500StockAnalyzer:
    """Analyzes S&P 500 stocks based on energy and returns."""

    def __init__(self, years_lookback: Optional[int] = None, num_stocks_to_test: Optional[int] = None):
        """
        Initialize the analyzer.

        Args:
            years_lookback: Number of years of historical data to fetch.
                           Defaults to settings.analysis.years_lookback.
            num_stocks_to_test: Limit number of stocks for testing.
        """
        self.years_lookback = years_lookback or settings.analysis.years_lookback
        self.start_date = str((datetime.now() - timedelta(days=self.years_lookback * 365)).date())
        self.end_date = str(datetime.now().date())
        self.ticker_to_name = self._initialize_tickers()
        self.tickers = list(self.ticker_to_name.keys())
        
        # Limit tickers for testing if specified
        if num_stocks_to_test and num_stocks_to_test > 0:
            self.tickers = self.tickers[:num_stocks_to_test]
            logger.info(f"Testing mode: Processing only {len(self.tickers)} stocks")

        self.all_data = None
        self.recommanded_tickers = None
        self.persistent_strong_stocks = None

        self.top_energy = None
        self.bottom_energy = None
        self.top_return = None
        self.bottom_return = None

        self.liquidity_horizons = LIQUIDITY_HORIZONS

        self._load_stock_data()

    def _load_stock_data(self):
        """Load stock data for all tickers in a single API call."""
        logger.info(f"Starting stock data download for {len(self.tickers)} stocks")
        start_time = time.time()

        data = yf.download(
            self.tickers,
            start=self.start_date,
            end=self.end_date,
            auto_adjust=True,
            progress=True,
            ignore_tz=True  # Prevents "No timezone found" errors
        )

        if data.empty:
            raise ValueError("No stock data downloaded")

        # Print raw data for debugging
        print(f"\n=== Raw Downloaded Data ===")
        print(f"Shape: {data.shape}")
        print(data.head(10))
        print(f"===========================\n")

        # Filter tickers to only those successfully downloaded
        downloaded_tickers = []
        for ticker in self.tickers:
            if ("Close", ticker) in data.columns:
                downloaded_tickers.append(ticker)
                data[("DailyReturn", ticker)] = data[("Close", ticker)] - data[("Close", ticker)].shift(1)
                data[("Energy", ticker)] = data[("DailyReturn", ticker)] * data[("Volume", ticker)]

        # Update tickers list to only include successful downloads
        failed_count = len(self.tickers) - len(downloaded_tickers)
        if failed_count > 0:
            logger.warning(f"Failed to download {failed_count} tickers, continuing with {len(downloaded_tickers)}")
        self.tickers = downloaded_tickers

        # Drop trailing rows where no ticker has a Close. yfinance's exclusive
        # end-date handling can emit an empty row for the current day.
        data = data.loc[data["Close"].notna().any(axis=1)]

        # DailyReturn/Energy start with a legitimate NaN from .shift(1); 0 is correct there.
        for field in ("DailyReturn", "Energy"):
            data[field] = data[field].fillna(0)

        # Prices must stay NaN if missing. A 0 Close silently becomes a -100% return.
        data["Close"] = data["Close"].ffill()

        self.all_data = data

        runtime_min = (time.time() - start_time) / 60
        logger.info(f"Stock data download completed in {runtime_min:.2f} minutes")

    def _initialize_tickers(self) -> dict:
        """Initialize SP500 tickers with company names."""
        sp_500_names = self._get_sp500_names()
        ticker_to_name = dict(zip(sp_500_names['Symbol'], sp_500_names["Security"]))

        # Add extra tickers from config
        ticker_to_name.update(EXTRA_TICKERS)
        return ticker_to_name

    def _get_sp500_names(self) -> pd.DataFrame:
        """Get SP500 company names from Wikipedia with caching."""
        cache = get_cache()
        cache_key = 'sp500_ticker_list'

        # Check if caching is enabled
        if settings.cache.enabled:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                logger.debug("Using cached S&P 500 ticker list")
                return pd.DataFrame(cached_data)

        # Fetch from Wikipedia
        logger.info("Fetching S&P 500 ticker list from Wikipedia")
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(SP500_WIKIPEDIA_URL, headers=headers)
        response = urllib.request.urlopen(req)
        html = response.read()
        df = pd.read_html(html)[0]

        logger.info(f"Loaded {len(df)} S&P 500 companies")

        # Cache the result
        if settings.cache.enabled:
            cache.set(cache_key, df.to_dict('records'), ttl=settings.cache.sp500_ttl)
            logger.debug(f"Cached S&P 500 ticker list (TTL: {settings.cache.sp500_ttl}s)")

        return df

    def _get_n_days_energy(self, n_day: int) -> pd.DataFrame:
        """Gets the energy in the last n days."""
        if n_day == 0:
            return pd.DataFrame()

        sub_data = self.all_data.loc[self.all_data.index[-n_day:]]
        col = f'{n_day}D_Energy'
        energy_df = pd.DataFrame(sub_data.Energy.sum(), columns=[col]).reset_index()
        energy_df["Stock"] = energy_df["Ticker"].replace(self.ticker_to_name)
        energy_df.sort_values(by=[col], ascending=[False], inplace=True)
        energy_df["Start_Date"] = sub_data.index.min()
        return energy_df.reset_index(drop=True)

    def _get_n_days_return(self, n_day: int) -> pd.DataFrame:
        """Calculate n-day returns for all stocks."""
        if n_day == 0:
            return pd.DataFrame()

        # An n-day return spans n intervals, so it needs n+1 rows of prices.
        # Clamp when history is shorter than the requested window.
        start_date = self.all_data.index[max(-(n_day + 1), -len(self.all_data))]

        last_day_data = self.all_data.loc[self.all_data.index[-1], ["Close"]]
        last_n_day_data = self.all_data.loc[start_date, ["Close"]]

        # Guard the divisor so bad data surfaces as NaN rather than inf.
        return_n_day = (last_day_data / last_n_day_data.replace(0, float("nan")) - 1).round(2)
        col_name = f"{n_day}D_Return"
        return_df = pd.DataFrame(return_n_day, columns=[col_name]).reset_index()
        return_df["Stock"] = return_df["Ticker"].replace(self.ticker_to_name)
        return_df["Start_Date"] = start_date
        return return_df.sort_values(col_name, ascending=False).reset_index(drop=True)

    def analyze_stocks(
        self,
        lookback_days: Optional[int] = None,
        top_n: Optional[int] = None
    ):
        """
        Main analysis method.

        Args:
            lookback_days: Number of days to analyze. Defaults to config value.
            top_n: Number of top results. Defaults to config value.
        """
        lookback_days = lookback_days or settings.analysis.lookback_days
        top_n = top_n or settings.analysis.top_n_results

        self.top_energy = self._get_n_days_energy(lookback_days)[:top_n]
        self.bottom_energy = self._get_n_days_energy(lookback_days)[-top_n:]
        self.top_return = self._get_n_days_return(lookback_days)[:top_n]
        self.bottom_return = self._get_n_days_return(lookback_days)[-top_n:]

        self.recommanded_tickers = list(set(self.top_energy.Ticker) | set(self.top_return.Ticker))

        return self.top_energy, self.bottom_energy, self.top_return, self.bottom_return

    def persistent_strong_momentum(
        self,
        top_n: Optional[int] = None,
        horizon_days: int = 120
    ) -> list:
        """Returns the top energy stocks within all the previous liquidity horizons up to half year."""
        top_n = top_n or settings.analysis.top_n_results
        top_energy_stocks = None
        top_return_stocks = None

        for liquidity in sorted(self.liquidity_horizons):
            if liquidity > horizon_days:
                break

            top_energy_cand = set(self._get_n_days_energy(liquidity)["Ticker"][:top_n])
            top_energy_stocks = top_energy_stocks & top_energy_cand if top_energy_stocks else top_energy_cand

            top_return_cand = set(self._get_n_days_return(liquidity)["Ticker"][:top_n])
            top_return_stocks = top_return_stocks & top_return_cand if top_return_stocks else top_return_cand

        return list(top_energy_stocks | top_return_stocks) if top_energy_stocks and top_return_stocks else []

    def get_recommanded_tickers(self):
        """Get recommended tickers from analysis."""
        return self.recommanded_tickers

    def save_to_csv(self, dir: str):
        """Save DataFrame to CSV."""
        self.top_energy.to_csv(os.path.join(dir, "top_energy.csv"), index=False)
        self.bottom_energy.to_csv(os.path.join(dir, "bottom_energy.csv"), index=False)
        self.top_return.to_csv(os.path.join(dir, "top_return.csv"), index=False)
        self.bottom_return.to_csv(os.path.join(dir, "bottom_return.csv"), index=False)

        logger.info(f"Analysis results saved to {dir}/")


if __name__ == '__main__':
    args = parse_args()

    # Create analyzer instance
    analyzer = SP500StockAnalyzer(
        years_lookback=args.years_lookback,
        num_stocks_to_test=args.num_stocks_to_test
    )

    # Run analysis
    top_energy, bottom_energy, top_return, bottom_return = analyzer.analyze_stocks(
        lookback_days=args.lookback_days,
        top_n=args.top_n
    )

    if args.output_dir:
        if not os.path.exists(args.output_dir):
            os.makedirs(args.output_dir)
        analyzer.save_to_csv(args.output_dir)

    print(f"\nTop {args.top_n} {args.lookback_days}D Energy:\n", top_energy)
    print(f"\nBottom {args.top_n} {args.lookback_days}D Energy:\n", bottom_energy)
    print(f"\nTop {args.top_n} {args.lookback_days}D Return:\n", top_return)
    print(f"\nBottom {args.top_n} {args.lookback_days}D Return:\n", bottom_return)
    print(f"Recommended Tickers ({len(analyzer.get_recommanded_tickers())}): {analyzer.get_recommanded_tickers()}")
    print(f"Persistent strong stocks: {analyzer.persistent_strong_momentum()}")
    print("\n")
