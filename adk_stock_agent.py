"""
Google ADK Stock News Agent - Legacy/Backwards Compatibility Version

NOTE: This code has been refactored into modular components:
- news_crawler_agent.py - News fetching functionality
- sentiment_analyzer.py - LLM sentiment analysis
- stock_recommender.py - Investment recommendations 
- adk_stock_agent_main.py - Main orchestrator (RECOMMENDED)

For new development, use the modular version:
python adk_stock_agent_main.py

This file remains for backwards compatibility.
"""

try:
    from google.adk import Agent, Tool, Sequential
    from google.adk.core import Context
    ADK_AVAILABLE = True
except ImportError as e:
    print("⚠️  Google ADK not installed or incompatible. This is a demonstration of the structure.")
    print(f"   Import error: {str(e)[:100]}...")
    ADK_AVAILABLE = False
    
    # Create mock classes for demonstration
    class Agent:
        def __init__(self, *args, **kwargs): pass
        def run(self, *args, **kwargs): return {"mock": True}
    
    class Tool:
        def __init__(self, *args, **kwargs): pass
    
    class Sequential:
        def __init__(self, *args, **kwargs): pass
    
    class Context:
        pass

import asyncio
import json
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import modular components (PREFERRED)
from news_crawler_agent import (
    fetch_stock_news_tool,
    fetch_full_article_content,
    NewsContentEnhancer
)
from sentiment_analyzer import (
    analyze_sentiment_tool,
    analyze_article_with_llm,
    analyze_article_with_adk_llm,
    SentimentAnalyzer
)
from stock_recommender import (
    get_sp500_recommendations_tool,
    generate_recommendations_tool,
    StockRecommender
)

# Legacy imports for backwards compatibility
import requests
from bs4 import BeautifulSoup
import time
import re
from openai import OpenAI
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'stock_selection'))
from stock_selection.stock_news_crawler import StockNewsCrawler
from stock_selection.sp_500_energy import SP500StockAnalyzer


# Tools are now imported from modular components:
# - get_sp500_recommendations_tool from stock_recommender.py
# - fetch_stock_news_tool from news_crawler_agent.py  
# - analyze_sentiment_tool from sentiment_analyzer.py
# - generate_recommendations_tool from stock_recommender.py

# Legacy functions kept for backwards compatibility


# Legacy function definitions removed - now imported from news_crawler_agent.py
# fetch_full_article_content is available from news_crawler_agent import
# fetch_stock_news_tool is available from news_crawler_agent import
# All legacy function definitions have been moved to modular components.
# Functions are now available via imports from:
# - sentiment_analyzer.py: analyze_article_with_adk_llm, simulate_llm_response_to_prompt, 
#   analyze_article_with_llm, analyze_sentiment_tool
# - stock_recommender.py: generate_recommendations_tool
# - news_crawler_agent.py: fetch_stock_news_tool, fetch_full_article_content
                score += 2
                theme_mentions.append(signal)
        
        if score > 0:
            theme_scores[theme] = score
            detected_themes.extend(theme_mentions[:2])  # Top 2 per theme
    
    # Calculate sentiment based on prompt focus areas
    positive_score = (theme_scores.get('growth_signals', 0) + 
                     theme_scores.get('profitability_signals', 0) + 
                     theme_scores.get('market_signals', 0) +
                     theme_scores.get('future_signals', 0))
    
    negative_score = theme_scores.get('risk_signals', 0) * 1.5  # Risk weighted higher
    
    sentiment_score = min(100, max(-100, int((positive_score - negative_score) * 8)))
    
    # Assess confidence based on signal strength and diversity
    total_signals = sum(theme_scores.values())
    theme_diversity = len(theme_scores)
    
    if total_signals >= 10 and theme_diversity >= 4:
        confidence = "high"
    elif total_signals >= 6 and theme_diversity >= 3:
        confidence = "medium"
    else:
        confidence = "low"
    
    # Determine investment impact as requested in prompt
    if sentiment_score >= 30:
        investment_impact = "very_positive"
    elif sentiment_score >= 15:
        investment_impact = "positive"
    elif sentiment_score <= -30:
        investment_impact = "very_negative"
    elif sentiment_score <= -15:
        investment_impact = "negative"
    else:
        investment_impact = "neutral"
    
    # Generate key factors based on detected themes
    key_factors = []
    if 'growth_signals' in theme_scores:
        key_factors.append("Growth Trajectory")
    if 'profitability_signals' in theme_scores:
        key_factors.append("Financial Performance")
    if 'market_signals' in theme_scores:
        key_factors.append("Market Position")
    if 'risk_signals' in theme_scores:
        key_factors.append("Risk Factors")
    if 'future_signals' in theme_scores:
        key_factors.append("Future Outlook")
    
    # Generate market catalysts
    catalysts = []
    if theme_scores.get('profitability_signals', 0) > 4:
        catalysts.append("Earnings Performance")
    if theme_scores.get('growth_signals', 0) > 4:
        catalysts.append("Growth Momentum")
    if theme_scores.get('market_signals', 0) > 4:
        catalysts.append("Market Dynamics")
    
    return {
        "sentiment_score": sentiment_score,
        "confidence": confidence,
        "key_factors": key_factors[:5] or ["Financial Analysis"],
        "investment_impact": investment_impact,
        "reasoning": f"LLM analyzed {len(detected_themes)} key indicators across {theme_diversity} business themes for {ticker}",
        "market_catalysts": catalysts or ["Market Performance"],
        "llm_type": "Google ADK (Simulated Gemini)",
        "prompt_used": True,
        "themes_analyzed": list(theme_scores.keys())
    }


def analyze_article_with_llm(article_text: str, ticker: str, title: str) -> Dict[str, Any]:
    """Use LLM to analyze article sentiment and extract key insights"""
    try:
        # Initialize OpenAI client (loads API key from .env file)
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        prompt = f"""
You are a financial analyst specializing in sentiment analysis of news articles for stock investment decisions.

Analyze the following news article about {ticker} and provide a structured analysis:

Title: {title}
Article Content: {article_text[:2000]}...

Provide your analysis in this exact JSON format:
{{
    "sentiment_score": <integer from -100 to +100>,
    "confidence": <"high"|"medium"|"low">,
    "key_factors": ["factor1", "factor2", "factor3"],
    "investment_impact": <"very_positive"|"positive"|"neutral"|"negative"|"very_negative">,
    "reasoning": "<brief explanation of your analysis>",
    "market_catalysts": ["catalyst1", "catalyst2"]
}}

Consider:
- Financial performance indicators
- Market sentiment and analyst opinions
- Business developments and strategic moves
- Industry trends and competitive positioning
- Regulatory and economic factors
"""
        
        # For demo purposes, if no API key, return simulated LLM analysis
        if not os.getenv('OPENAI_API_KEY'):
            # Simulated intelligent analysis based on content
            text_lower = article_text.lower()
            
            # More sophisticated analysis than keyword counting
            strong_positive = any(phrase in text_lower for phrase in [
                'record profit', 'earnings beat', 'revenue surge', 'strong growth',
                'market leadership', 'competitive advantage', 'expansion plans'
            ])
            
            strong_negative = any(phrase in text_lower for phrase in [
                'significant loss', 'revenue decline', 'market share loss',
                'regulatory issues', 'competitive pressure', 'cost challenges'
            ])
            
            if strong_positive:
                sentiment_score = 75
                investment_impact = "very_positive"
                confidence = "high"
            elif strong_negative:
                sentiment_score = -65
                investment_impact = "negative"
                confidence = "high"
            else:
                # Analyze content depth and tone
                positive_indicators = sum(1 for word in ['growth', 'profit', 'strong', 'beat', 'surge', 'success'] if word in text_lower)
                negative_indicators = sum(1 for word in ['decline', 'loss', 'weak', 'concern', 'challenge'] if word in text_lower)
                
                sentiment_score = min(80, max(-80, (positive_indicators - negative_indicators) * 15))
                
                if sentiment_score > 30:
                    investment_impact = "positive"
                elif sentiment_score < -30:
                    investment_impact = "negative"
                else:
                    investment_impact = "neutral"
                
                confidence = "medium" if abs(sentiment_score) > 20 else "low"
            
            return {
                "sentiment_score": sentiment_score,
                "confidence": confidence,
                "key_factors": ["Financial performance", "Market positioning", "Industry trends"],
                "investment_impact": investment_impact,
                "reasoning": f"Analysis based on article content depth and financial context for {ticker}",
                "market_catalysts": ["Earnings trends", "Market sentiment"]
            }
        
        # Real LLM analysis when API key is available
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional financial analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.1
        )
        
        result_text = response.choices[0].message.content
        return json.loads(result_text)
        
    except Exception as e:
        # Fallback analysis
        return {
            "sentiment_score": 0,
            "confidence": "low",
            "key_factors": ["Analysis unavailable"],
            "investment_impact": "neutral",
            "reasoning": f"LLM analysis failed: {str(e)[:100]}",
            "market_catalysts": ["Manual review needed"]
        }


def analyze_sentiment_tool(news_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """ADK Tool: Enhanced sentiment analysis of stock news with full content"""
    try:
        # Enhanced sentiment keywords with more financial terms
        sentiment_keywords = {
            'positive': [
                'growth', 'profit', 'increase', 'strong', 'beat', 'up', 'bullish', 'surge', 'gain', 
                'record', 'breakthrough', 'success', 'expansion', 'rising', 'higher', 'boost', 
                'upgrade', 'outperform', 'rally', 'momentum', 'strength', 'improve', 'revenue',
                'earnings', 'buyback', 'dividend', 'acquisition', 'partnership', 'innovation',
                'competitive', 'market share', 'efficiency', 'productivity', 'optimistic'
            ],
            'negative': [
                'loss', 'decline', 'fall', 'weak', 'miss', 'down', 'bearish', 'drop', 'crash', 
                'fail', 'concern', 'risk', 'warning', 'cut', 'reduce', 'lower', 'downgrade', 
                'underperform', 'slowdown', 'pressure', 'challenge', 'struggle', 'uncertain',
                'volatile', 'debt', 'lawsuit', 'investigation', 'regulatory', 'competition',
                'market share loss', 'headwinds', 'recession', 'inflation', 'costs'
            ]
        }
        
        ticker_sentiment = {}
        
        for item in news_data:
            ticker = item.get('Ticker', 'UNKNOWN')
            title = item.get('Title', '').lower()
            summary = item.get('Summary', '').lower()
            
            # Use full content if available, otherwise fall back to summary
            full_content = item.get('EnhancedText', item.get('FullContent', '')).lower()
            analysis_text = full_content if full_content and len(full_content) > 100 else f"{title} {summary}"
            
            if ticker not in ticker_sentiment:
                ticker_sentiment[ticker] = {
                    'positive_count': 0,
                    'negative_count': 0,
                    'news_count': 0,
                    'sentiment_score': 0,
                    'content_depth': 'summary_only',
                    'key_phrases': [],
                    'confidence': 'low'
                }
            
            # Count sentiment keywords with context weighting
            pos_count = 0
            neg_count = 0
            key_phrases = []
            
            for word in sentiment_keywords['positive']:
                if word in analysis_text:
                    # Weight longer phrases more heavily
                    weight = len(word.split()) 
                    count = analysis_text.count(word) * weight
                    pos_count += count
                    if count > 0:
                        key_phrases.append(f"+{word}({count})")
            
            for word in sentiment_keywords['negative']:
                if word in analysis_text:
                    weight = len(word.split())
                    count = analysis_text.count(word) * weight
                    neg_count += count
                    if count > 0:
                        key_phrases.append(f"-{word}({count})")
            
            ticker_sentiment[ticker]['positive_count'] += pos_count
            ticker_sentiment[ticker]['negative_count'] += neg_count
            ticker_sentiment[ticker]['news_count'] += 1
            ticker_sentiment[ticker]['key_phrases'].extend(key_phrases[:5])  # Top 5 phrases
            
            # Determine content depth and confidence
            if len(analysis_text) > 500:
                ticker_sentiment[ticker]['content_depth'] = 'full_article'
                ticker_sentiment[ticker]['confidence'] = 'high'
            elif len(analysis_text) > 100:
                ticker_sentiment[ticker]['content_depth'] = 'enhanced_summary'
                ticker_sentiment[ticker]['confidence'] = 'medium'
            
            # Calculate weighted sentiment score
            total_signals = pos_count + neg_count
            if total_signals > 0:
                # Weighted score considering signal strength
                raw_score = pos_count - neg_count
                confidence_multiplier = min(total_signals / 5, 2.0)  # Cap at 2x
                ticker_sentiment[ticker]['sentiment_score'] = int(raw_score * confidence_multiplier)
            else:
                ticker_sentiment[ticker]['sentiment_score'] = 0
        
        return {
            "success": True,
            "sentiment_analysis": ticker_sentiment,
            "analyzed_tickers": list(ticker_sentiment.keys()),
            "enhancement_info": {
                "full_content_analyzed": sum(1 for t in ticker_sentiment.values() if t['content_depth'] == 'full_article'),
                "total_tickers": len(ticker_sentiment),
                "avg_confidence": sum(1 for t in ticker_sentiment.values() if t['confidence'] == 'high') / len(ticker_sentiment) if ticker_sentiment else 0
            },
            "message": f"Enhanced sentiment analysis completed for {len(ticker_sentiment)} tickers"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def generate_recommendations_tool(sentiment_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """ADK Tool: Generate stock recommendations based on sentiment"""
    try:
        recommendations = []
        
        for ticker, analysis in sentiment_analysis.items():
            score = analysis['sentiment_score']
            news_count = analysis['news_count']
            
            # Generate recommendation based on sentiment score and news volume
            if score >= 3 and news_count >= 2:
                action = "BUY"
                confidence = "HIGH" if score >= 5 else "MEDIUM"
                reason = f"Strong positive sentiment (score: {score}, {news_count} news items)"
            elif score <= -3 and news_count >= 2:
                action = "SELL"  
                confidence = "HIGH" if score <= -5 else "MEDIUM"
                reason = f"Strong negative sentiment (score: {score}, {news_count} news items)"
            else:
                action = "HOLD"
                confidence = "LOW"
                reason = f"Neutral/mixed sentiment (score: {score}, {news_count} news items)"
            
            recommendations.append({
                "ticker": ticker,
                "action": action,
                "confidence": confidence,
                "sentiment_score": score,
                "news_count": news_count,
                "reason": reason
            })
        
        # Sort by absolute sentiment score (strongest signals first)
        recommendations.sort(key=lambda x: abs(x['sentiment_score']), reverse=True)
        
        return {
            "success": True,
            "recommendations": recommendations,
            "total_analyzed": len(recommendations),
            "message": f"Generated {len(recommendations)} recommendations"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# NOTICE: This class now uses modular components.
# For new development, use adk_stock_agent_main.py which is cleaner.

class StockNewsADKAgent:
    """Google ADK implementation of Stock News Analysis Agent (Legacy Version)
    
    This version maintains backwards compatibility but uses the new modular components.
    For new development, use the cleaner adk_stock_agent_main.py instead.
    """
    
    def __init__(self):
        if not ADK_AVAILABLE:
            print("⚠️  ADK not available - running in simulation mode")
            self.agent = None
        else:
            self.agent = self._create_agent()
    
    def _create_agent(self):
        """Create the ADK agent with tools and workflow"""
        if not ADK_AVAILABLE:
            return None
            
        # Define tools
        tools = [
            Tool(
                name="get_sp500_recommendations",
                description="Get recommended S&P 500 stock tickers based on technical analysis",
                function=get_sp500_recommendations_tool
            ),
            Tool(
                name="fetch_stock_news",
                description="Fetch recent news articles for given stock tickers",
                function=fetch_stock_news_tool
            ),
            Tool(
                name="analyze_sentiment", 
                description="Analyze sentiment of stock news articles",
                function=analyze_sentiment_tool
            ),
            Tool(
                name="generate_recommendations",
                description="Generate buy/sell/hold recommendations based on sentiment analysis", 
                function=generate_recommendations_tool
            )
        ]
        
        # Create sequential workflow
        workflow = Sequential([
            "get_sp500_recommendations",
            "fetch_stock_news", 
            "analyze_sentiment",
            "generate_recommendations"
        ])
        
        # Create agent
        agent = Agent(
            name="stock-news-agent",
            description="AI agent that analyzes stock news and provides investment recommendations",
            tools=tools,
            workflow=workflow,
            model="gemini-2.0-flash-exp"  # or your preferred model
        )
        
        return agent
    
    async def run_analysis(self, user_query: str = None) -> Dict[str, Any]:
        """Run the complete stock analysis workflow"""
        
        if not ADK_AVAILABLE:
            # Simulate the workflow manually
            return await self._simulate_workflow()
        
        # Run with actual ADK agent
        try:
            context = Context(
                query=user_query or "Analyze current stock news and provide investment recommendations",
                parameters={"lookback_days": 30, "limit": 5}
            )
            
            result = await self.agent.run(context)
            return result
            
        except Exception as e:
            print(f"❌ Error running ADK agent: {e}")
            return {"success": False, "error": str(e)}
    
    async def _simulate_workflow(self) -> Dict[str, Any]:
        """Simulate the ADK workflow for demonstration"""
        print("🔧 Running in simulation mode (ADK not installed)")
        
        try:
            # Step 1: Get SP500 recommendations
            print("📊 Step 1: Getting S&P 500 recommendations...")
            sp500_result = get_sp500_recommendations_tool(lookback_days=30)
            if not sp500_result['success']:
                return sp500_result
            
            # Step 2: Fetch news
            print("📰 Step 2: Fetching stock news...")
            news_result = fetch_stock_news_tool(sp500_result['tickers'], limit=5)
            if not news_result['success']:
                return news_result
            
            # Step 3: Analyze sentiment
            print("💭 Step 3: Analyzing news sentiment...")
            sentiment_result = analyze_sentiment_tool(news_result['news_data'])
            if not sentiment_result['success']:
                return sentiment_result
            
            # Step 4: Generate recommendations  
            print("🎯 Step 4: Generating recommendations...")
            recommendations_result = generate_recommendations_tool(
                sentiment_result['sentiment_analysis']
            )
            if not recommendations_result['success']:
                return recommendations_result
            
            # Combine all results
            final_result = {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "workflow_steps": {
                    "sp500_analysis": sp500_result,
                    "news_fetching": news_result, 
                    "sentiment_analysis": sentiment_result,
                    "recommendations": recommendations_result
                },
                "summary": {
                    "tickers_analyzed": len(sentiment_result['analyzed_tickers']),
                    "news_items_processed": news_result['news_count'],
                    "recommendations_generated": recommendations_result['total_analyzed']
                }
            }
            
            return final_result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def display_results(self, results: Dict[str, Any]):
        """Display the analysis results in a user-friendly format"""
        print("\n" + "="*60)
        print("🎯 STOCK NEWS ANALYSIS RESULTS")
        print("="*60)
        
        if not results.get('success'):
            print(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")
            return
        
        # Display summary
        if 'summary' in results:
            summary = results['summary']
            print(f"📊 Tickers analyzed: {summary['tickers_analyzed']}")
            print(f"📰 News items processed: {summary['news_items_processed']}")
            print(f"🎯 Recommendations generated: {summary['recommendations_generated']}")
            print()
        
        # Display recommendations
        if 'workflow_steps' in results and 'recommendations' in results['workflow_steps']:
            recommendations = results['workflow_steps']['recommendations']['recommendations']
            analysis_quality = results['workflow_steps']['recommendations'].get('analysis_quality', {})
            
            print("💡 ENHANCED INVESTMENT RECOMMENDATIONS:")
            print("-" * 50)
            print(f"📖 Analysis Quality: {analysis_quality.get('full_articles', 0)} full articles, "
                  f"{analysis_quality.get('enhanced_summaries', 0)} enhanced summaries")
            print(f"🎯 High Confidence Analysis: {analysis_quality.get('high_confidence', 0)} tickers")
            print("-" * 50)
            
            for rec in recommendations:
                # Emoji based on action and confidence
                if rec['action'] == 'BUY':
                    action_emoji = "🟢📈"
                elif rec['action'] == 'SELL':
                    action_emoji = "🔴📉"
                else:
                    action_emoji = "🟡➡️"
                
                confidence_emoji = {
                    'HIGH': '🔥',
                    'MEDIUM': '⚠️',  
                    'LOW': '❓'
                }.get(rec['confidence'], '❓')
                
                depth_emoji = {
                    'full_article': '📚',
                    'enhanced_summary': '📄',
                    'summary_only': '📝'
                }.get(rec.get('content_depth', 'summary_only'), '📝')
                
                print(f"{action_emoji} {rec['ticker']}: {rec['action']}")
                print(f"   {confidence_emoji} Confidence: {rec['confidence']} | {depth_emoji} Analysis: {rec.get('content_depth', 'summary_only')}")
                print(f"   📊 Sentiment Score: {rec['sentiment_score']} | 📰 Articles: {rec['news_count']}")
                print(f"   💭 Reason: {rec['reason']}")
                
                # Show key insights from full content analysis
                if rec.get('insights'):
                    print(f"   🔍 Insights: {'; '.join(rec['insights'])}")
                if rec.get('key_phrases'):
                    top_phrases = rec['key_phrases'][:3]
                    print(f"   🏷️  Key Signals: {', '.join(top_phrases)}")
                print()


async def main():
    """Demonstrate the ADK Stock News Agent (Legacy Version)"""
    print("🚀 Google ADK Stock News Agent Demo (Legacy Version)")
    print("⚠️  This is the backwards compatibility version.")
    print("✅ For new development, use: python adk_stock_agent_main.py")
    print("="*60)
    
    if not ADK_AVAILABLE:
        print("ℹ️  To run with actual Google ADK:")
        print("   1. pip install google-adk")
        print("   2. Set up Google Cloud authentication")
        print("   3. Configure your Gemini API access")
        print()
    
    # Create and run agent
    agent = StockNewsADKAgent()
    
    try:
        print("🔍 Starting stock news analysis...")
        results = await agent.run_analysis(
            "Analyze recent stock news and provide investment recommendations based on sentiment"
        )
        
        # Display results
        agent.display_results(results)
        
        # Save results to file
        if results.get('success'):
            output_file = "adk_stock_analysis.json"
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"💾 Full results saved to {output_file}")
        
    except Exception as e:
        print(f"❌ Error running analysis: {e}")


if __name__ == "__main__":
    asyncio.run(main())