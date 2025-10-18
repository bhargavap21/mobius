#!/usr/bin/env python3
"""
Check what posts are actually being fetched from Reddit
"""
import praw
from config import settings

# Initialize Reddit client
reddit = praw.Reddit(
    client_id=settings.reddit_client_id,
    client_secret=settings.reddit_client_secret,
    user_agent=settings.reddit_user_agent,
)

subreddit = reddit.subreddit("wallstreetbets")

print("🔥 First 20 HOT posts on r/wallstreetbets:")
print("=" * 80)

for i, post in enumerate(subreddit.hot(limit=20), 1):
    print(f"{i:2}. [{post.score:6}] {post.title[:70]}")

    # Check for GME mentions
    if "GME" in post.title.upper() or "$GME" in post.title.upper():
        print(f"    ^^^ GME MENTIONED! ^^^")

print("\n📰 First 20 NEW posts on r/wallstreetbets:")
print("=" * 80)

for i, post in enumerate(subreddit.new(limit=20), 1):
    print(f"{i:2}. [{post.score:6}] {post.title[:70]}")

    # Check for GME mentions
    if "GME" in post.title.upper() or "$GME" in post.title.upper():
        print(f"    ^^^ GME MENTIONED! ^^^")