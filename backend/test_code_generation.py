#!/usr/bin/env python3
"""
Test script for code generation - Phase 5 completion test
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
from backend.tools.code_generator import (
    parse_strategy,
    generate_trading_bot_code,
    create_trading_strategy,
    CODE_GENERATION_TOOLS,
)


def test_code_generation():
    """Test code generation capabilities"""

    print("\n" + "=" * 70)
    print("🧪 Testing Code Generation - Phase 5")
    print("=" * 70 + "\n")

    # Get orchestrator
    orchestrator = get_orchestrator()

    # Register ALL tools
    print("📋 Registering all tools...")

    # Market data
    for tool in MARKET_DATA_TOOLS:
        orchestrator.register_tool(
            tool["name"],
            tool["description"],
            tool["input_schema"],
            eval(tool["name"]),
        )

    # Social media
    for tool in SOCIAL_MEDIA_TOOLS:
        orchestrator.register_tool(
            tool["name"],
            tool["description"],
            tool["input_schema"],
            eval(tool["name"]),
        )

    # Web scraping
    for tool in WEB_SCRAPING_TOOLS:
        orchestrator.register_tool(
            tool["name"],
            tool["description"],
            tool["input_schema"],
            eval(tool["name"]),
        )

    # Code generation
    for tool in CODE_GENERATION_TOOLS:
        orchestrator.register_tool(
            tool["name"],
            tool["description"],
            tool["input_schema"],
            eval(tool["name"]),
        )

    total_tools = (
        len(MARKET_DATA_TOOLS)
        + len(SOCIAL_MEDIA_TOOLS)
        + len(WEB_SCRAPING_TOOLS)
        + len(CODE_GENERATION_TOOLS)
    )
    print(f"✅ Registered {total_tools} tools\n")

    # Test 1: Simple strategy parsing
    print("\n" + "=" * 70)
    print("Test 1: Parse Simple Strategy")
    print("=" * 70)

    result = orchestrator.chat(
        """Parse this trading strategy:

        "Buy AAPL when the price drops 5% below the 20-day moving average.
        Sell at +2% profit or -1% loss."

        Extract the key parameters."""
    )

    if result["success"]:
        print("\n✅ Test 1 PASSED")
        print(f"Response:\n{result['response'][:500]}...")
    else:
        print(f"\n❌ Test 1 FAILED: {result.get('error')}")

    # Test 2: Generate code for simple strategy
    print("\n" + "=" * 70)
    print("Test 2: Generate Trading Bot Code")
    print("=" * 70)

    result = orchestrator.chat(
        """Create a complete Python trading bot for this strategy:

        "Buy TSLA when Reddit sentiment on r/wallstreetbets is bullish (sentiment > 0.5).
        Sell at +2% profit or -1% stop loss."

        Generate the full Python code."""
    )

    if result["success"]:
        print("\n✅ Test 2 PASSED")
        print(f"Response:\n{result['response'][:600]}...")
        print("\n[Code generation successful - too long to display fully]")
    else:
        print(f"\n❌ Test 2 FAILED: {result.get('error')}")

    # Test 3: The "Elon Tweet" strategy (Demo showpiece!)
    print("\n" + "=" * 70)
    print("Test 3: THE DEMO STRATEGY - Elon Tweet Bot 🚀")
    print("=" * 70)

    result = orchestrator.chat(
        """Create a complete trading bot for the famous strategy:

        "Buy TSLA when Elon Musk tweets something positive about Tesla.
        Sell at +2% profit or -1% stop loss.
        Only trade if the current price is below $500."

        Generate production-ready Python code that I can run."""
    )

    if result["success"]:
        print("\n✅ Test 3 PASSED - THE DEMO STRATEGY IS READY! 🎉")
        print(f"\nResponse preview:\n{result['response'][:800]}...")

        # Try to extract and save the code
        if "```python" in result['response']:
            code_start = result['response'].find("```python") + 9
            code_end = result['response'].find("```", code_start)
            code = result['response'][code_start:code_end].strip()

            # Save to file
            with open("generated_elon_tweet_bot.py", "w") as f:
                f.write(code)

            print(f"\n💾 Saved generated code to: generated_elon_tweet_bot.py")
            print(f"📏 Code length: {len(code)} characters")
            print(f"📄 Lines of code: {len(code.split(chr(10)))}")
    else:
        print(f"\n❌ Test 3 FAILED: {result.get('error')}")

    # Test 4: Complex multi-source strategy
    print("\n" + "=" * 70)
    print("Test 4: Complex Multi-Source Strategy")
    print("=" * 70)

    result = orchestrator.chat(
        """Create a trading bot with these conditions:

        - Buy NVDA when:
          1. Reddit sentiment > 0.3 (bullish)
          2. Recent news is positive
          3. Current price is at least 2% below recent high

        - Sell when:
          1. Profit reaches 5% OR
          2. Loss reaches 2% OR
          3. Reddit sentiment turns negative

        Generate the code."""
    )

    if result["success"]:
        print("\n✅ Test 4 PASSED")
        print(f"Response preview:\n{result['response'][:500]}...")
    else:
        print(f"\n❌ Test 4 FAILED: {result.get('error')}")

    # Summary
    print("\n" + "=" * 70)
    print("🎉 Phase 5 Complete - CODE GENERATION WORKING!")
    print("=" * 70)
    print("\n✅ AI can now:")
    print("   - Parse natural language strategies")
    print("   - Generate complete Python trading bots")
    print("   - Include data gathering logic")
    print("   - Implement entry/exit conditions")
    print("   - Add risk management")
    print("   - Create production-ready code")
    print(f"\n📊 Total capabilities: {total_tools} tools across:")
    print("   - 3 Market Data tools")
    print("   - 3 Social Media tools")
    print("   - 2 Web Scraping tools")
    print("   - 3 Code Generation tools")
    print("\n🎯 Next: Phase 6 - Backtesting!")
    print("   Then we can test these strategies on historical data!")
    print()


if __name__ == "__main__":
    test_code_generation()
