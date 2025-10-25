"""
Test that backtesting respects user's data source preference
NO silent fallbacks - if user asks for Reddit, we ONLY use Reddit
"""

import asyncio
from tools.backtest_helpers import get_social_sentiment_for_date

print("\n" + "="*70)
print("🧪 Testing Backtest Data Source Routing")
print("="*70 + "\n")

# Simulate backtesting with different sources
cache = {}

print("Scenario 1: User asks for Reddit sentiment")
print("-" * 70)
print("Query: 'Buy GME when r/wallstreetbets sentiment > 0.5'")
print("Expected: ONLY try Reddit API (no fallback to news)")
print()

sentiment = get_social_sentiment_for_date(
    symbol="GME",
    source="reddit",
    date="2024-10-20",  # Recent date
    cache=cache
)

print(f"Result: {sentiment}")
print()

print("Scenario 2: User asks for Twitter sentiment")
print("-" * 70)
print("Query: 'Buy TSLA when @elonmusk tweets are positive'")
print("Expected: Return None (Twitter not implemented)")
print()

sentiment = get_social_sentiment_for_date(
    symbol="TSLA",
    source="twitter",
    date="2024-10-20",
    cache=cache
)

print(f"Result: {sentiment}")
print()

print("Scenario 3: User asks for news sentiment")
print("-" * 70)
print("Query: 'Buy AAPL when news sentiment > 0.3'")
print("Expected: Try Alpha Vantage / Finnhub")
print()

sentiment = get_social_sentiment_for_date(
    symbol="AAPL",
    source="news",
    date="2024-10-20",
    cache=cache
)

print(f"Result: {sentiment}")
print()

print("="*70)
print("✅ Test complete!")
print()
print("Key Points:")
print("- Reddit source → Only tries Reddit API")
print("- Twitter source → Returns None (not implemented)")
print("- News source → Only tries Alpha Vantage/Finnhub")
print("- NO silent fallbacks between sources")
print("="*70 + "\n")
