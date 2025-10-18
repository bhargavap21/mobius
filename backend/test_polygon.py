#!/usr/bin/env python3
"""
Test Polygon.io API with your API key
"""
import os
from dotenv import load_dotenv
from tools.real_historical_data import PolygonSentimentProvider
from datetime import datetime, timedelta

# Load .env file
load_dotenv()

print("🔍 Testing Polygon.io API")
print("=" * 60)

# Check if API key is loaded
api_key = os.getenv("POLYGON_API_KEY")
if api_key:
    print(f"✅ Polygon API key loaded: {api_key[:10]}...")
else:
    print("❌ No Polygon API key found in .env")
    exit()

# Initialize provider
provider = PolygonSentimentProvider(api_key)

# Test with GME for different recent dates
test_dates = [
    (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),  # Yesterday
    (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),  # Last week
    (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),  # Last month
    "2024-01-15",  # Specific historical date
]

print("\n📊 Testing GME sentiment on different dates:")
for date in test_dates:
    print(f"\n📅 Date: {date}")
    result = provider.get_sentiment("GME", date)

    if result:
        sentiment = result.get('sentiment', 0)
        source = result.get('source', 'unknown')
        count = result.get('count', 0)

        print(f"   ✅ Sentiment: {sentiment:.3f}")
        print(f"   📰 Source: {source}")
        print(f"   📊 Articles/Data points: {count}")

        if sentiment > 0.1:
            print(f"   🚀 Bullish sentiment detected!")
        elif sentiment < -0.1:
            print(f"   📉 Bearish sentiment detected!")
        else:
            print(f"   ➡️ Neutral sentiment")
    else:
        print(f"   ⚠️ No data available for this date")

print("\n" + "=" * 60)
print("✅ Polygon API test complete!")
print("Note: Free tier has 5 API calls/minute limit")