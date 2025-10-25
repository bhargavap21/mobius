#!/usr/bin/env python3
"""
Test that we don't double-count posts found via multiple methods
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from tools.backtest_helpers import get_social_sentiment_for_date

print("🧪 Testing Post Deduplication")
print("=" * 60)
print()

ticker = "BYND"
date = "2025-10-22"

print(f"📊 Testing with {ticker} on {date}")
print(f"   If deduplication works correctly:")
print(f"   - Each post should only be analyzed once")
print(f"   - Post IDs should be unique in seen_post_ids set")
print(f"   - Log should show '📝 Found via comments' only for NEW posts")
print()

cache = {}
sentiment = get_social_sentiment_for_date(ticker, 'reddit', date, cache)

print()
print("=" * 60)
if sentiment is not None:
    print(f"✅ Sentiment = {sentiment:.3f}")
    print(f"   Check logs above - posts should not be counted twice!")
else:
    print(f"⚠️  No sentiment data")
print("=" * 60)
