#!/usr/bin/env python3
"""
ADK Stock Agent Web Chat Server

A modern web interface with natural language chat capabilities for the ADK Stock Agent.
Features:
- Real-time chat interface
- Natural language processing
- Stock analysis integration
- WebSocket support for real-time updates
- Modern responsive UI
- Configurable host/port via environment
"""

import asyncio
import json
import logging
import os
import sys
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import threading
import time
import re

# Add the project paths to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import config
try:
    from stock_agent.config import settings, EXCLUDED_WORDS, MAX_DISPLAY_TICKERS
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    settings = None

# Web server imports
try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import urlparse, parse_qs, unquote
    import socket
    import socketserver
    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False

# Import the stock analysis components
try:
    from stock_agent.agents.main_agent import StockNewsADKAgent
    STOCK_AGENT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Stock agent import error: {e}")
    STOCK_AGENT_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChatMessage:
    """Represents a chat message"""
    def __init__(self, role: str, content: str, timestamp: datetime = None):
        self.role = role  # 'user' or 'assistant'
        self.content = content
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self):
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }

class NaturalLanguageProcessor:
    """Process natural language queries for stock analysis"""
    
    def __init__(self):
        self.patterns = {
            'analyze_stock': r'(?:analyze|analysis|look at|check|research)\s+(?:stock\s+)?([A-Z]{2,5})(?:\s+stock)?',
            'get_news': r'(?:news|recent news|latest news)\s+(?:about|for|on)\s+([A-Z]{2,5}|google|tesla|apple|microsoft|amazon)',
            'sentiment': r'(?:sentiment|feeling|mood)\s+(?:about|for|on)\s+([A-Z]{2,5})',
            'recommendations': r'(?:recommend|recommendation|suggestions?|advice|what should i buy|best stocks)',
            'portfolio': r'(?:portfolio|holdings|my stocks)',
            'market_overview': r'(?:market|overall|general|broad|how is.*market)\s*(?:overview|analysis|condition|doing|performing)',
            'help': r'(?:help|how|what can you do|commands|features|capabilities)',
            'conversational': r'(?:hello|hi|hey|thank|bye|goodbye|how are you)'
        }
    
    def parse_query(self, query: str) -> Dict[str, Any]:
        """Parse natural language query and extract intent and entities"""
        query_lower = query.lower().strip()
        
        result = {
            'intent': 'general_analysis',
            'entities': {},
            'original_query': query,
            'confidence': 0.5
        }
        
        # Check for specific patterns with higher confidence
        for intent, pattern in self.patterns.items():
            match = re.search(pattern, query_lower)
            if match:
                result['intent'] = intent
                result['confidence'] = 0.8
                
                if intent in ['analyze_stock', 'get_news', 'sentiment']:
                    result['entities']['ticker'] = match.group(1).upper()
                break
        
        # Extract multiple tickers if present (only likely stock tickers)
        ticker_matches = re.findall(r'\b([A-Z]{2,5})\b', query.upper())

        # Filter out common false positives and English words
        # Use constants if available, otherwise use fallback set
        if CONFIG_AVAILABLE:
            excluded_upper = {w.upper() for w in EXCLUDED_WORDS}
        else:
            excluded_upper = {
                'GET', 'THE', 'AND', 'FOR', 'ARE', 'CAN', 'YOU', 'HOW', 'WHY', 'WHAT', 'WHO', 'WHEN', 'WHERE',
                'THIS', 'THAT', 'BUT', 'NOT', 'ALL', 'ANY', 'HAS', 'HIS', 'HER', 'HAD', 'HIM', 'HAS', 'HER',
                'WAS', 'WERE', 'BEEN', 'HAVE', 'HELP', 'HELLO', 'THANK', 'THANKS', 'PLEASE', 'WILL', 'WOULD',
                'COULD', 'SHOULD', 'MIGHT', 'MUST', 'MAY', 'GOING', 'COME', 'CAME', 'WANT', 'NEED', 'LIKE',
                'NEWS', 'MARKET', 'PRICE', 'BUY', 'SELL', 'TRADE', 'INVEST', 'IS', 'AS', 'BE', 'TO', 'OF', 'IN'
            }

        # Only include potential tickers that are not common English words
        ticker_matches = [t for t in ticker_matches if t not in excluded_upper and len(t) >= 3]
        
        if ticker_matches:
            result['entities']['tickers'] = list(set(ticker_matches))
        
        # Extract time references
        time_matches = re.search(r'(?:last|past)\s+(\d+)\s+(days?|weeks?|months?)', query_lower)
        if time_matches:
            result['entities']['timeframe'] = {
                'value': int(time_matches.group(1)),
                'unit': time_matches.group(2)
            }
        
        # Adjust intent for conversational queries (lower confidence for general chat)
        conversational_words = ['hello', 'hi', 'hey', 'thanks', 'thank you', 'bye', 'goodbye', 'how are you']
        if any(word in query_lower for word in conversational_words):
            result['intent'] = 'conversational'
            result['confidence'] = 0.9
        
        return result

class StockChatHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the chat interface"""
    
    def __init__(self, *args, stock_agent=None, nlp=None, chat_history=None, **kwargs):
        self.stock_agent = stock_agent
        self.nlp = nlp
        self.chat_history = chat_history or []
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/' or path == '/index.html':
            self._serve_chat_interface()
        elif path == '/api/chat/history':
            self._serve_chat_history()
        elif path.startswith('/static/'):
            self._serve_static_file(path)
        else:
            self._serve_404()
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/chat/message':
            self._handle_chat_message()
        else:
            self._serve_404()
    
    def _serve_chat_interface(self):
        """Serve the main chat interface"""
        html = self._get_chat_html()
        self._send_response(200, html, 'text/html')
    
    def _handle_chat_message(self):
        """Handle incoming chat messages"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            user_message = data.get('message', '').strip()
            if not user_message:
                self._send_json_response({'error': 'Empty message'}, 400)
                return
            
            # Add user message to history
            user_msg = ChatMessage('user', user_message)
            self.chat_history.append(user_msg)
            
            # Process the message
            response = asyncio.run(self._process_user_message(user_message))
            
            # Add assistant response to history
            assistant_msg = ChatMessage('assistant', response)
            self.chat_history.append(assistant_msg)
            
            self._send_json_response({
                'response': response,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error handling chat message: {e}")
            self._send_json_response({'error': 'Internal server error'}, 500)
    
    async def _process_user_message(self, message: str) -> str:
        """Process user message and generate response"""
        try:
            # Parse the natural language query
            parsed = self.nlp.parse_query(message)
            intent = parsed['intent']
            entities = parsed['entities']
            
            logger.info(f"Parsed intent: {intent}, entities: {entities}")
            
            # Generate response based on intent
            if intent == 'help':
                return self._get_help_response()
            elif intent == 'recommendations':
                return await self._get_recommendations()
            elif intent == 'analyze_stock' and 'ticker' in entities:
                return await self._analyze_specific_stock(entities['ticker'])
            elif intent == 'get_news' and 'ticker' in entities:
                return await self._get_stock_news(entities['ticker'])
            elif intent == 'sentiment' and 'ticker' in entities:
                return await self._get_sentiment_analysis(entities['ticker'])
            elif intent == 'market_overview':
                return await self._get_market_overview()
            elif 'tickers' in entities and len(entities['tickers']) > 1:
                return await self._analyze_multiple_stocks(entities['tickers'])
            elif intent == 'portfolio':
                return self._get_portfolio_response()
            elif intent == 'conversational' or intent == 'general_analysis':
                return self._get_general_response(message, intent, entities)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    def _get_help_response(self) -> str:
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
    
    async def _get_recommendations(self) -> str:
        """Get stock recommendations"""
        if not STOCK_AGENT_AVAILABLE:
            return "❌ Stock analysis system is not available."
        
        try:
            results = await self.stock_agent.run_analysis(
                "Provide investment recommendations based on current stock news sentiment"
            )
            
            if not results.get('success'):
                return f"❌ Analysis failed: {results.get('error', 'Unknown error')}"
            
            return self._format_recommendations(results)
            
        except Exception as e:
            return f"❌ Error getting recommendations: {str(e)}"
    
    async def _analyze_specific_stock(self, ticker: str) -> str:
        """Analyze a specific stock"""
        if not STOCK_AGENT_AVAILABLE:
            return f"❌ Stock analysis system is not available. I can provide general information about {ticker}, but cannot run detailed analysis."
        
        try:
            # Create a targeted query for the specific stock
            query = f"Analyze {ticker} stock with recent news and sentiment analysis"
            results = await self.stock_agent.run_analysis(query)
            
            if not results.get('success'):
                return f"❌ Analysis failed for {ticker}: {results.get('error', 'Unknown error')}"
            
            return f"🔍 **Analysis Results for {ticker}**\n\n" + self._format_recommendations(results)
            
        except Exception as e:
            return f"❌ Error analyzing {ticker}: {str(e)}"
    
    async def _get_stock_news(self, ticker: str) -> str:
        """Get news for a specific stock - lightweight version"""
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
    
    async def _get_sentiment_analysis(self, ticker: str) -> str:
        """Get sentiment analysis for a specific stock"""
        return f"""💭 **Sentiment Analysis for {ticker}**

To get detailed sentiment analysis for {ticker}, I'll need to run a comprehensive analysis that includes:

• News sentiment from multiple sources
• Social media sentiment tracking
• Analyst sentiment and ratings
• Market momentum indicators

Say "analyze {ticker} sentiment" or "give me {ticker} recommendations" and I'll run the full analysis!

Quick tip: Sentiment analysis works best when combined with fundamental and technical analysis for complete insights.
        """.strip()

    async def _get_market_overview(self) -> str:
        """Get market overview"""
        if not STOCK_AGENT_AVAILABLE:
            return """📊 **Market Overview**

❌ Stock analysis system is not currently available. 

For current market information, I recommend checking:
• Market indices (S&P 500, NASDAQ, Dow Jones)
• Financial news websites
• Your broker's market dashboard

Say "give me stock recommendations" when you want me to run a full market analysis!
            """.strip()
        
        try:
            results = await self.stock_agent.run_analysis(
                "Provide market overview and investment recommendations based on current conditions"
            )
            
            if not results.get('success'):
                return f"❌ Market analysis failed: {results.get('error', 'Unknown error')}"
            
            return "📊 **Market Overview**\n\n" + self._format_recommendations(results)
            
        except Exception as e:
            return f"❌ Error getting market overview: {str(e)}"

    async def _analyze_multiple_stocks(self, tickers: List[str]) -> str:
        """Analyze multiple stocks"""
        if not STOCK_AGENT_AVAILABLE:
            ticker_list = ", ".join(tickers[:5])
            return f"❌ Stock analysis system is not available. Cannot analyze {ticker_list} at the moment."
        
        try:
            ticker_list = ", ".join(tickers[:5])  # Limit to 5 tickers
            query = f"Compare and analyze these stocks: {ticker_list}"
            results = await self.stock_agent.run_analysis(query)
            
            if not results.get('success'):
                return f"❌ Analysis failed for {ticker_list}: {results.get('error', 'Unknown error')}"
            
            return f"🔍 **Comparative Analysis: {ticker_list}**\n\n" + self._format_recommendations(results)
            
        except Exception as e:
            return f"❌ Error analyzing stocks: {str(e)}"
    
    def _get_portfolio_response(self) -> str:
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
    
    def _get_general_response(self, message: str, intent: str, entities: Dict[str, Any]) -> str:
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
            return self._get_help_response()
        
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
    
    def _format_recommendations(self, results: Dict[str, Any]) -> str:
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
    
    def _serve_chat_history(self):
        """Serve chat history as JSON"""
        history = [msg.to_dict() for msg in self.chat_history[-20:]]  # Last 20 messages
        self._send_json_response({'history': history})
    
    def _serve_static_file(self, path):
        """Serve static files (CSS, JS, etc.)"""
        self._serve_404()  # For now, no static files
    
    def _serve_404(self):
        """Serve 404 error"""
        self._send_response(404, "Not Found", 'text/plain')
    
    def _send_response(self, code, content, content_type='text/html'):
        """Send HTTP response"""
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.send_header('Content-length', len(content.encode('utf-8')))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))
    
    def _send_json_response(self, data, code=200):
        """Send JSON response"""
        content = json.dumps(data, indent=2)
        self._send_response(code, content, 'application/json')
    
    def _get_chat_html(self):
        """Generate the chat interface HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ADK Stock Chat Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .header h1 {
            color: white;
            font-size: 1.5rem;
            font-weight: 600;
        }
        
        .header p {
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9rem;
            margin-top: 0.25rem;
        }
        
        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            max-width: 800px;
            margin: 0 auto;
            padding: 1rem;
            width: 100%;
        }
        
        .chat-messages {
            flex: 1;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 1rem;
            padding: 1rem;
            margin-bottom: 1rem;
            overflow-y: auto;
            max-height: 60vh;
        }
        
        .message {
            margin-bottom: 1rem;
            padding: 0.75rem 1rem;
            border-radius: 0.75rem;
            max-width: 85%;
            word-wrap: break-word;
        }
        
        .message.user {
            background: #007AFF;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        
        .message.assistant {
            background: #f1f3f4;
            color: #333;
            border: 1px solid #e0e0e0;
        }
        
        .message-time {
            font-size: 0.75rem;
            opacity: 0.7;
            margin-top: 0.25rem;
        }
        
        .message-content {
            white-space: pre-wrap;
            line-height: 1.4;
        }
        
        .input-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 1rem;
            padding: 1rem;
            display: flex;
            gap: 0.75rem;
        }
        
        .chat-input {
            flex: 1;
            border: 2px solid #e0e0e0;
            border-radius: 0.75rem;
            padding: 0.75rem 1rem;
            font-size: 1rem;
            outline: none;
            transition: border-color 0.2s;
        }
        
        .chat-input:focus {
            border-color: #007AFF;
        }
        
        .send-button {
            background: #007AFF;
            color: white;
            border: none;
            border-radius: 0.75rem;
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        
        .send-button:hover {
            background: #0056b3;
        }
        
        .send-button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        .typing-indicator {
            display: none;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 1rem;
            color: #666;
            font-style: italic;
        }
        
        .typing-dots {
            display: flex;
            gap: 0.25rem;
        }
        
        .typing-dots span {
            width: 6px;
            height: 6px;
            background: #666;
            border-radius: 50%;
            animation: typing 1.5s infinite;
        }
        
        .typing-dots span:nth-child(2) {
            animation-delay: 0.2s;
        }
        
        .typing-dots span:nth-child(3) {
            animation-delay: 0.4s;
        }
        
        @keyframes typing {
            0%, 60%, 100% { opacity: 0.3; }
            30% { opacity: 1; }
        }
        
        .welcome-message {
            text-align: center;
            color: #666;
            margin: 2rem 0;
            font-style: italic;
        }
        
        @media (max-width: 768px) {
            .header {
                padding: 1rem;
            }
            
            .chat-container {
                padding: 0.5rem;
            }
            
            .message {
                max-width: 95%;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 ADK Stock Chat Assistant</h1>
        <p>Ask me anything about stocks, get recommendations, and analyze market sentiment</p>
    </div>
    
    <div class="chat-container">
        <div class="chat-messages" id="chatMessages">
            <div class="welcome-message">
                👋 Welcome! I'm your AI stock analysis assistant.<br>
                Try asking me: "Give me stock recommendations" or "Analyze AAPL stock"
            </div>
        </div>
        
        <div class="typing-indicator" id="typingIndicator">
            <span>Assistant is typing</span>
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
        
        <div class="input-container">
            <input 
                type="text" 
                id="chatInput" 
                class="chat-input" 
                placeholder="Ask me about stocks, recommendations, market analysis..."
                maxlength="500"
            >
            <button id="sendButton" class="send-button">Send</button>
        </div>
    </div>

    <script>
        const chatMessages = document.getElementById('chatMessages');
        const chatInput = document.getElementById('chatInput');
        const sendButton = document.getElementById('sendButton');
        const typingIndicator = document.getElementById('typingIndicator');
        
        // Load chat history on page load
        loadChatHistory();
        
        // Event listeners
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        sendButton.addEventListener('click', sendMessage);
        
        async function sendMessage() {
            const message = chatInput.value.trim();
            if (!message) return;
            
            // Clear input and disable send button
            chatInput.value = '';
            sendButton.disabled = true;
            
            // Add user message to chat
            addMessage('user', message);
            
            // Show typing indicator
            showTypingIndicator();
            
            try {
                // Send message to server
                const response = await fetch('/api/chat/message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    // Add assistant response
                    addMessage('assistant', data.response);
                } else {
                    addMessage('assistant', 'Sorry, I encountered an error: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                addMessage('assistant', 'Sorry, I couldn\\'t process your request. Please try again.');
                console.error('Error sending message:', error);
            } finally {
                // Hide typing indicator and re-enable send button
                hideTypingIndicator();
                sendButton.disabled = false;
                chatInput.focus();
            }
        }
        
        function addMessage(role, content) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = content;
            
            const timeDiv = document.createElement('div');
            timeDiv.className = 'message-time';
            timeDiv.textContent = new Date().toLocaleTimeString();
            
            messageDiv.appendChild(contentDiv);
            messageDiv.appendChild(timeDiv);
            
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function showTypingIndicator() {
            typingIndicator.style.display = 'flex';
        }
        
        function hideTypingIndicator() {
            typingIndicator.style.display = 'none';
        }
        
        async function loadChatHistory() {
            try {
                const response = await fetch('/api/chat/history');
                const data = await response.json();
                
                if (response.ok && data.history) {
                    // Clear welcome message
                    chatMessages.innerHTML = '';
                    
                    // Add messages from history
                    data.history.forEach(msg => {
                        addMessage(msg.role, msg.content);
                    });
                    
                    // If no history, show welcome message
                    if (data.history.length === 0) {
                        chatMessages.innerHTML = `
                            <div class="welcome-message">
                                👋 Welcome! I'm your AI stock analysis assistant.<br>
                                Try asking me: "Give me stock recommendations" or "Analyze AAPL stock"
                            </div>
                        `;
                    }
                }
            } catch (error) {
                console.error('Error loading chat history:', error);
            }
        }
        
        // Auto-focus on input
        chatInput.focus();
    </script>
</body>
</html>
        """.strip()
    
    def log_message(self, format, *args):
        """Override to reduce logging noise"""
        pass

class ADKWebChatServer:
    """Main web chat server class"""

    def __init__(self, host=None, port=None):
        # Use config defaults if available
        if CONFIG_AVAILABLE and settings:
            host = host or settings.server.host
            port = port or settings.server.port
        else:
            host = host or 'localhost'
            port = port or 8080
        self.host = host
        self.port = port
        self.stock_agent = None
        self.nlp = NaturalLanguageProcessor()
        self.chat_history = []
        
        # Initialize stock agent
        if STOCK_AGENT_AVAILABLE:
            self.stock_agent = StockNewsADKAgent()
            logger.info("✅ Stock agent initialized")
        else:
            logger.warning("⚠️ Stock agent not available")
    
    def create_handler_class(self):
        """Create a handler class with injected dependencies"""
        stock_agent = self.stock_agent
        nlp = self.nlp
        chat_history = self.chat_history
        
        class Handler(StockChatHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, stock_agent=stock_agent, nlp=nlp, chat_history=chat_history, **kwargs)
        
        return Handler
    
    def find_free_port(self):
        """Find a free port to use"""
        for port in range(self.port, self.port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind((self.host, port))
                    return port
            except OSError:
                continue
        raise RuntimeError("No free port found")
    
    def run(self, auto_open=True):
        """Run the web server"""
        if not WEB_AVAILABLE:
            logger.error("❌ Web server components not available")
            return
        
        # Find free port
        try:
            port = self.find_free_port()
            self.port = port
        except RuntimeError:
            logger.error("❌ Could not find a free port")
            return
        
        # Create server
        handler_class = self.create_handler_class()
        server = HTTPServer((self.host, port), handler_class)
        
        # Server info
        url = f"http://{self.host}:{port}"
        logger.info(f"🚀 ADK Stock Chat Server starting at {url}")
        logger.info(f"🤖 Stock Agent Available: {STOCK_AGENT_AVAILABLE}")
        
        # Open browser
        if auto_open:
            threading.Timer(1.0, lambda: webbrowser.open(url)).start()
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logger.info("🛑 Server stopped by user")
        finally:
            server.server_close()

def main():
    """Main entry point"""
    import argparse

    # Get defaults from config if available
    default_host = settings.server.host if CONFIG_AVAILABLE and settings else 'localhost'
    default_port = settings.server.port if CONFIG_AVAILABLE and settings else 8080

    parser = argparse.ArgumentParser(description='ADK Stock Chat Server')
    parser.add_argument('--host', default=default_host, help=f'Host to bind to (default: {default_host})')
    parser.add_argument('--port', type=int, default=default_port, help=f'Port to bind to (default: {default_port})')
    parser.add_argument('--no-browser', action='store_true', help="Don't open browser automatically")
    
    args = parser.parse_args()
    
    print("🚀 ADK Stock Chat Server")
    print("=" * 50)
    print("Features:")
    print("• 💬 Natural language chat interface")
    print("• 📊 Real-time stock analysis")
    print("• 🎯 Investment recommendations")
    print("• 📰 News sentiment analysis")
    print("• 🤖 AI-powered responses")
    print()
    
    server = ADKWebChatServer(host=args.host, port=args.port)
    server.run(auto_open=not args.no_browser)

if __name__ == "__main__":
    main()