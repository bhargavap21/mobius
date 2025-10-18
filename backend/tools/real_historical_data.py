"""
Real Historical Sentiment Data Providers
Alpha Vantage and Finnhub for comprehensive historical coverage
NO MOCK DATA - Only real APIs with actual historical data
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


class AlphaVantageProvider:
    """
    Alpha Vantage - News Sentiment API
    Free tier: 25 requests/day, 500 requests/month
    Provides: Historical news sentiment going back years
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.alpha_vantage_api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.session = requests.Session()

    def get_sentiment(self, ticker: str, date: str) -> Optional[Dict]:
        """
        Get news sentiment for a ticker on a specific date

        Args:
            ticker: Stock ticker (e.g., "GME")
            date: Date in YYYY-MM-DD format

        Returns:
            Dict with sentiment score and metadata
        """
        if not self.api_key:
            logger.warning("Alpha Vantage API key not configured")
            return None

        try:
            # Alpha Vantage News Sentiment endpoint
            # Format: YYYYMMDDTHHMM
            date_formatted = date.replace("-", "")
            params = {
                "function": "NEWS_SENTIMENT",
                "tickers": ticker.upper(),
                "apikey": self.api_key,
                "time_from": f"{date_formatted}T0000",
                "time_to": f"{date_formatted}T2359",
                "limit": 50
            }

            response = self.session.get(self.base_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Check for rate limit message
                if "Note" in data or "Information" in data:
                    logger.warning(f"Alpha Vantage rate limit: {data.get('Note', data.get('Information'))}")
                    return None

                # Process feed items
                feed = data.get('feed', [])
                if feed:
                    sentiments = []
                    relevance_scores = []

                    for article in feed:
                        # Get ticker-specific sentiment
                        ticker_sentiment = None
                        for ts in article.get('ticker_sentiment', []):
                            if ts.get('ticker') == ticker.upper():
                                ticker_sentiment = ts
                                break

                        if ticker_sentiment:
                            # Convert sentiment score from string to float
                            score = float(ticker_sentiment.get('ticker_sentiment_score', 0))
                            relevance = float(ticker_sentiment.get('relevance_score', 0))

                            # Weight by relevance
                            sentiments.append(score * relevance)
                            relevance_scores.append(relevance)

                    if sentiments:
                        # Calculate weighted average sentiment
                        avg_sentiment = sum(sentiments) / sum(relevance_scores) if sum(relevance_scores) > 0 else 0

                        logger.info(f"📰 Alpha Vantage: {ticker} on {date} - {len(sentiments)} articles, sentiment: {avg_sentiment:.3f}")
                        return {
                            "sentiment": avg_sentiment,
                            "source": "news",
                            "count": len(sentiments),
                            "provider": "alpha_vantage"
                        }

                # Try overall sentiment if no ticker-specific data
                overall_sentiment = data.get('sentiment_score_definition', {})
                if overall_sentiment:
                    logger.info(f"📊 Alpha Vantage: Using overall market sentiment for {date}")
                    return {
                        "sentiment": 0.0,  # Neutral if no specific data
                        "source": "market",
                        "count": 0,
                        "provider": "alpha_vantage"
                    }

            else:
                logger.warning(f"Alpha Vantage API error: {response.status_code}")

        except Exception as e:
            logger.error(f"Alpha Vantage error for {ticker}: {e}")

        return None


class FinnhubProvider:
    """
    Finnhub - Market News & Sentiment
    Free tier: 60 calls/minute, unlimited monthly
    Provides: Company news with sentiment analysis
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.finnhub_api_key
        self.base_url = "https://finnhub.io/api/v1"
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"X-Finnhub-Token": self.api_key})

    def get_sentiment(self, ticker: str, date: str) -> Optional[Dict]:
        """
        Get news sentiment from Finnhub for a specific date
        """
        if not self.api_key:
            logger.warning("Finnhub API key not configured")
            return None

        try:
            # Convert date to timestamps
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            next_day = date_obj + timedelta(days=1)

            # Finnhub uses YYYY-MM-DD format
            from_date = date_obj.strftime("%Y-%m-%d")
            to_date = next_day.strftime("%Y-%m-%d")

            # Get company news
            params = {
                "symbol": ticker.upper(),
                "from": from_date,
                "to": to_date,
                "token": self.api_key  # CRITICAL: Add the API token!
            }

            url = f"{self.base_url}/company-news"
            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 200:
                articles = response.json()

                if articles:
                    sentiments = []

                    for article in articles:
                        # Analyze headline and summary with VADER
                        text = f"{article.get('headline', '')} {article.get('summary', '')}"
                        if text.strip():
                            scores = sentiment_analyzer.polarity_scores(text)
                            sentiments.append(scores['compound'])

                    if sentiments:
                        avg_sentiment = sum(sentiments) / len(sentiments)
                        logger.info(f"📰 Finnhub: {ticker} on {date} - {len(sentiments)} articles, sentiment: {avg_sentiment:.3f}")
                        return {
                            "sentiment": avg_sentiment,
                            "source": "news",
                            "count": len(sentiments),
                            "provider": "finnhub"
                        }

                # No news for this date
                logger.debug(f"Finnhub: No news for {ticker} on {date}")

            elif response.status_code == 429:
                logger.warning("Finnhub rate limit reached (60/minute)")
            elif response.status_code == 401:
                logger.error("Finnhub authentication failed - check API key")
            else:
                logger.warning(f"Finnhub API error: {response.status_code}")

        except Exception as e:
            logger.error(f"Finnhub error for {ticker}: {e}")

        return None


class IEXCloudProvider:
    """
    IEX Cloud - Social sentiment indicators (kept as backup)
    Free tier: 50,000 messages/month
    Provides: Social sentiment scores
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.iex_api_key
        self.base_url = "https://cloud.iexapis.com/stable"

    def get_sentiment(self, ticker: str, date: str = None) -> Optional[float]:
        """
        Get social sentiment from IEX Cloud
        """
        if not self.api_key:
            logger.warning("IEX Cloud API key not configured")
            return None

        try:
            url = f"{self.base_url}/stock/{ticker}/sentiment"
            params = {
                "token": self.api_key,
                "type": "daily"
            }

            if date:
                params["date"] = date.replace("-", "")  # IEX wants YYYYMMDD

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                sentiment = data.get('sentiment', 0)
                positive = data.get('positive', 0)
                negative = data.get('negative', 0)

                # Calculate weighted sentiment
                if positive + negative > 0:
                    sentiment_score = (positive - negative) / (positive + negative)
                    logger.info(f"📊 IEX Cloud: {ticker} - Sentiment: {sentiment_score:.3f}")
                    return sentiment_score

        except Exception as e:
            logger.error(f"IEX Cloud error for {ticker}: {e}")

        return None


class RealHistoricalDataAggregator:
    """
    Aggregates real historical data from multiple sources
    Prioritizes sources based on data availability and reliability
    """

    def __init__(self):
        self.providers = {
            # Removed Alpha Vantage - 25 req/day is too restrictive
            'finnhub': FinnhubProvider(),
            'iex': IEXCloudProvider()
        }
        self.cache = {}
        self.request_count = {
            'finnhub': 0,
            'iex': 0
        }
        # Track when we started counting for rate limiting
        self.rate_limit_window_start = {
            'finnhub': time.time(),
            'iex': time.time()
        }

    def get_historical_sentiment(
        self,
        ticker: str,
        date: str,
        preferred_sources: List[str] = None
    ) -> Optional[float]:
        """
        Get real historical sentiment from available sources

        Args:
            ticker: Stock ticker
            date: Date in YYYY-MM-DD format
            preferred_sources: List of preferred sources to try

        Returns:
            Sentiment score (-1 to 1) or None if no data available
        """
        # Check cache
        cache_key = f"{ticker}_{date}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        if preferred_sources is None:
            # Default priority order
            # Finnhub first (60 req/min, good historical coverage)
            # IEX as backup
            preferred_sources = ['finnhub', 'iex']

        sentiments = []
        sources_used = []

        for source in preferred_sources:
            if source not in self.providers:
                continue

            try:
                sentiment = None

                # Rate limiting with proper time windows
                current_time = time.time()

                if source == 'finnhub':
                    # Finnhub: 60 requests per minute
                    # Check if we need to reset the counter (new minute window)
                    time_elapsed = current_time - self.rate_limit_window_start['finnhub']

                    if time_elapsed >= 60:
                        # New minute window - reset counter
                        self.request_count['finnhub'] = 0
                        self.rate_limit_window_start['finnhub'] = current_time
                        logger.info("🔄 Finnhub rate limit window reset")

                    # Check if we're at the limit for this minute
                    if self.request_count['finnhub'] >= 55:  # Use 55 as buffer
                        time_to_wait = 60 - time_elapsed
                        if time_to_wait > 0:
                            logger.warning(f"⏳ Finnhub rate limit (55/60), sleeping {time_to_wait:.1f}s...")
                            time.sleep(time_to_wait)
                            # Reset after waiting
                            self.request_count['finnhub'] = 0
                            self.rate_limit_window_start['finnhub'] = time.time()

                if source == 'alpha_vantage':
                    result = self.providers['alpha_vantage'].get_sentiment(ticker, date)
                    if result:
                        sentiment = result.get('sentiment')
                        self.request_count['alpha_vantage'] += 1
                elif source == 'finnhub':
                    result = self.providers['finnhub'].get_sentiment(ticker, date)
                    if result:
                        sentiment = result.get('sentiment')
                        self.request_count['finnhub'] += 1
                elif source == 'iex':
                    sentiment = self.providers['iex'].get_sentiment(ticker, date)
                    if sentiment is not None:
                        self.request_count['iex'] += 1

                if sentiment is not None:
                    sentiments.append(sentiment)
                    sources_used.append(source)
                    logger.info(f"✅ {source}: {ticker} on {date} = {sentiment:.3f}")

                # Small delay between requests to avoid hammering APIs
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Error getting sentiment from {source}: {e}")
                continue

        if sentiments:
            # Average all available sentiments
            final_sentiment = sum(sentiments) / len(sentiments)
            self.cache[cache_key] = final_sentiment
            logger.info(f"📊 Aggregated sentiment for {ticker} on {date}: {final_sentiment:.3f} (from {sources_used})")
            return final_sentiment

        logger.warning(f"⚠️ No real historical data available for {ticker} on {date}")
        return None


# Global aggregator instance
real_historical_data = RealHistoricalDataAggregator()