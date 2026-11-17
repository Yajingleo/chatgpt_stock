"""Assemble all model-callable tools; tool implementations live beside this module."""

from agent.tools.market import create_market_tools
from agent.tools.memory import create_memory_tools
from agent.tools.news import create_news_tools
from agent.tools.recommendations import create_recommendations_tools
from agent.tools.registry import ToolRegistry
from agent.tools.sentiment import create_sentiment_tools


def create_stock_tool_registry(stock_service, memory_service) -> ToolRegistry:
    return ToolRegistry([
        *create_market_tools(stock_service),
        *create_news_tools(stock_service),
        *create_sentiment_tools(stock_service, memory_service),
        *create_recommendations_tools(stock_service, memory_service),
        *create_memory_tools(memory_service),
    ])
