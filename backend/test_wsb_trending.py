"""
Check what stocks are actually trending on r/wallstreetbets RIGHT NOW
"""

import praw
from datetime import datetime
from collections import Counter
import re
from config import settings

print("\n" + "="*70)
print("📊 What's ACTUALLY trending on r/wallstreetbets?")
print("="*70 + "\n")

reddit = praw.Reddit(
    client_id=settings.reddit_client_id,
    client_secret=settings.reddit_client_secret,
    user_agent="TradingBotPlatform/1.0"
)

subreddit = reddit.subreddit("wallstreetbets")

# Pattern to find stock tickers (1-5 uppercase letters)
ticker_pattern = r'\b[A-Z]{1,5}\b'

# Common words to exclude
exclude = {"A", "I", "CEO", "IPO", "ETF", "DD", "YOLO", "WSB", "GME", "THE", "AND", "FOR",
           "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HER", "WAS", "ONE", "OUR", "OUT",
           "DAY", "GET", "HAS", "HIM", "HIS", "HOW", "ITS", "MAY", "NEW", "NOW", "OLD",
           "SEE", "TWO", "WHO", "BOY", "DID", "ILL", "OFF", "OWN", "SAY", "SHE", "TOO",
           "USE", "GOT", "PUT", "ATM", "ITM", "OTM", "RIP", "LOL", "IMO", "FYI", "FOMO",
           "MOON", "BULL", "BEAR", "LONG", "PUTS", "CALL", "BUY", "SELL", "HOLD", "HODL"}

tickers = Counter()

print("Analyzing last 100 HOT posts...\n")

for post in subreddit.hot(limit=100):
    title = post.title
    found = re.findall(ticker_pattern, title)
    for ticker in found:
        if ticker not in exclude and len(ticker) >= 2:
            tickers[ticker] += 1

print("🔥 Top 20 Most Mentioned Tickers:")
print("-" * 70)

for i, (ticker, count) in enumerate(tickers.most_common(20), 1):
    print(f"{i:2}. ${ticker:6} - {count:3} mentions")

print("\n" + "="*70)

# Now check posts for top 3 tickers
print("\n📰 Sample posts for top 3 tickers:\n")

for ticker, count in tickers.most_common(3):
    print(f"\n{ticker} ({count} mentions):")
    print("-" * 70)

    found_count = 0
    for post in subreddit.search(ticker, time_filter="week", limit=5):
        found_count += 1
        post_date = datetime.fromtimestamp(post.created_utc)
        print(f"  [{post.score}⬆] {post.title[:60]}")
        print(f"  Date: {post_date.strftime('%Y-%m-%d')}")

    if found_count == 0:
        print("  (No recent posts found in search)")

print("\n" + "="*70)
print("💡 Recommendation: Use one of the trending tickers for your backtest!")
print("="*70 + "\n")
