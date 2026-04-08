"""
Legacy import compatibility module

This module provides backward compatibility for code that imports from main_agent.py.
The agents have been refactored into separate files:
- GeneralStockAgent → general_agent.py
- StockNewsADKAgent → workflow_agent.py

DEPRECATED: Import directly from the new modules instead:
    from agent.agents import GeneralStockAgent
    from agent.agents import StockNewsADKAgent
"""

import warnings

# Show deprecation warning
warnings.warn(
    "Importing from 'agent.agents.main_agent' is deprecated. "
    "Use 'from agent.agents import GeneralStockAgent, StockNewsADKAgent' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export agents from their new locations
from agent.agents.general_agent import GeneralStockAgent
from agent.agents.workflow_agent import StockNewsADKAgent, WorkflowType

__all__ = ['GeneralStockAgent', 'StockNewsADKAgent', 'WorkflowType']
