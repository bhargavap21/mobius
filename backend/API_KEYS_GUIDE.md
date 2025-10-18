# API Keys Guide for Real Historical Sentiment Data

This trading bot uses **REAL historical data** from multiple sources. No mock data is used.

## Required API Keys for Full Functionality

### 1. **Quiver Quantitative** (WSB Historical Data) ⭐ RECOMMENDED
- **What it provides**: Historical r/wallstreetbets mention counts and sentiment
- **Free tier**: 20 requests/minute
- **Sign up**: https://www.quiverquant.com/
- **Get API Key**:
  1. Create account at https://www.quiverquant.com/register
  2. Go to Dashboard → API
  3. Copy your API key
- **Add to .env**: `QUIVER_API_KEY=your_key_here`

### 2. **Polygon.io** (Market & News Sentiment) ⭐ RECOMMENDED
- **What it provides**: Historical news sentiment, market data
- **Free tier**: 5 API calls/minute
- **Sign up**: https://polygon.io/
- **Get API Key**:
  1. Sign up at https://polygon.io/dashboard/signup
  2. API key is shown in dashboard
- **Add to .env**: `POLYGON_API_KEY=your_key_here`

### 3. **StockTwits** (Trader Sentiment)
- **What it provides**: Real-time trader sentiment (limited historical in free tier)
- **Free tier**: No API key needed for basic access
- **Historical data**: Requires paid subscription
- **No API key needed for basic functionality**

### 4. **IEX Cloud** (Social Sentiment Indicators)
- **What it provides**: Aggregated social sentiment scores
- **Free tier**: 50,000 messages/month
- **Sign up**: https://iexcloud.io/
- **Get API Key**:
  1. Create account at https://iexcloud.io/console/
  2. Get publishable token from API Tokens section
- **Add to .env**: `IEX_API_KEY=your_publishable_token_here`

### 5. **Alpha Vantage** (News Sentiment)
- **What it provides**: News sentiment analysis
- **Free tier**: 25 requests/day
- **Sign up**: https://www.alphavantage.co/
- **Get API Key**:
  1. Get free key at https://www.alphavantage.co/support/#api-key
- **Add to .env**: `ALPHA_VANTAGE_API_KEY=your_key_here`

### 6. **Finnhub** (Alternative Social Data)
- **What it provides**: Reddit/Twitter sentiment aggregation
- **Free tier**: 60 API calls/minute
- **Sign up**: https://finnhub.io/
- **Get API Key**:
  1. Register at https://finnhub.io/register
  2. API key shown after registration
- **Add to .env**: `FINNHUB_API_KEY=your_key_here`

## Setting Up Your .env File

Create a `.env` file in the `backend` directory with your API keys:

```env
# Core APIs (Required)
ANTHROPIC_API_KEY=your_anthropic_key

# Reddit API (for current data)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=TradingBot/1.0

# Historical Data APIs (At least 1-2 recommended)
QUIVER_API_KEY=your_quiver_key          # Best for WSB data
POLYGON_API_KEY=your_polygon_key        # Good for news sentiment
IEX_API_KEY=your_iex_key               # Social sentiment
ALPHA_VANTAGE_API_KEY=your_av_key      # News sentiment
FINNHUB_API_KEY=your_finnhub_key       # Alternative source
```

## Priority Recommendations

For best results with WSB/Reddit strategies:
1. **Get Quiver Quantitative API key** (best WSB historical data)
2. **Get Polygon.io API key** (news + market sentiment)
3. **Optional**: IEX Cloud for additional coverage

## Testing Your API Keys

Run the test script to verify your APIs are working:

```bash
python test_real_apis.py
```

## Data Availability Notes

- **Quiver**: Has WSB data going back to 2020
- **Polygon**: News data for last 2 years (free tier)
- **StockTwits**: Real-time only in free tier
- **IEX Cloud**: Rolling 30-day window (free tier)
- **Alpha Vantage**: Recent news only (7 days)
- **Finnhub**: Last 1 year of sentiment data

## Fallback Behavior

If no API keys are configured:
- System will log warnings about missing data
- Backtesting will show "No historical data available"
- Only current Reddit data (via PRAW) will work

## Important: No Mock Data

This system uses **ONLY REAL DATA**. If historical sentiment is not available:
- The system will return `None`
- Trades won't execute without sentiment data
- This is by design - we don't fake functionality