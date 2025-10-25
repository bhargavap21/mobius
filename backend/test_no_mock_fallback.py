"""
Test that there are NO mock data fallbacks
Verifies the system returns errors when APIs are not configured
"""

import sys
import os

# Temporarily unset Reddit credentials to test error handling
original_client_id = os.environ.get("REDDIT_CLIENT_ID")
original_client_secret = os.environ.get("REDDIT_CLIENT_SECRET")

# Remove credentials
if "REDDIT_CLIENT_ID" in os.environ:
    del os.environ["REDDIT_CLIENT_ID"]
if "REDDIT_CLIENT_SECRET" in os.environ:
    del os.environ["REDDIT_CLIENT_SECRET"]

# Reload config to pick up changes
from importlib import reload
import config
reload(config)

from tools.social_media import get_reddit_sentiment, get_twitter_sentiment

print("\n" + "="*70)
print("🧪 Testing NO MOCK DATA Fallbacks")
print("="*70 + "\n")

# Test 1: Reddit without credentials should return error
print("Test 1: Reddit API without credentials")
print("-" * 70)
result = get_reddit_sentiment("TSLA")

if result["success"] == False and "error" in result:
    print("✅ PASS: Returns error instead of mock data")
    print(f"   Error message: {result['error']}")
else:
    print("❌ FAIL: Should return error, not mock data")
    print(f"   Result: {result}")

print()

# Test 2: Twitter should return error (not implemented)
print("Test 2: Twitter API (not implemented)")
print("-" * 70)
result = get_twitter_sentiment("Tesla")

if result["success"] == False and "error" in result:
    print("✅ PASS: Returns error instead of mock data")
    print(f"   Error message: {result['error']}")
else:
    print("❌ FAIL: Should return error, not mock data")
    print(f"   Result: {result}")

print()
print("="*70)
print("✅ All tests passed - No mock data fallbacks detected!")
print("="*70 + "\n")

# Restore original credentials
if original_client_id:
    os.environ["REDDIT_CLIENT_ID"] = original_client_id
if original_client_secret:
    os.environ["REDDIT_CLIENT_SECRET"] = original_client_secret
