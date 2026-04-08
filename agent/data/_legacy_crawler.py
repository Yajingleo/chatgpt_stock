import pandas as pd
import yfinance as yf
import argparse
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

from agent.config import settings
from agent.utils import get_logger

logger = get_logger('agent.news_crawler')


class StockNewsCrawler:
    """Fetch and display stock news from Yahoo Finance with parallel processing."""

    def __init__(self, tickers: list[str], max_workers: int = None):
        self.tickers = tickers
        self.news_df = pd.DataFrame()
        self.max_workers = max_workers or settings.processing.max_workers
        self._lock = None  # Will be set if needed for thread safety

    def _get_stock_news_for_ticker(self, ticker: str) -> List[Dict[str, Any]]:
        """Fetch news for a single ticker. Returns list of news items."""
        news_items_list = []
        try:
            stock = yf.Ticker(ticker)
            news_items = stock.news or []

            for item in news_items:
                content = item.get('content', {})
                canonical_url = content.get('canonicalUrl', {})

                news_items_list.append({
                    'PublishedTime': content.get('pubDate', 'No date'),
                    'Ticker': ticker,
                    'Title': content.get('title', 'No title'),
                    'Link': canonical_url.get('url', 'No link'),
                    'Summary': content.get('summary', 'No summary')
                })

            logger.info(f"Fetched {len(news_items_list)} news items for {ticker}")

        except Exception as e:
            logger.warning(f"Error fetching news for {ticker}: {e}")

        return news_items_list

    def get_stock_news(self):
        """Fetch news for all tickers in parallel."""
        logger.info(f"Fetching news for {len(self.tickers)} tickers using {self.max_workers} workers")

        all_news = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_ticker = {
                executor.submit(self._get_stock_news_for_ticker, ticker): ticker
                for ticker in self.tickers
            }

            # Collect results as they complete
            completed = 0
            total = len(self.tickers)
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                completed += 1
                try:
                    news_items = future.result()
                    all_news.extend(news_items)
                    logger.info(f"[{completed}/{total}] Completed {ticker}: {len(news_items)} articles")
                except Exception as e:
                    logger.error(f"[{completed}/{total}] Failed {ticker}: {e}")

        # Convert to DataFrame
        if all_news:
            self.news_df = pd.DataFrame(all_news)

        logger.info(f"Total news fetched: {len(self.news_df)} articles from {len(self.tickers)} tickers")

    def save_news_to_csv(self, dirname="report", filename="stock_news.csv"):
        """Save the news DataFrame to a CSV file."""
        filepath = os.path.join(dirname, filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        self.news_df.to_csv(filepath, index=False)
        print(f"News saved to {filepath}")


def parse_ticker_list(ticker_str: str) -> list[str]:
    """Parse a comma-separated string of tickers into a list."""
    return [ticker.strip().upper() for ticker in ticker_str.split(',') if ticker.strip()]

if __name__ == "__main__":
    from agent.data.sp500_analyzer import SP500StockAnalyzer

    # Create argument parser
    parser = argparse.ArgumentParser(description='Get stock news from Yahoo Finance')
    parser.add_argument('--tickers', type=parse_ticker_list, default="APPL,MSFT,GOOGL,AMZN,TSLA,NVDA,META",
                      help='Comma-separated list of stock ticker symbols (default: PARA)')

    # Parse arguments
    args = parser.parse_args()

    # Get SP500 recommended tickers
    sp_500_analyzer = SP500StockAnalyzer()
    sp_500_analyzer.analyze_stocks(lookback_days=30)
    sp_500_tickers = sp_500_analyzer.get_recommanded_tickers()
    print(f"SP500 recommended tickers: {sp_500_tickers}")

    # Combine user tickers with SP500 recommended tickers
    all_tickers = list(set(args.tickers + sp_500_tickers))
    print(f"Fetching news for tickers: {all_tickers}")      
    crawler = StockNewsCrawler(all_tickers)
    crawler.get_stock_news()
    crawler.save_news_to_csv(dirname="report", filename="stock_news.csv")


    
   