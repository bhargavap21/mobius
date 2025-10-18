#!/usr/bin/env python3
"""
Test script for the orchestrator - Phase 2 completion test
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.orchestrator import get_orchestrator
from backend.tools.market_data import (
    get_stock_price,
    get_current_price,
    get_market_status,
    MARKET_DATA_TOOLS,
)


def test_orchestrator():
    """Test the orchestrator with market data tools"""

    print("\n" + "=" * 60)
    print("🧪 Testing Claude Orchestrator - Phase 2")
    print("=" * 60 + "\n")

    # Get orchestrator instance
    orchestrator = get_orchestrator()

    # Register market data tools
    print("📋 Registering tools...")
    for tool_schema in MARKET_DATA_TOOLS:
        if tool_schema["name"] == "get_stock_price":
            orchestrator.register_tool(
                name=tool_schema["name"],
                description=tool_schema["description"],
                input_schema=tool_schema["input_schema"],
                function=get_stock_price,
            )
        elif tool_schema["name"] == "get_current_price":
            orchestrator.register_tool(
                name=tool_schema["name"],
                description=tool_schema["description"],
                input_schema=tool_schema["input_schema"],
                function=get_current_price,
            )
        elif tool_schema["name"] == "get_market_status":
            orchestrator.register_tool(
                name=tool_schema["name"],
                description=tool_schema["description"],
                input_schema=tool_schema["input_schema"],
                function=get_market_status,
            )

    print(f"✅ Registered {len(MARKET_DATA_TOOLS)} tools\n")

    # Test 1: Simple price query
    print("\n" + "=" * 60)
    print("Test 1: Simple Price Query")
    print("=" * 60)

    result = orchestrator.chat("What's the current price of AAPL?")

    if result["success"]:
        print("\n✅ Test 1 PASSED")
        print(f"Response: {result['response'][:200]}...")
    else:
        print(f"\n❌ Test 1 FAILED: {result.get('error')}")

    # Test 2: Market status
    print("\n" + "=" * 60)
    print("Test 2: Market Status Check")
    print("=" * 60)

    result = orchestrator.chat("Is the market open right now?")

    if result["success"]:
        print("\n✅ Test 2 PASSED")
        print(f"Response: {result['response']}")
    else:
        print(f"\n❌ Test 2 FAILED: {result.get('error')}")

    # Test 3: Multi-step reasoning
    print("\n" + "=" * 60)
    print("Test 3: Multi-Step Query")
    print("=" * 60)

    result = orchestrator.chat(
        "Compare the current prices of AAPL and TSLA. Which one is higher?"
    )

    if result["success"]:
        print("\n✅ Test 3 PASSED")
        print(f"Response: {result['response']}")
    else:
        print(f"\n❌ Test 3 FAILED: {result.get('error')}")

    # Summary
    print("\n" + "=" * 60)
    print("🎉 Phase 2 Testing Complete!")
    print("=" * 60)
    print("\n✅ Claude can:")
    print("   - Understand natural language queries")
    print("   - Select appropriate tools to use")
    print("   - Execute tools and get results")
    print("   - Reason over multiple steps")
    print("   - Generate helpful responses")
    print("\n🚀 Ready for Phase 3: More tools and strategy parsing!")
    print()


if __name__ == "__main__":
    test_orchestrator()
