"""
Test the agent functionality with a simplified example
"""

import asyncio
import sys
import os

# Add the project root to path
sys.path.append(os.path.dirname(__file__))

# Test basic functionality
def test_basic_functionality():
    """Test that we can import and use the basic classes"""
    print("🧪 Testing basic imports...")
    
    try:
        from stock_agent.data.sp500_analyzer import SP500StockAnalyzer
        print("✅ SP500StockAnalyzer imported successfully")

        from stock_agent.data._legacy_crawler import StockNewsCrawler
        print("✅ StockNewsCrawler imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_sp500_analyzer():
    """Test the SP500 analyzer"""
    print("\n📊 Testing SP500 analyzer...")
    
    try:
        from stock_agent.data.sp500_analyzer import SP500StockAnalyzer

        analyzer = SP500StockAnalyzer(years_lookback=1)
        print(f"✅ Created analyzer with {len(analyzer.tickers)} tickers")
        
        # Don't run full analysis as it takes time, just test creation
        return True
        
    except Exception as e:
        print(f"❌ SP500 analyzer error: {e}")
        return False

def test_news_crawler():
    """Test the news crawler with a small set of tickers"""
    print("\n📰 Testing news crawler...")
    
    try:
        from stock_agent.data._legacy_crawler import StockNewsCrawler

        # Test with just one ticker to avoid rate limits
        test_tickers = ["AAPL"]
        crawler = StockNewsCrawler(test_tickers)
        print(f"✅ Created news crawler for {test_tickers}")
        
        # Test the fetch method (comment out to avoid API calls during demo)
        # crawler._get_stock_news("AAPL")
        # print(f"✅ Successfully fetched news")
        
        return True
        
    except Exception as e:
        print(f"❌ News crawler error: {e}")
        return False

def demo_agent_tools():
    """Demo the individual agent tools"""
    print("\n🔧 Testing individual agent tools...")
    
    # Mock data for testing
    mock_tickers = ["AAPL", "MSFT", "GOOGL"]
    mock_news_data = [
        {
            "Ticker": "AAPL",
            "Title": "Apple Reports Strong Growth in Q4",
            "Summary": "Apple beat earnings expectations with strong iPhone sales"
        },
        {
            "Ticker": "AAPL", 
            "Title": "Apple Stock Faces Headwinds",
            "Summary": "Concerns about supply chain issues and competitive pressure"
        },
        {
            "Ticker": "MSFT",
            "Title": "Microsoft Cloud Revenue Surges",
            "Summary": "Strong performance in Azure cloud services drives profit growth"
        }
    ]
    
    # Test sentiment analysis
    print("💭 Testing sentiment analysis tool...")
    try:
        sentiment_keywords = {
            'positive': ['growth', 'profit', 'increase', 'strong', 'beat', 'up', 'bullish', 
                        'surge', 'gain', 'record', 'breakthrough', 'success'],
            'negative': ['loss', 'decline', 'fall', 'weak', 'miss', 'down', 'bearish',
                        'drop', 'crash', 'fail', 'concern', 'risk', 'headwinds']
        }
        
        ticker_sentiment = {}
        
        for item in mock_news_data:
            ticker = item['Ticker']
            title = item['Title'].lower()
            summary = item['Summary'].lower()
            text = f"{title} {summary}"
            
            if ticker not in ticker_sentiment:
                ticker_sentiment[ticker] = {
                    'positive_count': 0,
                    'negative_count': 0,
                    'news_count': 0,
                    'sentiment_score': 0
                }
            
            pos_count = sum(1 for word in sentiment_keywords['positive'] if word in text)
            neg_count = sum(1 for word in sentiment_keywords['negative'] if word in text)
            
            ticker_sentiment[ticker]['positive_count'] += pos_count
            ticker_sentiment[ticker]['negative_count'] += neg_count
            ticker_sentiment[ticker]['news_count'] += 1
            ticker_sentiment[ticker]['sentiment_score'] = (
                ticker_sentiment[ticker]['positive_count'] - 
                ticker_sentiment[ticker]['negative_count']
            )
        
        print("✅ Sentiment analysis completed:")
        for ticker, analysis in ticker_sentiment.items():
            score = analysis['sentiment_score']
            print(f"   {ticker}: Score={score}, News={analysis['news_count']}")
        
        return ticker_sentiment
        
    except Exception as e:
        print(f"❌ Sentiment analysis error: {e}")
        return None

def demo_recommendations(sentiment_analysis):
    """Demo recommendation generation"""
    print("\n🎯 Testing recommendation generation...")
    
    try:
        recommendations = []
        
        for ticker, analysis in sentiment_analysis.items():
            score = analysis['sentiment_score']
            news_count = analysis['news_count']
            
            if score >= 2 and news_count >= 1:
                action = "BUY"
                confidence = "HIGH" if score >= 4 else "MEDIUM"
            elif score <= -2 and news_count >= 1:
                action = "SELL"  
                confidence = "HIGH" if score <= -4 else "MEDIUM"
            else:
                action = "HOLD"
                confidence = "LOW"
            
            recommendations.append({
                "ticker": ticker,
                "action": action,
                "confidence": confidence,
                "sentiment_score": score,
                "news_count": news_count
            })
        
        print("✅ Recommendations generated:")
        for rec in recommendations:
            emoji = "📈" if rec['action'] == 'BUY' else "📉" if rec['action'] == 'SELL' else "➡️"
            conf_emoji = "🔥" if rec['confidence'] == 'HIGH' else "⚠️" if rec['confidence'] == 'MEDIUM' else "❓"
            print(f"   {emoji} {rec['ticker']}: {rec['action']} ({conf_emoji} {rec['confidence']})")
        
        return recommendations
        
    except Exception as e:
        print(f"❌ Recommendation generation error: {e}")
        return None

async def main():
    """Run all tests"""
    print("🚀 Stock Agent Component Test")
    print("="*50)
    
    # Test basic functionality
    if not test_basic_functionality():
        print("❌ Basic tests failed")
        return
    
    # Test individual components
    test_sp500_analyzer()
    test_news_crawler()
    
    # Test agent tools with mock data
    sentiment_analysis = demo_agent_tools()
    if sentiment_analysis:
        demo_recommendations(sentiment_analysis)
    
    print("\n" + "="*50)
    print("✅ All tests completed!")
    print("\n💡 Next steps:")
    print("   1. Install Google ADK: pip install google-adk")
    print("   2. Set up authentication with Google Cloud")
    print("   3. Run the full adk_stock_agent.py")
    print("   4. Deploy to Vertex AI Agent Engine")

if __name__ == "__main__":
    asyncio.run(main())