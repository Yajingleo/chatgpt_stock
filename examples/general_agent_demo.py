#!/usr/bin/env python3
"""
Demo of GeneralStockAgent using OpenAI function calling.

This agent dynamically decides which tools to call based on the user's query,
unlike the traditional workflow-based agent.

Usage:
    python examples/general_agent_demo.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.agents.general_agent import GeneralStockAgent


async def demo():
    """Run demo queries with the general agent"""

    agent = GeneralStockAgent()

    # Example queries that will trigger different tool combinations
    queries = [
        "What's the sentiment on AAPL?",
        "Give me stock recommendations",
        "Compare sentiment between AAPL and MSFT",
        "Show me recent news for Tesla",
    ]

    print("=" * 60)
    print("GeneralStockAgent Demo")
    print("=" * 60)
    print()

    for query in queries:
        print(f"\n{'=' * 60}")
        print(f"Query: {query}")
        print(f"{'=' * 60}\n")

        result = await agent.run_analysis(query)

        if result["success"]:
            print(f"Answer ({result['iterations']} iterations):")
            print(result["answer"])
        else:
            print(f"Error: {result.get('error')}")

        print()


if __name__ == "__main__":
    asyncio.run(demo())
