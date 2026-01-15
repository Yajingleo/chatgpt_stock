import pandas as pd
import yfinance as yf
import argparse
import os

try:
    from sp_500_energy import SP500StockAnalyzer
except ImportError:
    from .sp_500_energy import SP500StockAnalyzer

class StockNewsCrawler:
    """Fetch and display stock news from Yahoo Finance."""

    def __init__(self, tickers: list[str]):
        self.tickers = tickers
        self.news_df = pd.DataFrame()

    def _get_stock_news(self, ticker: str):
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

                # Append news to DataFrame
                self.news_df = pd.concat([self.news_df, pd.DataFrame([{
                    'PublishedTime': item['content'].get('pubDate', 'No date'),
                    'Ticker': ticker,
                    'Title': item['content'].get('title', 'No title'),
                    'Link': item['content']['canonicalUrl'].get('url', 'No link'),
                    'Summary': item['content'].get('summary', 'No summary')
                }])], ignore_index=True)

                print("-" * 50)
            
        except Exception as e:
            print(f"Error fetching news: {e}")
    
    def get_stock_news(self):
        for ticker in self.tickers:
            self._get_stock_news(ticker)
            print("\n" + "=" * 80 + "\n")  # Separator between different stocks
        print(self.news_df)

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


    
   