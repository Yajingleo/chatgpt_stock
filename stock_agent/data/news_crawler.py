"""
News Crawler Agent Module

This module handles all news fetching and content scraping functionality
for stock news analysis. It provides tools for fetching stock news with
optional full content extraction from article URLs.

Features:
- Retry logic with exponential backoff for HTTP requests
- Rate limiting to prevent server throttling
- Configurable timeouts and content limits
"""

import re
import time
from typing import List, Dict, Any

import requests
from bs4 import BeautifulSoup

from stock_agent.config import (
    settings,
    ARTICLE_SELECTORS,
    DEFAULT_USER_AGENT,
)
from stock_agent.utils import (
    get_logger,
    retry,
    get_rate_limiter,
    RetryError,
)

# Import existing functionality
from stock_agent.data._legacy_crawler import StockNewsCrawler

logger = get_logger('stock_agent.news_crawler')


def fetch_full_article_content(url: str) -> str:
    """
    Scrape full article content from URL with retry logic.

    Args:
        url: The article URL to fetch

    Returns:
        The extracted article text, truncated to max length
    """
    try:
        # Use rate limiter for news fetching
        limiter = get_rate_limiter('news')
        limiter.acquire()

        return _fetch_article_with_retry(url)
    except RetryError as e:
        logger.warning(f"All retries failed for {url}: {e}")
        return f"Could not fetch article content after retries: {str(e)[:100]}"
    except Exception as e:
        return f"Could not fetch article content: {str(e)[:100]}"


@retry(
    max_attempts=3,
    base_delay=1.0,
    retryable_exceptions=(requests.RequestException, requests.Timeout)
)
def _fetch_article_with_retry(url: str) -> str:
    """Fetch article content with retry logic."""
    headers = {'User-Agent': DEFAULT_USER_AGENT}

    response = requests.get(
        url,
        headers=headers,
        timeout=settings.rate_limit.request_timeout
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    # Try different article content selectors
    article_text = ""
    for selector in ARTICLE_SELECTORS:
        elements = soup.select(selector)
        if elements:
            article_text = ' '.join([elem.get_text(strip=True) for elem in elements])
            break

    # Fallback: get all paragraph text
    if not article_text:
        paragraphs = soup.find_all('p')
        article_text = ' '.join([p.get_text(strip=True) for p in paragraphs])

    # Clean and limit text
    article_text = re.sub(r'\s+', ' ', article_text)
    max_length = settings.content.max_article_text_length
    return article_text[:max_length] if len(article_text) > max_length else article_text


def fetch_stock_news_tool(
    tickers: List[str],
    limit: int = None,
    fetch_full_content: bool = True
) -> Dict[str, Any]:
    """
    ADK Tool: Fetch stock news for given tickers with optional full content.

    Args:
        tickers: List of stock ticker symbols
        limit: Maximum number of tickers to process (defaults to config)
        fetch_full_content: Whether to fetch full article content

    Returns:
        Dictionary with news data and metadata
    """
    limit = limit or settings.processing.news_limit

    try:
        # Limit tickers
        limited_tickers = tickers[:limit] if len(tickers) > limit else tickers

        crawler = StockNewsCrawler(limited_tickers)
        crawler.get_stock_news()

        # Convert DataFrame to dict for JSON serialization
        news_data = crawler.news_df.to_dict('records')

        # Enhance with full article content if requested
        if fetch_full_content:
            logger.info("Fetching full article content for enhanced analysis")
            max_articles = settings.processing.max_articles_to_enhance
            enhancer = NewsContentEnhancer()
            news_data = enhancer.enhance_news_items(news_data, max_items=max_articles)

        return {
            "success": True,
            "news_count": len(news_data),
            "tickers_analyzed": limited_tickers,
            "news_data": news_data,
            "enhanced_content": fetch_full_content,
            "message": f"Fetched {len(news_data)} news items{'with full content' if fetch_full_content else ''} for {len(limited_tickers)} tickers"
        }
    except Exception as e:
        logger.error(f"Error fetching stock news: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


class NewsContentEnhancer:
    """Helper class to enhance news content with full article text."""

    def __init__(self, rate_limit_delay: float = None):
        """
        Initialize the enhancer.

        Args:
            rate_limit_delay: Delay between requests in seconds.
                            Defaults to config value.
        """
        self.rate_limit_delay = rate_limit_delay or settings.rate_limit.news_rate_limit_delay

    def enhance_news_items(
        self,
        news_data: List[Dict[str, Any]],
        max_items: int = None
    ) -> List[Dict[str, Any]]:
        """
        Enhance news items with full article content.

        Args:
            news_data: List of news items to enhance
            max_items: Maximum items to process (defaults to config)

        Returns:
            Enhanced news items with full content
        """
        max_items = max_items or settings.processing.max_articles_to_enhance
        enhanced_news = []
        total_items = min(len(news_data), max_items)
        logger.info(f"Enhancing {total_items} articles with full content")

        for idx, item in enumerate(news_data[:max_items], 1):
            url = item.get('Link', '')
            ticker = item.get('Ticker', 'UNKNOWN')
            if url and url != 'No link':
                logger.info(f"[{idx}/{total_items}] Fetching {ticker}: {item.get('Title', 'Unknown')[:40]}...")
                full_content = fetch_full_article_content(url)
                item['FullContent'] = full_content
                item['EnhancedText'] = f"{item.get('Summary', '')} {full_content}"

                # Rate limiting is handled in fetch_full_article_content
                # Add small additional delay to be respectful
                time.sleep(self.rate_limit_delay)
            else:
                item['FullContent'] = "No content available"
                item['EnhancedText'] = item.get('Summary', '')

            enhanced_news.append(item)

        return enhanced_news

    def get_content_quality_metrics(self, news_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Get metrics about content quality and depth.

        Args:
            news_data: List of news items to analyze

        Returns:
            Dictionary with content quality metrics
        """
        min_full_content = settings.content.min_full_content_length
        metrics = {
            'full_articles': 0,
            'enhanced_summaries': 0,
            'summary_only': 0,
            'total_items': len(news_data)
        }

        for item in news_data:
            enhanced_text = item.get('EnhancedText', '')
            full_content = item.get('FullContent', '')

            if full_content and len(full_content) > min_full_content and 'Could not fetch' not in full_content:
                metrics['full_articles'] += 1
            elif enhanced_text and len(enhanced_text) > 100:
                metrics['enhanced_summaries'] += 1
            else:
                metrics['summary_only'] += 1

        return metrics


def create_news_crawler_tools():
    """Create ADK tools for news crawling functionality."""
    try:
        from google.adk import Tool

        return [
            Tool(
                name="fetch_stock_news",
                description="Fetch recent news articles for given stock tickers with optional full content",
                function=fetch_stock_news_tool
            )
        ]
    except ImportError:
        # Return mock tools if ADK not available
        return [
            {
                'name': 'fetch_stock_news',
                'description': 'Fetch recent news articles for given stock tickers with optional full content',
                'function': fetch_stock_news_tool
            }
        ]
