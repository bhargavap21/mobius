"""
Test Reddit API Handler
"""

import asyncio
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

from tools.api_handlers.reddit_handler import RedditHandler


async def test_reddit_handler():
    """Test Reddit handler functionality"""

    print("\n" + "="*60)
    print("🧪 Testing Reddit API Handler")
    print("="*60 + "\n")

    handler = RedditHandler()

    if not handler.initialized:
        print("❌ Reddit API not initialized")
        print("\nTo use Reddit API:")
        print("1. Go to https://www.reddit.com/prefs/apps")
        print("2. Create an app (script type)")
        print("3. Add to backend/.env:")
        print("   REDDIT_CLIENT_ID=your_client_id")
        print("   REDDIT_CLIENT_SECRET=your_client_secret")
        return

    print("✅ Reddit API initialized\n")

    # Test 1: Fetch subreddit sentiment
    print("-" * 60)
    print("Test 1: Fetch r/wallstreetbets sentiment for GME")
    print("-" * 60)

    result = await handler.fetch_subreddit_sentiment(
        subreddit="wallstreetbets",
        keywords=["GME", "GameStop"],
        limit=50,
        time_filter="week"
    )

    if result["success"]:
        print(f"✅ Success!")
        print(f"   Posts analyzed: {result['post_count']}")
        print(f"   Average sentiment: {result['sentiment']:.2f}")
        print(f"   Average score: {result['avg_score']:.1f}")
        print(f"\n   Top 3 posts:")
        for i, post in enumerate(result["top_posts"][:3], 1):
            print(f"   {i}. [{post['score']}⬆] {post['title'][:60]}...")
            print(f"      Sentiment: {post['sentiment']:.2f}")
    else:
        print(f"❌ Failed: {result.get('error')}")

    # Test 2: Trending tickers
    print("\n" + "-" * 60)
    print("Test 2: Find trending tickers in r/wallstreetbets")
    print("-" * 60)

    result = handler.get_trending_tickers(
        subreddit="wallstreetbets",
        limit=100
    )

    if result["success"]:
        print(f"✅ Success!")
        print(f"   Tickers found: {len(result['tickers'])}")
        print(f"\n   Top 5 trending:")
        for i, (ticker, data) in enumerate(
            list(result["tickers"].items())[:5], 1
        ):
            print(
                f"   {i}. ${ticker}: {data['count']} mentions, "
                f"sentiment={data['sentiment']:.2f}"
            )
    else:
        print(f"❌ Failed: {result.get('error')}")

    # Test 3: Test with simple query (no keywords)
    print("\n" + "-" * 60)
    print("Test 3: Fetch general r/stocks sentiment")
    print("-" * 60)

    result = await handler.fetch_subreddit_sentiment(
        subreddit="stocks",
        limit=30,
        time_filter="day"
    )

    if result["success"]:
        print(f"✅ Success!")
        print(f"   Posts analyzed: {result['post_count']}")
        print(f"   Average sentiment: {result['sentiment']:.2f}")
    else:
        print(f"❌ Failed: {result.get('error')}")

    print("\n" + "="*60)
    print("✅ Reddit handler tests complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(test_reddit_handler())
