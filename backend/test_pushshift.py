#!/usr/bin/env python3
"""
Test Pushshift API for real historical Reddit data
"""
from tools.historical_sentiment import PushshiftRedditProvider
from datetime import datetime, timedelta

print("🔍 Testing Pushshift API for Historical Reddit Data")
print("=" * 60)

# Initialize provider
provider = PushshiftRedditProvider()

# Test different dates
test_dates = [
    "2024-10-14",  # 1 year ago
    "2024-06-01",  # Summer 2024
    "2024-01-15",  # Early 2024
    "2023-10-14",  # 2 years ago
]

print("\n📊 Testing GME sentiment on different dates:")
for date in test_dates:
    print(f"\n📅 Date: {date}")
    sentiment = provider.get_historical_sentiment("GME", date)

    if sentiment is not None:
        print(f"   ✅ Sentiment: {sentiment:.3f}")
        if sentiment > 0.5:
            print(f"   🚀 Very Bullish!")
        elif sentiment > 0.1:
            print(f"   📈 Bullish")
        elif sentiment > -0.1:
            print(f"   ➡️ Neutral")
        else:
            print(f"   📉 Bearish")
    else:
        print(f"   ⚠️ No data available")

print("\n" + "=" * 60)
print("Note: Pushshift API may have rate limits or be temporarily unavailable")
print("Consider getting API keys for Alpha Vantage and Finnhub for redundancy")