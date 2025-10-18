#!/usr/bin/env python3
"""
Test StockTwits sentiment provider
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.real_historical_data import StockTwitsProvider
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

def test_stocktwits():
    """Test StockTwits API with various tickers"""
    print("🔍 Testing StockTwits API")
    print("=" * 60)

    provider = StockTwitsProvider()

    # Test popular tickers
    tickers = ['GME', 'AMC', 'AAPL', 'TSLA']

    for ticker in tickers:
        print(f"\n📊 Testing {ticker}:")

        # Test current sentiment
        sentiment = provider.get_sentiment(ticker)
        if sentiment is not None:
            print(f"   ✅ Current sentiment: {sentiment:.3f}")
            if sentiment > 0:
                print(f"   🚀 Bullish sentiment detected!")
            elif sentiment < 0:
                print(f"   🐻 Bearish sentiment detected!")
            else:
                print(f"   😐 Neutral sentiment")
        else:
            print(f"   ⚠️ No sentiment data available")

        # Test with date (recent)
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        print(f"\n   Testing for {yesterday}:")
        dated_sentiment = provider.get_sentiment(ticker, yesterday)
        if dated_sentiment is not None:
            print(f"   ✅ Sentiment on {yesterday}: {dated_sentiment:.3f}")
        else:
            print(f"   ⚠️ No data for {yesterday}")

    print("\n" + "=" * 60)
    print("✅ StockTwits API test complete!")
    print("\nNote: StockTwits free tier has rate limits")
    print("      If you see 429 errors, wait a minute and retry")

if __name__ == "__main__":
    test_stocktwits()