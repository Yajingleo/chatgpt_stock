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

# Add the project paths to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import config
try:
    from agent.config import settings
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
    from agent import Orchestrator
    STOCK_AGENT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Stock agent import error: {e}")
    STOCK_AGENT_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import modular components
from web.utils import StreamingLogHandler
from web.models import ChatMessage, NaturalLanguageProcessor
from web.templates import get_chat_html
from web.formatters import (
    get_help_response,
    get_portfolio_response,
    get_general_response,
    get_stock_news_message,
    get_sentiment_analysis_message,
    get_market_overview_unavailable,
    format_recommendations
)



class StockChatHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the chat interface"""
    
    def __init__(self, *args, agent=None, nlp=None, chat_history=None, **kwargs):
        self.agent = agent
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
        elif path == '/api/chat/stream':
            self._handle_chat_stream()
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

    def _handle_chat_stream(self):
        """Handle streaming chat messages with Server-Sent Events"""
        streaming_handler = None
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

            # Set up SSE headers
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            # Helper to send SSE log events
            def send_log_event(log_message):
                try:
                    event_data = json.dumps({
                        'type': 'log',
                        'log': log_message,
                        'timestamp': datetime.now().isoformat()
                    })
                    self.wfile.write(f"data: {event_data}\n\n".encode('utf-8'))
                    self.wfile.flush()
                except Exception:
                    pass

            # Attach streaming log handler to capture agent logs only
            streaming_handler = StreamingLogHandler(send_log_event)
            streaming_handler.setLevel(logging.INFO)

            # Only attach to agent logger (not root) to avoid third-party noise
            agent_logger = logging.getLogger('agent')
            agent_logger.addHandler(streaming_handler)

            # Progress callback for status updates
            def progress_callback(step, message, log=None):
                event_data = json.dumps({
                    'type': 'progress',
                    'step': step,
                    'message': message,
                    'log': log or message,
                    'timestamp': datetime.now().isoformat()
                })
                try:
                    self.wfile.write(f"data: {event_data}\n\n".encode('utf-8'))
                    self.wfile.flush()
                except Exception:
                    pass

            # Process the message with progress callback
            response = asyncio.run(self._process_user_message_with_progress(user_message, progress_callback))

            # Add assistant response to history
            assistant_msg = ChatMessage('assistant', response)
            self.chat_history.append(assistant_msg)

            # Send final response
            final_data = json.dumps({
                'type': 'response',
                'response': response,
                'timestamp': datetime.now().isoformat()
            })
            self.wfile.write(f"data: {final_data}\n\n".encode('utf-8'))
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()

        except Exception as e:
            logger.error(f"Error handling stream: {e}")
            try:
                error_data = json.dumps({'type': 'error', 'error': str(e)})
                self.wfile.write(f"data: {error_data}\n\n".encode('utf-8'))
                self.wfile.flush()
            except Exception:
                pass
        finally:
            # Clean up: remove the streaming handler
            if streaming_handler:
                agent_logger = logging.getLogger('agent')
                agent_logger.removeHandler(streaming_handler)

    async def _process_user_message_with_progress(self, message: str, progress_callback) -> str:
        """Process user message with progress updates"""
        try:
            # Route all queries through the provider-neutral orchestrator.
            if not STOCK_AGENT_AVAILABLE:
                return "❌ Stock analysis system is not available."

            logger.info(f"Processing query with Orchestrator: {message}")

            results = await self.agent.run(
                message,
                progress_callback=progress_callback
            )

            if not results.get('success'):
                return f"❌ Analysis failed: {results.get('error', 'Unknown error')}"

            # Return the agent's answer directly
            return results.get('answer', 'No response generated')

        except Exception as e:
            logger.error(f"Error processing message with progress: {e}")
            return f"I encountered an error: {str(e)}"

    async def _get_recommendations_with_progress(self, progress_callback) -> str:
        """Get stock recommendations with progress updates"""
        if not STOCK_AGENT_AVAILABLE:
            return "❌ Stock analysis system is not available."

        try:
            results = await self.agent.run(
                "Provide investment recommendations based on current stock news sentiment",
                progress_callback=progress_callback
            )

            if not results.get('success'):
                return f"❌ Analysis failed: {results.get('error', 'Unknown error')}"

            return self._format_recommendations(results)

        except Exception as e:
            return f"❌ Error getting recommendations: {str(e)}"

    async def _analyze_stock_with_progress(self, ticker: str, progress_callback) -> str:
        """Analyze specific stock with progress updates"""
        if not STOCK_AGENT_AVAILABLE:
            return f"❌ Stock analysis system is not available."

        try:
            progress_callback("init", f"Starting analysis for {ticker}...", f"Analyzing {ticker}")
            query = f"Analyze {ticker} stock with recent news and sentiment analysis"
            results = await self.agent.run(query, progress_callback=progress_callback)

            if not results.get('success'):
                return f"❌ Analysis failed for {ticker}: {results.get('error', 'Unknown error')}"

            return f"🔍 **Analysis Results for {ticker}**\n\n" + self._format_recommendations(results)

        except Exception as e:
            return f"❌ Error analyzing {ticker}: {str(e)}"

    async def _get_market_overview_with_progress(self, progress_callback) -> str:
        """Get market overview with progress updates"""
        if not STOCK_AGENT_AVAILABLE:
            return "❌ Stock analysis system is not available."

        try:
            results = await self.agent.run(
                "Provide market overview and investment recommendations",
                progress_callback=progress_callback
            )

            if not results.get('success'):
                return f"❌ Analysis failed: {results.get('error', 'Unknown error')}"

            return "📊 **Market Overview**\n\n" + self._format_recommendations(results)

        except Exception as e:
            return f"❌ Error: {str(e)}"

    async def _process_user_message(self, message: str) -> str:
        """Process user message and generate response"""
        try:
            # Special case: help requests
            if message.lower().strip() in ['help', '/help', '?']:
                return self._get_help_response()

            # Route all other queries through the provider-neutral orchestrator.
            if not STOCK_AGENT_AVAILABLE:
                return "❌ Stock analysis system is not available."

            logger.info(f"Processing query with Orchestrator: {message}")

            results = await self.agent.run(message)

            if not results.get('success'):
                return f"❌ Analysis failed: {results.get('error', 'Unknown error')}"

            # Return the agent's answer directly
            return results.get('answer', 'No response generated')

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    def _get_help_response(self) -> str:
        """Generate help response - delegates to formatter"""
        return get_help_response()
    
    async def _get_recommendations(self) -> str:
        """Get stock recommendations"""
        if not STOCK_AGENT_AVAILABLE:
            return "❌ Stock analysis system is not available."
        
        try:
            results = await self.agent.run(
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
            results = await self.agent.run(query)
            
            if not results.get('success'):
                return f"❌ Analysis failed for {ticker}: {results.get('error', 'Unknown error')}"
            
            return f"🔍 **Analysis Results for {ticker}**\n\n" + self._format_recommendations(results)
            
        except Exception as e:
            return f"❌ Error analyzing {ticker}: {str(e)}"
    
    async def _get_stock_news(self, ticker: str) -> str:
        """Get news for a specific stock - delegates to formatter"""
        return get_stock_news_message(ticker)
    
    async def _get_sentiment_analysis(self, ticker: str) -> str:
        """Get sentiment analysis for a specific stock - delegates to formatter"""
        return get_sentiment_analysis_message(ticker)

    async def _get_market_overview(self) -> str:
        """Get market overview"""
        if not STOCK_AGENT_AVAILABLE:
            return get_market_overview_unavailable()
        
        try:
            results = await self.agent.run(
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
            results = await self.agent.run(query)
            
            if not results.get('success'):
                return f"❌ Analysis failed for {ticker_list}: {results.get('error', 'Unknown error')}"
            
            return f"🔍 **Comparative Analysis: {ticker_list}**\n\n" + self._format_recommendations(results)
            
        except Exception as e:
            return f"❌ Error analyzing stocks: {str(e)}"
    
    def _get_portfolio_response(self) -> str:
        """Get portfolio-related response - delegates to formatter"""
        return get_portfolio_response()
    
    def _get_general_response(self, message: str, intent: str, entities: Dict[str, Any]) -> str:
        """Handle general queries without running stock analysis - delegates to formatter"""
        return get_general_response(message, intent, entities)
    
    def _format_recommendations(self, results: Dict[str, Any]) -> str:
        """Format analysis results for chat display - delegates to formatter"""
        return format_recommendations(results)
    
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
        """Generate the chat interface HTML - delegates to template"""
        return get_chat_html()
    
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
        self.agent = None
        self.nlp = NaturalLanguageProcessor()
        self.chat_history = []
        
        # Initialize the provider-neutral stock orchestrator.
        if STOCK_AGENT_AVAILABLE:
            self.agent = Orchestrator.from_settings()
            logger.info("✅ Stock orchestrator initialized (tool calling enabled)")
        else:
            logger.warning("⚠️ Stock agent not available")
    
    def create_handler_class(self):
        """Create a handler class with injected dependencies"""
        agent = self.agent
        nlp = self.nlp
        chat_history = self.chat_history
        
        class Handler(StockChatHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, agent=agent, nlp=nlp, chat_history=chat_history, **kwargs)
        
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
