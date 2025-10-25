#!/usr/bin/env python3
"""
Test FinBERT sentiment analysis on BYND
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from tools.backtest_helpers import get_social_sentiment_for_date

print("🧪 Testing FinBERT Sentiment Analysis")
print("=" * 60)
print()

ticker = "BYND"
date = "2025-10-22"

print(f"📊 Analyzing {ticker} on {date} with FinBERT")
print()
print("FinBERT advantages over TextBlob:")
print("  ✓ Understands financial context")
print("  ✓ Doesn't rely on simple keywords")
print("  ✓ Can understand 'Not selling' = bullish hold")
print("  ✓ Better at detecting nuanced sentiment")
print()
print("-" * 60)
print()

cache = {}
sentiment = get_social_sentiment_for_date(ticker, 'reddit', date, cache)

print()
print("=" * 60)
if sentiment is not None:
    print(f"✅ FinBERT Sentiment: {sentiment:.3f}")
    print()
    if sentiment > 0.5:
        print("   🚀 BULLISH - Would trigger BUY")
    elif sentiment > 0:
        print("   📈 Slightly positive")
    elif sentiment == 0:
        print("   ➖ NEUTRAL")
    else:
        print("   📉 Slightly negative")
else:
    print(f"⚠️  No sentiment data")
print("=" * 60)
