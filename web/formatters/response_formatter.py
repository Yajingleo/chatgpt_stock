"""Response formatting utilities for chat interface"""

from typing import Dict, Any


def get_help_response() -> str:
    """Generate help response"""
    return """
🤖 **ADK Stock Assistant Help**

I can help you with various stock analysis tasks:

📊 **Stock Analysis**
- "Analyze AAPL stock"
- "What's the sentiment on TSLA?"
- "Check the latest news for MSFT"

🎯 **Recommendations**
- "Give me stock recommendations"
- "What should I buy?"
- "Any investment advice?"

🔍 **Market Overview**
- "How is the market doing?"
- "Market overview"
- "General market conditions"

💡 **Examples**:
- "Analyze AAPL and TSLA stocks"
- "What's the recent news about Google?"
- "Give me investment recommendations based on current sentiment"
- "How is the tech sector performing?"

Just ask me anything about stocks in natural language! 🚀
    """.strip()


def get_portfolio_response() -> str:
    """Get portfolio-related response"""
    return """💼 **Portfolio Management**

I can help you with portfolio analysis and stock recommendations! Here's what I can do:

📊 **Analysis Services:**
• Get stock recommendations based on current market sentiment
• Analyze specific stocks (e.g., "analyze AAPL")
• Compare multiple stocks
• Market overview and trends

💡 **How to use me:**
• "Give me stock recommendations" - Full market analysis
• "Analyze TSLA stock" - Specific stock analysis
• "Compare AAPL and MSFT" - Multi-stock comparison
• "Market overview" - Current market conditions

🔍 **Example queries:**
• "What are the best stocks to buy now?"
• "Should I buy Tesla stock?"
• "How is the tech sector performing?"

What would you like to analyze today?
    """.strip()


def get_general_response(message: str, intent: str, entities: Dict[str, Any]) -> str:
    """Handle general queries without running stock analysis"""
    message_lower = message.lower()

    # Check for common conversational patterns
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
        return """👋 Hello! I'm your AI stock analysis assistant.

I can help you with:
• Stock recommendations and analysis
• Market sentiment analysis
• Company news and trends
• Investment insights

What would you like to analyze today? Try asking:
• "Give me stock recommendations"
• "Analyze Apple stock"
• "How is the market doing?"
        """.strip()

    elif any(word in message_lower for word in ['thank', 'thanks', 'appreciate']):
        return "You're welcome! Feel free to ask me about any stocks or market analysis you'd like. I'm here to help with your investment research! 📈"

    elif any(word in message_lower for word in ['bye', 'goodbye', 'see you', 'exit']):
        return "Goodbye! Come back anytime for stock analysis and investment insights. Happy investing! 🚀"

    elif 'what can you do' in message_lower or 'your capabilities' in message_lower:
        return get_help_response()

    # Check if this might be a stock-related query that wasn't parsed correctly
    elif any(word in message_lower for word in ['stock', 'invest', 'buy', 'sell', 'market', 'trading', 'portfolio']):
        return f"""🤔 I understand you're asking about: "{message}"

I'm here to help with stock analysis! Here are some ways you can ask me:

📊 **For recommendations:** "Give me stock recommendations"
🔍 **For specific stocks:** "Analyze [TICKER] stock" (e.g., "Analyze AAPL stock")
📰 **For news:** "What's the latest on Tesla?"
📈 **For market overview:** "How is the market doing?"

Would you like me to run a stock analysis for you?
        """.strip()

    else:
        return f"""I'm a stock analysis assistant focused on helping with investment research and market insights.

Your message: "{message}"

I can help you with:
• 📊 Stock recommendations and analysis
• 📰 Company news and sentiment analysis
• 📈 Market trends and insights
• 💡 Investment guidance

Try asking something like:
• "Give me stock recommendations"
• "Analyze Microsoft stock"
• "How is the tech sector doing?"

What would you like to analyze?
        """.strip()


def get_stock_news_message(ticker: str) -> str:
    """Get news message for a specific stock"""
    return f"""📰 **Latest News for {ticker}**

I can help you get the latest news for {ticker}. Would you like me to run a full analysis including:

• Recent news headlines and sentiment
• Market analysis and recommendations
• Technical indicators

Just say "analyze {ticker}" or "give me recommendations" and I'll run the complete analysis for you!

For now, you can also check financial news websites like:
• Yahoo Finance: https://finance.yahoo.com/quote/{ticker}
• MarketWatch: https://www.marketwatch.com/investing/stock/{ticker}
• Seeking Alpha: https://seekingalpha.com/symbol/{ticker}
    """.strip()


def get_sentiment_analysis_message(ticker: str) -> str:
    """Get sentiment analysis message for a specific stock"""
    return f"""💭 **Sentiment Analysis for {ticker}**

To get detailed sentiment analysis for {ticker}, I'll need to run a comprehensive analysis that includes:

• News sentiment from multiple sources
• Social media sentiment tracking
• Analyst sentiment and ratings
• Market momentum indicators

Say "analyze {ticker} sentiment" or "give me {ticker} recommendations" and I'll run the full analysis!

Quick tip: Sentiment analysis works best when combined with fundamental and technical analysis for complete insights.
    """.strip()


def get_market_overview_unavailable() -> str:
    """Get market overview unavailable message"""
    return """📊 **Market Overview**

❌ Stock analysis system is not currently available.

For current market information, I recommend checking:
• Market indices (S&P 500, NASDAQ, Dow Jones)
• Financial news websites
• Your broker's market dashboard

Say "give me stock recommendations" when you want me to run a full market analysis!
    """.strip()


def format_recommendations(results: Dict[str, Any]) -> str:
    """Format analysis results for chat display"""
    if not results.get('success'):
        return f"❌ Analysis failed: {results.get('error', 'Unknown error')}"

    response = "📈 **Stock Analysis Results**\n\n"

    # Add summary
    if 'summary' in results:
        summary = results['summary']
        response += f"📊 **Analysis Summary:**\n"
        response += f"• Tickers analyzed: {summary.get('tickers_analyzed', 0)}\n"
        response += f"• News items processed: {summary.get('news_items_processed', 0)}\n"
        response += f"• Recommendations generated: {summary.get('recommendations_generated', 0)}\n\n"

    # Add recommendations
    if ('workflow_steps' in results and
        'recommendations' in results['workflow_steps'] and
        'recommendations' in results['workflow_steps']['recommendations']):

        recommendations = results['workflow_steps']['recommendations']['recommendations']
        response += "🎯 **Investment Recommendations:**\n\n"

        for rec in recommendations[:5]:  # Show top 5
            action_emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(rec['action'], "⚪")
            confidence_emoji = {"HIGH": "🔥", "MEDIUM": "⚠️", "LOW": "❓"}.get(rec['confidence'], "❓")

            response += f"{action_emoji} **{rec['ticker']}**: {rec['action']}\n"
            response += f"   {confidence_emoji} Confidence: {rec['confidence']}\n"
            response += f"   📊 Sentiment: {rec['sentiment_score']:.2f} | 📰 Articles: {rec['news_count']}\n"
            response += f"   💭 {rec['reason']}\n\n"

    return response
