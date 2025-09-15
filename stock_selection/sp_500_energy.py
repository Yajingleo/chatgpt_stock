"""
Find S&P 500 good tickers.
"""
import argparse
from datetime import datetime, timedelta

import os
import urllib
import yfinance as yf
import pandas as pd
import time
from multiprocessing import Pool, freeze_support
import numpy as np

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

    parser.add_argument('--output_dir', type=str, default=None,
                       help='Output directory for CSV files (optional)')

    return parser.parse_args()

class SP500StockAnalyzer:
    def __init__(self, years_lookback=1):
        self.years_lookback = years_lookback
        self.start_date = str((datetime.now() - timedelta(days=years_lookback * 365)).date())
        self.end_date = str(datetime.now().date())
        self.ticker_to_name = self._initialize_tickers()
        self.tickers = list(self.ticker_to_name.keys())

        self.all_data = pd.DataFrame()
        self.recommanded_tickers = []

        self.top_energy = pd.DataFrame()
        self.bottom_energy = pd.DataFrame()
        self.top_return = pd.DataFrame()
        self.bottom_return = pd.DataFrame()

    def _initialize_tickers(self) -> dict:
        """Initialize SP500 tickers with company names."""
        sp_500_names = self._get_sp500_names()
        ticker_to_name = dict(zip(sp_500_names['Symbol'], sp_500_names["Security"]))
        
        extra_ticker_to_name = {
            "ARM": "Arm Holdings",
            "TSM": "Taiwan SemiConductor Manufacturing Company",
            "NUKZ": "Range Nuclear Renaissance Index ETF",
            "NLR": "VanEck Uranium and Nuclear ETF",
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
    
    def _fetch_stock_data(self, stock: str) -> pd.DataFrame:
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

        last_day_data = self.all_data.loc[self.all_data.index[-1], ["Close"]]
        last_n_day_data = self.all_data.loc[self.all_data.index[-n_day], ["Close"]]

        return_n_day = (last_day_data / last_n_day_data - 1).apply(lambda x: round(x, 2))
        col_name = f"{n_day}D_Return"
        return_df = pd.DataFrame(return_n_day, columns=[col_name]).reset_index()
        return_df["Stock"] = return_df["Ticker"].replace(self.ticker_to_name)
        return_df["Start_Date"] = self.all_data.index[-n_day]
        return return_df.sort_values(col_name, ascending=False).reset_index(drop=True)
    
    def analyze_stocks(self, num_processes=10, lookback_days=20, top_n=30):
        """Main analysis method."""
        start_time = time.time()
        
        with Pool(num_processes) as pool:
            df_list = pool.map(self._fetch_stock_data, self.tickers)
        
        self.all_data = pd.concat(df_list, axis=1)
        
        runtime_min = (time.time() - start_time)/60
        print(f"\nRuntime Mins: {runtime_min}")

        self.top_energy = self._get_n_days_energy(lookback_days)[:top_n]
        self.bottom_energy = self._get_n_days_energy(lookback_days)[-top_n:]
        self.top_return = self._get_n_days_return(lookback_days)[:top_n]
        self.bottom_return = self._get_n_days_return(lookback_days)[-top_n:]

        self.recommanded_tickers = list(set(self.top_energy.Ticker) | set(self.top_return.Ticker))

        return self.top_energy, self.bottom_energy, self.top_return, self.bottom_return

    def get_recommanded_tickers(self):
        return self.recommanded_tickers
    
    def save_to_csv(self, dir: str):
        """Save DataFrame to CSV."""
        self.top_energy.to_csv(os.path.join(dir, "top_energy.csv"), index=False)
        self.bottom_energy.to_csv(os.path.join(dir, "bottom_energy.csv"), index=False)
        self.top_return.to_csv(os.path.join(dir, "top_return.csv"), index=False)
        self.bottom_return.to_csv(os.path.join(dir, "bottom_return.csv"), index=False)

        print(f"Saved to {dir}/")

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

    if args.output_dir:
        if not os.path.exists(args.output_dir):
            os.makedirs(args.output_dir)
        analyzer.save_to_csv(args.output_dir)

    print(f"\nTop {args.top_n} {args.lookback_days}D Energy:\n", top_energy)
    print(f"\nBottom {args.top_n} {args.lookback_days}D Energy:\n", bottom_energy)
    print(f"\nTop {args.top_n} {args.lookback_days}D Return:\n", top_return)
    print(f"\nBottom {args.top_n} {args.lookback_days}D Return:\n", bottom_return)
    print(f"Recommanded Tickers ({len(analyzer.get_recommanded_tickers())}): {analyzer.get_recommanded_tickers()}")
    print("\n")
