"""
Stock Agent - Professional Stock Analysis System

A comprehensive stock analysis system with AI-powered sentiment analysis,
news crawling, fundamental data fetching, and investment recommendations.

Main components:
- agents: Orchestration and workflow management
- data: Data fetching (news, fundamentals, S&P 500, SEC filings)
- analysis: Sentiment analysis and recommendation engine
- utils: Shared utilities (logging, validation, caching)
- config: Configuration management

Example usage:
    from stock_agent.agents.main_agent import StockNewsADKAgent

    agent = StockNewsADKAgent()
    results = await agent.run_analysis()
    agent.display_results(results)
"""

__version__ = '1.0.0'
__author__ = 'Stock Agent Team'

from stock_agent.agents.main_agent import StockNewsADKAgent
from stock_agent.utils.logging_config import setup_logger, get_logger

__all__ = ['StockNewsADKAgent', 'setup_logger', 'get_logger']
