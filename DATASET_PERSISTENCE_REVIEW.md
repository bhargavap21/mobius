# Dataset Persistence Plan Review & Recommendations

## ✅ Overall Assessment

**Status: APPROVED with modifications**

The plan is well-structured and addresses a critical performance bottleneck. However, there are several important considerations that need to be addressed before implementation.

---

## 🔴 Critical Issues to Address

### 1. **Bot ID Timing Problem** (HIGH PRIORITY)

**Issue**: The `bot_id` doesn't exist during workflow execution. Bots are created AFTER the workflow completes when the user saves the strategy.

**Current Flow**:
```
Session Created → Workflow Runs → Bot Saved (bot_id created)
```

**Solution Options**:
- **Option A (Recommended)**: Use `session_id` as temporary identifier
  - Store datasets with `session_id` initially (allow NULL `bot_id`)
  - When bot is saved, associate datasets with `bot_id` via `session_id`
  - Update unique constraint to allow NULL `bot_id`
  
- **Option B**: Create a temporary "draft bot" early in workflow
  - More complex, requires cleanup logic for unsaved bots

**Recommended Schema Change**:
```sql
CREATE TABLE trading_datasets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  bot_id UUID REFERENCES trading_bots(id) ON DELETE CASCADE,
  session_id TEXT, -- Temporary identifier during workflow
  ticker VARCHAR(10) NOT NULL,
  data_source VARCHAR(20) NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  data JSONB NOT NULL,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  -- Allow NULL bot_id for draft datasets
  CONSTRAINT unique_dataset UNIQUE(bot_id, ticker, data_source, start_date, end_date),
  CONSTRAINT unique_session_dataset UNIQUE(session_id, ticker, data_source, start_date, end_date)
);
```

### 2. **Async/Sync Mismatch** (HIGH PRIORITY)

**Issue**: `get_social_sentiment_for_date()` is **synchronous**, but `DatasetManager` methods are **async**.

**Current Code**:
```python
# Synchronous function
def get_social_sentiment_for_date(symbol, source, date, cache) -> Optional[float]:
    # Called from synchronous backtest loop
    ...
```

**Solutions**:
- **Option A**: Make `get_social_sentiment_for_date()` async (BREAKING CHANGE)
  - Requires updating all callers
  - Backtester loop becomes async
  
- **Option B**: Use sync wrapper for DatasetManager (RECOMMENDED)
  - Keep DatasetManager async for DB operations
  - Create sync wrapper methods that use `asyncio.run()` or thread pool
  - Less invasive, maintains backward compatibility

**Recommended Approach**:
```python
class DatasetManager:
    async def _get_sentiment_for_date_async(self, ...):
        # Async implementation
        
    def get_sentiment_for_date(self, ...):
        # Sync wrapper
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If already in async context, use thread pool
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._get_sentiment_for_date_async(...))
                    return future.result()
            else:
                return loop.run_until_complete(self._get_sentiment_for_date_async(...))
        except RuntimeError:
            return asyncio.run(self._get_sentiment_for_date_async(...))
```

### 3. **Date Range Determination** (MEDIUM PRIORITY)

**Issue**: Need to know `start_date` and `end_date` before fetching, but these are determined during backtest setup.

**Current Flow**:
- Supervisor determines `days` parameter
- Backtester calculates `start_date = now - days`, `end_date = now`
- But we want to pre-fetch before iterations start

**Solution**:
- Pre-fetch in Supervisor before iterations start
- Use the `days` parameter to calculate date range
- Pass pre-fetched dataset to Backtester

**Implementation**:
```python
# In Supervisor.process()
days = input_data.get('days', default_days)
end_date = datetime.now()
start_date = end_date - timedelta(days=days)

# Pre-fetch datasets for all tickers/data sources needed
if session_id:
    await dataset_manager.pre_fetch_datasets(
        session_id=session_id,
        ticker=ticker,  # Extract from strategy or user_query
        data_source='reddit',
        start_date=start_date,
        end_date=end_date
    )
```

---

## 🟡 Important Considerations

### 4. **Data Storage Granularity**

**Current**: Only sentiment scores are returned
**Question**: Should we store full post data or just sentiment?

**Recommendation**: Store both sentiment AND lightweight metadata:
```json
{
  "2024-01-15": {
    "sentiment": 0.45,
    "post_count": 12,
    "avg_score": 150,
    "sample_posts": [...] // Optional: first 5 posts for debugging
  }
}
```

**Rationale**: 
- Full post data could be huge (60 days × 50 posts × ~1KB = 3MB per dataset)
- Sentiment + metadata is sufficient for backtesting
- Can always fetch full posts later if needed

### 5. **Unique Constraint Logic**

**Issue**: Multiple bots might use same ticker/date range

**Current Constraint**: `UNIQUE(bot_id, ticker, data_source, start_date, end_date)`

**Problem**: If two users create bots for same ticker/date, we'd duplicate data

**Solution**: 
- **Option A**: Share datasets across bots (remove `bot_id` from unique constraint)
  - More efficient storage
  - Datasets become "global" resources
  
- **Option B**: Keep bot-specific datasets
  - Better isolation
  - More storage overhead

**Recommendation**: **Option A** - Share datasets globally, track usage via `bot_id` relationship table if needed.

**Revised Schema**:
```sql
-- Datasets are global, not bot-specific
CONSTRAINT unique_dataset UNIQUE(ticker, data_source, start_date, end_date)

-- Track which bots use which datasets
CREATE TABLE bot_dataset_usage (
  bot_id UUID REFERENCES trading_bots(id) ON DELETE CASCADE,
  dataset_id UUID REFERENCES trading_datasets(id) ON DELETE CASCADE,
  created_at TIMESTAMP DEFAULT NOW(),
  PRIMARY KEY (bot_id, dataset_id)
);
```

### 6. **Pre-fetching Strategy**

**Current Plan**: Pre-fetch before iterations start

**Challenge**: Don't know exact ticker/data sources until strategy is generated

**Solution**: 
- **Iteration 1**: Fetch on-demand, store as we go
- **Iteration 2+**: Use cached data
- **Future**: Pre-fetch common tickers/data sources proactively

**Alternative**: Extract ticker from `user_query` before code generation (if possible)

---

## ✅ Recommended Implementation Order

### Phase 1: Foundation (Week 1)
1. ✅ Create database schema with `session_id` support
2. ✅ Create `DatasetManager` service with sync wrappers
3. ✅ Add `session_id` parameter to Backtester

### Phase 2: Integration (Week 1-2)
4. ✅ Update `get_social_sentiment_for_date()` to check DatasetManager
5. ✅ Modify Backtester to pass `session_id` to helper functions
6. ✅ Update Supervisor to pass `session_id` through workflow

### Phase 3: Association (Week 2)
7. ✅ When bot is saved, associate datasets via `session_id` → `bot_id`
8. ✅ Add cleanup job for orphaned datasets (no bot_id, old session_id)

### Phase 4: Optimization (Week 2-3)
9. ✅ Implement pre-fetching in Supervisor
10. ✅ Add dataset sharing logic (remove bot_id from unique constraint)
11. ✅ Add API endpoints for dataset management

---

## 📝 Code Structure Recommendations

### DatasetManager Interface

```python
class DatasetManager:
    """Manages persistent storage of trading datasets"""
    
    # Sync wrappers for use in synchronous code
    def get_sentiment_for_date(
        self,
        session_id: Optional[str],
        ticker: str,
        data_source: str,
        target_date: date
    ) -> Optional[float]:
        """Sync wrapper - checks DB cache first"""
        
    def store_sentiment_for_date(
        self,
        session_id: Optional[str],
        ticker: str,
        data_source: str,
        date: date,
        sentiment: float,
        metadata: Dict[str, Any]
    ):
        """Sync wrapper - stores sentiment in DB"""
    
    # Async methods for internal use
    async def _get_dataset_async(self, ...):
        """Internal async implementation"""
    
    async def associate_with_bot(self, session_id: str, bot_id: UUID):
        """Associate session datasets with bot when saved"""
```

### Backtester Integration

```python
class Backtester:
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id
        self.dataset_manager = DatasetManager() if session_id else None
        self.social_cache = {}  # Keep for backward compat
```

### Supervisor Integration

```python
# In Supervisor.process()
session_id = input_data.get('session_id')

# Pass session_id to backtester
backtester = Backtester(session_id=session_id)
```

---

## 🎯 Success Metrics

- **Performance**: Iteration 2+ should be < 5 seconds (vs 1-2 minutes currently)
- **Storage**: Datasets should be reusable across bots for same ticker/date range
- **Reliability**: No data loss when workflow fails mid-execution

---

## ⚠️ Potential Risks

1. **Database Size**: Storing datasets could grow quickly
   - **Mitigation**: Add TTL/cleanup for old datasets
   
2. **Race Conditions**: Multiple workflows for same ticker/date
   - **Mitigation**: Use database locks or unique constraint handling

3. **Backward Compatibility**: Existing code expects sync functions
   - **Mitigation**: Use sync wrappers, maintain existing interfaces

---

## ✅ Final Recommendation

**APPROVE** the plan with these modifications:
1. Use `session_id` instead of `bot_id` during workflow
2. Add sync wrappers for DatasetManager
3. Make datasets global (shareable across bots)
4. Store sentiment + metadata (not full posts)
5. Associate datasets with `bot_id` when bot is saved

**Ready to proceed?** Yes, with the above modifications.

