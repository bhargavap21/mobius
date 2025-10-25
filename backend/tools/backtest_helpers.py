"""
Helper methods for backtesting with real social media and news data
"""
import logging
from datetime import datetime
from typing import Dict, Optional, Any, List

logger = logging.getLogger(__name__)

# Import actual tools
try:
    from tools.social_media import get_reddit_sentiment, get_twitter_sentiment
    from tools.web_scraper import scrape_company_news
    TOOLS_AVAILABLE = True
except ImportError:
    TOOLS_AVAILABLE = False
    logger.warning("⚠️  Social media tools not available")

# Ticker to company name and alternative terms mapping
# This helps find posts that mention the company but not the ticker
TICKER_ALTERNATIVES = {
    # Meme stocks
    "GME": ["GameStop", "Gamestop", "game stop"],
    "AMC": ["AMC Entertainment", "AMC Theatres", "AMC theaters"],
    "BBBY": ["Bed Bath & Beyond", "Bed Bath and Beyond", "BBBY"],
    "BB": ["BlackBerry"],

    # Alternative meat/food
    "BYND": ["Beyond Meat", "beyond meat", "fake meat", "plant based meat", "impossible competitor"],

    # EV/Tech
    "TSLA": ["Tesla", "Elon", "Musk"],
    "RIVN": ["Rivian"],
    "LCID": ["Lucid", "Lucid Motors"],
    "NIO": ["Nio"],

    # Tech giants
    "AAPL": ["Apple", "iPhone", "Tim Cook"],
    "MSFT": ["Microsoft"],
    "GOOGL": ["Google", "Alphabet"],
    "META": ["Meta", "Facebook", "Zuckerberg"],
    "AMZN": ["Amazon", "Bezos"],
    "NVDA": ["Nvidia", "Jensen Huang"],
    "AMD": ["AMD", "Lisa Su"],

    # Finance
    "JPM": ["JPMorgan", "JP Morgan", "Jamie Dimon"],
    "BAC": ["Bank of America", "BofA"],
    "GS": ["Goldman Sachs", "Goldman"],
    "MS": ["Morgan Stanley"],

    # Retail/Consumer
    "WMT": ["Walmart", "Wal-Mart"],
    "TGT": ["Target"],
    "COST": ["Costco"],
    "HD": ["Home Depot"],

    # Airlines
    "AAL": ["American Airlines"],
    "DAL": ["Delta", "Delta Airlines"],
    "UAL": ["United Airlines"],
    "LUV": ["Southwest", "Southwest Airlines"],

    # Entertainment/Media
    "DIS": ["Disney", "Mickey Mouse"],
    "NFLX": ["Netflix"],
    "SPOT": ["Spotify"],

    # AI/Crypto related
    "COIN": ["Coinbase"],
    "MSTR": ["MicroStrategy", "Saylor"],
    "AI": ["C3.ai", "C3 AI"],
    "PLTR": ["Palantir"],
}

def get_search_terms(ticker: str) -> List[str]:
    """
    Get all search terms for a ticker including alternatives

    Args:
        ticker: Stock ticker symbol

    Returns:
        List of search terms including ticker and company names
    """
    terms = [ticker, f"${ticker}"]

    # Add company name alternatives if available
    if ticker in TICKER_ALTERNATIVES:
        terms.extend(TICKER_ALTERNATIVES[ticker])

    return terms


def get_social_sentiment_for_date(
    symbol: str,
    source: str,
    date: str,
    cache: Dict[str, Any]
) -> Optional[float]:
    """
    Get social sentiment for a specific date using real historical data

    IMPORTANT: Respects the source parameter - if user asks for 'reddit',
    we ONLY try Reddit API. No silent fallback to news APIs.

    Args:
        symbol: Stock ticker
        source: 'twitter', 'reddit', or 'news'
        date: Date string (YYYY-MM-DD)
        cache: Cache dict to store results

    Returns:
        Sentiment score (-1 to 1) or None
    """
    cache_key = f"{symbol}_{source}_{date}"

    # Check cache first
    if cache_key in cache:
        return cache[cache_key]

    # Route to specific source handler - NO FALLBACKS
    if source == 'reddit':
        # User specifically asked for Reddit - only try Reddit API
        try:
            from tools.api_handlers.reddit_handler import RedditHandler

            handler = RedditHandler()
            if not handler.initialized:
                logger.warning(f"⚠️ Reddit API not configured - cannot get Reddit sentiment for {symbol} on {date}")
                cache[cache_key] = None
                return None

            # Call synchronous Reddit search (no async needed)
            # Use PRAW's synchronous API directly
            import praw
            from datetime import datetime as dt, timedelta
            from tools.finbert_sentiment import get_finbert_sentiments_batch

            reddit = praw.Reddit(
                client_id=handler.reddit.config.client_id,
                client_secret=handler.reddit.config.client_secret,
                user_agent="TradingBotPlatform/1.0"
            )

            # Parse date
            target_date = dt.strptime(date, "%Y-%m-%d")

            # Get all search terms (ticker + company names + alternatives)
            search_terms = get_search_terms(symbol)
            logger.info(f"🔍 Searching for {symbol} using terms: {search_terms[:5]}{'...' if len(search_terms) > 5 else ''}")

            # Search Reddit for posts
            subreddit = reddit.subreddit("wallstreetbets")
            posts_found = []
            seen_post_ids = set()  # Track post IDs to prevent duplicates

            # Strategy 1: Search for posts with ticker AND company name alternatives in title/body
            # Reddit search works better with separate queries than complex OR queries
            # Do multiple searches with deduplication

            # Search 1: Ticker symbols (most reliable)
            try:
                for post in subreddit.search(f"{symbol} OR ${symbol}", time_filter="all", limit=100):
                    post_date = dt.fromtimestamp(post.created_utc)
                    if abs((post_date - target_date).days) <= 1:
                        if post.id not in seen_post_ids:
                            posts_found.append(post)
                            seen_post_ids.add(post.id)
                    if len(posts_found) >= 50:
                        break
            except Exception as e:
                logger.debug(f"Ticker search error: {e}")

            # Search 2: Company name (if we have alternatives and still need more posts)
            if len(posts_found) < 50 and symbol in TICKER_ALTERNATIVES:
                company_name = TICKER_ALTERNATIVES[symbol][0]  # First alternative is usually company name
                try:
                    for post in subreddit.search(f'"{company_name}"', time_filter="all", limit=50):
                        post_date = dt.fromtimestamp(post.created_utc)
                        if abs((post_date - target_date).days) <= 1:
                            if post.id not in seen_post_ids:
                                posts_found.append(post)
                                seen_post_ids.add(post.id)
                                logger.info(f"📝 Found {symbol} via company name search: '{post.title[:50]}...'")
                        if len(posts_found) >= 50:
                            break
                except Exception as e:
                    logger.debug(f"Company name search error: {e}")

            # Strategy 2: Also check recent hot/new posts for ticker mentions in comments
            # This catches image posts or posts where ticker is only in comments
            all_recent_posts = []
            try:
                # Get posts from the target date range
                for post in subreddit.new(limit=100):
                    post_date = dt.fromtimestamp(post.created_utc)
                    if abs((post_date - target_date).days) <= 1:
                        all_recent_posts.append(post)
                    if len(all_recent_posts) >= 30:  # Limit to 30 posts to check
                        break
            except Exception as e:
                logger.debug(f"Could not fetch new posts: {e}")

            # Check comments for ticker mentions using alternative terms (skip duplicates)
            for post in all_recent_posts:
                # Skip if already found via search (O(1) lookup with set)
                if post.id in seen_post_ids:
                    continue

                # Check if ticker OR company name appears in comments
                ticker_in_comments = False
                try:
                    post.comments.replace_more(limit=0)  # Don't expand "load more comments"
                    for comment in post.comments.list()[:20]:  # Check first 20 comments
                        comment_upper = comment.body.upper()
                        # Check ticker and all alternative terms
                        for term in search_terms:
                            if term.upper() in comment_upper:
                                ticker_in_comments = True
                                break
                        if ticker_in_comments:
                            break
                except Exception as e:
                    logger.debug(f"Error checking comments for post {post.id}: {e}")

                if ticker_in_comments:
                    posts_found.append(post)
                    seen_post_ids.add(post.id)  # Mark as seen
                    logger.info(f"📝 Found {symbol} via comments in post: '{post.title[:50]}...'")

                if len(posts_found) >= 50:
                    break

            if not posts_found:
                logger.warning(f"⚠️ No Reddit posts found for {symbol} on {date}")
                cache[cache_key] = None
                return None

            # Calculate sentiment from posts AND their comments using FinBERT
            # Use weighted average based on post score (upvotes)
            import math

            # First, collect all texts and weights
            texts = []
            weights = []

            for post in posts_found:
                # Include post title and body
                text = f"{post.title} {post.selftext}"

                # Also include sentiment from comments mentioning the ticker OR company name
                try:
                    post.comments.replace_more(limit=0)
                    for comment in post.comments.list()[:20]:
                        comment_upper = comment.body.upper()
                        # Check if any search term appears in comment
                        for term in search_terms:
                            if term.upper() in comment_upper:
                                text += f" {comment.body}"
                                break  # Only add comment once even if multiple terms match
                except Exception as e:
                    logger.debug(f"Error processing comments: {e}")

                texts.append(text)

                # Weight by post score (upvotes), with minimum weight of 1
                # Use log scale to prevent viral posts from dominating
                post_score = max(post.score, 1)  # Ensure at least 1
                weight = math.log10(post_score + 10)  # Log scale, +10 to handle negatives
                weights.append(weight)

            # Use FinBERT for batch sentiment analysis (more efficient than one-by-one)
            logger.info(f"📊 Analyzing {len(texts)} posts with FinBERT...")
            sentiments = get_finbert_sentiments_batch(texts)

            # Weighted average
            total_weight = sum(weights)
            if total_weight > 0:
                sentiment = round(sum(s * w for s, w in zip(sentiments, weights)) / total_weight, 3)
            else:
                sentiment = round(sum(sentiments) / len(sentiments), 3)  # Fallback to simple average
            cache[cache_key] = sentiment
            logger.info(f"✅ Real Reddit sentiment for {symbol} on {date}: {sentiment:.2f} ({len(posts_found)} posts)")
            return sentiment

        except Exception as e:
            logger.error(f"❌ Error getting Reddit sentiment: {e}")
            cache[cache_key] = None
            return None

    elif source == 'twitter':
        # User specifically asked for Twitter - only try Twitter (Apify in future)
        logger.warning(f"⚠️ Twitter historical data not yet implemented (requires Apify)")
        cache[cache_key] = None
        return None

    elif source == 'news':
        # User asked for news sentiment - try Alpha Vantage / Finnhub
        try:
            from tools.real_historical_data import real_historical_data

            preferred_sources = ['alpha_vantage', 'finnhub']
            sentiment = real_historical_data.get_historical_sentiment(symbol, date, preferred_sources)

            if sentiment is not None:
                cache[cache_key] = sentiment
                logger.info(f"✅ Real news sentiment for {symbol} on {date}: {sentiment:.2f}")
                return sentiment

        except ImportError:
            logger.warning("Real historical data module not available")
        except Exception as e:
            logger.error(f"Error getting news sentiment: {e}")

        logger.warning(f"⚠️ No news sentiment available for {symbol} on {date}")
        cache[cache_key] = None
        return None

    else:
        logger.error(f"Unknown sentiment source: {source}")
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
