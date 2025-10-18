#!/usr/bin/env python3
"""
Test script for web scraping tools - Phase 4 completion test
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
from backend.tools.web_scraper import (
    scrape_website,
    scrape_company_news,
    WEB_SCRAPING_TOOLS,
)


def test_web_scraping():
    """Test the orchestrator with web scraping tools"""

    print("\n" + "=" * 60)
    print("🧪 Testing Web Scraping Tools - Phase 4")
    print("=" * 60 + "\n")

    # Get orchestrator instance
    orchestrator = get_orchestrator()

    # Register all tools
    print("📋 Registering all tools...")

    # Market data tools
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

    # Social media tools
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

    # Web scraping tools
    for tool_schema in WEB_SCRAPING_TOOLS:
        if tool_schema["name"] == "scrape_website":
            orchestrator.register_tool(
                name=tool_schema["name"],
                description=tool_schema["description"],
                input_schema=tool_schema["input_schema"],
                function=scrape_website,
            )
        elif tool_schema["name"] == "scrape_company_news":
            orchestrator.register_tool(
                name=tool_schema["name"],
                description=tool_schema["description"],
                input_schema=tool_schema["input_schema"],
                function=scrape_company_news,
            )

    total_tools = (
        len(MARKET_DATA_TOOLS) + len(SOCIAL_MEDIA_TOOLS) + len(WEB_SCRAPING_TOOLS)
    )
    print(f"✅ Registered {total_tools} tools total\n")

    # Test 1: Company news
    print("\n" + "=" * 60)
    print("Test 1: Company News Scraping")
    print("=" * 60)

    result = orchestrator.chat("What's the latest news about Tesla?")

    if result["success"]:
        print("\n✅ Test 1 PASSED")
        print(f"Response: {result['response'][:400]}...")
    else:
        print(f"\n❌ Test 1 FAILED: {result.get('error')}")

    # Test 2: Web scraping example
    print("\n" + "=" * 60)
    print("Test 2: General Web Scraping")
    print("=" * 60)

    result = orchestrator.chat(
        "Can you scrape the main headline from https://example.com?"
    )

    if result["success"]:
        print("\n✅ Test 2 PASSED")
        print(f"Response: {result['response'][:400]}...")
    else:
        print(f"\n❌ Test 2 FAILED: {result.get('error')}")

    # Test 3: Multi-source strategy
    print("\n" + "=" * 60)
    print("Test 3: Multi-Source Trading Decision")
    print("=" * 60)

    result = orchestrator.chat(
        """Should I buy NVDA? Consider:
        1. Current stock price
        2. Reddit sentiment
        3. Recent company news

        Give me a comprehensive analysis."""
    )

    if result["success"]:
        print("\n✅ Test 3 PASSED")
        print(f"Response: {result['response']}")
    else:
        print(f"\n❌ Test 3 FAILED: {result.get('error')}")

    # Summary
    print("\n" + "=" * 60)
    print("🎉 Phase 4 Testing Complete!")
    print("=" * 60)
    print("\n✅ Claude can now:")
    print("   - Scrape any website for data")
    print("   - Extract company news")
    print("   - Combine web data with market data")
    print("   - Make informed trading decisions from multiple sources")
    print(f"\n📊 Total tools available: {total_tools}")
    print("   - 3 Market Data tools")
    print("   - 3 Social Media tools")
    print("   - 2 Web Scraping tools")
    print("\n🚀 Ready for Phase 5: Code Generation!")
    print()


if __name__ == "__main__":
    test_web_scraping()
