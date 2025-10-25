"""
Isolated test to check if GME posts exist on r/wallstreetbets
Tests the actual Reddit API to see what data is available
"""

import praw
from datetime import datetime, timedelta
from config import settings

print("\n" + "="*70)
print("🔍 Checking for GME posts on r/wallstreetbets")
print("="*70 + "\n")

# Initialize Reddit
reddit = praw.Reddit(
    client_id=settings.reddit_client_id,
    client_secret=settings.reddit_client_secret,
    user_agent="TradingBotPlatform/1.0"
)

print("✅ Reddit API initialized\n")

subreddit = reddit.subreddit("wallstreetbets")

# Test 1: Search for GME posts (any time)
print("Test 1: Searching for 'GME' posts (all time, limit 50)")
print("-" * 70)

posts_found = []
for post in subreddit.search("GME", time_filter="all", limit=50):
    post_date = datetime.fromtimestamp(post.created_utc)
    posts_found.append({
        "title": post.title,
        "score": post.score,
        "date": post_date,
        "url": f"https://reddit.com{post.permalink}"
    })

if posts_found:
    print(f"✅ Found {len(posts_found)} posts mentioning 'GME'\n")
    print("Most recent 10 posts:")
    for i, post in enumerate(sorted(posts_found, key=lambda x: x['date'], reverse=True)[:10], 1):
        print(f"{i}. [{post['score']}⬆] {post['title'][:60]}")
        print(f"   Date: {post['date'].strftime('%Y-%m-%d %H:%M:%S')}")
else:
    print("❌ No posts found for 'GME'\n")

# Test 2: Check recent hot posts in wallstreetbets
print("\n" + "-" * 70)
print("Test 2: Checking recent HOT posts on r/wallstreetbets")
print("-" * 70)

hot_posts = []
for post in subreddit.hot(limit=25):
    post_date = datetime.fromtimestamp(post.created_utc)
    hot_posts.append({
        "title": post.title,
        "score": post.score,
        "date": post_date,
        "has_gme": "GME" in post.title.upper() or "GAMESTOP" in post.title.upper()
    })

print(f"\nFound {len(hot_posts)} hot posts")
gme_in_hot = [p for p in hot_posts if p['has_gme']]
print(f"Posts mentioning GME/GameStop: {len(gme_in_hot)}")

if gme_in_hot:
    print("\nGME posts in hot:")
    for post in gme_in_hot:
        print(f"  - [{post['score']}⬆] {post['title']}")
        print(f"    Date: {post['date'].strftime('%Y-%m-%d %H:%M:%S')}")

# Test 3: Check what dates the found posts are from
if posts_found:
    print("\n" + "-" * 70)
    print("Test 3: Date distribution of GME posts")
    print("-" * 70)

    dates = [p['date'] for p in posts_found]
    oldest = min(dates)
    newest = max(dates)

    print(f"Oldest post: {oldest.strftime('%Y-%m-%d')}")
    print(f"Newest post: {newest.strftime('%Y-%m-%d')}")
    print(f"Date range: {(newest - oldest).days} days")

    # Check how many in last 6 months
    six_months_ago = datetime.now() - timedelta(days=180)
    recent_posts = [p for p in posts_found if p['date'] >= six_months_ago]
    print(f"\nPosts in last 6 months (since {six_months_ago.strftime('%Y-%m-%d')}): {len(recent_posts)}")

    if recent_posts:
        print("\nRecent GME posts:")
        for post in sorted(recent_posts, key=lambda x: x['date'], reverse=True)[:5]:
            print(f"  - {post['date'].strftime('%Y-%m-%d')}: {post['title'][:50]}")

# Test 4: Try different search terms
print("\n" + "-" * 70)
print("Test 4: Trying alternative search terms")
print("-" * 70)

search_terms = ["GameStop", "$GME", "GME stock", "gme"]
for term in search_terms:
    count = 0
    for _ in subreddit.search(term, time_filter="month", limit=10):
        count += 1
    print(f"  '{term}' (last month): {count} posts")

print("\n" + "="*70)
print("✅ Test Complete")
print("="*70 + "\n")
