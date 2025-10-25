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
            logger.error("❌ Reddit API not configured - credentials required")
            return {
                "success": False,
                "error": "Reddit API credentials not configured. Please add REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET to .env",
                "ticker": ticker,
            }

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

        # Twitter API requires Apify integration (Phase 1, Week 2)
        logger.error("❌ Twitter sentiment not implemented - requires Apify integration")

        return {
            "success": False,
            "error": "Twitter sentiment requires Apify integration. Coming in Phase 1, Week 2.",
            "keyword": keyword,
            "user": user,
        }

    except Exception as e:
        logger.error(f"❌ Error analyzing Twitter sentiment: {e}")
        return {
            "success": False,
            "error": str(e),
            "keyword": keyword,
        }


def get_trending_stocks_reddit(
    subreddit: str = "wallstreetbets",
    limit: int = 100,
    top_n: int = 10,
    min_mentions: int = 3
) -> Dict[str, Any]:
    """
    Get trending stocks from Reddit based on mention frequency and sentiment

    Args:
        subreddit: Subreddit to search (default: wallstreetbets)
        limit: Max posts to analyze
        top_n: Number of top trending stocks to return
        min_mentions: Minimum mentions required to be included

    Returns:
        Dict with trending stocks ranked by weighted score (mentions + sentiment)
    """
    try:
        logger.info(f"📈 Getting trending stocks from r/{subreddit}")

        # Check if Reddit credentials are configured
        if not settings.reddit_client_id or not settings.reddit_client_secret:
            logger.error("❌ Reddit API not configured")
            return {
                "success": False,
                "error": "Reddit API credentials not configured",
                "trending_stocks": []
            }

        import praw
        from collections import defaultdict

        # Initialize Reddit client
        reddit = praw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent,
        )

        subreddit_obj = reddit.subreddit(subreddit)

        # Track mentions and sentiment for each ticker
        ticker_data = defaultdict(lambda: {
            'mentions': 0,
            'sentiment_scores': [],
            'upvotes': 0,
            'posts': []
        })

        # Ticker patterns: either $TICKER or standalone uppercase 2-5 letters
        ticker_pattern_with_dollar = re.compile(r'\$([A-Z]{1,5})\b')
        ticker_pattern_standalone = re.compile(r'\b[A-Z]{2,5}\b')  # At least 2 letters to filter out 'A', 'I'

        # Exclude common words that look like tickers
        excluded_words = {
            'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL',
            'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET',
            'HAS', 'HIM', 'HIS', 'HOW', 'ITS', 'MAY', 'NEW', 'NOW',
            'OLD', 'SEE', 'TWO', 'WHO', 'BOY', 'DID', 'ITS', 'LET',
            'PUT', 'SAY', 'SHE', 'TOO', 'USE', 'YOLO', 'WSB', 'IMO',
            'EDIT', 'TLDR', 'ELI5', 'AMA', 'TIL', 'PSA', 'FYI', 'BTW',
            'ATH', 'ATL', 'DD', 'ER', 'EOD', 'EOW', 'PM', 'AM',
            'USA', 'SEC', 'CEO', 'CFO', 'IPO', 'ETF', 'ROTH', 'IRA',
            # Additional common words
            'I', 'A', 'TO', 'IN', 'IT', 'IS', 'AT', 'ON', 'BY', 'OF',
            'SO', 'IF', 'OR', 'AS', 'BE', 'DO', 'GO', 'NO', 'UP', 'WE',
            'MY', 'AN', 'ME', 'US', 'HE', 'VERY', 'MUCH', 'BEEN', 'JUST',
            'LIKE', 'HAVE', 'WILL', 'THIS', 'THAT', 'FROM', 'THEY', 'WERE',
            'WHAT', 'WHEN', 'WHERE', 'WHICH', 'YEAR', 'ALSO', 'MORE', 'SOME',
            'WITH', 'INTO', 'THAN', 'OVER', 'SUCH', 'ONLY', 'EVEN', 'WELL',
            'BACK', 'GOOD', 'VERY', 'HIGH', 'MUCH', 'BOTH', 'EACH', 'MOST'
        }

        # Get hot and new posts
        all_posts = []
        for post in subreddit_obj.hot(limit=limit):
            all_posts.append(post)

        for post in subreddit_obj.new(limit=limit // 2):
            if post not in all_posts:
                all_posts.append(post)

        logger.info(f"   Analyzing {len(all_posts)} posts...")

        # Analyze posts for ticker mentions
        for post in all_posts:
            # Check if post is recent (last 3 days)
            post_time = datetime.fromtimestamp(post.created_utc)
            time_diff = datetime.now() - post_time
            if time_diff > timedelta(days=3):
                continue

            # Extract text
            full_text = f"{post.title} {post.selftext}"
            full_text_upper = full_text.upper()

            # Find tickers with $ prefix (high confidence)
            dollar_tickers = ticker_pattern_with_dollar.findall(full_text_upper)

            # Find standalone uppercase tickers (medium confidence)
            standalone_tickers = ticker_pattern_standalone.findall(full_text_upper)

            # Combine tickers (prioritize $ tickers)
            mentioned_tickers = set()

            # Add $TICKER matches (high confidence)
            for ticker in dollar_tickers:
                if ticker not in excluded_words:
                    mentioned_tickers.add(ticker)

            # Add standalone matches if not in excluded words
            for ticker in standalone_tickers:
                if ticker not in excluded_words and len(ticker) >= 2:
                    mentioned_tickers.add(ticker)

            # Analyze sentiment for this post
            sentiment_score = sentiment_analyzer.polarity_scores(full_text)['compound']

            # Update ticker data
            for ticker in mentioned_tickers:
                ticker_data[ticker]['mentions'] += 1
                ticker_data[ticker]['sentiment_scores'].append(sentiment_score)
                ticker_data[ticker]['upvotes'] += post.score
                ticker_data[ticker]['posts'].append({
                    'title': post.title,
                    'score': post.score,
                    'url': f"https://reddit.com{post.permalink}"
                })

        # Calculate weighted scores for each ticker
        trending_stocks = []
        for ticker, data in ticker_data.items():
            if data['mentions'] >= min_mentions:
                avg_sentiment = sum(data['sentiment_scores']) / len(data['sentiment_scores'])

                # Weighted score: mentions * (1 + sentiment) * log(upvotes + 1)
                import math
                upvote_factor = math.log10(data['upvotes'] + 10)
                weighted_score = data['mentions'] * (1 + avg_sentiment) * upvote_factor

                trending_stocks.append({
                    'ticker': ticker,
                    'mentions': data['mentions'],
                    'avg_sentiment': round(avg_sentiment, 3),
                    'upvotes': data['upvotes'],
                    'weighted_score': round(weighted_score, 2),
                    'sample_posts': data['posts'][:3]  # Top 3 posts
                })

        # Sort by weighted score
        trending_stocks.sort(key=lambda x: x['weighted_score'], reverse=True)

        # Return top N
        top_trending = trending_stocks[:top_n]

        logger.info(f"✅ Found {len(trending_stocks)} trending stocks")
        if top_trending:
            top_3_str = ', '.join([f"{s['ticker']} ({s['mentions']} mentions)" for s in top_trending[:3]])
            logger.info(f"   Top 3: {top_3_str}")

        return {
            "success": True,
            "subreddit": subreddit,
            "trending_stocks": top_trending,
            "total_analyzed": len(all_posts),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error getting trending stocks: {e}")
        return {
            "success": False,
            "error": str(e),
            "trending_stocks": []
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
