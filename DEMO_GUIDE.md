# 🚀 AI Trading Bot Generator - Demo Guide

## ✅ System Status

**Backend:** ✅ Running on http://localhost:8000
**Frontend:** ✅ Running on http://localhost:5173

---

## 🎬 Quick Demo Script (5 minutes)

### Opening (30 seconds)
"Hi! This is an AI-powered trading bot generator. You describe your trading strategy in plain English, and our AI writes production-ready Python code for you in seconds."

### Demo Flow

#### 1. Show the Interface (30 seconds)
- Point out the clean, dark UI
- Show the example strategies
- Explain: "These are pre-loaded examples you can try"

#### 2. The "Elon Tweet" Strategy (2 minutes) 🚀
**Click on: "Elon Tweet Strategy 🚀"**

Strategy loaded:
```
Buy TSLA when Elon Musk tweets something positive about Tesla.
Sell at +2% profit or -1% stop loss.
```

**Click "Generate Trading Bot"**

While generating (show loading spinner):
- "The AI is analyzing the strategy"
- "Identifying data sources needed: Twitter API, Stock prices"
- "Writing production-ready Python code"

**Show the Results:**
- Strategy Overview card
  - Asset: TSLA
  - Take Profit: +2.0%
  - Stop Loss: -1.0%
  - Data Sources: twitter, price

- Generated Code (194 lines!)
  - Point out: SentimentAnalyzer class
  - TwitterMonitor class
  - Trading logic with entry/exit
  - Risk management
  - Professional logging

**Key Points:**
- ✅ Complete, working code
- ✅ Includes error handling
- ✅ Production-ready
- ✅ Copy or download ready

#### 3. Custom Strategy (1.5 minutes)
**Click "New Strategy"**

Type your own:
```
Buy NVDA when:
1. Reddit sentiment on r/wallstreetbets is bullish (> 0.3)
2. Recent news is positive
3. Price is below recent high

Sell at +5% profit or -2% stop loss
```

**Generate and show:**
- More complex strategy
- Multiple data sources combined
- AI handles complexity automatically

#### 4. The Wow Factor (30 seconds)
- Show the download button
- "This code is ready to run with your API keys"
- Mention: "Normally takes hours to write, AI does it in seconds"

---

## 🎯 Judge Questions & Answers

### Q: "How does it work?"
**A:** "We use Claude Sonnet 4.5 to:
1. Parse natural language into structured parameters
2. Generate Python code using best practices
3. Include proper error handling and logging
4. Integrate with real APIs (Alpaca, Twitter, Reddit)"

### Q: "Can it really trade?"
**A:** "Yes! The code uses Alpaca's paper trading API - real trades with fake money. Perfect for testing. We show the Alpaca API connection in our test files."

### Q: "What makes this innovative?"
**A:**
- "Democratizes algo trading - no coding needed"
- "Multi-agent AI system with 11 specialized tools"
- "Real-time data integration (social media, news, prices)"
- "Production-ready code, not pseudocode"

### Q: "What's the tech stack?"
**A:**
- **AI:** Claude Sonnet 4.5 (via Anthropic API)
- **Backend:** Python, FastAPI
- **Frontend:** React, Tailwind CSS
- **Trading:** Alpaca API
- **Data:** Reddit (PRAW), Twitter, web scraping

### Q: "Did you train a model?"
**A:** "No - we use Claude's existing capabilities but architected a multi-agent system with 11 specialized tools. The innovation is in the orchestration and tool design."

### Q: "How long did this take?"
**A:** "Built in ~18 hours during the hackathon. Shows the power of modern AI tools for rapid prototyping."

---

## 💡 Key Features to Highlight

1. **Natural Language → Code**
   - No programming required
   - Handles complex strategies

2. **Multi-Source Data**
   - Social media sentiment
   - News analysis
   - Market data
   - Web scraping

3. **Production Ready**
   - Real API integration
   - Error handling
   - Logging
   - Risk management

4. **Beautiful UI**
   - Dark theme
   - Smooth animations
   - Copy/Download code

5. **11 AI Tools**
   - Market data (3)
   - Social media (3)
   - Web scraping (2)
   - Code generation (3)

---

## 🎨 Example Strategies to Try

### 1. Elon Tweet (Demo Favorite)
```
Buy TSLA when Elon Musk tweets something positive about Tesla.
Sell at +2% profit or -1% stop loss.
```

### 2. Reddit Sentiment
```
Buy GME when r/wallstreetbets sentiment is bullish (> 0.5).
Sell at +5% profit or -2% stop loss.
```

### 3. Technical Indicator
```
Buy AAPL when RSI drops below 30.
Sell when RSI goes above 70 or at -1% stop loss.
```

### 4. Multi-Source (Advanced)
```
Buy NVDA when:
- Reddit sentiment > 0.3
- Recent news is positive
- Current price is at least 2% below recent high

Sell when:
- Profit reaches 5% OR
- Loss reaches 2% OR
- Reddit sentiment turns negative
```

---

## 🏆 Why This Wins

### INVENT Track Criteria:

**✅ Bold Idea**
- AI that writes trading bots
- Democratizes quantitative trading

**✅ Bolder Build**
- Multi-agent AI system
- Real API integrations
- Production-ready code

**✅ Innovation**
- Novel application of AI
- Complex orchestration
- Multiple data sources

**✅ Unconventional**
- Not another CRUD app
- Practical and fun
- "Elon tweet" strategy = memorable

**✅ Pushing Boundaries**
- Natural language programming
- Financial AI application
- Self-learning potential

---

## 📊 Stats to Mention

- **194 lines** of generated code (Elon bot)
- **11 AI tools** in the system
- **4 data sources** integrated
- **~18 hours** build time
- **48-hour** hackathon project

---

## 🚨 Common Issues

### Frontend not loading?
```bash
cd /Users/bhargavap/dubhacks25/frontend/frontend
npm run dev
```

### Backend error?
```bash
cd /Users/bhargavap/dubhacks25/backend
source ../venv/bin/activate
python -m uvicorn main:app --reload
```

### CORS error?
- Check backend is running on port 8000
- Frontend should be on port 5173

---

## 🎤 Closing Statement

"This project shows how AI can make complex technical domains accessible to everyone. What used to take hours of coding and debugging now takes seconds. We're not just generating code - we're democratizing quantitative trading."

**Thank you!**

---

## 📁 Project Structure
```
dubhacks25/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── orchestrator.py      # AI orchestration
│   ├── tools/               # 11 specialized tools
│   └── test_*.py           # Demos
├── frontend/frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── components/
│   └── package.json
├── generated_elon_tweet_bot.py  # Example output
└── DEMO_GUIDE.md           # This file
```

---

**Built with ❤️ for DubHacks 2025**
