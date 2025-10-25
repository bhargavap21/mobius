#!/usr/bin/env python3
"""
Test company name and alternative terms search
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from tools.backtest_helpers import get_social_sentiment_for_date, get_search_terms

print("🧪 Testing Company Name & Alternative Terms Search")
print("=" * 60)
print()

# Test 1: BYND (Beyond Meat)
ticker = "BYND"
date = "2025-10-22"

print(f"📊 Test 1: {ticker} (Beyond Meat)")
print(f"   Search terms: {get_search_terms(ticker)}")
print()

cache = {}
sentiment = get_social_sentiment_for_date(ticker, 'reddit', date, cache)

if sentiment is not None:
    print(f"   ✅ Found sentiment = {sentiment:.3f}")
else:
    print(f"   ⚠️  No sentiment found")

print()
print("-" * 60)
print()

# Test 2: GME (GameStop)
ticker = "GME"
date = "2025-10-22"

print(f"📊 Test 2: {ticker} (GameStop)")
print(f"   Search terms: {get_search_terms(ticker)}")
print()

sentiment = get_social_sentiment_for_date(ticker, 'reddit', date, cache)

if sentiment is not None:
    print(f"   ✅ Found sentiment = {sentiment:.3f}")
else:
    print(f"   ⚠️  No sentiment found")

print()
print("=" * 60)
print("✅ Company name search should now find more posts!")
print("   - Posts mentioning 'Beyond Meat' without ticker 'BYND'")
print("   - Posts mentioning 'GameStop' without ticker 'GME'")
print("   - Comments discussing company by name")
print("=" * 60)
