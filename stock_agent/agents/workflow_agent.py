"""
Workflow Stock Agent - Google ADK Implementation

This agent runs a fixed sequential workflow:
1. Get S&P 500 recommendations (momentum analysis)
2. Fetch stock news for top performers
3. Analyze sentiment using LLM
4. Generate investment recommendations

This is the original workflow-based agent. For more flexible, query-driven
behavior, see GeneralStockAgent which uses OpenAI function calling.
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
import os
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

from stock_agent.config import settings
from stock_agent.utils import get_logger

# Import modular components
from stock_agent.data.news_crawler import fetch_stock_news_tool
from stock_agent.analysis.sentiment import analyze_sentiment_tool
from stock_agent.analysis.recommender import (
    get_sp500_recommendations_tool,
    generate_recommendations_tool
)

# Report directory for saving results
REPORT_DIR = os.path.join(os.path.dirname(__file__), '..', 'report')


class WorkflowType(Enum):
    """Supported workflow types"""
    FULL_ANALYSIS = "full_analysis"      # Complete pipeline
    NEWS_ONLY = "news_only"              # Just fetch news
    SENTIMENT_ONLY = "sentiment_only"    # Analyze provided tickers
    SINGLE_TICKER = "single_ticker"      # Focus on specific ticker(s)
    HELP = "help"                        # Show help


class StockNewsADKAgent:
    """Google ADK implementation of Stock News Analysis Agent"""

    def __init__(self, risk_tolerance: str = "moderate"):
        self.risk_tolerance = risk_tolerance
        self.logger = get_logger('stock_agent.workflow')
        self.workflow_prompts = self._build_workflow_prompts()
        if not ADK_AVAILABLE:
            self.logger.info("ADK not available - running in simulation mode")
            self.agent = None
        else:
            self.agent = self._create_agent()

    def _build_workflow_prompts(self) -> Dict[str, str]:
        """Prompts that describe each workflow step for logging/UI."""
        return {
            "sp500_load": "Loading SP500 trading data",
            "sp500_momentum": "Analyzing the momentum",
            "news": "Crawling the latest news for top performers",
            "sentiment": "Doing sentiment analysis using LLM",
            "recommendations": "Generating investment recommendations",
        }

    def _create_agent(self):
        """Create the ADK agent with tools and workflow"""
        if not ADK_AVAILABLE:
            return None

        # Collect tools from all modules
        tools = [
            fetch_stock_news_tool,
            analyze_sentiment_tool,
            get_sp500_recommendations_tool,
            generate_recommendations_tool
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

    async def run_analysis(self, user_query: str = None, progress_callback=None) -> Dict[str, Any]:
        """Run the complete stock analysis workflow

        Args:
            user_query: The user's query
            progress_callback: Optional callback function(step, message, log) for progress updates
        """
        self.progress_callback = progress_callback

        if not ADK_AVAILABLE:
            # Simulate the workflow manually using our modular components
            return await self._simulate_workflow()

        # Run with actual ADK agent
        try:
            context = Context(
                query=user_query or "Analyze current stock news and provide investment recommendations",
                parameters={
                    "lookback_days": settings.analysis.lookback_days,
                    "limit": settings.processing.news_limit,
                    "workflow_prompts": self.workflow_prompts
                }
            )

            result = await self.agent.run(context)
            return result

        except Exception as e:
            self.logger.error(f"Error running ADK agent: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def _emit_progress(self, step: str, message: str, log: str = None):
        """Emit progress update to callback if available"""
        if hasattr(self, 'progress_callback') and self.progress_callback:
            try:
                self.progress_callback(step, message, log)
            except Exception as e:
                self.logger.warning(f"Progress callback error: {e}")

    def _save_all_results(
        self,
        sp500_result: Dict[str, Any],
        news_result: Dict[str, Any],
        sentiment_result: Dict[str, Any],
        recommendations_result: Dict[str, Any]
    ):
        """Save all analysis results to CSV files."""
        try:
            os.makedirs(REPORT_DIR, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            # Save SP500 recommended tickers
            if sp500_result.get('success') and sp500_result.get('tickers'):
                sp500_df = pd.DataFrame({
                    'Ticker': sp500_result['tickers'],
                    'Analysis_Date': datetime.now().isoformat()
                })
                sp500_path = os.path.join(REPORT_DIR, f'sp500_recommendations_{timestamp}.csv')
                sp500_df.to_csv(sp500_path, index=False)
                self.logger.info(f"SP500 recommendations saved to {sp500_path}")

            # Save news data
            if news_result.get('success') and news_result.get('news_data'):
                news_df = pd.DataFrame(news_result['news_data'])
                news_path = os.path.join(REPORT_DIR, f'news_data_{timestamp}.csv')
                news_df.to_csv(news_path, index=False)
                self.logger.info(f"News data saved to {news_path}")

            # Save sentiment analysis
            if sentiment_result.get('success') and sentiment_result.get('sentiment_analysis'):
                sentiment_data = []
                for ticker, data in sentiment_result['sentiment_analysis'].items():
                    sentiment_data.append({
                        'Ticker': ticker,
                        'Sentiment_Score': data.get('sentiment_score', 0),
                        'Positive_Count': data.get('positive_count', 0),
                        'Negative_Count': data.get('negative_count', 0),
                        'News_Count': data.get('news_count', 0),
                        'Confidence': data.get('confidence', 'low'),
                        'Content_Depth': data.get('content_depth', 'summary_only'),
                        'Key_Phrases': '; '.join(data.get('key_phrases', [])[:5])
                    })
                sentiment_df = pd.DataFrame(sentiment_data)
                sentiment_path = os.path.join(REPORT_DIR, f'sentiment_analysis_{timestamp}.csv')
                sentiment_df.to_csv(sentiment_path, index=False)
                self.logger.info(f"Sentiment analysis saved to {sentiment_path}")

            # Save final recommendations
            if recommendations_result.get('success') and recommendations_result.get('recommendations'):
                rec_df = pd.DataFrame(recommendations_result['recommendations'])
                rec_path = os.path.join(REPORT_DIR, f'recommendations_{timestamp}.csv')
                rec_df.to_csv(rec_path, index=False)
                self.logger.info(f"Recommendations saved to {rec_path}")

            self.logger.info(f"All results saved to {REPORT_DIR}")

        except Exception as e:
            self.logger.warning(f"Failed to save results to CSV: {e}", exc_info=True)

    async def _simulate_workflow(self) -> Dict[str, Any]:
        """Simulate the ADK workflow using our modular components"""
        self.logger.info("Running in simulation mode (ADK not installed)")
        self._emit_progress("init", "Initializing analysis...", "Starting workflow simulation")

        try:
            # Step 1: Load SP500 trading data
            self._emit_progress("sp500_load", self.workflow_prompts['sp500_load'], self.workflow_prompts['sp500_load'])
            self.logger.info(self.workflow_prompts['sp500_load'])
            sp500_result = get_sp500_recommendations_tool(
                lookback_days=settings.analysis.lookback_days
            )
            if not sp500_result['success']:
                return sp500_result

            # Step 2: Analyze the momentum
            self._emit_progress("sp500_momentum", self.workflow_prompts['sp500_momentum'], self.workflow_prompts['sp500_momentum'])
            self.logger.info(self.workflow_prompts['sp500_momentum'])
            self._emit_progress("sp500_momentum", f"Found {sp500_result['count']} recommended tickers", f"Momentum analysis complete: {sp500_result['count']} tickers")

            # Step 3: Crawl latest news for top performers
            self._emit_progress("news", self.workflow_prompts['news'], self.workflow_prompts['news'])
            self.logger.info(self.workflow_prompts['news'])
            news_result = fetch_stock_news_tool(
                sp500_result['tickers'],
                limit=settings.processing.news_limit
            )
            if not news_result['success']:
                return news_result
            self._emit_progress("news", f"Retrieved {news_result['news_count']} news articles", f"News fetching complete: {news_result['news_count']} articles")

            # Step 4: Sentiment analysis using LLM
            self._emit_progress("sentiment", self.workflow_prompts['sentiment'], self.workflow_prompts['sentiment'])
            self.logger.info(self.workflow_prompts['sentiment'])
            sentiment_result = analyze_sentiment_tool(news_result['news_data'])
            if not sentiment_result['success']:
                return sentiment_result
            self._emit_progress("sentiment", f"Analyzed {len(sentiment_result['analyzed_tickers'])} tickers", f"Sentiment analysis complete: {len(sentiment_result['analyzed_tickers'])} tickers")

            # Step 5: Generate recommendations
            self._emit_progress("recommendations", self.workflow_prompts['recommendations'], self.workflow_prompts['recommendations'])
            self.logger.info(self.workflow_prompts['recommendations'])
            recommendations_result = generate_recommendations_tool(
                sentiment_result['sentiment_analysis']
            )
            if not recommendations_result['success']:
                return recommendations_result
            self._emit_progress("complete", "Analysis complete!", f"Generated {recommendations_result['total_analyzed']} recommendations")

            # Save all results to CSV
            self._save_all_results(
                sp500_result=sp500_result,
                news_result=news_result,
                sentiment_result=sentiment_result,
                recommendations_result=recommendations_result
            )

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
