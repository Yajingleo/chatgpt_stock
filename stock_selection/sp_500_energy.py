"""
Find S&P 500 good tickers.
"""
import argparse
from datetime import datetime, timedelta

import urllib
import yfinance as yf
import pandas as pd
import time
from multiprocessing import Pool, freeze_support
import numpy as np

class SP500StockAnalyzer:
    def __init__(self, years_lookback=1, n_batch=50, days_lookback=365):
        self.years_lookback = years_lookback
        self.n_batch = n_batch
        self.days_lookback = days_lookback
        self.start_date = str((datetime.now() - timedelta(days=years_lookback * 365)).date())
        self.end_date = str(datetime.now().date())
        self.ticker_to_name = self._initialize_tickers()
        self.tickers = list(self.ticker_to_name.keys())
        
    def _initialize_tickers(self) -> dict:
        """Initialize SP500 tickers with company names."""
        sp_500_names = self._get_sp500_names()
        ticker_to_name = dict(zip(sp_500_names['Symbol'], sp_500_names["Security"]))
        
        extra_ticker_to_name = {
            "ARM": "Arm Holdings",
            "TSM": "Taiwan SemiConductor Manufacturing Company",
        }
        ticker_to_name.update(extra_ticker_to_name)
        return ticker_to_name
    
    def _get_sp500_names(self) -> pd.DataFrame:
        """Get SP500 company names from Wikipedia."""
        sp_500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(sp_500_url, headers=headers)
        response = urllib.request.urlopen(req)
        html = response.read()
        return pd.read_html(html)[0]
    
    def fetch_stock_data(self, stock: str) -> pd.DataFrame:
        """Fetch stock data for a single ticker."""
        try:
            print(f"Downloading: {stock}")
            data = yf.download(stock, start=self.start_date, end=self.end_date, 
                             auto_adjust=None)
            data[("DailyReturn", stock)] = data.Close - data.Close.shift(1)
            data[("Energy", stock)] = data.DailyReturn * data.Volume
            return data.fillna(0)
        except Exception as e:
            print(f"Error: {stock}: {e}")
    
    def get_n_days_energy(self, all_data: pd.DataFrame, n_day: int) -> pd.DataFrame:
        """Gets the energy in the last n days."""
        if n_day == 0:
            return pd.DataFrame()
        
        sub_data = all_data.loc[all_data.index[-n_day:]]
        col = f'{n_day}D_Energy'
        energy_df = pd.DataFrame(sub_data.Energy.sum(), columns=[col]).reset_index()
        energy_df["Stock"] = energy_df["Ticker"].replace(self.ticker_to_name)
        energy_df.sort_values(by=[col], ascending=[False], inplace=True)
        return energy_df
    
    def get_n_days_return(self, all_data: pd.DataFrame, n_day: int) -> pd.DataFrame:
        """Calculate n-day returns for all stocks."""
        if n_day == 0:
            return pd.DataFrame()
        
        last_day_data = all_data.loc[all_data.index[-1], ["Close"]]
        last_n_day_data = all_data.loc[all_data.index[-n_day], ["Close"]]
        
        return_n_day = (last_day_data / last_n_day_data - 1).apply(lambda x: round(x, 2))
        col_name = f"{n_day}D_Return"
        return_df = pd.DataFrame(return_n_day, columns=[col_name]).reset_index()
        return_df["Stock"] = return_df["Ticker"].replace(self.ticker_to_name)
        return return_df.sort_values(col_name, ascending=False)
    
    def analyze_stocks(self, num_processes=10, lookback_days=10, top_n=30):
        """Main analysis method."""
        start_time = time.time()
        
        with Pool(num_processes) as pool:
            df_list = pool.map(self.fetch_stock_data, self.tickers)
        
        all_data = pd.concat(df_list, axis=1)
        
        runtime_min = (time.time() - start_time)/60
        print(f"\nRuntime Mins: {runtime_min}")

        top_energy = self.get_n_days_energy(all_data, lookback_days)[:top_n]
        bottom_energy = self.get_n_days_energy(all_data, lookback_days)[-top_n:]
        top_return = self.get_n_days_return(all_data, lookback_days)[:top_n]
        bottom_return = self.get_n_days_return(all_data, lookback_days)[-top_n:]

        return top_energy, bottom_energy, top_return, bottom_return
    
def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='S&P 500 Stock Energy Analysis with customizable parameters',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument('--lookback_days', type=int, default=10,
                       help='Number of days to look back for analysis (default: 10)')
    
    parser.add_argument('--num_processes', type=int, default=10,
                       help='Number of parallel processes for data fetching (default: 10)')
    
    parser.add_argument('--top_n', type=int, default=30,
                       help='Number of top/bottom results to display (default: 30)')
    
    parser.add_argument('--years_lookback', type=int, default=1,
                       help='Number of years of historical data to fetch (default: 1)')
    
    parser.add_argument('--output', type=str, default=None,
                       help='Output CSV file path (optional)')
    
    return parser.parse_args()

if __name__ == '__main__':
    freeze_support()
    args = parse_args()

    # Create analyzer instance
    analyzer = SP500StockAnalyzer(years_lookback=args.years_lookback)

    # Run analysis
    top_energy, bottom_energy, top_return, bottom_return = analyzer.analyze_stocks(
        num_processes=args.num_processes,
        lookback_days=args.lookback_days,
        top_n=args.top_n
    )

    print(f"\nTop {args.top_n} {args.lookback_days}D Energy:\n", top_energy)
    print(f"\nBottom {args.top_n} {args.lookback_days}D Energy:\n", bottom_energy)
    print(f"\nTop {args.top_n} {args.lookback_days}D Return:\n", top_return)
    print(f"\nBottom {args.top_n} {args.lookback_days}D Return:\n", bottom_return)
    print("\n")


