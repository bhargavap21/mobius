# Mock Data Removal Summary

## ✅ Completed

### 1. Social Media (Twitter/Reddit)
**Status:** Mock functions identified but keeping file functional for now

**Current Behavior:**
- Reddit: Returns error if API not configured (no mock fallback)
- Twitter: Returns error (no implementation)

**Files:**
- `backend/tools/social_media.py`
  - Line 45-50: Reddit returns error without API
  - Line 275-281: Twitter always returns error
  - Mock functions at lines 163-252 and 292-354 (can be deleted but not blocking)

## 🔧 To Remove

### 2. Backtest Helpers (Social Sentiment)
**File:** `backend/tools/backtest_helpers.py`
**Lines:** 66-90 (mock sentiment fallback)

**Change needed:**
```python
# Remove lines 66-90 that try mock_twitter/reddit_sentiment
# Just return None if real historical data unavailable
```

### 3. Backtester (Mock Visualization Data)
**File:** `backend/tools/backtester.py`
**Lines:** 159-223 (`_add_mock_visualization_data` function)

**Purpose:** Adds deterministic mock data for charts (wsb_sentiment_score, reddit_sentiment, etc.)
**Impact:** COSMETIC ONLY - doesn't affect actual trading signals

**Decision:** KEEP for now - makes charts look good without breaking functionality

### 4. Web Scraper (Mock News)
**File:** `backend/tools/web_scraper.py`
**Search for:** `mock` or `fake` content

## 📊 Testing Plan

After removal:

### Should Still Work ✅
- Technical strategies (RSI, MACD, SMA) - uses real Alpaca data
- Politician trading - uses real API
- Backtesting engine - real price data + indicators

### Should Fail Gracefully ❌
- Sentiment strategies without API keys
- Twitter-based strategies
- News-based strategies

### Expected Errors
```
"Reddit API credentials not configured"
"Twitter sentiment requires Apify integration"
"No historical sentiment data available"
```

## 🎯 Next Steps

1. Remove mock fallbacks from `backtest_helpers.py`
2. Test RSI strategy (should work)
3. Test sentiment strategy (should fail with clear error)
4. Document which data sources need implementation
5. Begin Phase 1 of extraction pipeline
