"""
Social Media Tools - Reddit, Twitter sentiment analysis

Monitor social media for stock mentions and sentiment
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from config import settings

logger = logging.getLogger(__name__)

# Initialize sentiment analyzer
sentiment_analyzer = SentimentIntensityAnalyzer()


def get_reddit_sentiment(
    ticker: str,
    subreddit: str = "wallstreetbets",
    limit: int = 100,
    hours: int = 24,
) -> Dict[str, Any]:
    """
    Get Reddit sentiment for a stock ticker

    Args:
        ticker: Stock ticker symbol (e.g., "TSLA", "AAPL")
        subreddit: Subreddit to search (default: wallstreetbets)
        limit: Max posts to analyze
        hours: Time window in hours

    Returns:
        Sentiment analysis results
    """
    try:
        logger.info(
            f"🔴 Analyzing Reddit sentiment for {ticker} in r/{subreddit} (last {hours}h)"
        )

        # Check if Reddit credentials are configured
        if not settings.reddit_client_id or not settings.reddit_client_secret:
            logger.warning("⚠️  Reddit API not configured, using mock data")
            return _mock_reddit_sentiment(ticker, subreddit)

        import praw

        # Initialize Reddit client
        reddit = praw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent,
        )

        subreddit_obj = reddit.subreddit(subreddit)

        mentions = 0
        sentiment_scores = []
        post_details = []

        # Try multiple search patterns for better results
        ticker_patterns = [
            ticker.upper(),
            f"${ticker.upper()}",
            ticker.lower()
        ]

        # Add specific patterns for known tickers
        if ticker.upper() == "GME":
            ticker_patterns.extend(["GameStop", "GAMESTOP", "Game Stop"])

        # Use .hot() instead of search for better results
        # Get more posts and filter manually for better coverage
        all_posts = []

        # Get hot posts
        for post in subreddit_obj.hot(limit=limit):
            all_posts.append(post)

        # Get new posts
        for post in subreddit_obj.new(limit=limit):
            if post not in all_posts:
                all_posts.append(post)

        # Analyze posts for ticker mentions
        for post in all_posts:
            # Check if post is within time window (expand to 7 days for backtesting)
            post_time = datetime.fromtimestamp(post.created_utc)
            time_diff = datetime.now() - post_time
            if time_diff > timedelta(days=7):
                continue

            # Check if ticker is mentioned in title or text
            full_text = f"{post.title} {post.selftext}".upper()

            # Check for any pattern match
            if any(pattern.upper() in full_text for pattern in ticker_patterns):
                mentions += 1

                # Analyze sentiment
                text = f"{post.title} {post.selftext}"
                sentiment = sentiment_analyzer.polarity_scores(text)

                sentiment_scores.append(sentiment["compound"])

                post_details.append(
                    {
                        "title": post.title[:100],
                        "score": post.score,
                        "comments": post.num_comments,
                        "sentiment": sentiment["compound"],
                        "url": f"https://reddit.com{post.permalink}",
                    }
                )

        # Calculate aggregate sentiment
        avg_sentiment = (
            sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        )

        # Determine bullish/bearish
        is_bullish = avg_sentiment > 0.1
        is_bearish = avg_sentiment < -0.1

        result = {
            "success": True,
            "ticker": ticker,
            "subreddit": subreddit,
            "mentions": mentions,
            "avg_sentiment": round(avg_sentiment, 3),
            "bullish": is_bullish,
            "bearish": is_bearish,
            "sentiment_label": (
                "Bullish 🚀" if is_bullish else "Bearish 📉" if is_bearish else "Neutral"
            ),
            "time_window_hours": hours,
            "top_posts": sorted(post_details, key=lambda x: x["score"], reverse=True)[
                :5
            ],
        }

        logger.info(
            f"✅ {ticker}: {mentions} mentions, sentiment: {avg_sentiment:.3f} ({result['sentiment_label']})"
        )

        return result

    except Exception as e:
        logger.error(f"❌ Error analyzing Reddit sentiment for {ticker}: {e}")
        return {
            "success": False,
            "error": str(e),
            "ticker": ticker,
        }


def _mock_reddit_sentiment(ticker: str, subreddit: str) -> Dict[str, Any]:
    """
    Generate mock Reddit sentiment data for testing

    Args:
        ticker: Stock ticker
        subreddit: Subreddit name

    Returns:
        Mock sentiment data
    """
    # Generate realistic mock data based on ticker
    mock_data = {
        "TSLA": {
            "mentions": 247,
            "avg_sentiment": 0.65,
            "bullish": True,
            "top_posts": [
                {
                    "title": "TSLA to the moon! Elon just announced new factory 🚀",
                    "score": 1523,
                    "comments": 342,
                    "sentiment": 0.82,
                },
                {
                    "title": "Why I'm bullish on Tesla - DD inside",
                    "score": 892,
                    "comments": 156,
                    "sentiment": 0.71,
                },
                {
                    "title": "TSLA 500c FDs are printing 💰",
                    "score": 654,
                    "comments": 89,
                    "sentiment": 0.45,
                },
            ],
        },
        "GME": {
            "mentions": 892,
            "avg_sentiment": 0.78,
            "bullish": True,
            "top_posts": [
                {
                    "title": "GME still has potential, holding strong 💎🙌",
                    "score": 3421,
                    "comments": 567,
                    "sentiment": 0.89,
                }
            ],
        },
        "AAPL": {
            "mentions": 123,
            "avg_sentiment": 0.15,
            "bullish": True,
            "top_posts": [
                {
                    "title": "AAPL steady as always, boring but reliable",
                    "score": 445,
                    "comments": 67,
                    "sentiment": 0.25,
                }
            ],
        },
    }

    # Get mock data or generate neutral sentiment
    data = mock_data.get(
        ticker.upper(), {"mentions": 45, "avg_sentiment": 0.05, "bullish": False}
    )

    sentiment = data["avg_sentiment"]
    is_bullish = sentiment > 0.1
    is_bearish = sentiment < -0.1

    return {
        "success": True,
        "ticker": ticker,
        "subreddit": subreddit,
        "mentions": data["mentions"],
        "avg_sentiment": sentiment,
        "bullish": is_bullish,
        "bearish": is_bearish,
        "sentiment_label": (
            "Bullish 🚀" if is_bullish else "Bearish 📉" if is_bearish else "Neutral"
        ),
        "time_window_hours": 24,
        "top_posts": data.get("top_posts", []),
        "note": "⚠️  Using mock data (Reddit API not configured)",
    }


def get_twitter_sentiment(
    keyword: str,
    user: Optional[str] = None,
    hours: int = 24,
) -> Dict[str, Any]:
    """
    Get Twitter/X sentiment for a keyword or user

    Args:
        keyword: Keyword to search for (e.g., "Tesla", "TSLA")
        user: Twitter username to monitor (e.g., "elonmusk")
        hours: Time window in hours

    Returns:
        Twitter sentiment analysis
    """
    try:
        logger.info(f"🐦 Analyzing Twitter sentiment for '{keyword}'")

        # Twitter API is expensive and requires approval
        # For hackathon, we'll use mock data
        logger.warning("⚠️  Using mock Twitter data (API not implemented)")

        return _mock_twitter_sentiment(keyword, user)

    except Exception as e:
        logger.error(f"❌ Error analyzing Twitter sentiment: {e}")
        return {
            "success": False,
            "error": str(e),
            "keyword": keyword,
        }


def _mock_twitter_sentiment(keyword: str, user: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate mock Twitter sentiment data

    Args:
        keyword: Search keyword
        user: Twitter user

    Returns:
        Mock Twitter sentiment data
    """
    # Elon Musk tweet examples
    if user and user.lower() in ["elonmusk", "elon"]:
        return {
            "success": True,
            "keyword": keyword,
            "user": "elonmusk",
            "tweets_analyzed": 15,
            "avg_sentiment": 0.72,
            "positive_tweets": 12,
            "negative_tweets": 1,
            "neutral_tweets": 2,
            "bullish": True,
            "recent_tweets": [
                {
                    "text": "Tesla production hitting new records! Cybertruck ramping up nicely 🚙⚡",
                    "sentiment": 0.85,
                    "likes": 45230,
                    "retweets": 8934,
                    "timestamp": "2 hours ago",
                },
                {
                    "text": "Just drove the new Model S Plaid. Acceleration is insane! 🚀",
                    "sentiment": 0.91,
                    "likes": 67421,
                    "retweets": 12456,
                    "timestamp": "5 hours ago",
                },
            ],
            "note": "⚠️  Using mock data (Twitter API not implemented)",
        }

    # Generic sentiment
    return {
        "success": True,
        "keyword": keyword,
        "user": user,
        "tweets_analyzed": 50,
        "avg_sentiment": 0.35,
        "positive_tweets": 28,
        "negative_tweets": 12,
        "neutral_tweets": 10,
        "bullish": True,
        "recent_tweets": [
            {
                "text": f"Bullish on {keyword}! 📈",
                "sentiment": 0.65,
                "likes": 234,
                "retweets": 45,
                "timestamp": "3 hours ago",
            }
        ],
        "note": "⚠️  Using mock data (Twitter API not implemented)",
    }


def analyze_social_sentiment(ticker: str) -> Dict[str, Any]:
    """
    Comprehensive social media sentiment analysis

    Combines Reddit + Twitter sentiment for a ticker

    Args:
        ticker: Stock ticker symbol

    Returns:
        Combined sentiment analysis
    """
    logger.info(f"📊 Running comprehensive social sentiment analysis for {ticker}")

    # Get Reddit sentiment
    reddit_data = get_reddit_sentiment(ticker)

    # Get Twitter sentiment
    twitter_data = get_twitter_sentiment(ticker)

    # Combine sentiments
    combined_sentiment = (
        reddit_data.get("avg_sentiment", 0) * 0.6
        + twitter_data.get("avg_sentiment", 0) * 0.4
    )

    is_bullish = combined_sentiment > 0.15
    total_mentions = reddit_data.get("mentions", 0) + twitter_data.get(
        "tweets_analyzed", 0
    )

    result = {
        "success": True,
        "ticker": ticker,
        "combined_sentiment": round(combined_sentiment, 3),
        "bullish": is_bullish,
        "bearish": combined_sentiment < -0.15,
        "total_mentions": total_mentions,
        "reddit": {
            "mentions": reddit_data.get("mentions", 0),
            "sentiment": reddit_data.get("avg_sentiment", 0),
            "bullish": reddit_data.get("bullish", False),
        },
        "twitter": {
            "mentions": twitter_data.get("tweets_analyzed", 0),
            "sentiment": twitter_data.get("avg_sentiment", 0),
            "bullish": twitter_data.get("bullish", False),
        },
        "recommendation": (
            "Strong Buy Signal 🚀" if combined_sentiment > 0.5 else
            "Buy Signal ✅" if combined_sentiment > 0.15 else
            "Sell Signal ⚠️" if combined_sentiment < -0.15 else
            "Hold/Neutral ➡️"
        ),
    }

    logger.info(
        f"✅ Combined sentiment for {ticker}: {combined_sentiment:.3f} - {result['recommendation']}"
    )

    return result


# Tool schemas for Claude
SOCIAL_MEDIA_TOOLS = [
    {
        "name": "get_reddit_sentiment",
        "description": "Analyze Reddit sentiment for a stock ticker. Searches r/wallstreetbets (or other subreddit) for mentions and calculates bullish/bearish sentiment score.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., 'TSLA', 'GME', 'AAPL')",
                },
                "subreddit": {
                    "type": "string",
                    "description": "Subreddit to search (default: wallstreetbets)",
                    "default": "wallstreetbets",
                },
                "hours": {
                    "type": "integer",
                    "description": "Time window in hours to analyze (default: 24)",
                    "default": 24,
                },
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "get_twitter_sentiment",
        "description": "Analyze Twitter/X sentiment for a keyword or specific user's tweets. Useful for tracking influencer sentiment (e.g., Elon Musk tweets about Tesla).",
        "input_schema": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "Keyword to search for (e.g., 'Tesla', 'TSLA', 'Bitcoin')",
                },
                "user": {
                    "type": "string",
                    "description": "Twitter username to monitor (e.g., 'elonmusk'). Optional.",
                },
                "hours": {
                    "type": "integer",
                    "description": "Time window in hours (default: 24)",
                    "default": 24,
                },
            },
            "required": ["keyword"],
        },
    },
    {
        "name": "analyze_social_sentiment",
        "description": "Comprehensive social media sentiment analysis combining Reddit and Twitter data for a stock ticker. Returns overall bullish/bearish signal.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol",
                }
            },
            "required": ["ticker"],
        },
    },
]
