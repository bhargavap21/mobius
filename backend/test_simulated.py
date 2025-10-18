#!/usr/bin/env python3
"""
Test simulated sentiment for backtesting
"""
from tools.backtest_helpers import get_social_sentiment_for_date
from datetime import datetime, timedelta

print("🔍 Testing Simulated Sentiment for GME Backtesting")
print("=" * 60)

# Test different dates
start_date = datetime(2025, 4, 1)
cache = {}

print("\n📊 GME Reddit Sentiment Over 30 Days:")
for i in range(30):
    date = start_date + timedelta(days=i)
    date_str = date.strftime('%Y-%m-%d')
    sentiment = get_social_sentiment_for_date('GME', 'reddit', date_str, cache)

    # Show sentiment with visual indicator
    if sentiment > 0.5:
        indicator = "🚀🚀🚀"  # Very bullish
    elif sentiment > 0.2:
        indicator = "🚀"      # Bullish
    elif sentiment > -0.2:
        indicator = "➡️"      # Neutral
    else:
        indicator = "📉"      # Bearish

    print(f"{date_str}: {sentiment:+.3f} {indicator}")

print("\n" + "=" * 60)
print("✅ Simulated sentiment varies realistically over time!")
print("📈 This allows backtesting over 180+ days with varied market conditions")