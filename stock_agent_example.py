"""
Stock News Analysis Agent Examples

This file demonstrates how to wrap the stock news crawler functionality 
into an AI agent using different frameworks:
1. Simple ReAct-style pattern
2. Google ADK framework example
"""

import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd

# Import existing functionality
from stock_agent.data._legacy_crawler import StockNewsCrawler
from stock_agent.data.sp500_analyzer import SP500StockAnalyzer

class StockNewsReActAgent:
    """
    A ReAct (Reasoning + Acting) style agent for stock news analysis.
    
    This agent follows the Think -> Act -> Observe pattern to analyze stock news
    and make recommendations based on sentiment and market signals.
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client  # Could be OpenAI, Anthropic, etc.
        self.tools = {
            "get_sp500_recommendations": self._get_sp500_recommendations,
            "fetch_stock_news": self._fetch_stock_news,
            "analyze_news_sentiment": self._analyze_news_sentiment,
            "save_analysis_results": self._save_analysis_results
        }
        self.memory = []  # Store conversation history
        self.analysis_results = {}
    
    def _get_sp500_recommendations(self, lookback_days: int = 30) -> List[str]:
        """Tool: Get SP500 recommended tickers"""
        analyzer = SP500StockAnalyzer()
        analyzer.analyze_stocks(lookback_days=lookback_days)
        tickers = analyzer.get_recommanded_tickers()
        return tickers
    
    def _fetch_stock_news(self, tickers: List[str]) -> pd.DataFrame:
        """Tool: Fetch stock news for given tickers"""
        crawler = StockNewsCrawler(tickers)
        crawler.get_stock_news()
        return crawler.news_df
    
    def _analyze_news_sentiment(self, news_df: pd.DataFrame) -> Dict[str, Any]:
        """Tool: Analyze sentiment of news (simplified version)"""
        # In a real implementation, this would use NLP models
        # For demo purposes, we'll use simple keyword analysis
        sentiment_keywords = {
            'positive': ['growth', 'profit', 'increase', 'strong', 'beat', 'up', 'bullish'],
            'negative': ['loss', 'decline', 'fall', 'weak', 'miss', 'down', 'bearish']
        }
        
        analysis = {}
        for ticker in news_df['Ticker'].unique():
            ticker_news = news_df[news_df['Ticker'] == ticker]
            pos_count = 0
            neg_count = 0
            
            for _, row in ticker_news.iterrows():
                text = (row['Title'] + ' ' + row['Summary']).lower()
                pos_count += sum(1 for word in sentiment_keywords['positive'] if word in text)
                neg_count += sum(1 for word in sentiment_keywords['negative'] if word in text)
            
            sentiment_score = pos_count - neg_count
            analysis[ticker] = {
                'sentiment_score': sentiment_score,
                'positive_mentions': pos_count,
                'negative_mentions': neg_count,
                'news_count': len(ticker_news)
            }
        
        return analysis
    
    def _save_analysis_results(self, results: Dict[str, Any], filename: str = "agent_analysis.json"):
        """Tool: Save analysis results to file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        return f"Results saved to {filename}"
    
    def think(self, task: str, context: Dict[str, Any] = None) -> str:
        """Generate reasoning about what to do next"""
        # In a real implementation, this would call an LLM
        # For demo, we'll use rule-based reasoning
        
        if "analyze news" in task.lower():
            return """
            THOUGHT: I need to analyze stock news. My plan:
            1. First get SP500 recommendations to focus on promising stocks
            2. Fetch recent news for those stocks
            3. Analyze sentiment of the news
            4. Provide recommendations based on the analysis
            
            Let me start by getting SP500 recommendations.
            """
        
        return f"THOUGHT: I need to process the task: {task}"
    
    def act(self, action: str, **kwargs) -> Any:
        """Execute an action using available tools"""
        if action in self.tools:
            result = self.tools[action](**kwargs)
            return result
        else:
            return f"ERROR: Tool '{action}' not available. Available tools: {list(self.tools.keys())}"
    
    def observe(self, result: Any) -> str:
        """Process and summarize the result of an action"""
        return f"OBSERVATION: Action completed. Result: {str(result)[:200]}..."
    
    async def run(self, task: str) -> Dict[str, Any]:
        """Main agent loop following ReAct pattern"""
        
        # Think
        thought = self.think(task)
        print(f"🤔 {thought}")
        
        # Act 1: Get SP500 recommendations
        print("🔍 ACTION: Getting SP500 recommendations...")
        sp500_tickers = self.act("get_sp500_recommendations", lookback_days=30)
        observation = self.observe(sp500_tickers)
        print(f"👀 {observation}")
        
        # Act 2: Fetch news
        print("📰 ACTION: Fetching stock news...")
        news_df = self.act("fetch_stock_news", tickers=sp500_tickers[:5])  # Limit to 5 for demo
        observation = self.observe(f"Fetched {len(news_df)} news items")
        print(f"👀 {observation}")
        
        # Act 3: Analyze sentiment
        print("💭 ACTION: Analyzing news sentiment...")
        sentiment_analysis = self.act("analyze_news_sentiment", news_df=news_df)
        observation = self.observe(sentiment_analysis)
        print(f"👀 {observation}")
        
        # Act 4: Save results
        results = {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "sp500_tickers": sp500_tickers,
            "news_summary": {
                "total_news_items": len(news_df),
                "tickers_analyzed": list(news_df['Ticker'].unique())
            },
            "sentiment_analysis": sentiment_analysis,
            "recommendations": self._generate_recommendations(sentiment_analysis)
        }
        
        self.act("save_analysis_results", results=results)
        
        return results
    
    def _generate_recommendations(self, sentiment_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate stock recommendations based on sentiment analysis"""
        recommendations = []
        
        for ticker, analysis in sentiment_analysis.items():
            score = analysis['sentiment_score']
            if score > 2:
                recommendations.append({
                    "ticker": ticker,
                    "action": "BUY",
                    "confidence": "HIGH" if score > 5 else "MEDIUM",
                    "reason": f"Strong positive sentiment (score: {score})"
                })
            elif score < -2:
                recommendations.append({
                    "ticker": ticker,
                    "action": "SELL",
                    "confidence": "HIGH" if score < -5 else "MEDIUM", 
                    "reason": f"Strong negative sentiment (score: {score})"
                })
            else:
                recommendations.append({
                    "ticker": ticker,
                    "action": "HOLD",
                    "confidence": "LOW",
                    "reason": f"Neutral sentiment (score: {score})"
                })
        
        return sorted(recommendations, key=lambda x: abs(sentiment_analysis[x['ticker']]['sentiment_score']), reverse=True)


class GoogleADKStockAgent:
    """
    Example structure for a Google ADK-based stock agent.
    
    Note: This is a conceptual example. To run this, you'd need to:
    1. pip install google-adk
    2. Set up authentication with Google Cloud
    3. Configure the actual ADK components
    """
    
    def __init__(self):
        # In real ADK implementation, you'd have:
        # from google.adk import Agent, Tool, Sequential
        # self.agent = Agent(...)
        pass
    
    def create_adk_agent_config(self):
        """
        Example ADK agent configuration (pseudo-code)
        """
        config = {
            "agent": {
                "name": "stock-news-agent",
                "description": "AI agent for stock news analysis and recommendations",
                "model": {
                    "provider": "gemini",
                    "model": "gemini-2.0-flash-exp"
                }
            },
            "tools": [
                {
                    "name": "get_sp500_recommendations",
                    "description": "Get recommended S&P 500 tickers based on analysis",
                    "function": "stock_agent.data.sp500_analyzer.SP500StockAnalyzer"
                },
                {
                    "name": "fetch_stock_news",
                    "description": "Fetch recent news for given stock tickers",
                    "function": "stock_agent.data._legacy_crawler.StockNewsCrawler"
                },
                {
                    "name": "analyze_sentiment",
                    "description": "Analyze sentiment of stock news",
                    "function": "sentiment_analyzer"
                }
            ],
            "workflow": {
                "type": "sequential",
                "steps": [
                    {"tool": "get_sp500_recommendations", "params": {"lookback_days": 30}},
                    {"tool": "fetch_stock_news", "params": {"tickers": "$previous_result"}},
                    {"tool": "analyze_sentiment", "params": {"news_data": "$previous_result"}},
                    {"action": "generate_recommendations"}
                ]
            }
        }
        return config


# Example usage
async def main():
    """Demonstrate the ReAct agent in action"""
    print("🚀 Starting Stock News Analysis Agent Demo")
    print("=" * 60)
    
    # Create and run ReAct agent
    agent = StockNewsReActAgent()
    
    try:
        results = await agent.run("Analyze recent stock news and provide investment recommendations")
        
        print("\n" + "=" * 60)
        print("📊 FINAL RECOMMENDATIONS:")
        print("=" * 60)
        
        for rec in results['recommendations']:
            confidence_emoji = "🔥" if rec['confidence'] == "HIGH" else "⚠️" if rec['confidence'] == "MEDIUM" else "❓"
            action_emoji = "📈" if rec['action'] == "BUY" else "📉" if rec['action'] == "SELL" else "➡️"
            
            print(f"{confidence_emoji} {action_emoji} {rec['ticker']}: {rec['action']}")
            print(f"   Confidence: {rec['confidence']}")
            print(f"   Reason: {rec['reason']}\n")
            
    except Exception as e:
        print(f"❌ Error running agent: {e}")
    
    print("\n🎯 To implement with Google ADK:")
    print("1. Install: pip install google-adk")
    print("2. Set up Google Cloud authentication")
    print("3. Use the GoogleADKStockAgent configuration above")
    print("4. Deploy to Vertex AI Agent Engine or Cloud Run")


if __name__ == "__main__":
    asyncio.run(main())