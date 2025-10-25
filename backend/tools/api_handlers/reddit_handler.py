"""
Reddit API Handler
Real data extraction using PRAW (Python Reddit API Wrapper)
"""

import logging
import praw
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from textblob import TextBlob

from config import settings

logger = logging.getLogger(__name__)


class RedditHandler:
    """
    Official Reddit API integration using PRAW

    Features:
    - Fetch posts from any subreddit
    - Fetch comments for sentiment analysis
    - Search by keywords
    - Historical data support (using Reddit's search)
    - Sentiment analysis using TextBlob

    Example:
        handler = RedditHandler()
        result = await handler.fetch_subreddit_sentiment(
            subreddit="wallstreetbets",
            keywords=["GME", "GameStop"],
            limit=100
        )
    """

    def __init__(self):
        """Initialize Reddit API client"""
        self.reddit = None
        self.initialized = False

        # Check credentials
        if not settings.reddit_client_id or not settings.reddit_client_secret:
            logger.warning("⚠️ Reddit credentials not configured")
            return

        try:
            self.reddit = praw.Reddit(
                client_id=settings.reddit_client_id,
                client_secret=settings.reddit_client_secret,
                user_agent="TradingBotPlatform/1.0"
            )

            # Test connection
            self.reddit.user.me()  # This will fail if auth is invalid
            self.initialized = True
            logger.info("✅ Reddit API handler initialized")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Reddit API: {e}")
            self.initialized = False

    async def fetch_subreddit_sentiment(
        self,
        subreddit: str,
        keywords: Optional[List[str]] = None,
        limit: int = 100,
        time_filter: str = "day"
    ) -> Dict[str, Any]:
        """
        Fetch posts from subreddit and calculate sentiment

        Args:
            subreddit: Subreddit name (e.g., "wallstreetbets")
            keywords: Optional list of keywords to filter by
            limit: Number of posts to fetch (max 100)
            time_filter: "hour", "day", "week", "month", "year", "all"

        Returns:
            {
                "success": True,
                "subreddit": "wallstreetbets",
                "sentiment": 0.42,  # -1 to 1
                "post_count": 87,
                "avg_score": 124.5,
                "top_posts": [...]
            }
        """
        if not self.initialized:
            return {
                "success": False,
                "error": "Reddit API not initialized. Check credentials.",
                "subreddit": subreddit
            }

        try:
            sub = self.reddit.subreddit(subreddit)

            # Fetch posts
            posts = []
            if keywords:
                # Search for posts containing keywords
                query = " OR ".join(keywords)
                for post in sub.search(query, time_filter=time_filter, limit=limit):
                    posts.append(post)
            else:
                # Get hot posts
                for post in sub.hot(limit=limit):
                    posts.append(post)

            if not posts:
                logger.warning(f"⚠️ No posts found in r/{subreddit}")
                return {
                    "success": True,
                    "subreddit": subreddit,
                    "sentiment": 0.0,
                    "post_count": 0,
                    "avg_score": 0,
                    "top_posts": []
                }

            # Analyze sentiment
            sentiments = []
            scores = []
            top_posts = []

            for post in posts:
                # Sentiment analysis on title + selftext
                text = f"{post.title} {post.selftext}"
                blob = TextBlob(text)
                sentiment = blob.sentiment.polarity

                sentiments.append(sentiment)
                scores.append(post.score)

                # Track top posts
                top_posts.append({
                    "title": post.title,
                    "score": post.score,
                    "sentiment": round(sentiment, 3),
                    "url": f"https://reddit.com{post.permalink}",
                    "created_utc": datetime.fromtimestamp(post.created_utc).isoformat(),
                    "num_comments": post.num_comments
                })

            # Sort by score
            top_posts.sort(key=lambda x: x["score"], reverse=True)

            result = {
                "success": True,
                "subreddit": subreddit,
                "sentiment": round(sum(sentiments) / len(sentiments), 3),
                "post_count": len(posts),
                "avg_score": round(sum(scores) / len(scores), 2),
                "top_posts": top_posts[:10],  # Top 10 posts
                "keywords": keywords,
                "time_filter": time_filter
            }

            logger.info(
                f"✅ Fetched r/{subreddit}: {len(posts)} posts, "
                f"sentiment={result['sentiment']:.2f}"
            )

            return result

        except Exception as e:
            logger.error(f"❌ Error fetching r/{subreddit}: {e}")
            return {
                "success": False,
                "error": str(e),
                "subreddit": subreddit
            }

    async def fetch_historical_sentiment(
        self,
        subreddit: str,
        date: str,
        keywords: Optional[List[str]] = None,
        limit: int = 50
    ) -> Optional[float]:
        """
        Fetch historical sentiment for a specific date

        Args:
            subreddit: Subreddit name
            date: Date string (YYYY-MM-DD)
            keywords: Optional keywords to search for
            limit: Number of posts to analyze

        Returns:
            Sentiment score (-1 to 1) or None
        """
        if not self.initialized:
            logger.error("❌ Reddit API not initialized")
            return None

        try:
            # Parse date
            target_date = datetime.strptime(date, "%Y-%m-%d")

            # Reddit search doesn't support exact date filtering
            # We'll search from that day and filter manually
            sub = self.reddit.subreddit(subreddit)

            posts = []
            if keywords:
                query = " OR ".join(keywords)
                for post in sub.search(query, time_filter="all", limit=limit * 2):
                    post_date = datetime.fromtimestamp(post.created_utc)

                    # Check if post is from target date (±1 day tolerance)
                    if abs((post_date - target_date).days) <= 1:
                        posts.append(post)

                    if len(posts) >= limit:
                        break
            else:
                # Without keywords, we can't efficiently search historical data
                logger.warning(
                    f"⚠️ Historical search for r/{subreddit} requires keywords"
                )
                return None

            if not posts:
                logger.warning(
                    f"⚠️ No historical posts found for r/{subreddit} on {date}"
                )
                return None

            # Calculate sentiment
            sentiments = []
            for post in posts:
                text = f"{post.title} {post.selftext}"
                blob = TextBlob(text)
                sentiments.append(blob.sentiment.polarity)

            avg_sentiment = sum(sentiments) / len(sentiments)

            logger.info(
                f"✅ Historical sentiment for r/{subreddit} on {date}: "
                f"{avg_sentiment:.2f} ({len(posts)} posts)"
            )

            return round(avg_sentiment, 3)

        except Exception as e:
            logger.error(
                f"❌ Error fetching historical sentiment for r/{subreddit}: {e}"
            )
            return None

    async def fetch_user_posts(
        self,
        username: str,
        limit: int = 25
    ) -> Dict[str, Any]:
        """
        Fetch recent posts from a specific user

        Args:
            username: Reddit username
            limit: Number of posts to fetch

        Returns:
            {
                "success": True,
                "username": "deepfuckingvalue",
                "post_count": 15,
                "posts": [...]
            }
        """
        if not self.initialized:
            return {
                "success": False,
                "error": "Reddit API not initialized",
                "username": username
            }

        try:
            user = self.reddit.redditor(username)

            posts = []
            for submission in user.submissions.new(limit=limit):
                posts.append({
                    "title": submission.title,
                    "subreddit": submission.subreddit.display_name,
                    "score": submission.score,
                    "created_utc": datetime.fromtimestamp(
                        submission.created_utc
                    ).isoformat(),
                    "url": f"https://reddit.com{submission.permalink}"
                })

            logger.info(f"✅ Fetched {len(posts)} posts from u/{username}")

            return {
                "success": True,
                "username": username,
                "post_count": len(posts),
                "posts": posts
            }

        except Exception as e:
            logger.error(f"❌ Error fetching posts from u/{username}: {e}")
            return {
                "success": False,
                "error": str(e),
                "username": username
            }

    def get_trending_tickers(
        self,
        subreddit: str = "wallstreetbets",
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Identify trending stock tickers in subreddit

        Returns:
            {
                "success": True,
                "subreddit": "wallstreetbets",
                "tickers": {
                    "GME": {"count": 45, "sentiment": 0.65},
                    "TSLA": {"count": 32, "sentiment": 0.42},
                    ...
                }
            }
        """
        if not self.initialized:
            return {
                "success": False,
                "error": "Reddit API not initialized"
            }

        try:
            import re

            sub = self.reddit.subreddit(subreddit)

            # Common stock ticker pattern (1-5 uppercase letters)
            ticker_pattern = r'\b[A-Z]{1,5}\b'

            # Track ticker mentions and sentiment
            ticker_data = {}

            for post in sub.hot(limit=limit):
                text = f"{post.title} {post.selftext}"

                # Find tickers
                tickers = re.findall(ticker_pattern, text)

                # Calculate sentiment
                blob = TextBlob(text)
                sentiment = blob.sentiment.polarity

                for ticker in tickers:
                    # Filter out common words
                    if ticker in ["A", "I", "CEO", "IPO", "ETF", "DD", "YOLO"]:
                        continue

                    if ticker not in ticker_data:
                        ticker_data[ticker] = {
                            "count": 0,
                            "total_sentiment": 0
                        }

                    ticker_data[ticker]["count"] += 1
                    ticker_data[ticker]["total_sentiment"] += sentiment

            # Calculate average sentiment for each ticker
            trending_tickers = {}
            for ticker, data in ticker_data.items():
                if data["count"] >= 3:  # Minimum 3 mentions
                    trending_tickers[ticker] = {
                        "count": data["count"],
                        "sentiment": round(
                            data["total_sentiment"] / data["count"], 3
                        )
                    }

            # Sort by count
            trending_tickers = dict(
                sorted(
                    trending_tickers.items(),
                    key=lambda x: x[1]["count"],
                    reverse=True
                )
            )

            logger.info(
                f"✅ Found {len(trending_tickers)} trending tickers in r/{subreddit}"
            )

            return {
                "success": True,
                "subreddit": subreddit,
                "tickers": trending_tickers,
                "analyzed_posts": limit
            }

        except Exception as e:
            logger.error(f"❌ Error finding trending tickers: {e}")
            return {
                "success": False,
                "error": str(e)
            }
