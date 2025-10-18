#!/usr/bin/env python3
"""
Test Reddit sentiment detection for GME
"""
import asyncio
from tools.social_media import get_reddit_sentiment

async def test_reddit():
    print("\n🔍 Testing Reddit Sentiment for GME...")
    print("=" * 60)

    # Test with different parameters
    test_cases = [
        {"ticker": "GME", "limit": 50, "hours": 24},
        {"ticker": "GME", "limit": 100, "hours": 48},
        {"ticker": "GME", "limit": 100, "hours": 168},  # 7 days
    ]

    for test in test_cases:
        print(f"\n📊 Testing: {test}")
        result = get_reddit_sentiment(**test)

        if result.get('success'):
            print(f"✅ Success!")
            print(f"   Mentions found: {result['mentions']}")
            print(f"   Average sentiment: {result['avg_sentiment']:.3f}")
            print(f"   Sentiment label: {result['sentiment_label']}")
            print(f"   Top posts:")
            for i, post in enumerate(result.get('top_posts', [])[:3], 1):
                print(f"   {i}. {post['title'][:60]}...")
                print(f"      Score: {post['score']}, Comments: {post['comments']}, Sentiment: {post['sentiment']:.3f}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_reddit())