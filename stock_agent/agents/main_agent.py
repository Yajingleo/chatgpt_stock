"""
Google ADK Stock News Agent - Main Orchestrator

This is the main orchestrator that coordinates the modular components:
- News crawler agent for fetching stock news
- Sentiment analyzer for analyzing article sentiment  
- Stock recommender for generating investment recommendations

To run this:
1. pip install google-adk
2. Set up Google Cloud authentication 
3. Run: python adk_stock_agent_main.py
"""

try:
    from google.adk import Agent, Tool, Sequential
    from google.adk.core import Context
    ADK_AVAILABLE = True
except ImportError as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Google ADK not installed or incompatible. Running in simulation mode.")
    logger.debug(f"ADK import error: {str(e)}")
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
from typing import Dict, Any
from datetime import datetime

# Import logging
from stock_agent.utils.logging_config import get_logger

# Import our modular components
from stock_agent.data.news_crawler import (
    fetch_stock_news_tool
)
from stock_agent.analysis.sentiment import (
    analyze_sentiment_tool
)
from stock_agent.analysis.recommender import (
    get_sp500_recommendations_tool,
    generate_recommendations_tool
)


class StockNewsADKAgent:
    """Google ADK implementation of Stock News Analysis Agent"""

    def __init__(self, risk_tolerance: str = "moderate"):
        self.risk_tolerance = risk_tolerance
        self.logger = get_logger('stock_agent.main')
        if not ADK_AVAILABLE:
            self.logger.info("ADK not available - running in simulation mode")
            self.agent = None
        else:
            self.agent = self._create_agent()
    
    def _create_agent(self):
        """Create the ADK agent with tools and workflow"""
        if not ADK_AVAILABLE:
            return None
            
        # Collect tools from all modules
        tools = []
        tools.extend(create_news_crawler_tools())
        tools.extend(create_sentiment_analysis_tools())
        tools.extend(create_recommendation_tools())
        
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
            # Simulate the workflow manually using our modular components
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
            self.logger.error(f"Error running ADK agent: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def _simulate_workflow(self) -> Dict[str, Any]:
        """Simulate the ADK workflow using our modular components"""
        self.logger.info("Running in simulation mode (ADK not installed)")

        try:
            # Step 1: Get SP500 recommendations
            self.logger.info("Step 1: Getting S&P 500 recommendations")
            sp500_result = get_sp500_recommendations_tool(lookback_days=30)
            if not sp500_result['success']:
                return sp500_result

            # Step 2: Fetch news
            self.logger.info("Step 2: Fetching stock news")
            news_result = fetch_stock_news_tool(sp500_result['tickers'], limit=5)
            if not news_result['success']:
                return news_result

            # Step 3: Analyze sentiment
            self.logger.info("Step 3: Analyzing news sentiment")
            sentiment_result = analyze_sentiment_tool(news_result['news_data'])
            if not sentiment_result['success']:
                return sentiment_result

            # Step 4: Generate recommendations
            self.logger.info("Step 4: Generating recommendations")
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
            self.logger.error(f"Error in workflow simulation: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def display_results(self, results: Dict[str, Any]):
        """Display the analysis results in a user-friendly format"""
        self.logger.info("="*60)
        self.logger.info("STOCK NEWS ANALYSIS RESULTS")
        self.logger.info("="*60)

        if not results.get('success'):
            error_msg = results.get('error', 'Unknown error')
            self.logger.error(f"Analysis failed: {error_msg}")
            print(f"❌ Analysis failed: {error_msg}")
            return

        # Display summary
        if 'summary' in results:
            summary = results['summary']
            self.logger.info(f"Tickers analyzed: {summary['tickers_analyzed']}")
            self.logger.info(f"News items processed: {summary['news_items_processed']}")
            self.logger.info(f"Recommendations generated: {summary['recommendations_generated']}")

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

            self.logger.info("Generated recommendations:")
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
                
                recommendation_text = (
                    f"{rec['ticker']}: {rec['action']} (Confidence: {rec['confidence']}, "
                    f"Sentiment: {rec['sentiment_score']}, Articles: {rec['news_count']})"
                )
                self.logger.info(recommendation_text)

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