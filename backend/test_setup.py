#!/usr/bin/env python3
"""Test script to verify API connections"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import settings


def test_gemini_api():
    """Test Gemini API connection"""
    print("\n🤖 Testing Gemini API...")

    if not settings.gemini_api_key:
        print("❌ GEMINI_API_KEY not set in .env")
        return False

    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Simple test message
        response = model.generate_content(
            "Say 'API connection successful' and nothing else.",
            generation_config=genai.GenerationConfig(
                max_output_tokens=100,
                temperature=0.7,
            )
        )

        result = response.text
        print(f"✅ Gemini API: {result}")
        return True

    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
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
        "Gemini API": test_gemini_api(),
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
    critical_apis = ["Gemini API", "Alpaca API"]
    if all(results.get(api) for api in critical_apis):
        print("🎉 All critical APIs are working! Ready to proceed.")
        return 0
    else:
        print("⚠️  Some critical APIs failed. Please check your .env file.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
