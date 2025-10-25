#!/usr/bin/env python3
"""
Test enhanced Reddit sentiment detection with comment checking
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from tools.backtest_helpers import get_social_sentiment_for_date

print("🧪 Testing Enhanced Reddit Sentiment Detection")
print("=" * 60)
print()

# Test with BYND on a recent date (Oct 22, 2025)
ticker = "BYND"
date = "2025-10-22"

print(f"📊 Fetching Reddit sentiment for {ticker} on {date}")
print(f"   This should now:")
print(f"   1. Search for posts with '{ticker}' in title/body")
print(f"   2. Check recent posts for '{ticker}' mentions in comments")
print(f"   3. Include comment sentiment in analysis")
print()

cache = {}
sentiment = get_social_sentiment_for_date(ticker, 'reddit', date, cache)

print()
print("=" * 60)
if sentiment is not None:
    print(f"✅ SUCCESS: Found sentiment = {sentiment:.3f}")
    print(f"   This should be higher than before if we caught more posts!")
else:
    print(f"⚠️  No sentiment data found")
print("=" * 60)
