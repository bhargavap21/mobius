# Dataset Persistence Implementation Plan

## Current Implementation Problems

### 1. Reddit Data Fetching (backtest_helpers.py:140-174)
- For EACH backtest run, it searches Reddit day-by-day
- For a 60-day backtest, it makes 60+ API calls to Reddit
- Each iteration re-fetches the same data again
- Only has in-memory cache (`self.social_cache`) that's lost between runs

### 2. Current Flow
```
User creates strategy → Iteration 1 (fetch 60 days of Reddit data)
                     → Iteration 2 (RE-FETCH same 60 days)
                     → Future backtests (RE-FETCH AGAIN)
```

### 3. Cache is Temporary
- `cache: Dict[str, Any]` in `get_social_sentiment_for_date()` is only in-memory
- Cache is per-Backtester instance, lost when process ends
- No persistence to database or disk

---

## Implementation Plan: Dataset Persistence System

### Architecture

```
┌─────────────────┐
│  Strategy Bot   │
├─────────────────┤
│ - bot_id        │
│ - strategy_desc │
│ - ticker        │
└────────┬────────┘
         │
         │ has many
         ▼
┌─────────────────────────┐
│  Dataset (Supabase)     │
├─────────────────────────┤
│ - id                    │
│ - bot_id (FK)           │
│ - ticker                │
│ - data_source (reddit)  │
│ - start_date            │
│ - end_date              │
│ - data (JSONB)          │
│ - created_at            │
│ - updated_at            │
└─────────────────────────┘
```

### Phase 1: Database Schema (Supabase)

Create new table `trading_datasets`:

```sql
CREATE TABLE trading_datasets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  bot_id UUID REFERENCES trading_bots(id) ON DELETE CASCADE,
  ticker VARCHAR(10) NOT NULL,
  data_source VARCHAR(20) NOT NULL, -- 'reddit', 'twitter', 'news'
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  data JSONB NOT NULL, -- {date: {sentiment: 0.5, posts: [...]}}
  metadata JSONB, -- {total_posts: 150, avg_sentiment: 0.3}
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  -- Index for fast lookups
  CONSTRAINT unique_dataset UNIQUE(bot_id, ticker, data_source, start_date, end_date)
);

CREATE INDEX idx_datasets_bot ON trading_datasets(bot_id);
CREATE INDEX idx_datasets_ticker_source ON trading_datasets(ticker, data_source);
CREATE INDEX idx_datasets_dates ON trading_datasets(start_date, end_date);
```

### Phase 2: Dataset Manager Service

Create `backend/services/dataset_manager.py`:

```python
class DatasetManager:
    """Manages persistent storage of trading datasets"""

    async def get_or_create_dataset(
        self,
        bot_id: str,
        ticker: str,
        data_source: str,  # 'reddit', 'twitter', 'news'
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        1. Check if dataset exists in database
        2. If yes, return cached data
        3. If no, fetch from API and store
        """

    async def fetch_and_store_reddit_data(
        self,
        ticker: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Fetch Reddit data and store in database"""

    async def get_sentiment_for_date(
        self,
        bot_id: str,
        ticker: str,
        data_source: str,
        target_date: date
    ) -> Optional[float]:
        """
        Get sentiment for specific date from cached dataset
        No API call needed if dataset exists
        """
```

### Phase 3: Integration Points

#### 3.1. Modify Backtester (`tools/backtester.py`)

```python
class Backtester:
    def __init__(self, bot_id: Optional[str] = None):
        self.bot_id = bot_id
        self.dataset_manager = DatasetManager() if bot_id else None
        self.social_cache = {}  # Keep for backward compat
```

#### 3.2. Modify Supervisor (`agents/supervisor.py`)
- Pass `bot_id` to backtester
- Pre-fetch datasets ONCE before iterations start
- Share dataset across all iterations

#### 3.3. Update `get_social_sentiment_for_date()`

```python
def get_social_sentiment_for_date(..., bot_id: Optional[str] = None):
    # Priority 1: Check database if bot_id provided
    if bot_id and dataset_manager:
        cached = await dataset_manager.get_sentiment_for_date(...)
        if cached is not None:
            return cached

    # Priority 2: Check in-memory cache
    if cache_key in cache:
        return cache[cache_key]

    # Priority 3: Fetch from API and store
    sentiment = fetch_from_reddit(...)
    if bot_id:
        await dataset_manager.store_datapoint(...)
    cache[cache_key] = sentiment
    return sentiment
```

### Phase 4: Benefits

#### Immediate
- ✅ Fetch Reddit data ONCE per ticker/date range
- ✅ Reuse across iterations (Iteration 1 fetches, Iteration 2 reuses)
- ✅ Reuse across future backtests of same bot
- ✅ Dramatically faster iteration times (no Reddit API calls after first)

#### Long-term
- ✅ Historical dataset library grows over time
- ✅ Can share datasets between similar bots
- ✅ Can export datasets for analysis
- ✅ Can pre-warm cache for popular tickers
- ✅ Audit trail of what data was used for each strategy

### Phase 5: Implementation Steps

1. **Create Supabase migration** for `trading_datasets` table
2. **Create `DatasetManager` service** in `backend/services/`
3. **Update `Backtester`** to accept `bot_id` and use DatasetManager
4. **Update `Supervisor`** to pass `bot_id` through workflow
5. **Update `get_social_sentiment_for_date()`** to check database first
6. **Add API endpoints** to view/manage datasets (optional)
7. **Test** with Reddit strategy end-to-end

---

## Implementation Priority

### High Priority (P0)
- Database schema creation
- DatasetManager basic implementation
- Integration with backtester for Reddit data

### Medium Priority (P1)
- Extend to Twitter/news data sources
- API endpoints for dataset management
- Dataset cleanup/expiration policies

### Low Priority (P2)
- Dataset sharing between users
- Pre-warming popular ticker datasets
- Advanced analytics on dataset usage

## Performance Estimates

### Before Implementation
- First backtest: ~60 Reddit API calls (1-2 minutes)
- Iteration 2: ~60 Reddit API calls again (1-2 minutes)
- Total for 2 iterations: ~120 API calls (~2-4 minutes)

### After Implementation
- First backtest: ~60 Reddit API calls (1-2 minutes) + DB write
- Iteration 2: ~60 DB reads (< 1 second)
- Total for 2 iterations: ~60 API calls + DB operations (~1-2 minutes)
- **~50% time savings**

### Future Runs (Same Ticker/Dates)
- All data from DB cache (< 1 second)
- **~99% time savings**
