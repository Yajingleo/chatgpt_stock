"""
Agent Orchestration Layer

This module contains agent implementations for stock analysis:
- GeneralStockAgent: Dynamic function calling agent (OpenAI)
- StockNewsADKAgent: Fixed workflow agent (Google ADK)
"""

from stock_agent.agents.general_agent import GeneralStockAgent
from stock_agent.agents.workflow_agent import StockNewsADKAgent, WorkflowType

__all__ = [
    'GeneralStockAgent',     # Recommended: Dynamic query-driven agent
    'StockNewsADKAgent',     # Legacy: Fixed workflow agent
    'WorkflowType'
]
