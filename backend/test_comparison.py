#!/usr/bin/env python3
"""
Compare enhanced detection vs old results for BYND
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from tools.backtest_helpers import get_social_sentiment_for_date

print("🧪 BYND Detection Comparison")
print("=" * 60)
print()

ticker = "BYND"
date = "2025-10-22"

print(f"Testing {ticker} on {date}")
print()
print("Previous system:")
print("  - Only searched for 'BYND' or '$BYND'")
print("  - Only checked comments if <10 posts found")
print("  - Result: ~32 posts, sentiment ~0.06")
print()
print("Enhanced system:")
print("  - Searches for 'BYND', '$BYND', 'Beyond Meat'")
print("  - ALWAYS checks comments for ticker mentions")
print("  - Checks for company name alternatives")
print()
print("-" * 60)
print()

cache = {}
sentiment = get_social_sentiment_for_date(ticker, 'reddit', date, cache)

print()
print("=" * 60)
if sentiment is not None:
    print(f"✅ Enhanced Result: sentiment = {sentiment:.3f}")
    print()
    print("Check logs above to see:")
    print("  - How many posts were found")
    print("  - Whether '📝 Found via comments' messages appear")
    print("  - If company name search found additional posts")
else:
    print(f"⚠️  No sentiment data found")
print("=" * 60)
