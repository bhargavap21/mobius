# Performance Optimization Plan - Reddit Sentiment Backtesting

## Current Performance
- **Total Runtime:** ~3-5 minutes for 90-day backtest
- **Breakdown:**
  - FinBERT Model Loading: ~5-10 seconds (first time only)
  - Reddit API Calls: ~60-90 seconds (90 days × ~1 second per date)
  - FinBERT Sentiment Analysis: ~60-120 seconds
  - Price Data & Backtest Execution: ~10-20 seconds

---

## 🚀 Optimization Strategies (Ranked by Impact)

### **Phase 1: Quick Wins (30 min implementation, 50% speedup)**

#### 1. Cache Reddit Searches Across Dates ⭐ BIGGEST WIN
**Current Issue:** Searching the same ticker multiple times for overlapping date ranges
- Searching Oct 22 with ±1 day tolerance fetches Oct 21-23 posts
- Then searching Oct 23 re-fetches Oct 22-24 posts (duplicates!)

**Solution:**
```python
# Cache search results at the search level, not just sentiment level
search_cache = {}  # Cache actual posts, not just sentiment
```

**Expected Speedup:** **40-50% faster** (3-5 min → 1.5-2.5 min)

---

#### 2. Skip FinBERT When No Posts Found
**Current:** Loading and calling FinBERT even when no posts exist

**Solution:**
```python
if not posts_found:
    return None  # Skip FinBERT entirely
```

**Expected Speedup:** **10-15% faster** for stocks with sparse data

---

#### 3. Increase FinBERT Batch Size
**Current:** Processing posts in small batches

**Solution:**
```python
# Instead of batch size ~10-20
# Use batch size 50-100 (limited by memory)
sentiments = get_finbert_sentiments_batch(texts, batch_size=50)
```

**Expected Speedup:** **20-30% faster FinBERT**

**Phase 1 Expected Result:** 3-5 min → **1.5-2.5 min**

---

### **Phase 2: Medium Effort (2 hours, additional 40% speedup)**

#### 4. Reduce Reddit API Calls with Smarter Date Batching
**Current:** Making 3 searches per date:
- Ticker search
- Company name search
- Recent posts for comments

**Optimization:**
```python
# Batch fetch posts for entire week, then filter by date
# Instead of: 7 days × 3 searches = 21 API calls
# Do: 1 search for week × 3 types = 3 API calls
```

**Expected Speedup:** **50-60% fewer API calls**

---

#### 5. Parallel Reddit API Calls
**Current:** Sequential API calls

**Solution:**
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(search_reddit, date) for date in dates]
    results = [f.result() for f in futures]
```

**Expected Speedup:** **3-4x faster Reddit fetching** (watch rate limits!)

**Phase 2 Expected Result:** 1.5-2.5 min → **1-1.5 min**

---

### **Phase 3: Advanced Optimizations (if needed)**

#### 6. GPU Acceleration for FinBERT
**Current:** CPU-based inference

**Check if GPU available:**
```python
import torch
if torch.cuda.is_available():
    model.to('cuda')  # 5-10x faster
```

**Expected Speedup:** **70-80% faster FinBERT** if GPU available

---

#### 7. Persistent Model in Memory
**Current:** Model loaded per request

**Solution:**
- Keep FinBERT model in memory across requests
- Use global singleton pattern (already implemented)

**Expected Speedup:** **5-10 seconds saved** on subsequent backtests

**Phase 3 Expected Result:** 1-1.5 min → **30-60 seconds**

---

## ⚖️ Accuracy vs Speed Tradeoff

### Things to AVOID (hurt accuracy)
- ❌ Reducing number of posts analyzed
- ❌ Simplifying to TextBlob (75% faster but much less accurate)
- ❌ Skipping comment checking
- ❌ Reducing search terms
- ❌ Lowering sentiment analysis quality

### Safe Optimizations (no accuracy loss)
- ✅ Caching
- ✅ Parallelization
- ✅ Batch processing
- ✅ GPU acceleration
- ✅ Smarter API call patterns

---

## Implementation Priority

1. **Phase 1 - Do First** (Highest ROI)
   - Cache search results across dates
   - Skip FinBERT when no posts
   - Increase batch size

2. **Phase 2 - Do Second** (Medium ROI)
   - Date batching for API calls
   - Parallel API calls with rate limiting

3. **Phase 3 - Optional** (Hardware dependent)
   - GPU acceleration
   - Memory optimizations

---

## Benchmarking Plan

After each phase, measure:
- Total backtest time
- Reddit API call count
- FinBERT inference time
- Memory usage
- Accuracy metrics (compare results before/after)

---

## Current Bottlenecks (in order)

1. **Reddit API Calls** (40% of time) → Cache + Parallelize
2. **FinBERT Inference** (35% of time) → Batch size + GPU
3. **Comment Processing** (15% of time) → Optimize iteration
4. **Model Loading** (10% of time) → Persistent memory

---

## Notes

- Current 3-5 minute runtime is acceptable for development
- Target < 1 minute for production use
- Maintain FinBERT accuracy (crucial for trading decisions)
- Monitor Reddit API rate limits (60 requests/minute)
