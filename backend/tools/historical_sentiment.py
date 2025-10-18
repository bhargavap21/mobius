"""
Historical Sentiment Data Providers
Real data sources for backtesting - NO MOCK DATA
"""

import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from config import settings

logger = logging.getLogger(__name__)
sentiment_analyzer = SentimentIntensityAnalyzer()


class PushshiftRedditProvider:
    """
    Pushshift API for historical Reddit data
    Free, no API key required
    """

    def __init__(self):
        self.base_url = "https://api.pushshift.io/reddit"
        self.session = requests.Session()

    def get_historical_sentiment(
        self,
        ticker: str,
        date: str,  # YYYY-MM-DD format
        subreddit: str = "wallstreetbets"
    ) -> Optional[float]:
        """
        Get sentiment for a specific historical date
        """
        try:
            # Convert date string to timestamps
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            start_timestamp = int(date_obj.timestamp())
            end_timestamp = int((date_obj + timedelta(days=1)).timestamp())

            # Search for submissions (posts)
            url = f"{self.base_url}/search/submission/"
            params = {
                "subreddit": subreddit,
                "q": f"{ticker} OR ${ticker}",
                "after": start_timestamp,
                "before": end_timestamp,
                "size": 100,
                "sort": "score",
                "sort_type": "desc"
            }

            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                posts = data.get('data', [])

                if not posts:
                    logger.info(f"No Reddit posts found for {ticker} on {date}")
                    return None

                # Analyze sentiment
                sentiments = []
                for post in posts:
                    text = f"{post.get('title', '')} {post.get('selftext', '')}"
                    if ticker.upper() in text.upper():
                        sentiment = sentiment_analyzer.polarity_scores(text)
                        sentiments.append(sentiment['compound'])

                if sentiments:
                    avg_sentiment = sum(sentiments) / len(sentiments)
                    logger.info(f"📊 Pushshift: {ticker} on {date} - {len(sentiments)} posts, sentiment: {avg_sentiment:.3f}")
                    return avg_sentiment

            else:
                logger.warning(f"Pushshift API error: {response.status_code}")

        except Exception as e:
            logger.error(f"Pushshift error for {ticker} on {date}: {e}")

        return None


class AlphaVantageNewsProvider:
    """
    Alpha Vantage for news sentiment
    Free tier: 25 requests/day
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.alpha_vantage_api_key
        self.base_url = "https://www.alphavantage.co/query"

    def get_historical_sentiment(
        self,
        ticker: str,
        date: str
    ) -> Optional[float]:
        """
        Get news sentiment for a specific date
        """
        if not self.api_key:
            logger.warning("Alpha Vantage API key not configured")
            return None

        try:
            # Alpha Vantage provides sentiment for recent news
            params = {
                "function": "NEWS_SENTIMENT",
                "tickers": ticker,
                "time_from": f"{date}T0000",
                "time_to": f"{date}T2359",
                "apikey": self.api_key
            }

            response = requests.get(self.base_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                if "feed" in data:
                    sentiments = []
                    for article in data["feed"]:
                        # Get ticker-specific sentiment
                        for ticker_data in article.get("ticker_sentiment", []):
                            if ticker_data["ticker"] == ticker:
                                score = float(ticker_data["ticker_sentiment_score"])
                                sentiments.append(score)

                    if sentiments:
                        avg_sentiment = sum(sentiments) / len(sentiments)
                        logger.info(f"📰 Alpha Vantage: {ticker} on {date} - {len(sentiments)} articles, sentiment: {avg_sentiment:.3f}")
                        return avg_sentiment

        except Exception as e:
            logger.error(f"Alpha Vantage error for {ticker} on {date}: {e}")

        return None


class FinnhubSentimentProvider:
    """
    Finnhub for aggregated social sentiment
    Free tier: 60 calls/minute
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.finnhub_api_key
        self.base_url = "https://finnhub.io/api/v1"

    def get_historical_sentiment(
        self,
        ticker: str,
        date: str
    ) -> Optional[float]:
        """
        Get social sentiment from Finnhub
        """
        if not self.api_key:
            logger.warning("Finnhub API key not configured")
            return None

        try:
            # Finnhub provides daily sentiment
            url = f"{self.base_url}/stock/social-sentiment"
            params = {
                "symbol": ticker,
                "from": date,
                "to": date,
                "token": self.api_key
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Extract Reddit sentiment
                reddit_data = data.get("reddit", [])
                if reddit_data:
                    sentiments = [d.get("score", 0) for d in reddit_data]
                    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
                    logger.info(f"📊 Finnhub: {ticker} on {date} - sentiment: {avg_sentiment:.3f}")
                    return avg_sentiment

        except Exception as e:
            logger.error(f"Finnhub error for {ticker} on {date}: {e}")

        return None


class HistoricalSentimentAggregator:
    """
    Aggregates sentiment from multiple sources
    Falls back to next provider if one fails
    """

    def __init__(self):
        self.providers = {
            'pushshift': PushshiftRedditProvider(),
            'alpha_vantage': AlphaVantageNewsProvider(),
            'finnhub': FinnhubSentimentProvider()
        }
        self.cache = {}

    def get_sentiment(
        self,
        ticker: str,
        date: str,
        sources: List[str] = None
    ) -> Optional[float]:
        """
        Get sentiment from available sources

        Args:
            ticker: Stock ticker
            date: Date in YYYY-MM-DD format
            sources: List of sources to try (default: all)

        Returns:
            Sentiment score (-1 to 1) or None
        """
        # Check cache
        cache_key = f"{ticker}_{date}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        if sources is None:
            sources = ['pushshift', 'alpha_vantage', 'finnhub']

        sentiments = []

        for source in sources:
            if source in self.providers:
                sentiment = self.providers[source].get_historical_sentiment(ticker, date)
                if sentiment is not None:
                    sentiments.append(sentiment)

                # Rate limiting
                time.sleep(0.1)

        if sentiments:
            # Average sentiment from all available sources
            final_sentiment = sum(sentiments) / len(sentiments)
            self.cache[cache_key] = final_sentiment
            logger.info(f"✅ Aggregated sentiment for {ticker} on {date}: {final_sentiment:.3f} (from {len(sentiments)} sources)")
            return final_sentiment

        logger.warning(f"⚠️ No sentiment data available for {ticker} on {date}")
        return None


# Global aggregator instance
historical_sentiment = HistoricalSentimentAggregator()