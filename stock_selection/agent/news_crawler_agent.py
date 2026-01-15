"""
News Crawler Agent Module

This module handles all news fetching and content scraping functionality 
for stock news analysis. It provides tools for fetching stock news with 
optional full content extraction from article URLs.
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from typing import List, Dict, Any
import sys
import os

# Import existing functionality
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from stock_news_crawler import StockNewsCrawler


def fetch_full_article_content(url: str) -> str:
    """Scrape full article content from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Try different article content selectors
        article_selectors = [
            'article',
            '.article-body', 
            '.story-content',
            '.article-content',
            '.post-content',
            '.entry-content',
            'main .content',
            '[data-module="ArticleBody"]',
            '.caas-body'
        ]
        
        article_text = ""
        for selector in article_selectors:
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
        return article_text[:3000] if len(article_text) > 3000 else article_text
        
    except Exception as e:
        return f"Could not fetch article content: {str(e)[:100]}"


def fetch_stock_news_tool(tickers: List[str], limit: int = 5, fetch_full_content: bool = True) -> Dict[str, Any]:
    """ADK Tool: Fetch stock news for given tickers with optional full content"""
    try:
        # Limit tickers for demo purposes
        limited_tickers = tickers[:limit] if len(tickers) > limit else tickers
        
        crawler = StockNewsCrawler(limited_tickers)
        crawler.get_stock_news()
        
        # Convert DataFrame to dict for JSON serialization
        news_data = crawler.news_df.to_dict('records')
        
        # Enhance with full article content if requested
        if fetch_full_content:
            print(f"📖 Fetching full article content for enhanced analysis...")
            enhanced_news = []
            
            for item in news_data[:15]:  # Limit to avoid rate limits
                url = item.get('Link', '')
                if url and url != 'No link':
                    print(f"  Reading: {item.get('Title', 'Unknown')[:50]}...")
                    full_content = fetch_full_article_content(url)
                    item['FullContent'] = full_content
                    item['EnhancedText'] = f"{item.get('Summary', '')} {full_content}"
                    
                    # Add small delay to be respectful to servers
                    time.sleep(0.5)
                else:
                    item['FullContent'] = "No content available"
                    item['EnhancedText'] = item.get('Summary', '')
                
                enhanced_news.append(item)
            
            news_data = enhanced_news
        
        return {
            "success": True,
            "news_count": len(news_data),
            "tickers_analyzed": limited_tickers,
            "news_data": news_data,
            "enhanced_content": fetch_full_content,
            "message": f"Fetched {len(news_data)} news items{'with full content' if fetch_full_content else ''} for {len(limited_tickers)} tickers"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


class NewsContentEnhancer:
    """Helper class to enhance news content with full article text"""
    
    def __init__(self, rate_limit_delay: float = 0.5):
        self.rate_limit_delay = rate_limit_delay
    
    def enhance_news_items(self, news_data: List[Dict[str, Any]], max_items: int = 15) -> List[Dict[str, Any]]:
        """Enhance news items with full article content"""
        enhanced_news = []
        
        for item in news_data[:max_items]:
            url = item.get('Link', '')
            if url and url != 'No link':
                print(f"  Reading: {item.get('Title', 'Unknown')[:50]}...")
                full_content = fetch_full_article_content(url)
                item['FullContent'] = full_content
                item['EnhancedText'] = f"{item.get('Summary', '')} {full_content}"
                
                # Add delay to be respectful to servers
                time.sleep(self.rate_limit_delay)
            else:
                item['FullContent'] = "No content available"
                item['EnhancedText'] = item.get('Summary', '')
            
            enhanced_news.append(item)
        
        return enhanced_news
    
    def get_content_quality_metrics(self, news_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get metrics about content quality and depth"""
        metrics = {
            'full_articles': 0,
            'enhanced_summaries': 0,
            'summary_only': 0,
            'total_items': len(news_data)
        }
        
        for item in news_data:
            enhanced_text = item.get('EnhancedText', '')
            full_content = item.get('FullContent', '')
            
            if full_content and len(full_content) > 500 and 'Could not fetch' not in full_content:
                metrics['full_articles'] += 1
            elif enhanced_text and len(enhanced_text) > 100:
                metrics['enhanced_summaries'] += 1
            else:
                metrics['summary_only'] += 1
        
        return metrics


def create_news_crawler_tools():
    """Create ADK tools for news crawling functionality"""
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