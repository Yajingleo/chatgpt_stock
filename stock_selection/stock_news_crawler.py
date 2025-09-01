import requests
from bs4 import BeautifulSoup
import yfinance as yf
import argparse

def get_stock_news(ticker="PARA"):
    try:
        # Get news from Yahoo Finance
        stock = yf.Ticker(ticker)
        news_items = stock.news
        
        print(f"Recent news for {ticker}:")
        for item in news_items:
            # print(item['content'])
            # print(item['content'].keys())
        
            print(f"\nTitle: {item['content'].get('title', 'No title')}")
            print(f"Link: {item['content']['canonicalUrl'].get('url', 'No link')}")
            print(f"Published: {item['content'].get('pubDate', 'No date')}")
            print(f"Summary: {item['content'].get('summary', 'No summary')}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Error fetching news: {e}")

def parse_ticker_list(ticker_string):
    """Parse comma-separated ticker string into a list."""
    return [ticker.strip().upper() for ticker in ticker_string.split(',')]

if __name__ == "__main__":
    # Create argument parser
    parser = argparse.ArgumentParser(description='Get stock news from Yahoo Finance')
    parser.add_argument('--tickers', type=parse_ticker_list, default="PARA",
                      help='Comma-separated list of stock ticker symbols (default: PARA)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Get news for each specified ticker
    for ticker in args.tickers:
        get_stock_news(ticker)
        print("\n" + "=" * 80 + "\n")  # Separator between different stocks