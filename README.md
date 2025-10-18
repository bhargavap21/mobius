# 🤖 AI Trading Bot - Self-Learning Trading Strategies

> Transform plain English into professional trading bots that backtest, deploy, and improve themselves.

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- API Keys:
  - Anthropic Claude API
  - Alpaca (paper trading account)
  - Reddit API (optional)

### Setup

1. **Clone and navigate to project:**
```bash
cd dubhacks25
```

2. **Set up backend:**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

3. **Configure environment variables:**
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API keys
```

4. **Test API connections:**
```bash
python backend/test_setup.py
```

5. **Set up frontend:**
```bash
cd frontend
npm install
npm run dev
```

6. **Start backend server:**
```bash
# In a new terminal
cd backend
uvicorn main:app --reload
```

## 🎯 What This Does

**Input:** "Buy TSLA when Elon tweets something positive. Sell at +2% or -1%"

**Output:**
1. ✅ Parses your strategy into structured format
2. ✅ Generates Python trading bot code
3. ✅ Backtests on 2 years of historical data
4. ✅ Shows performance metrics (win rate, Sharpe ratio, etc.)
5. ✅ Deploys to paper trading
6. ✅ Monitors live performance
7. ✅ Suggests improvements based on results

## 🏗️ Architecture

```
User Request (Natural Language)
         ↓
Claude AI Orchestrator
         ↓
    ┌────┴────┐
    │  Tools  │
    ├─────────┤
    │ Market Data (Alpaca, yfinance)
    │ Social Media (Reddit, Twitter)
    │ Web Scraping (BeautifulSoup)
    │ Code Generation (Claude)
    │ Backtesting (Backtrader)
    │ Live Trading (Alpaca)
    └─────────┘
         ↓
Working Trading Bot
```

## 📁 Project Structure

```
dubhacks25/
├── backend/
│   ├── main.py                 # FastAPI server
│   ├── orchestrator.py         # Claude AI orchestration
│   ├── config.py               # Configuration
│   ├── test_setup.py          # API connection tests
│   └── tools/
│       ├── market_data.py      # Stock prices, indicators
│       ├── social_media.py     # Reddit/Twitter sentiment
│       ├── web_scraper.py      # Generic web scraping
│       ├── code_generator.py   # Generate trading code
│       ├── backtester.py       # Backtest engine
│       ├── live_trader.py      # Live trading execution
│       └── analyzer.py         # Performance analysis
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   ├── StrategyInput.jsx
│   │   │   ├── BacktestResults.jsx
│   │   │   └── LiveDashboard.jsx
│   │   └── components/
│   └── package.json
├── .env.example
└── IMPLEMENTATION_PLAN.md
```

## 🔑 Getting API Keys

### Anthropic Claude API
1. Go to https://console.anthropic.com/
2. Sign up / Log in
3. Go to API Keys section
4. Create new API key
5. Add to `.env`: `ANTHROPIC_API_KEY=sk-...`

### Alpaca (Paper Trading)
1. Go to https://alpaca.markets
2. Sign up for free account
3. Enable paper trading
4. Get API keys from dashboard
5. Add to `.env`:
   ```
   ALPACA_API_KEY=PK...
   ALPACA_SECRET_KEY=...
   ```

### Reddit API (Optional)
1. Go to https://www.reddit.com/prefs/apps
2. Create app (script type)
3. Get client ID and secret
4. Add to `.env`:
   ```
   REDDIT_CLIENT_ID=...
   REDDIT_CLIENT_SECRET=...
   ```

## 🎮 Usage Examples

### Example 1: Simple Technical Strategy
```
"Buy AAPL when RSI goes below 30, sell when it hits 70"
```

### Example 2: Social Sentiment Strategy
```
"Buy NVDA when r/wallstreetbets sentiment is bullish and mentions spike above 100"
```

### Example 3: News-Based Strategy
```
"Buy tech stocks when positive AI news articles increase by 50%"
```

### Example 4: Elon Tweet Strategy (Demo Favorite!)
```
"Buy TSLA when Elon Musk tweets positively about Tesla. Sell at +2% profit or -1% stop loss"
```

## 🧪 Development

### Run Tests
```bash
# Backend tests
pytest backend/tests/

# Frontend tests
cd frontend
npm test
```

### Code Style
```bash
# Python
black backend/
pylint backend/

# JavaScript
cd frontend
npm run lint
```

## 📊 Tech Stack

- **AI**: Claude Sonnet 4.5 (Anthropic)
- **Backend**: Python, FastAPI
- **Frontend**: React, Vite, Tailwind CSS
- **Trading**: Alpaca API (paper trading)
- **Data**: yfinance, Reddit (PRAW), Twitter
- **Backtesting**: Backtrader
- **Technical Analysis**: TA-Lib

## ⚠️ Disclaimer

This is a **paper trading demo** for educational purposes.

- Only uses fake money (Alpaca paper trading)
- Not financial advice
- Past performance ≠ future results
- Trading involves risk

## 🏆 Built for DubHacks 2025

Team: [Your Team Name]
Track: INVENT

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

This is a hackathon project, but feel free to fork and improve!

## 📧 Contact

Questions? Reach out to [your-email]

---

**Made with ❤️ and Claude AI**
