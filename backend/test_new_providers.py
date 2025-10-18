#!/usr/bin/env python3
"""
Test Alpha Vantage and Finnhub sentiment providers
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.real_historical_data import AlphaVantageProvider, FinnhubProvider, RealHistoricalDataAggregator
from datetime import datetime, timedelta
import logging
from config import settings

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

def test_providers():
    """Test new sentiment data providers"""
    print("🔍 Testing New Sentiment Data Providers")
    print("=" * 60)

    # Check API keys
    print("\n📋 API Key Status:")
    print(f"  Alpha Vantage: {'✅ Configured' if settings.alpha_vantage_api_key else '❌ Not configured'}")
    print(f"  Finnhub:       {'✅ Configured' if settings.finnhub_api_key else '❌ Not configured'}")

    if not settings.alpha_vantage_api_key and not settings.finnhub_api_key:
        print("\n⚠️  No API keys configured!")
        print("\n📝 To get free API keys:")
        print("  1. Alpha Vantage: https://www.alphavantage.co/support/#api-key")
        print("  2. Finnhub:       https://finnhub.io/register")
        print("\n  Add to your .env file:")
        print("  ALPHA_VANTAGE_API_KEY=your_key_here")
        print("  FINNHUB_API_KEY=your_key_here")
        return

    # Test dates
    test_dates = [
        datetime.now().strftime('%Y-%m-%d'),  # Today
        (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),  # Yesterday
        (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),  # Week ago
        (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),  # Month ago
    ]

    ticker = "GME"

    # Test Alpha Vantage
    if settings.alpha_vantage_api_key:
        print(f"\n📊 Testing Alpha Vantage for {ticker}:")
        print("-" * 40)
        alpha = AlphaVantageProvider()

        for date in test_dates[:2]:  # Only test 2 dates due to rate limit
            print(f"\n  Date: {date}")
            result = alpha.get_sentiment(ticker, date)

            if result:
                sentiment = result.get('sentiment', 0)
                count = result.get('count', 0)
                print(f"    ✅ Sentiment: {sentiment:.3f}")
                print(f"    📰 Articles:  {count}")

                if sentiment > 0:
                    print(f"    🚀 Bullish sentiment!")
                elif sentiment < 0:
                    print(f"    🐻 Bearish sentiment!")
                else:
                    print(f"    😐 Neutral sentiment")
            else:
                print(f"    ⚠️  No data available")

    # Test Finnhub
    if settings.finnhub_api_key:
        print(f"\n📊 Testing Finnhub for {ticker}:")
        print("-" * 40)
        finnhub = FinnhubProvider()

        for date in test_dates:
            print(f"\n  Date: {date}")
            result = finnhub.get_sentiment(ticker, date)

            if result:
                sentiment = result.get('sentiment', 0)
                count = result.get('count', 0)
                print(f"    ✅ Sentiment: {sentiment:.3f}")
                print(f"    📰 Articles:  {count}")

                if sentiment > 0:
                    print(f"    🚀 Bullish sentiment!")
                elif sentiment < 0:
                    print(f"    🐻 Bearish sentiment!")
                else:
                    print(f"    😐 Neutral sentiment")
            else:
                print(f"    ⚠️  No data available")

    # Test aggregator
    print(f"\n📊 Testing Aggregator for {ticker}:")
    print("-" * 40)

    aggregator = RealHistoricalDataAggregator()

    for date in test_dates[:2]:
        print(f"\n  Date: {date}")
        sentiment = aggregator.get_historical_sentiment(ticker, date)

        if sentiment is not None:
            print(f"    ✅ Aggregated sentiment: {sentiment:.3f}")

            if sentiment > 0:
                print(f"    🚀 Bullish signal - BUY conditions met!")
            elif sentiment < 0:
                print(f"    🐻 Bearish signal - Avoid buying")
            else:
                print(f"    😐 Neutral - No clear signal")
        else:
            print(f"    ⚠️  No sentiment data available")

    print("\n" + "=" * 60)
    print("✅ Test complete!")
    print("\nNotes:")
    print("  - Alpha Vantage: 25 requests/day limit")
    print("  - Finnhub: 60 requests/minute limit")
    print("  - Data availability varies by date and ticker")

if __name__ == "__main__":
    test_providers()