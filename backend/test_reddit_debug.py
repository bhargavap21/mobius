#!/usr/bin/env python3
"""
Debug Reddit API connection and post fetching
"""
import praw
from config import settings
from datetime import datetime, timedelta

print("🔍 Testing Reddit API Connection...")
print("=" * 60)

# Check if credentials are set
print(f"Client ID configured: {bool(settings.reddit_client_id)}")
print(f"Client Secret configured: {bool(settings.reddit_client_secret)}")
print(f"User Agent: {settings.reddit_user_agent}")

if not settings.reddit_client_id or not settings.reddit_client_secret:
    print("❌ Reddit credentials not configured!")
    print("Using mock data would be triggered here.")
    exit()

try:
    # Initialize Reddit client
    reddit = praw.Reddit(
        client_id=settings.reddit_client_id,
        client_secret=settings.reddit_client_secret,
        user_agent=settings.reddit_user_agent,
    )

    print(f"\n✅ Reddit client initialized")
    print(f"Read-only mode: {reddit.read_only}")

    # Access subreddit
    subreddit = reddit.subreddit("wallstreetbets")
    print(f"\n📊 Subreddit: r/{subreddit.display_name}")
    print(f"Subscribers: {subreddit.subscribers:,}")

    # Get hot posts
    print("\n🔥 Getting HOT posts...")
    hot_posts = list(subreddit.hot(limit=10))
    print(f"Found {len(hot_posts)} hot posts")

    # Check for GME mentions
    gme_patterns = ["GME", "$GME", "GAMESTOP", "GAME STOP"]
    gme_posts = []

    for post in hot_posts:
        text = f"{post.title} {post.selftext}".upper()
        if any(pattern in text for pattern in gme_patterns):
            gme_posts.append(post)
            print(f"  ✅ GME mentioned: {post.title[:60]}...")

    # Get new posts
    print("\n📰 Getting NEW posts...")
    new_posts = list(subreddit.new(limit=50))
    print(f"Found {len(new_posts)} new posts")

    for post in new_posts:
        text = f"{post.title} {post.selftext}".upper()
        if any(pattern in text for pattern in gme_patterns):
            if post not in gme_posts:
                gme_posts.append(post)
                post_age = datetime.now() - datetime.fromtimestamp(post.created_utc)
                print(f"  ✅ GME mentioned ({post_age.days}d ago): {post.title[:50]}...")

    print(f"\n📈 Total GME mentions found: {len(gme_posts)}")

    # Show details of first few GME posts
    if gme_posts:
        print("\n📝 GME Post Details:")
        for i, post in enumerate(gme_posts[:5], 1):
            post_time = datetime.fromtimestamp(post.created_utc)
            age = datetime.now() - post_time
            print(f"\n{i}. {post.title}")
            print(f"   Posted: {age.days} days, {age.seconds//3600} hours ago")
            print(f"   Score: {post.score}, Comments: {post.num_comments}")
            print(f"   URL: https://reddit.com{post.permalink}")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)