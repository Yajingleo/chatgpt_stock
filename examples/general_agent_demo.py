#!/usr/bin/env python3
"""
Demo of the provider-neutral stock analysis orchestrator.

Usage:
    python examples/general_agent_demo.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent import Orchestrator


async def demo():
    """Run demo queries with the general agent"""

    agent = Orchestrator.from_settings()

    # Example queries that will trigger different tool combinations
    queries = [
        "What's the sentiment on AAPL?",
        "Give me stock recommendations",
        "Compare sentiment between AAPL and MSFT",
        "Show me recent news for Tesla",
    ]

    print("=" * 60)
    print("Stock Orchestrator Demo")
    print("=" * 60)
    print()

    for query in queries:
        print(f"\n{'=' * 60}")
        print(f"Query: {query}")
        print(f"{'=' * 60}\n")

        result = await agent.run(query)

        if result["success"]:
            print(f"Answer ({result['iterations']} iterations):")
            print(result["answer"])
        else:
            print(f"Error: {result.get('error')}")

        print()


if __name__ == "__main__":
    asyncio.run(demo())
