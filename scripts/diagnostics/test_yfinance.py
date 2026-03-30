#!/usr/bin/env python3
"""
Simple test script to verify yfinance API functionality.
Tests basic download operations with individual stocks.
"""
import sys
import yfinance as yf
from datetime import datetime, timedelta
import warnings
import pandas as pd

print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"yfinance version: {yf.__version__}")
print(f"pandas version: {pd.__version__}")
print("-" * 50)

if __name__ == "__main__":
    # Load the stock data for Apple
    tickers = ["MMM", "AAPL", "AMZN", "GOOGL", "META", "MSFT", "NVDA", "TSLA", "UNH"]
    
    # Suppress yfinance warnings for cleaner output
    warnings.filterwarnings("ignore", category=FutureWarning, module="yfinance")
    
    print(f"Loading stock data for {tickers}...")
    
    # Set date range (last 30 days)
    start_date = str((datetime.now() - timedelta(days=30)).date())
    end_date = str(datetime.now().date())
    print(f"Date range: {start_date} to {end_date}")
    
    try:
        # Download stock data
        print("Calling yf.download()...")
        data = yf.download(
            tickers,
            start=start_date,
            end=end_date,
            auto_adjust=True,
            progress=True  # Show progress
        )
        
        print(f"\nData type: {type(data)}")
        print(f"Data shape: {data.shape}")
        print(f"Data empty: {data.empty}")
        print(f"Columns: {list(data.columns)[:10]}...")  # First 10 columns
        
        if data.empty:
            print(f"❌ No data returned - DataFrame is empty!")
            print("Trying single ticker test...")
            single = yf.download("AAPL", period="5d", progress=True)
            print(f"Single ticker result: {single.shape}, empty={single.empty}")
        else:
            print(f"\n✅ Successfully loaded {len(data)} days of data")
            print(data.head())
            
    except Exception as e:
        import traceback
        print(f"❌ Error: {e}")
        traceback.print_exc()