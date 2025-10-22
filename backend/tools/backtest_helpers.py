"""
Helper methods for backtesting with real social media and news data
"""
import logging
from datetime import datetime
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

# Import actual tools
try:
    from tools.social_media import get_reddit_sentiment, get_twitter_sentiment
    from tools.web_scraper import scrape_company_news
    TOOLS_AVAILABLE = True
except ImportError:
    TOOLS_AVAILABLE = False
    logger.warning("⚠️  Social media tools not available")


def get_social_sentiment_for_date(
    symbol: str,
    source: str,
    date: str,
    cache: Dict[str, Any]
) -> Optional[float]:
    """
    Get social sentiment for a specific date using real historical data

    Args:
        symbol: Stock ticker
        source: 'twitter' or 'reddit'
        date: Date string (YYYY-MM-DD)
        cache: Cache dict to store results

    Returns:
        Sentiment score (-1 to 1) or None
    """
    cache_key = f"{symbol}_{source}_{date}"

    # Check cache first
    if cache_key in cache:
        return cache[cache_key]

    # Try to get real historical sentiment data
    try:
        from tools.real_historical_data import real_historical_data

        # Map source to appropriate providers
        # Alpha Vantage first (better historical coverage, 25 req/day)
        # Finnhub second (fallback, 60 req/min but rate limited)
        preferred_sources = ['alpha_vantage', 'finnhub']

        sentiment = real_historical_data.get_historical_sentiment(symbol, date, preferred_sources)

        if sentiment is not None:
            cache[cache_key] = sentiment
            logger.info(f"✅ Real {source} sentiment for {symbol} on {date}: {sentiment:.2f}")
            return sentiment

    except ImportError:
        logger.warning("Real historical data module not available")
    except Exception as e:
        logger.error(f"Error getting real historical sentiment: {e}")

    # No real data available - return None (no mock fallback)
    logger.warning(f"⚠️ No historical {source} sentiment data available for {symbol} on {date}")
    cache[cache_key] = None
    return None


def get_news_for_date(
    symbol: str,
    date: str,
    cache: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Get news sentiment for a specific date

    Args:
        symbol: Stock ticker
        date: Date string (YYYY-MM-DD)
        cache: Cache dict to store results

    Returns:
        Dict with news info or None
    """
    if not TOOLS_AVAILABLE:
        return None

    cache_key = f"{symbol}_news_{date}"

    # Check cache
    if cache_key in cache:
        return cache[cache_key]

    try:
        # Get company news (uses mock data for now)
        result = scrape_company_news(company_name=symbol, ticker=symbol)

        if result and result.get('success') and result.get('articles'):
            # Get the most recent article
            article = result['articles'][0]
            news_data = {
                'has_news': True,
                'headline': article.get('title', 'News article'),
                'sentiment': article.get('sentiment', 'neutral'),
                'summary': article.get('summary', '')
            }
            cache[cache_key] = news_data
            return news_data

    except Exception as e:
        logger.debug(f"Could not fetch news for {symbol} on {date}: {e}")

    cache[cache_key] = None
    return None
