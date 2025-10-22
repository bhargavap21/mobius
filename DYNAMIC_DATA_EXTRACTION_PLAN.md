# Self-Learning Trading Agent: Dynamic Data Extraction Implementation Plan

## Executive Summary

Transform the existing Mobius trading bot platform into a truly autonomous system that can extract data from ANY source, analyze it, and generate trading signals. Users can request strategies like "trade Tesla on Elon's tweets" and the system automatically figures out how to get that data, backtest it, and deploy it.

**Timeline:** 10 weeks
**Estimated Hours:** 320-400 hours
**Key Innovation:** Multi-tier data extraction with intelligent fallback strategy

---

## Table of Contents
1. [Current State Analysis](#current-state-analysis)
2. [Architecture Overview](#architecture-overview)
3. [Implementation Phases](#implementation-phases)
4. [Code Structure](#code-structure)
5. [Database Schema](#database-schema)
6. [Key Components](#key-components)
7. [Agent Prompts](#agent-prompts)
8. [Testing Strategy](#testing-strategy)
9. [Deployment Plan](#deployment-plan)
10. [Cost Analysis](#cost-analysis)

---

## Current State Analysis

### ✅ What Already Works (Keep & Enhance)
```
backend/agents/
├── supervisor.py              # Multi-agent orchestration ✓
├── code_generator.py          # Strategy parsing ✓
├── backtest_runner.py         # Backtesting engine ✓
├── strategy_analyst.py        # Performance analysis ✓
├── intelligent_orchestrator.py # Data-driven optimization ✓
└── insights_generator.py      # Visualization config ✓

backend/tools/
├── backtester.py              # Execution engine ✓
├── code_generator.py          # Strategy code generation ✓
└── politician_trades.py       # Example alt data source ✓

frontend/
└── [React app]                # UI working well ✓
```

### ❌ What Needs Major Enhancement
```
backend/tools/
├── social_media.py            # Currently mock/limited ✗
├── web_scraper.py             # Too simple, needs multi-tier ✗
└── backtest_helpers.py        # Mock sentiment data ✗

Missing:
├── data_source_router.py      # NEW - Intelligent routing
├── extraction_orchestrator.py # NEW - Job management
├── scraper_generator.py       # NEW - Dynamic scraper creation
├── data_pipeline.py           # NEW - Processing & cleaning
└── sentiment_analyzer.py      # NEW - Advanced sentiment
```

### 🔧 Integration Points
The existing multi-agent system is well-designed. New data extraction components will:
1. **Plug into** existing `backtest_runner.py` via enhanced data fetching
2. **Enhance** `intelligent_orchestrator.py` with real data instead of mocks
3. **Preserve** current user experience (natural language input)
4. **Add** new data source options without breaking existing strategies

---

## Architecture Overview

### Multi-Tier Data Extraction Strategy

```
┌─────────────────────────────────────────────────────────┐
│                    USER INPUT                           │
│  "Trade Tesla on Elon's tweets and WSB sentiment"       │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│            🧠 DATA SOURCE ROUTER AGENT                  │
│  ┌─────────────────────────────────────────┐            │
│  │ 1. Parse user intent                    │            │
│  │ 2. Identify data sources needed         │            │
│  │ 3. Select optimal extraction method     │            │
│  │ 4. Generate extraction plan             │            │
│  └─────────────────────────────────────────┘            │
│                                                          │
│  Output: {                                               │
│    "twitter.com/elonmusk": "apify",                     │
│    "reddit.com/r/wallstreetbets": "api"                 │
│  }                                                       │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│         🎯 EXTRACTION ORCHESTRATOR                      │
│  ┌──────────────┬──────────────┬──────────────┐         │
│  │   API Tier   │  Apify Tier  │ Browser Tier │         │
│  │              │              │              │         │
│  │ - Reddit API │ - Twitter    │ - Custom     │         │
│  │ - News API   │ - Instagram  │ - Niche sites│         │
│  │ - SEC Edgar  │ - LinkedIn   │ - Forums     │         │
│  │ - YouTube    │ - TikTok     │ - Any site   │         │
│  └──────────────┴──────────────┴──────────────┘         │
│                                                          │
│  Features:                                               │
│  - Job queuing & scheduling                              │
│  - Rate limiting & retries                               │
│  - Caching & deduplication                               │
│  - Fallback cascade (API → Apify → Browser)             │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│           📊 DATA PROCESSING PIPELINE                   │
│  ┌─────────────────────────────────────────┐            │
│  │ 1. Raw data validation                  │            │
│  │ 2. Deduplication & normalization        │            │
│  │ 3. Sentiment analysis (text sources)    │            │
│  │ 4. Feature engineering                  │            │
│  │ 5. Time-series formatting               │            │
│  │ 6. Quality scoring                      │            │
│  └─────────────────────────────────────────┘            │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│         💾 TIME-SERIES DATABASE (Supabase)              │
│  ┌─────────────────────────────────────────┐            │
│  │ Tables:                                  │            │
│  │ - data_sources (source configs)         │            │
│  │ - extraction_jobs (job queue)           │            │
│  │ - raw_data (unprocessed)                │            │
│  │ - signals (processed trading signals)   │            │
│  │ - data_quality_metrics                  │            │
│  └─────────────────────────────────────────┘            │
└────────────────────┬────────────────────────────────────┘
                     ↓
        ┌────────────┴────────────┐
        ↓                         ↓
┌──────────────┐          ┌──────────────┐
│ BACKTESTING  │          │ LIVE TRADING │
│ (existing)   │          │ (existing)   │
└──────────────┘          └──────────────┘
```

---

## Implementation Phases

### Phase 1: Foundation & Core Routing (Weeks 1-2, 60-80 hours)

#### Week 1: Data Source Router Agent
**Goal:** Agent that understands user intent and selects optimal data extraction method

**Tasks:**
1. Create `backend/agents/data_source_router.py`
   - Parse user strategy to identify data requirements
   - Classify data sources (social media, news, custom)
   - Select extraction tier (API/Apify/Browser/Firecrawl)
   - Generate extraction plan with schedule

2. Create `backend/tools/data_source_registry.py`
   - Registry of known data sources and optimal methods
   - Pattern matching for common requests
   - Fallback chain configuration

3. Database setup
   - Create `data_sources` table
   - Create `extraction_plans` table
   - Initial migration scripts

**Deliverables:**
```python
# Example usage:
router = DataSourceRouterAgent()
plan = router.plan_extraction({
    "user_query": "Trade Tesla on Elon's tweets and WSB sentiment",
    "strategy": {...}
})

# Output:
{
    "sources": [
        {
            "name": "twitter_elonmusk",
            "url": "twitter.com/elonmusk",
            "method": "apify",
            "actor": "apify/twitter-scraper",
            "schedule": "realtime",
            "historical": True
        },
        {
            "name": "reddit_wsb",
            "url": "reddit.com/r/wallstreetbets",
            "method": "api",
            "schedule": "5min",
            "historical": True
        }
    ],
    "confidence": 0.95
}
```

#### Week 2: Basic API Tier Implementation
**Goal:** Get real Reddit and News data working

**Tasks:**
1. Enhance `backend/tools/social_media.py`
   - Implement PRAW (Reddit API) properly
   - Add NewsAPI integration
   - Create data caching layer
   - Historical data fetching

2. Create `backend/tools/api_handlers/`
   - `reddit_handler.py` - PRAW wrapper
   - `news_handler.py` - NewsAPI wrapper
   - `base_handler.py` - Common interface

3. Update `backtest_runner.py`
   - Replace mock sentiment with real API calls
   - Integrate with new data source router

**Deliverables:**
- Working Reddit sentiment extraction
- Working news sentiment extraction
- Cached historical data for backtesting
- First end-to-end test: "Trade on WSB sentiment"

---

### Phase 2: Apify Integration (Weeks 3-4, 60-80 hours)

#### Week 3: Apify Client & Twitter Scraping
**Goal:** Scrape Twitter via Apify actors

**Tasks:**
1. Create `backend/tools/apify_client.py`
   - Apify API integration
   - Job submission and monitoring
   - Result fetching and parsing
   - Cost tracking

2. Implement Twitter scraper
   - Configure `apify/twitter-scraper` actor
   - Handle authentication tokens
   - Parse tweet data (text, timestamp, engagement)
   - Store in time-series format

3. Create `backend/tools/scrapers/`
   - `twitter_scraper.py` - Apify wrapper
   - `scraper_base.py` - Common interface

**Deliverables:**
```python
# Example usage:
scraper = TwitterScraperApify()
tweets = await scraper.get_tweets(
    username="elonmusk",
    start_date="2024-01-01",
    end_date="2024-10-01",
    keywords=["Tesla", "TSLA"]
)

# Output: List of tweets with metadata
```

#### Week 4: Multi-Platform Apify Support
**Goal:** Add Instagram, TikTok, LinkedIn scrapers

**Tasks:**
1. Implement additional Apify actors
   - Instagram scraper (for influencer trends)
   - TikTok scraper (for viral content)
   - LinkedIn scraper (for business sentiment)

2. Create `backend/tools/extraction_orchestrator.py` (initial version)
   - Job queue management
   - Parallel execution
   - Rate limiting
   - Basic retry logic

3. Test multi-source strategies
   - "Trade on Twitter + Instagram sentiment"
   - Validate data alignment across sources

**Deliverables:**
- 4+ Apify actors integrated (Twitter, Instagram, TikTok, LinkedIn)
- Basic orchestrator running parallel jobs
- Multi-source strategy working end-to-end

---

### Phase 3: Intelligent Scraping (Weeks 5-6, 80-100 hours)

#### Week 5: Browserbase Integration & Scraper Generator
**Goal:** AI generates custom scrapers for any website

**Tasks:**
1. Create `backend/agents/scraper_generator.py`
   - Claude-powered scraper code generation
   - Analyzes target website structure
   - Generates Playwright/Puppeteer code
   - Includes anti-bot measures

2. Create `backend/tools/browserbase_client.py`
   - Browserbase API integration
   - Session management
   - Proxy and fingerprint rotation

3. Implement scraper execution
   - Run generated code in Browserbase
   - Parse and validate results
   - Handle errors gracefully

**Deliverables:**
```python
# Example usage:
generator = ScraperGeneratorAgent()
scraper_code = await generator.generate({
    "target_url": "https://niche-forum.com/crypto-discussions",
    "data_requirements": {
        "fields": ["post_text", "author", "upvotes", "timestamp"],
        "filters": ["keyword:Bitcoin"],
        "format": "json"
    }
})

# Output: Working Playwright script
# System automatically tests and deploys it
```

#### Week 6: Firecrawl Integration & Fallback Logic
**Goal:** Complete all 4 tiers with intelligent fallback

**Tasks:**
1. Integrate Firecrawl
   - For static content (blogs, news sites)
   - LLM-friendly markdown conversion
   - Content extraction and summarization

2. Implement complete fallback chain
   - Try API first
   - Fallback to Apify if API unavailable
   - Fallback to Browserbase if Apify fails
   - Fallback to Firecrawl for static content

3. Enhanced orchestrator
   - Intelligent tier selection
   - Automatic fallback on failure
   - Cost-aware routing (prefer cheaper methods)

**Deliverables:**
- 4-tier extraction system fully working
- Automatic fallback logic
- Test: "Trade on [obscure website]" works

---

### Phase 4: Data Processing Pipeline (Weeks 7-8, 80-100 hours)

#### Week 7: Sentiment Analysis & Feature Engineering
**Goal:** Convert raw data into trading signals

**Tasks:**
1. Create `backend/tools/sentiment_analyzer.py`
   - Multi-model sentiment analysis
   - Context-aware scoring (sarcasm, market jargon)
   - Bulk processing for efficiency
   - Confidence scoring

2. Create `backend/tools/data_pipeline.py`
   - Data validation and cleaning
   - Deduplication logic
   - Normalization (timestamps, text format)
   - Feature extraction

3. Enhance feature engineering
   - Engagement metrics (likes, shares, comments)
   - Trend detection (velocity, acceleration)
   - Cross-source correlation
   - Composite signals

**Deliverables:**
```python
# Example pipeline:
pipeline = DataPipeline()

raw_tweets = [...] # From Apify
processed = await pipeline.process(
    data=raw_tweets,
    steps=[
        'validate',
        'deduplicate',
        'normalize_timestamps',
        'extract_sentiment',
        'calculate_engagement_score',
        'generate_signal'
    ]
)

# Output: Clean, timestamped trading signals
```

#### Week 8: Quality Monitoring & Storage Optimization
**Goal:** Ensure data quality and efficient storage

**Tasks:**
1. Create `backend/tools/data_quality.py`
   - Schema validation
   - Anomaly detection
   - Completeness checking
   - Quality scoring

2. Optimize database schema
   - Time-series partitioning
   - Efficient indexing
   - Compression for historical data
   - Query optimization

3. Add monitoring
   - Data quality dashboards
   - Extraction success rates
   - Cost tracking per source
   - Alert on quality degradation

**Deliverables:**
- Data quality metrics dashboard
- Automated quality alerts
- Optimized storage (50%+ reduction)
- Quality gates before backtesting

---

### Phase 5: Orchestration & Scaling (Weeks 9-10, 60-80 hours)

#### Week 9: Job Orchestration & Scheduling
**Goal:** Production-ready job management

**Tasks:**
1. Implement job queue (choose: Temporal/Inngest/BullMQ)
   - Job scheduling (cron, realtime, event-based)
   - Priority queue management
   - Worker pool management
   - Dead letter queue

2. Advanced retry logic
   - Exponential backoff
   - Circuit breaker pattern
   - Tier fallback on repeated failures
   - Alert on exhausted retries

3. Caching layer (Redis/Upstash)
   - Cache API responses
   - Cache scraping results
   - TTL management
   - Cache invalidation strategy

**Deliverables:**
- Production job queue system
- Smart retry and fallback logic
- Caching reducing API costs by 60%+
- 99%+ extraction success rate

#### Week 10: Polish, Testing & Documentation
**Goal:** Production-ready system

**Tasks:**
1. Comprehensive testing
   - Unit tests for all new components
   - Integration tests for full pipeline
   - Load testing for concurrent strategies
   - Cost simulation tests

2. Documentation
   - API documentation (OpenAPI)
   - Data source integration guide
   - Troubleshooting runbook
   - Cost optimization guide

3. UI enhancements
   - Data source selection UI
   - Real-time extraction status
   - Data quality visualization
   - Cost monitoring dashboard

4. Performance optimization
   - Batch processing optimizations
   - Database query optimization
   - API call reduction
   - Memory usage optimization

**Deliverables:**
- 90%+ test coverage on new code
- Complete documentation
- Enhanced UI for data sources
- Performance benchmarks documented

---

## Code Structure

```
backend/
├── agents/
│   ├── supervisor.py                    # Existing - orchestrates all agents
│   ├── code_generator.py                # Existing - generates strategy code
│   ├── backtest_runner.py               # Enhanced - uses new data sources
│   ├── strategy_analyst.py              # Existing - analyzes performance
│   ├── intelligent_orchestrator.py      # Enhanced - real data analysis
│   ├── insights_generator.py            # Existing - visualization config
│   ├── 🆕 data_source_router.py         # NEW - intelligent data source selection
│   ├── 🆕 scraper_generator.py          # NEW - generates custom scrapers
│   └── 🆕 sentiment_analyzer.py         # NEW - advanced sentiment analysis
│
├── tools/
│   ├── extraction/
│   │   ├── 🆕 extraction_orchestrator.py   # Main orchestrator
│   │   ├── 🆕 data_source_registry.py      # Known sources registry
│   │   ├── 🆕 extraction_plan.py           # Plan data structure
│   │   └── 🆕 job_queue.py                 # Job queue management
│   │
│   ├── api_handlers/
│   │   ├── 🆕 base_handler.py              # Base API handler
│   │   ├── 🆕 reddit_handler.py            # PRAW wrapper
│   │   ├── 🆕 news_handler.py              # NewsAPI wrapper
│   │   ├── 🆕 youtube_handler.py           # YouTube Data API
│   │   └── 🆕 sec_handler.py               # SEC Edgar API
│   │
│   ├── scrapers/
│   │   ├── 🆕 apify_client.py              # Apify API client
│   │   ├── 🆕 browserbase_client.py        # Browserbase client
│   │   ├── 🆕 firecrawl_client.py          # Firecrawl client
│   │   ├── 🆕 twitter_scraper.py           # Twitter via Apify
│   │   ├── 🆕 instagram_scraper.py         # Instagram via Apify
│   │   ├── 🆕 tiktok_scraper.py            # TikTok via Apify
│   │   ├── 🆕 linkedin_scraper.py          # LinkedIn via Apify
│   │   └── 🆕 custom_scraper.py            # Browserbase executor
│   │
│   ├── processing/
│   │   ├── 🆕 data_pipeline.py             # Main processing pipeline
│   │   ├── 🆕 data_validator.py            # Schema validation
│   │   ├── 🆕 data_cleaner.py              # Cleaning and normalization
│   │   ├── 🆕 feature_engineering.py       # Feature extraction
│   │   ├── 🆕 sentiment_analysis.py        # Sentiment scoring
│   │   └── 🆕 data_quality.py              # Quality monitoring
│   │
│   ├── storage/
│   │   ├── 🆕 timeseries_db.py             # Time-series storage
│   │   ├── 🆕 cache_manager.py             # Redis caching
│   │   └── 🆕 data_archiver.py             # Historical data archival
│   │
│   ├── backtester.py                    # Enhanced - uses real data
│   ├── code_generator.py                # Existing
│   ├── market_data.py                   # Existing - Alpaca integration
│   ├── social_media.py                  # Enhanced - real sentiment
│   ├── web_scraper.py                   # Enhanced - multi-tier
│   └── politician_trades.py             # Existing - example alt data
│
├── db/
│   ├── models.py                        # Enhanced - new tables
│   ├── repositories/
│   │   ├── 🆕 data_source_repository.py    # Data sources CRUD
│   │   ├── 🆕 extraction_job_repository.py # Jobs CRUD
│   │   ├── 🆕 signal_repository.py         # Signals CRUD
│   │   └── 🆕 quality_metrics_repository.py
│   └── migrations/
│       ├── 🆕 003_create_data_sources.sql
│       ├── 🆕 004_create_extraction_jobs.sql
│       ├── 🆕 005_create_raw_data.sql
│       ├── 🆕 006_create_signals.sql
│       └── 🆕 007_create_quality_metrics.sql
│
├── config/
│   ├── 🆕 apify_config.py                  # Apify actors configuration
│   ├── 🆕 browserbase_config.py            # Browserbase settings
│   ├── 🆕 data_sources.yaml                # Known data sources registry
│   └── 🆕 extraction_limits.yaml           # Rate limits per source
│
├── main.py                              # Enhanced - new endpoints
├── config.py                            # Enhanced - new env vars
└── llm_client.py                        # Existing

frontend/
├── src/
│   ├── pages/
│   │   ├── 🆕 DataSourcesPage.jsx          # Browse available data sources
│   │   └── 🆕 ExtractionMonitorPage.jsx    # Monitor extraction jobs
│   ├── components/
│   │   ├── 🆕 DataSourceSelector.jsx       # Select data sources for strategy
│   │   ├── 🆕 ExtractionStatus.jsx         # Show extraction progress
│   │   ├── 🆕 DataQualityIndicator.jsx     # Data quality visualization
│   │   └── 🆕 CostEstimator.jsx            # Estimate extraction costs
│   └── ...

scripts/
├── 🆕 seed_data_sources.py                 # Seed known sources
├── 🆕 test_extraction.py                   # Test extraction pipeline
└── 🆕 monitor_costs.py                     # Cost monitoring script
```

---

## Database Schema

### New Tables

#### 1. `data_sources`
Tracks all configured data sources

```sql
CREATE TABLE data_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    type VARCHAR(50) NOT NULL, -- 'social', 'news', 'custom', 'financial'
    platform VARCHAR(100), -- 'twitter', 'reddit', 'instagram', etc.
    extraction_method VARCHAR(50) NOT NULL, -- 'api', 'apify', 'browserbase', 'firecrawl'

    -- Method-specific configuration
    config JSONB NOT NULL, -- API keys, actor IDs, selectors, etc.

    -- Rate limiting
    rate_limit_calls INTEGER, -- Max calls per period
    rate_limit_period INTEGER, -- Period in seconds

    -- Cost tracking
    cost_per_call DECIMAL(10, 4), -- Cost per API call/scrape

    -- Status
    is_active BOOLEAN DEFAULT true,
    health_status VARCHAR(50) DEFAULT 'healthy', -- 'healthy', 'degraded', 'down'
    last_check_at TIMESTAMPTZ,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

-- Indexes
CREATE INDEX idx_data_sources_type ON data_sources(type);
CREATE INDEX idx_data_sources_platform ON data_sources(platform);
CREATE INDEX idx_data_sources_method ON data_sources(extraction_method);
```

#### 2. `extraction_jobs`
Manages extraction job queue

```sql
CREATE TABLE extraction_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    data_source_id UUID NOT NULL REFERENCES data_sources(id),
    strategy_id UUID REFERENCES trading_bots(id), -- Link to strategy

    -- Job configuration
    job_type VARCHAR(50) NOT NULL, -- 'historical', 'realtime', 'scheduled'
    schedule VARCHAR(100), -- Cron expression or 'realtime'
    parameters JSONB NOT NULL, -- { "username": "elonmusk", "keywords": ["Tesla"] }

    -- Job status
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
    priority INTEGER DEFAULT 5, -- 1-10, higher = more important

    -- Execution tracking
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,

    -- Results
    items_extracted INTEGER DEFAULT 0,
    cost_incurred DECIMAL(10, 4) DEFAULT 0,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_extraction_jobs_status ON extraction_jobs(status);
CREATE INDEX idx_extraction_jobs_source ON extraction_jobs(data_source_id);
CREATE INDEX idx_extraction_jobs_strategy ON extraction_jobs(strategy_id);
CREATE INDEX idx_extraction_jobs_schedule ON extraction_jobs(schedule) WHERE status = 'pending';
```

#### 3. `raw_data`
Stores unprocessed extracted data (time-series optimized)

```sql
CREATE TABLE raw_data (
    id UUID DEFAULT uuid_generate_v4(),
    extraction_job_id UUID NOT NULL REFERENCES extraction_jobs(id),
    data_source_id UUID NOT NULL REFERENCES data_sources(id),

    -- Time-series data
    timestamp TIMESTAMPTZ NOT NULL, -- When the data was created (not extracted)
    extracted_at TIMESTAMPTZ DEFAULT NOW(), -- When we extracted it

    -- Content
    content_type VARCHAR(50) NOT NULL, -- 'tweet', 'post', 'article', 'filing', etc.
    content_text TEXT, -- Main text content
    content_metadata JSONB, -- { "author": "...", "likes": 123, "url": "..." }

    -- Processing status
    is_processed BOOLEAN DEFAULT false,
    processed_at TIMESTAMPTZ,

    -- Deduplication
    content_hash VARCHAR(64), -- SHA-256 of content for dedup

    PRIMARY KEY (id, timestamp)
) PARTITION BY RANGE (timestamp);

-- Create partitions (monthly)
CREATE TABLE raw_data_2024_10 PARTITION OF raw_data
    FOR VALUES FROM ('2024-10-01') TO ('2024-11-01');

-- Indexes
CREATE INDEX idx_raw_data_timestamp ON raw_data(timestamp DESC);
CREATE INDEX idx_raw_data_source ON raw_data(data_source_id, timestamp DESC);
CREATE INDEX idx_raw_data_hash ON raw_data(content_hash);
CREATE INDEX idx_raw_data_unprocessed ON raw_data(is_processed) WHERE is_processed = false;
```

#### 4. `signals`
Processed trading signals (time-series optimized)

```sql
CREATE TABLE signals (
    id UUID DEFAULT uuid_generate_v4(),
    data_source_id UUID NOT NULL REFERENCES data_sources(id),
    strategy_id UUID REFERENCES trading_bots(id),
    raw_data_id UUID, -- Link back to raw data

    -- Time-series
    timestamp TIMESTAMPTZ NOT NULL, -- Signal timestamp

    -- Signal data
    signal_type VARCHAR(50) NOT NULL, -- 'sentiment', 'volume', 'engagement', etc.
    signal_value DECIMAL(10, 6) NOT NULL, -- Normalized value (usually -1 to 1 or 0 to 1)
    confidence DECIMAL(5, 4), -- 0 to 1

    -- Context
    symbol VARCHAR(10), -- Stock symbol if applicable
    metadata JSONB, -- Additional signal context

    -- Quality
    quality_score DECIMAL(5, 4), -- Data quality metric

    PRIMARY KEY (id, timestamp)
) PARTITION BY RANGE (timestamp);

-- Create partitions (monthly)
CREATE TABLE signals_2024_10 PARTITION OF signals
    FOR VALUES FROM ('2024-10-01') TO ('2024-11-01');

-- Indexes
CREATE INDEX idx_signals_timestamp ON signals(timestamp DESC);
CREATE INDEX idx_signals_source ON signals(data_source_id, timestamp DESC);
CREATE INDEX idx_signals_strategy ON signals(strategy_id, timestamp DESC);
CREATE INDEX idx_signals_symbol ON signals(symbol, timestamp DESC) WHERE symbol IS NOT NULL;
```

#### 5. `data_quality_metrics`
Tracks data quality over time

```sql
CREATE TABLE data_quality_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    data_source_id UUID NOT NULL REFERENCES data_sources(id),
    extraction_job_id UUID REFERENCES extraction_jobs(id),

    -- Time period
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,

    -- Quality metrics
    total_items INTEGER NOT NULL,
    valid_items INTEGER NOT NULL,
    duplicate_items INTEGER NOT NULL,
    missing_fields INTEGER NOT NULL,

    -- Completeness
    completeness_score DECIMAL(5, 4), -- 0 to 1

    -- Freshness
    avg_data_age_seconds INTEGER, -- How old is the data

    -- Anomalies
    anomaly_count INTEGER DEFAULT 0,
    anomaly_details JSONB,

    -- Overall score
    quality_score DECIMAL(5, 4), -- 0 to 1, computed from above

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_quality_metrics_source ON data_quality_metrics(data_source_id, period_start DESC);
CREATE INDEX idx_quality_metrics_job ON data_quality_metrics(extraction_job_id);
CREATE INDEX idx_quality_metrics_period ON data_quality_metrics(period_start, period_end);
```

### Enhanced Existing Tables

#### Update `trading_bots` table
```sql
ALTER TABLE trading_bots
ADD COLUMN data_sources JSONB, -- Array of data source IDs used
ADD COLUMN extraction_schedule VARCHAR(100), -- How often to extract data
ADD COLUMN data_quality_threshold DECIMAL(5, 4) DEFAULT 0.7; -- Minimum quality to trade
```

---

## Key Components

### 1. Data Source Router Agent

**File:** `backend/agents/data_source_router.py`

```python
"""
Data Source Router Agent
Analyzes user strategy and intelligently routes to optimal data extraction method
"""

from typing import Dict, List, Any
from anthropic import Anthropic
import json
import re

class DataSourceRouterAgent:
    """
    Intelligent routing of data extraction requests

    Responsibilities:
    1. Parse user intent from strategy description
    2. Identify all data sources mentioned
    3. Select optimal extraction method for each source
    4. Generate extraction plan with schedule
    """

    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.source_registry = DataSourceRegistry()

    async def plan_extraction(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive extraction plan

        Args:
            request: {
                "user_query": "Trade Tesla on Elon's tweets",
                "strategy": {...parsed strategy...}
            }

        Returns:
            {
                "sources": [{...source configs...}],
                "schedule": "realtime" | "5min" | "1hour",
                "confidence": 0.0-1.0
            }
        """
        user_query = request.get("user_query", "")

        # Step 1: Use Claude to extract data requirements
        data_requirements = await self._extract_data_requirements(user_query)

        # Step 2: Match requirements to known sources or generate custom
        sources = []
        for req in data_requirements:
            source_config = await self._route_source(req)
            sources.append(source_config)

        # Step 3: Determine optimal schedule
        schedule = self._determine_schedule(data_requirements)

        return {
            "sources": sources,
            "schedule": schedule,
            "confidence": self._calculate_confidence(sources),
            "estimated_cost": self._estimate_cost(sources, schedule)
        }

    async def _extract_data_requirements(self, user_query: str) -> List[Dict]:
        """
        Use Claude to understand what data user wants
        """
        prompt = f"""Analyze this trading strategy request and extract data requirements:

User Query: "{user_query}"

Identify:
1. All data sources mentioned (websites, platforms, social media)
2. Type of data needed (sentiment, volume, posts, articles)
3. Specific filters (username, hashtag, keyword, time range)
4. Update frequency needed (realtime, hourly, daily)

Return JSON format:
[
  {{
    "source": "twitter.com",
    "target": "elonmusk",
    "data_type": "tweets",
    "filters": {{"keywords": ["Tesla", "TSLA"]}},
    "frequency": "realtime"
  }}
]"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse JSON from response
        text = response.content[0].text
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        return []

    async def _route_source(self, requirement: Dict) -> Dict:
        """
        Determine optimal extraction method for a data requirement

        Priority:
        1. Check if official API exists → use API
        2. Check if Apify actor exists → use Apify
        3. Check if Firecrawl can handle (static site) → use Firecrawl
        4. Generate Browserbase scraper → use Browserbase
        """
        source = requirement.get("source", "")

        # Check registry for known source
        known_source = self.source_registry.lookup(source)

        if known_source and known_source["method"] == "api":
            return {
                "name": f"{source}_{requirement.get('target', 'default')}",
                "source": source,
                "method": "api",
                "handler": known_source["handler"],
                "config": {
                    "target": requirement.get("target"),
                    "filters": requirement.get("filters", {}),
                    "frequency": requirement.get("frequency", "1hour")
                }
            }

        elif known_source and known_source["method"] == "apify":
            return {
                "name": f"{source}_{requirement.get('target', 'default')}",
                "source": source,
                "method": "apify",
                "actor": known_source["actor"],
                "config": {
                    "username": requirement.get("target"),
                    **requirement.get("filters", {}),
                    "frequency": requirement.get("frequency", "1hour")
                }
            }

        elif self._is_static_site(source):
            return {
                "name": f"{source}_content",
                "source": source,
                "method": "firecrawl",
                "config": {
                    "url": f"https://{source}",
                    "selectors": requirement.get("selectors"),
                    "frequency": requirement.get("frequency", "6hour")
                }
            }

        else:
            # Need custom scraper - will be generated by ScraperGeneratorAgent
            return {
                "name": f"{source}_custom",
                "source": source,
                "method": "browserbase",
                "needs_generation": True,
                "config": {
                    "url": f"https://{source}",
                    "data_requirements": requirement,
                    "frequency": requirement.get("frequency", "1hour")
                }
            }

    def _determine_schedule(self, requirements: List[Dict]) -> str:
        """
        Determine optimal extraction schedule based on all requirements
        """
        frequencies = [req.get("frequency", "1hour") for req in requirements]

        # If any source needs realtime, do realtime
        if "realtime" in frequencies:
            return "realtime"

        # Otherwise use most frequent requirement
        freq_map = {"5min": 5, "15min": 15, "1hour": 60, "6hour": 360, "daily": 1440}
        min_minutes = min(freq_map.get(f, 60) for f in frequencies)

        for freq, minutes in freq_map.items():
            if minutes == min_minutes:
                return freq

        return "1hour"

    def _calculate_confidence(self, sources: List[Dict]) -> float:
        """
        Calculate confidence in extraction plan
        """
        if not sources:
            return 0.0

        # High confidence if all sources use known methods (API/Apify)
        known_methods = sum(1 for s in sources if s["method"] in ["api", "apify"])
        return min(1.0, (known_methods / len(sources)) * 1.2)

    def _estimate_cost(self, sources: List[Dict], schedule: str) -> Dict:
        """
        Estimate monthly cost for extraction plan
        """
        # Cost estimates (per 1000 calls/items)
        cost_per_1k = {
            "api": 0.10,  # Most APIs are cheap/free
            "apify": 5.00,  # Apify ~$5/1000 results
            "browserbase": 10.00,  # Browserbase ~$10/1000 page loads
            "firecrawl": 0.50   # Firecrawl ~$0.50/1000 pages
        }

        schedule_multiplier = {
            "realtime": 43200,  # Every minute = 43.2k/month
            "5min": 8640,
            "15min": 2880,
            "1hour": 720,
            "6hour": 120,
            "daily": 30
        }

        total_cost = 0
        for source in sources:
            method = source["method"]
            calls_per_month = schedule_multiplier.get(schedule, 720)
            cost = (calls_per_month / 1000) * cost_per_1k.get(method, 1.0)
            total_cost += cost

        return {
            "estimated_monthly_cost": round(total_cost, 2),
            "breakdown": [
                {
                    "source": s["name"],
                    "method": s["method"],
                    "calls_per_month": schedule_multiplier.get(schedule, 720),
                    "cost": round((schedule_multiplier.get(schedule, 720) / 1000) * cost_per_1k.get(s["method"], 1.0), 2)
                }
                for s in sources
            ]
        }

    def _is_static_site(self, source: str) -> bool:
        """
        Heuristic to detect if site is static (good for Firecrawl)
        """
        static_indicators = [
            "blog", "medium.com", ".wordpress.com", "substack.com",
            "news", "article", "post"
        ]
        return any(ind in source.lower() for ind in static_indicators)


class DataSourceRegistry:
    """
    Registry of known data sources and optimal extraction methods
    """

    KNOWN_SOURCES = {
        "reddit.com": {
            "method": "api",
            "handler": "reddit_handler",
            "cost": "free",
            "rate_limit": "60/min"
        },
        "twitter.com": {
            "method": "apify",
            "actor": "apify/twitter-scraper",
            "cost": "$5/1000",
            "rate_limit": "unlimited"
        },
        "x.com": {
            "method": "apify",
            "actor": "apify/twitter-scraper",
            "cost": "$5/1000",
            "rate_limit": "unlimited"
        },
        "instagram.com": {
            "method": "apify",
            "actor": "apify/instagram-scraper",
            "cost": "$5/1000",
            "rate_limit": "unlimited"
        },
        "tiktok.com": {
            "method": "apify",
            "actor": "apify/tiktok-scraper",
            "cost": "$5/1000",
            "rate_limit": "unlimited"
        },
        "linkedin.com": {
            "method": "apify",
            "actor": "apify/linkedin-scraper",
            "cost": "$5/1000",
            "rate_limit": "unlimited"
        },
        "youtube.com": {
            "method": "api",
            "handler": "youtube_handler",
            "cost": "free",
            "rate_limit": "10000/day"
        },
        "newsapi.org": {
            "method": "api",
            "handler": "news_handler",
            "cost": "free",
            "rate_limit": "100/day"
        }
    }

    def lookup(self, source: str) -> Dict:
        """
        Look up known configuration for a source
        """
        # Exact match
        if source in self.KNOWN_SOURCES:
            return self.KNOWN_SOURCES[source]

        # Partial match (e.g., "reddit" matches "reddit.com")
        for known_source, config in self.KNOWN_SOURCES.items():
            if source in known_source or known_source in source:
                return config

        return None
```

---

### 2. Extraction Orchestrator

**File:** `backend/tools/extraction/extraction_orchestrator.py`

```python
"""
Extraction Orchestrator
Manages parallel extraction from multiple sources with intelligent fallback
"""

import asyncio
from typing import Dict, List, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ExtractionOrchestrator:
    """
    Orchestrates data extraction across multiple tiers

    Features:
    - Parallel execution of extraction jobs
    - Rate limiting per source
    - Automatic fallback on failures
    - Caching to reduce costs
    - Job queue management
    """

    def __init__(self):
        from tools.api_handlers.reddit_handler import RedditHandler
        from tools.api_handlers.news_handler import NewsHandler
        from tools.scrapers.apify_client import ApifyClient
        from tools.scrapers.browserbase_client import BrowserbaseClient
        from tools.scrapers.firecrawl_client import FirecrawlClient
        from tools.storage.cache_manager import CacheManager

        # Initialize handlers
        self.api_handlers = {
            "reddit": RedditHandler(),
            "news": NewsHandler(),
            "youtube": YouTubeHandler(),
        }

        self.apify_client = ApifyClient()
        self.browserbase_client = BrowserbaseClient()
        self.firecrawl_client = FirecrawlClient()
        self.cache = CacheManager()

        # Job tracking
        self.active_jobs = {}
        self.job_queue = asyncio.Queue()

    async def execute_extraction_plan(
        self,
        plan: Dict[str, Any],
        strategy_id: str = None
    ) -> Dict[str, Any]:
        """
        Execute a complete extraction plan

        Args:
            plan: Output from DataSourceRouterAgent
            strategy_id: Link extraction to a strategy

        Returns:
            {
                "success": True/False,
                "sources": [{...extracted data...}],
                "errors": [...],
                "cost": 0.00
            }
        """
        sources = plan.get("sources", [])

        # Execute all sources in parallel
        tasks = [
            self._execute_source(source, strategy_id)
            for source in sources
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate results
        successful = []
        errors = []
        total_cost = 0

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                errors.append({
                    "source": sources[i]["name"],
                    "error": str(result)
                })
            elif result.get("success"):
                successful.append(result)
                total_cost += result.get("cost", 0)
            else:
                errors.append({
                    "source": sources[i]["name"],
                    "error": result.get("error")
                })

        return {
            "success": len(successful) > 0,
            "sources": successful,
            "errors": errors,
            "total_cost": total_cost,
            "items_extracted": sum(s.get("items_count", 0) for s in successful)
        }

    async def _execute_source(
        self,
        source: Dict[str, Any],
        strategy_id: str = None
    ) -> Dict[str, Any]:
        """
        Execute extraction for a single source with fallback logic
        """
        method = source.get("method")
        source_name = source.get("name")

        logger.info(f"Extracting from {source_name} using {method}")

        # Check cache first
        cache_key = self._get_cache_key(source)
        cached = await self.cache.get(cache_key)
        if cached:
            logger.info(f"Cache hit for {source_name}")
            return {
                "success": True,
                "source": source_name,
                "data": cached,
                "from_cache": True,
                "cost": 0
            }

        # Try primary method
        try:
            result = await self._execute_method(source, method)

            # Cache successful result
            if result.get("success"):
                await self.cache.set(
                    cache_key,
                    result.get("data"),
                    ttl=self._get_cache_ttl(source)
                )

            return result

        except Exception as e:
            logger.error(f"Primary method {method} failed for {source_name}: {e}")

            # Try fallback
            return await self._execute_fallback(source, method, e)

    async def _execute_method(
        self,
        source: Dict[str, Any],
        method: str
    ) -> Dict[str, Any]:
        """
        Execute extraction using specified method
        """
        if method == "api":
            return await self._execute_api(source)
        elif method == "apify":
            return await self._execute_apify(source)
        elif method == "browserbase":
            return await self._execute_browserbase(source)
        elif method == "firecrawl":
            return await self._execute_firecrawl(source)
        else:
            raise ValueError(f"Unknown method: {method}")

    async def _execute_api(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute via official API
        """
        handler_name = source.get("handler")
        handler = self.api_handlers.get(handler_name)

        if not handler:
            raise ValueError(f"No handler found for {handler_name}")

        config = source.get("config", {})
        data = await handler.fetch(**config)

        return {
            "success": True,
            "source": source.get("name"),
            "method": "api",
            "data": data,
            "items_count": len(data) if isinstance(data, list) else 1,
            "cost": 0  # Most APIs are free
        }

    async def _execute_apify(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute via Apify actor
        """
        actor = source.get("actor")
        config = source.get("config", {})

        result = await self.apify_client.run_actor(actor, config)

        return {
            "success": True,
            "source": source.get("name"),
            "method": "apify",
            "data": result.get("items", []),
            "items_count": len(result.get("items", [])),
            "cost": result.get("cost", 0)
        }

    async def _execute_browserbase(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute via Browserbase (custom scraper)
        """
        # If scraper needs generation, generate it first
        if source.get("needs_generation"):
            from agents.scraper_generator import ScraperGeneratorAgent
            generator = ScraperGeneratorAgent()

            scraper_code = await generator.generate(source.get("config"))
            source["scraper_code"] = scraper_code

        # Execute scraper in Browserbase
        result = await self.browserbase_client.execute_scraper(
            source.get("scraper_code"),
            source.get("config")
        )

        return {
            "success": True,
            "source": source.get("name"),
            "method": "browserbase",
            "data": result.get("items", []),
            "items_count": len(result.get("items", [])),
            "cost": result.get("cost", 0)
        }

    async def _execute_firecrawl(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute via Firecrawl (static site scraping)
        """
        config = source.get("config", {})
        result = await self.firecrawl_client.scrape(config.get("url"))

        return {
            "success": True,
            "source": source.get("name"),
            "method": "firecrawl",
            "data": result.get("content"),
            "items_count": 1,
            "cost": 0.001  # Very cheap
        }

    async def _execute_fallback(
        self,
        source: Dict[str, Any],
        failed_method: str,
        error: Exception
    ) -> Dict[str, Any]:
        """
        Try fallback methods in order: API → Apify → Browserbase
        """
        fallback_chain = {
            "api": ["apify", "browserbase"],
            "apify": ["browserbase"],
            "browserbase": [],  # No fallback for browserbase
            "firecrawl": ["browserbase"]
        }

        fallbacks = fallback_chain.get(failed_method, [])

        for fallback_method in fallbacks:
            try:
                logger.info(f"Trying fallback: {fallback_method}")
                return await self._execute_method(source, fallback_method)
            except Exception as e:
                logger.error(f"Fallback {fallback_method} also failed: {e}")
                continue

        # All fallbacks exhausted
        return {
            "success": False,
            "source": source.get("name"),
            "error": f"All methods failed. Last error: {error}"
        }

    def _get_cache_key(self, source: Dict[str, Any]) -> str:
        """
        Generate cache key for a source
        """
        import hashlib
        import json

        # Hash of source config
        config_str = json.dumps(source, sort_keys=True)
        return f"extraction:{hashlib.md5(config_str.encode()).hexdigest()}"

    def _get_cache_ttl(self, source: Dict[str, Any]) -> int:
        """
        Determine cache TTL based on frequency
        """
        frequency = source.get("config", {}).get("frequency", "1hour")

        ttl_map = {
            "realtime": 60,      # 1 minute
            "5min": 300,         # 5 minutes
            "15min": 900,        # 15 minutes
            "1hour": 3600,       # 1 hour
            "6hour": 21600,      # 6 hours
            "daily": 86400       # 24 hours
        }

        return ttl_map.get(frequency, 3600)
```

---

## (Continued in next message due to length...)

Would you like me to continue with:
- Agent Prompts
- Testing Strategy
- Deployment Plan
- Cost Analysis

Or would you prefer I focus on a specific section first?