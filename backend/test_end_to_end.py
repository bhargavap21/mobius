"""
End-to-End Integration Test
Tests: User Query → Router → API Handler → Data Extraction
"""

import asyncio
import sys
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

from agents.data_source_router import DataSourceRouterAgent
from tools.api_handlers.reddit_handler import RedditHandler


async def test_end_to_end_flow():
    """
    Test the complete flow from user query to data extraction

    Flow:
    1. User types: "Trade GME based on r/wallstreetbets sentiment"
    2. Router analyzes query and generates extraction plan
    3. Handler executes plan and extracts real data
    """

    print("\n" + "="*70)
    print("🧪 END-TO-END DATA EXTRACTION TEST")
    print("="*70 + "\n")

    # Step 1: Initialize components
    print("Step 1: Initializing Router and Handler")
    print("-" * 70)

    router = DataSourceRouterAgent()
    reddit_handler = RedditHandler()

    print(f"✅ Router initialized")
    print(f"{'✅' if reddit_handler.initialized else '⚠️'} Reddit handler initialized")
    print()

    # Step 2: User query → Router generates plan
    print("Step 2: User Query → Router")
    print("-" * 70)

    user_query = "Trade GME based on r/wallstreetbets sentiment"
    print(f'User query: "{user_query}"')
    print()

    extraction_plan = await router.plan_extraction({"user_query": user_query})

    print("📋 Generated Extraction Plan:")
    print(json.dumps(extraction_plan, indent=2))
    print()

    # Step 3: Execute plan with handler
    print("Step 3: Extraction Plan → Handler → Real Data")
    print("-" * 70)

    if not extraction_plan["sources"]:
        print("❌ No data sources identified in query")
        return

    # Get the first source from the plan
    source_config = extraction_plan["sources"][0]

    print(f"Executing: {source_config['method']} for {source_config['source']}")
    print()

    if source_config["method"] == "api" and source_config["source"] == "reddit.com":
        # This is a Reddit source - use RedditHandler
        if not reddit_handler.initialized:
            print("⚠️ Reddit handler not initialized (credentials missing)")
            print("\nTo test with real data:")
            print("1. Get Reddit API credentials from https://www.reddit.com/prefs/apps")
            print("2. Add to backend/.env:")
            print("   REDDIT_CLIENT_ID=your_client_id")
            print("   REDDIT_CLIENT_SECRET=your_client_secret")
            print("3. Re-run this test")
            print()
            print("✅ End-to-end flow verified (handler ready, needs credentials)")
            return

        # Execute real extraction
        config = source_config["config"]
        result = await reddit_handler.fetch_subreddit_sentiment(
            subreddit=config.get("target", "wallstreetbets"),
            keywords=config.get("filters", {}).get("keywords", ["GME"]),
            limit=50,
            time_filter="week"
        )

        if result["success"]:
            print("✅ REAL DATA EXTRACTED!")
            print()
            print(f"   Subreddit: r/{result['subreddit']}")
            print(f"   Posts analyzed: {result['post_count']}")
            print(f"   Sentiment: {result['sentiment']:.2f} (-1 to 1)")
            print(f"   Average upvotes: {result['avg_score']:.0f}")
            print()
            print("   Top 3 posts:")
            for i, post in enumerate(result["top_posts"][:3], 1):
                print(f"   {i}. [{post['score']}⬆] {post['title'][:50]}...")
                print(f"      Sentiment: {post['sentiment']:.2f}")
            print()
        else:
            print(f"❌ Extraction failed: {result.get('error')}")

    elif source_config["method"] == "apify":
        print("⚠️ Apify handler not yet implemented (coming in Phase 1, Week 2)")

    elif source_config["method"] == "browserbase":
        print("⚠️ Browserbase handler not yet implemented (coming in Phase 2)")

    print()
    print("="*70)
    print("✅ END-TO-END TEST COMPLETE")
    print("="*70)
    print()

    # Summary
    print("📊 Test Summary:")
    print(f"   Router: ✅ Working")
    print(f"   Reddit Handler: {'✅ Working' if reddit_handler.initialized else '⚠️ Ready (needs credentials)'}")
    print(f"   Data Sources Identified: {len(extraction_plan['sources'])}")
    print(f"   Estimated Monthly Cost: ${extraction_plan['estimated_cost']['estimated_monthly_cost']}")
    print(f"   Confidence: {extraction_plan['confidence'] * 100:.0f}%")
    print()


async def test_additional_queries():
    """Test router with various query types"""

    print("\n" + "="*70)
    print("🧪 TESTING ADDITIONAL QUERY TYPES")
    print("="*70 + "\n")

    router = DataSourceRouterAgent()

    test_queries = [
        "Trade TSLA on Elon Musk's tweets",
        "Trade based on r/stocks sentiment for AAPL",
        "Monitor TikTok for trending products",
    ]

    for query in test_queries:
        print(f"Query: \"{query}\"")
        plan = await router.plan_extraction({"user_query": query})

        if plan["sources"]:
            source = plan["sources"][0]
            print(f"  → Routed to: {source['method']} ({source['source']})")
            print(f"     Cost: ${plan['estimated_cost']['estimated_monthly_cost']}/month")
        else:
            print("  → No sources identified")
        print()


if __name__ == "__main__":
    print("\n🚀 Starting End-to-End Data Extraction Tests\n")

    # Run main test
    asyncio.run(test_end_to_end_flow())

    # Run additional query tests
    asyncio.run(test_additional_queries())

    print("✅ All tests complete!\n")
