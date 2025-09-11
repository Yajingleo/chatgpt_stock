#!/usr/bin/env python3
"""
Enhanced Stock Market Cap and Sector Data Fetcher
Extends your existing analysis with fundamental company information
"""

import yfinance as yf
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockFundamentalData:
    """Fetch market cap, sector, and other fundamental data for stocks"""
    
    def __init__(self):
        self.cache = {}
    
    def get_stock_info(self, ticker):
        """Get comprehensive stock information including market cap and sector"""
        if ticker in self.cache:
            return self.cache[ticker]
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Extract key fundamental data
            stock_data = {
                'ticker': ticker,
                'market_cap': info.get('marketCap', None),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'country': info.get('country', 'Unknown'),
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', 'Unknown'),
                'full_name': info.get('longName', info.get('shortName', ticker)),
                'pe_ratio': info.get('trailingPE', None),
                'forward_pe': info.get('forwardPE', None),
                'price_to_book': info.get('priceToBook', None),
                'debt_to_equity': info.get('debtToEquity', None),
                'return_on_equity': info.get('returnOnEquity', None),
                'profit_margin': info.get('profitMargins', None),
                'revenue': info.get('totalRevenue', None),
                'ebitda': info.get('ebitda', None),
                'dividend_yield': info.get('dividendYield', None),
                'beta': info.get('beta', None),
                '52_week_high': info.get('fiftyTwoWeekHigh', None),
                '52_week_low': info.get('fiftyTwoWeekLow', None),
                'avg_volume': info.get('averageVolume', None),
                'shares_outstanding': info.get('sharesOutstanding', None),
                'float_shares': info.get('floatShares', None),
                'employees': info.get('fullTimeEmployees', None),
                'business_summary': info.get('longBusinessSummary', ''),
            }
            
            # Cache the result
            self.cache[ticker] = stock_data
            logger.info(f"Retrieved data for {ticker}: {stock_data['full_name']}")
            
            return stock_data
            
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {str(e)}")
            return {
                'ticker': ticker,
                'market_cap': None,
                'sector': 'Error',
                'industry': 'Error',
                'full_name': ticker,
                'error': str(e)
            }
    
    def get_multiple_stocks_info(self, tickers, max_workers=5):
        """Get fundamental data for multiple stocks concurrently"""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_ticker = {
                executor.submit(self.get_stock_info, ticker): ticker 
                for ticker in tickers
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Exception for {ticker}: {e}")
                    results.append({
                        'ticker': ticker,
                        'market_cap': None,
                        'sector': 'Error',
                        'error': str(e)
                    })
                
                # Small delay to be respectful to the API
                time.sleep(0.1)
        
        return results

def format_market_cap(market_cap):
    """Format market cap in human-readable format"""
    if pd.isna(market_cap) or market_cap is None:
        return "N/A"
    
    if market_cap >= 1e12:
        return f"${market_cap/1e12:.2f}T"
    elif market_cap >= 1e9:
        return f"${market_cap/1e9:.2f}B"
    elif market_cap >= 1e6:
        return f"${market_cap/1e6:.2f}M"
    else:
        return f"${market_cap:,.0f}"

if __name__ == "__main__":
    # Sample tickers from your analysis
    sample_tickers = ['AVGO', 'GOOGL', 'TSLA', 'GOOG', 'UNH']
    
    # Initialize the data fetcher
    fetcher = StockFundamentalData()
    
    # Get fundamental data
    print("Fetching fundamental data...")
    fundamental_data = fetcher.get_multiple_stocks_info(sample_tickers)
    
    # Create DataFrame
    fundamentals_df = pd.DataFrame(fundamental_data)
    
    # Display results
    print("\n=== STOCK FUNDAMENTAL DATA ===")
    for _, row in fundamentals_df.iterrows():
        print(f"{row['ticker']:>6} | {row['full_name'][:30]:30} | "
              f"{row['sector']:15} | {format_market_cap(row['market_cap']):>10}")
    
    # Save to CSV
    output_file = "stock_fundamentals.csv"
    fundamentals_df.to_csv(output_file, index=False)
    print(f"\nData saved to {output_file}")
