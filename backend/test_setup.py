#!/usr/bin/env python3
"""Test script to verify API connections"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import settings


def test_claude_api():
    """Test Claude API connection"""
    print("\n🤖 Testing Claude API...")

    if not settings.anthropic_api_key:
        print("❌ ANTHROPIC_API_KEY not set in .env")
        return False

    try:
        from anthropic import Anthropic

        client = Anthropic(api_key=settings.anthropic_api_key)

        # Simple test message
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": "Say 'API connection successful' and nothing else."
            }]
        )

        result = response.content[0].text
        print(f"✅ Claude API: {result}")
        return True

    except Exception as e:
        print(f"❌ Claude API Error: {e}")
        return False


def test_alpaca_api():
    """Test Alpaca API connection"""
    print("\n📈 Testing Alpaca API...")

    if not settings.alpaca_api_key or not settings.alpaca_secret_key:
        print("❌ Alpaca API keys not set in .env")
        return False

    try:
        from alpaca.trading.client import TradingClient

        client = TradingClient(
            api_key=settings.alpaca_api_key,
            secret_key=settings.alpaca_secret_key,
            paper=True
        )

        # Get account info
        account = client.get_account()
        print(f"✅ Alpaca API Connected!")
        print(f"   Account Status: {account.status}")
        print(f"   Buying Power: ${float(account.buying_power):,.2f}")
        print(f"   Cash: ${float(account.cash):,.2f}")
        return True

    except Exception as e:
        print(f"❌ Alpaca API Error: {e}")
        return False


def test_reddit_api():
    """Test Reddit API connection"""
    print("\n🔴 Testing Reddit API...")

    if not settings.reddit_client_id or not settings.reddit_client_secret:
        print("⚠️  Reddit API keys not set (optional for MVP)")
        return None

    try:
        import praw

        reddit = praw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent
        )

        # Test by getting a subreddit
        subreddit = reddit.subreddit("wallstreetbets")
        print(f"✅ Reddit API Connected!")
        print(f"   Subreddit: r/{subreddit.display_name}")
        print(f"   Subscribers: {subreddit.subscribers:,}")
        return True

    except Exception as e:
        print(f"❌ Reddit API Error: {e}")
        return False


def main():
    """Run all API tests"""
    print("=" * 60)
    print("🚀 Testing API Connections for Trading Bot")
    print("=" * 60)

    results = {
        "Claude API": test_claude_api(),
        "Alpaca API": test_alpaca_api(),
        "Reddit API": test_reddit_api()
    }

    print("\n" + "=" * 60)
    print("📊 Summary:")
    print("=" * 60)

    for api, status in results.items():
        if status is True:
            print(f"✅ {api}: Connected")
        elif status is False:
            print(f"❌ {api}: Failed")
        else:
            print(f"⚠️  {api}: Optional (not configured)")

    print("\n")

    # Check if critical APIs are working
    critical_apis = ["Claude API", "Alpaca API"]
    if all(results.get(api) for api in critical_apis):
        print("🎉 All critical APIs are working! Ready to proceed.")
        return 0
    else:
        print("⚠️  Some critical APIs failed. Please check your .env file.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
