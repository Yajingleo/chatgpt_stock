"""
General Stock Agent - OpenAI Function Calling Implementation

This agent uses OpenAI function calling to dynamically decide which tools to call
based on user queries. Unlike the workflow-based agent, it adapts its behavior
to the specific question being asked.

Example queries:
- "What's the sentiment on AAPL?"
- "Give me stock recommendations"
- "Compare AAPL and MSFT"
- "Show me news for Tesla"
"""

import asyncio
import json
import os
from typing import Dict, Any, List, Optional

from stock_agent.config import settings
from stock_agent.utils import get_logger

# Import modular components
from stock_agent.data.news_crawler import fetch_stock_news_tool
from stock_agent.analysis.sentiment import analyze_sentiment_tool
from stock_agent.analysis.recommender import (
    get_sp500_recommendations_tool,
    generate_recommendations_tool
)

# OpenAI for function calling
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None


class GeneralStockAgent:
    """
    General-purpose stock agent that uses OpenAI function calling.

    Unlike StockNewsADKAgent which runs a fixed workflow, this agent dynamically
    decides which tools to call based on the user's query.

    Example queries:
    - "What's the sentiment on AAPL?"
    - "Give me stock recommendations"
    - "Compare AAPL and MSFT"
    - "Show me news for Tesla"
    """

    def __init__(self):
        self.logger = get_logger('stock_agent.general')

        # Store intermediate results to avoid passing large data through GPT
        self._cached_news_data = None
        self._cached_sentiment_data = None

        if not OPENAI_AVAILABLE:
            self.logger.warning("OpenAI not available. GeneralStockAgent requires openai package.")
            self.client = None
            return

        # Initialize OpenAI client
        api_key = settings.openai.api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            self.logger.warning("No OpenAI API key found. Set OPENAI_API_KEY environment variable.")
            self.client = None
            return

        self.client = OpenAI(api_key=api_key)

        # Define available tools for OpenAI function calling
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_sp500_recommendations",
                    "description": "Get top momentum stocks from S&P 500 based on recent trading performance. Use this when user asks for stock recommendations or wants to analyze top performing stocks.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lookback_days": {
                                "type": "integer",
                                "description": "Number of days to analyze for momentum calculation",
                                "default": 30
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "fetch_stock_news",
                    "description": "Fetch recent news articles for specific stock ticker symbols. Use this when user asks about news, recent events, or wants to analyze specific stocks.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "tickers": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of stock ticker symbols (e.g., ['AAPL', 'MSFT', 'GOOGL'])"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of tickers to process",
                                "default": 10
                            }
                        },
                        "required": ["tickers"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_sentiment",
                    "description": "Analyze sentiment of news articles using LLM. Use this after fetching news to understand market sentiment and investor perception. News data from the previous fetch_stock_news call will be used automatically.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_recommendations",
                    "description": "Generate buy/sell/hold recommendations based on sentiment analysis. Use this after analyzing sentiment to provide investment advice. Sentiment data from the previous analyze_sentiment call will be used automatically.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }
        ]

        # Map function names to actual implementations
        self.function_map = {
            "get_sp500_recommendations": self._call_get_sp500_recommendations,
            "fetch_stock_news": self._call_fetch_stock_news,
            "analyze_sentiment": self._call_analyze_sentiment,
            "generate_recommendations": self._call_generate_recommendations
        }

    def _call_get_sp500_recommendations(self, lookback_days: int = None) -> Dict[str, Any]:
        """Wrapper for get_sp500_recommendations_tool"""
        lookback_days = lookback_days or settings.analysis.lookback_days
        self.logger.info(f"Calling get_sp500_recommendations(lookback_days={lookback_days})")
        return get_sp500_recommendations_tool(lookback_days=lookback_days)

    def _call_fetch_stock_news(self, tickers: List[str], limit: int = None) -> Dict[str, Any]:
        """Wrapper for fetch_stock_news_tool"""
        limit = limit or settings.processing.news_limit
        self.logger.info(f"Calling fetch_stock_news(tickers={tickers}, limit={limit})")
        result = fetch_stock_news_tool(tickers=tickers, limit=limit)

        # Cache the full news data for use by subsequent functions
        if result.get('success') and 'news_data' in result:
            self._cached_news_data = result['news_data']
            self.logger.info(f"Cached {len(self._cached_news_data)} news articles")

        return result

    def _call_analyze_sentiment(self, news_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Wrapper for analyze_sentiment_tool"""
        # Use cached news data if available and provided data is missing/truncated
        if news_data is None or (self._cached_news_data and len(self._cached_news_data) > len(news_data)):
            self.logger.info(f"Using cached news data ({len(self._cached_news_data)} articles) instead of provided data")
            news_data = self._cached_news_data

        if not news_data:
            return {"success": False, "error": "No news data available for sentiment analysis"}

        self.logger.info(f"Calling analyze_sentiment({len(news_data)} articles)")
        result = analyze_sentiment_tool(news_data=news_data)

        # Cache sentiment results for recommendations
        if result.get('success') and 'sentiment_analysis' in result:
            self._cached_sentiment_data = result['sentiment_analysis']
            self.logger.info(f"Cached sentiment data for {len(self._cached_sentiment_data)} tickers")

        return result

    def _call_generate_recommendations(self, sentiment_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Wrapper for generate_recommendations_tool"""
        # Use cached sentiment data if available and provided data is missing/incomplete
        if sentiment_analysis is None or (self._cached_sentiment_data and len(self._cached_sentiment_data) > len(sentiment_analysis)):
            self.logger.info(f"Using cached sentiment data ({len(self._cached_sentiment_data)} tickers) instead of provided data")
            sentiment_analysis = self._cached_sentiment_data

        if not sentiment_analysis:
            return {"success": False, "error": "No sentiment data available for generating recommendations"}

        self.logger.info(f"Calling generate_recommendations({len(sentiment_analysis)} tickers)")
        return generate_recommendations_tool(sentiment_analysis=sentiment_analysis)

    def _truncate_result_for_context(self, result: Dict[str, Any], function_name: str) -> Dict[str, Any]:
        """
        Truncate large results to avoid token limit issues.

        This keeps only essential information for GPT to continue the conversation,
        while the full data is still used by subsequent function calls.
        """
        if not result.get('success'):
            # Keep error messages as-is
            return result

        truncated = {"success": result['success']}

        if function_name == "fetch_stock_news":
            # For news data, only keep metadata, not full article content
            if 'news_data' in result:
                news_data = result['news_data']
                # Summarize each article to just ticker, title, and summary
                truncated['news_data'] = [
                    {
                        'ticker': article.get('ticker', ''),
                        'title': article.get('title', '')[:200],  # Limit title length
                        'summary': article.get('summary', '')[:500],  # Limit summary length
                        'url': article.get('url', ''),
                        'published': article.get('published', '')
                        # Exclude: content, content_type (these are large)
                    }
                    for article in news_data[:50]  # Limit to 50 articles max
                ]
                truncated['news_count'] = result.get('news_count', len(news_data))
                truncated['message'] = f"Fetched {truncated['news_count']} articles (showing {len(truncated['news_data'])} summaries)"

        elif function_name == "analyze_sentiment":
            # For sentiment, keep only summary stats per ticker
            if 'sentiment_analysis' in result:
                sentiment = result['sentiment_analysis']
                truncated['sentiment_analysis'] = {
                    ticker: {
                        'sentiment_score': data.get('sentiment_score', 0),
                        'news_count': data.get('news_count', 0),
                        'positive_count': data.get('positive_count', 0),
                        'negative_count': data.get('negative_count', 0),
                        'confidence': data.get('confidence', 'low'),
                        'key_phrases': data.get('key_phrases', [])[:3]  # Only top 3 phrases
                        # Exclude: insights, full key_phrases list
                    }
                    for ticker, data in list(sentiment.items())[:30]  # Limit to 30 tickers
                }
                truncated['analyzed_tickers'] = result.get('analyzed_tickers', [])
                truncated['message'] = f"Analyzed {len(truncated['sentiment_analysis'])} tickers"

        elif function_name == "generate_recommendations":
            # For recommendations, keep only essential info
            if 'recommendations' in result:
                recs = result['recommendations']
                truncated['recommendations'] = [
                    {
                        'ticker': rec['ticker'],
                        'action': rec['action'],
                        'confidence': rec['confidence'],
                        'sentiment_score': rec['sentiment_score'],
                        'reason': rec.get('reason', '')[:300]  # Limit reason length
                    }
                    for rec in recs[:20]  # Limit to 20 recommendations
                ]
                truncated['total_analyzed'] = result.get('total_analyzed', len(recs))
                truncated['message'] = f"Generated {truncated['total_analyzed']} recommendations"

        elif function_name == "get_sp500_recommendations":
            # For SP500, just keep ticker list
            truncated['tickers'] = result.get('tickers', [])[:30]  # Limit to 30 tickers
            truncated['count'] = result.get('count', len(truncated['tickers']))
            truncated['message'] = result.get('message', '')

        else:
            # For unknown functions, keep as-is but truncate if too large
            truncated = result

        return truncated

    async def run_analysis(self, user_query: str, max_iterations: int = 10, progress_callback=None) -> Dict[str, Any]:
        """
        Run the agent with function calling to handle the user query dynamically.

        Args:
            user_query: The user's natural language query
            max_iterations: Maximum number of function call iterations
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary with success status and response
        """
        if not self.client:
            return {
                "success": False,
                "error": "OpenAI client not initialized. Check API key and openai package installation."
            }

        self.logger.info(f"Starting GeneralStockAgent with query: {user_query}")

        # Clear cached data from previous runs
        self._cached_news_data = None
        self._cached_sentiment_data = None

        # Initialize conversation
        messages = [
            {
                "role": "system",
                "content": """You are a stock analysis assistant with access to real-time tools.

Your capabilities:
- Analyze S&P 500 stocks for momentum and performance
- Fetch recent news for specific stocks
- Analyze sentiment of news articles using advanced LLM
- Generate investment recommendations (buy/sell/hold)

RECOMMENDED WORKFLOW for comprehensive analysis:
1. Get top momentum stocks: Call get_sp500_recommendations to identify promising tickers
2. Fetch news: Call fetch_stock_news with the recommended tickers
3. Analyze sentiment: Call analyze_sentiment on the fetched news
4. Generate recommendations: Call generate_recommendations based on sentiment data
5. Provide your final answer with clear reasoning

For specific queries:
- "Show me news for [stock]" → Just fetch_stock_news
- "What's the sentiment on [stock]?" → fetch_stock_news, then analyze_sentiment
- "Give me recommendations" → Run the full 4-step pipeline above for best results

IMPORTANT: When a user asks for news about a company, always attempt to fetch the news using the company's ticker symbol, even if you're unsure whether it's publicly traded. Let the tool handle any errors. If the user provides a company name instead of a ticker, try to infer the ticker symbol (e.g., "Microsoft" → "MSFT", "Apple" → "AAPL", "Tesla" → "TSLA").

Always explain your reasoning and cite the data you used."""
            },
            {
                "role": "user",
                "content": user_query
            }
        ]

        iteration = 0

        try:
            while iteration < max_iterations:
                iteration += 1
                self.logger.info(f"Iteration {iteration}/{max_iterations}")

                # Call OpenAI with function definitions
                try:
                    response = self.client.chat.completions.create(
                        model=settings.openai.model,
                        messages=messages,
                        tools=self.tools,
                        tool_choice="auto",  # Let the model decide
                        temperature=0.7
                    )
                    assistant_message = response.choices[0].message
                except Exception as api_error:
                    error_msg = str(api_error)
                    self.logger.error(f"OpenAI API error: {error_msg}")

                    # Check if it's a token limit error
                    if "context_length_exceeded" in error_msg or "maximum context length" in error_msg:
                        self.logger.warning("Context length exceeded. Attempting to recover with condensed history.")

                        # Try to recover by keeping only the system message and last few messages
                        if len(messages) > 5:
                            # Keep system message + last 3 exchanges
                            condensed_messages = [messages[0]] + messages[-6:]
                            self.logger.info(f"Condensed messages from {len(messages)} to {len(condensed_messages)}")

                            try:
                                response = self.client.chat.completions.create(
                                    model=settings.openai.model,
                                    messages=condensed_messages,
                                    tools=self.tools,
                                    tool_choice="auto",
                                    temperature=0.7
                                )
                                assistant_message = response.choices[0].message
                                messages = condensed_messages  # Use condensed history going forward
                                self.logger.info("✓ Recovery successful with condensed history")
                            except Exception as retry_error:
                                self.logger.error(f"Recovery failed: {retry_error}")
                                # Return partial results if available
                                return {
                                    "success": False,
                                    "error": f"Context limit exceeded and recovery failed: {str(retry_error)}",
                                    "partial_note": "Some functions executed successfully but agent couldn't generate final answer"
                                }
                        else:
                            # Can't condense further
                            return {
                                "success": False,
                                "error": f"OpenAI API error: {error_msg}",
                                "hint": "Try asking a more specific question or reducing the scope"
                            }
                    else:
                        # Other API error, continue to skip and retry
                        self.logger.warning(f"Skipping this iteration due to API error: {error_msg}")
                        continue

                # Add assistant's response to conversation
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": assistant_message.tool_calls
                })

                # Check if the model wants to call functions
                if assistant_message.tool_calls:
                    self.logger.info(f"GPT wants to call {len(assistant_message.tool_calls)} function(s)")

                    # Execute each function call
                    for tool_call in assistant_message.tool_calls:
                        function_name = tool_call.function.name
                        arguments = json.loads(tool_call.function.arguments)

                        self.logger.info(f"🤖 Calling: {function_name}({arguments})")

                        if progress_callback:
                            progress_callback(
                                function_name,
                                f"Executing {function_name}...",
                                f"Agent calling {function_name} with args: {arguments}"
                            )

                        # Execute the function
                        if function_name in self.function_map:
                            try:
                                result = self.function_map[function_name](**arguments)
                                self.logger.info(f"✓ {function_name} completed successfully")
                            except Exception as e:
                                self.logger.error(f"✗ {function_name} failed: {e}", exc_info=True)
                                result = {"success": False, "error": str(e)}
                        else:
                            result = {"success": False, "error": f"Unknown function: {function_name}"}

                        # Truncate result to avoid token limits
                        truncated_result = self._truncate_result_for_context(result, function_name)

                        # Add function result to conversation
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": json.dumps(truncated_result, default=str)
                        })
                else:
                    # Model finished, return final answer
                    self.logger.info("GPT finished - returning final answer")

                    if progress_callback:
                        progress_callback("complete", "Analysis complete", "Agent finished")

                    return {
                        "success": True,
                        "answer": assistant_message.content,
                        "iterations": iteration,
                        "query": user_query
                    }

            # Max iterations reached
            self.logger.warning(f"Max iterations ({max_iterations}) reached")
            return {
                "success": False,
                "error": f"Agent exceeded maximum iterations ({max_iterations})",
                "partial_answer": messages[-1].get("content") if messages else None
            }

        except Exception as e:
            self.logger.error(f"Error in GeneralStockAgent: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
