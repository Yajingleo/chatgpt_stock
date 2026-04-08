"""
Stock Agent - Professional Stock Analysis System

A comprehensive stock analysis system with AI-powered sentiment analysis,
news crawling, fundamental data fetching, and investment recommendations.

Main components:
- agents: Orchestration and workflow management (GeneralStockAgent, StockNewsADKAgent)
- data: Data fetching (news, fundamentals, S&P 500, SEC filings)
- analysis: Sentiment analysis and recommendation engine
- utils: Shared utilities (logging, validation, caching)
- config: Configuration management

Example usage:
    # Dynamic query-driven agent (recommended)
    from agent.agents import GeneralStockAgent

    agent = GeneralStockAgent()
    results = await agent.run_analysis("Give me stock recommendations")

    # Or use the legacy workflow agent
    from agent.agents import StockNewsADKAgent

    agent = StockNewsADKAgent()
    results = await agent.run_analysis()
    agent.display_results(results)
"""

__version__ = '1.0.0'
__author__ = 'Stock Agent Team'

from agent.agents import GeneralStockAgent, StockNewsADKAgent
from agent.utils.logging_config import setup_logger, get_logger

__all__ = ['GeneralStockAgent', 'StockNewsADKAgent', 'setup_logger', 'get_logger']
