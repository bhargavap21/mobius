#!/usr/bin/env python3
"""
Test script for social media tools - Phase 3 completion test
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
from backend.tools.social_media import (
    get_reddit_sentiment,
    get_twitter_sentiment,
    analyze_social_sentiment,
    SOCIAL_MEDIA_TOOLS,
)


def test_social_media_tools():
    """Test the orchestrator with social media tools"""

    print("\n" + "=" * 60)
    print("🧪 Testing Social Media Tools - Phase 3")
    print("=" * 60 + "\n")

    # Get orchestrator instance
    orchestrator = get_orchestrator()

    # Register market data tools
    print("📋 Registering market data tools...")
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

    # Register social media tools
    print("📋 Registering social media tools...")
    for tool_schema in SOCIAL_MEDIA_TOOLS:
        if tool_schema["name"] == "get_reddit_sentiment":
            orchestrator.register_tool(
                name=tool_schema["name"],
                description=tool_schema["description"],
                input_schema=tool_schema["input_schema"],
                function=get_reddit_sentiment,
            )
        elif tool_schema["name"] == "get_twitter_sentiment":
            orchestrator.register_tool(
                name=tool_schema["name"],
                description=tool_schema["description"],
                input_schema=tool_schema["input_schema"],
                function=get_twitter_sentiment,
            )
        elif tool_schema["name"] == "analyze_social_sentiment":
            orchestrator.register_tool(
                name=tool_schema["name"],
                description=tool_schema["description"],
                input_schema=tool_schema["input_schema"],
                function=analyze_social_sentiment,
            )

    total_tools = len(MARKET_DATA_TOOLS) + len(SOCIAL_MEDIA_TOOLS)
    print(f"✅ Registered {total_tools} tools total\n")

    # Test 1: Reddit sentiment
    print("\n" + "=" * 60)
    print("Test 1: Reddit Sentiment Analysis")
    print("=" * 60)

    result = orchestrator.chat(
        "What's the sentiment on r/wallstreetbets for TSLA right now?"
    )

    if result["success"]:
        print("\n✅ Test 1 PASSED")
        print(f"Response: {result['response']}")
    else:
        print(f"\n❌ Test 1 FAILED: {result.get('error')}")

    # Test 2: Twitter sentiment
    print("\n" + "=" * 60)
    print("Test 2: Twitter Sentiment Analysis")
    print("=" * 60)

    result = orchestrator.chat(
        "Has Elon Musk tweeted anything positive about Tesla recently?"
    )

    if result["success"]:
        print("\n✅ Test 2 PASSED")
        print(f"Response: {result['response']}")
    else:
        print(f"\n❌ Test 2 FAILED: {result.get('error')}")

    # Test 3: Trading strategy based on social sentiment
    print("\n" + "=" * 60)
    print("Test 3: Social Sentiment Trading Strategy")
    print("=" * 60)

    result = orchestrator.chat(
        """Should I buy TSLA based on social media sentiment?
        Check both Reddit and Twitter, and consider the current price."""
    )

    if result["success"]:
        print("\n✅ Test 3 PASSED")
        print(f"Response: {result['response']}")
    else:
        print(f"\n❌ Test 3 FAILED: {result.get('error')}")

    # Test 4: Compare social sentiment
    print("\n" + "=" * 60)
    print("Test 4: Compare Multiple Stocks")
    print("=" * 60)

    result = orchestrator.chat(
        "Compare the Reddit sentiment for TSLA vs GME. Which one has more bullish sentiment?"
    )

    if result["success"]:
        print("\n✅ Test 4 PASSED")
        print(f"Response: {result['response']}")
    else:
        print(f"\n❌ Test 4 FAILED: {result.get('error')}")

    # Summary
    print("\n" + "=" * 60)
    print("🎉 Phase 3 Testing Complete!")
    print("=" * 60)
    print("\n✅ Claude can now:")
    print("   - Analyze Reddit sentiment (r/wallstreetbets)")
    print("   - Monitor Twitter/influencer tweets")
    print("   - Combine social + market data")
    print("   - Make trading recommendations based on sentiment")
    print("\n🚀 Ready for Phase 4: Web Scraping!")
    print()


if __name__ == "__main__":
    test_social_media_tools()
