# 🚀 Setup Instructions - Get Started in 10 Minutes

## Step 1: Get Your API Keys (5 minutes)

### 1.1 Anthropic Claude API (Required)
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to **API Keys** in the dashboard
4. Click **Create Key**
5. Copy the key (starts with `sk-ant-...`)

💰 **Cost:** ~$2-5 for entire hackathon
⏱️ **Time:** 2 minutes

### 1.2 Alpaca Paper Trading (Required)
1. Go to https://alpaca.markets
2. Click **Sign Up** (free account)
3. Complete registration
4. **Enable MFA** (Multi-Factor Authentication) - Required by Alpaca
   - You'll see a prompt asking to "Activate" MFA
   - Click "Activate" and set up an authenticator app (Google Authenticator, Authy, etc.)
5. After MFA is set up, click **"API"** in the left sidebar
6. Look for **"Paper Trading"** or **"Your API Keys"** section
7. You should see:
   - **API Key ID** (starts with `PK...`)
   - **Secret Key** (click "Regenerate" if you need to see it again)
8. Copy both keys - you'll need them for `.env` file

> **Important:**
> - Make sure you see "Paper Trading" indicator at the top (should say "Paper - [ID]")
> - Paper trading uses fake money - perfect for development!
> - If you don't see API keys, look for a "Generate" button

💰 **Cost:** FREE (paper trading with $100K virtual money)
⏱️ **Time:** 5 minutes (including MFA setup)

### 1.3 Reddit API (Optional - Can Mock)
1. Go to https://www.reddit.com/prefs/apps
2. Scroll down, click **Create App** or **Create Another App**
3. Fill in:
   - **Name:** TradingBot
   - **Type:** Select "script"
   - **Description:** Trading strategy bot
   - **Redirect URI:** http://localhost:8080
4. Click **Create app**
5. Copy:
   - **Client ID** (under app name)
   - **Secret** (labeled as "secret")

💰 **Cost:** FREE
⏱️ **Time:** 2 minutes (optional - can skip for MVP)

---

## Step 2: Configure Environment (1 minute)

1. **Copy the example environment file:**
```bash
cp .env.example .env
```

2. **Edit `.env` file and add your keys:**
```bash
# Open in your favorite editor
nano .env
# or
code .env
```

3. **Fill in the required keys:**
```env
# REQUIRED
ANTHROPIC_API_KEY=sk-ant-your-key-here
ALPACA_API_KEY=PKyour-key-here
ALPACA_SECRET_KEY=your-secret-here

# OPTIONAL (can leave blank for MVP)
REDDIT_CLIENT_ID=your-reddit-client-id
REDDIT_CLIENT_SECRET=your-reddit-secret
```

4. **Save and close**

---

## Step 3: Install Dependencies (3 minutes)

### Backend (Python)

Dependencies are already installed! But if you need to reinstall:

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate     # Windows

# Install all dependencies
pip install -r backend/requirements.txt
```

### Frontend (Node.js)

```bash
cd frontend
npm install
cd ..
```

---

## Step 4: Test Your Setup (1 minute)

Run the test script to verify all APIs are working:

```bash
# Make sure venv is activated
source venv/bin/activate

# Run tests
python backend/test_setup.py
```

### Expected Output:

```
============================================================
🚀 Testing API Connections for Trading Bot
============================================================

🤖 Testing Claude API...
✅ Claude API: API connection successful

📈 Testing Alpaca API...
✅ Alpaca API Connected!
   Account Status: ACTIVE
   Buying Power: $100,000.00
   Cash: $100,000.00

🔴 Testing Reddit API...
✅ Reddit API Connected!
   Subreddit: r/wallstreetbets
   Subscribers: 15,234,567

============================================================
📊 Summary:
============================================================
✅ Claude API: Connected
✅ Alpaca API: Connected
✅ Reddit API: Connected

🎉 All critical APIs are working! Ready to proceed.
```

### Troubleshooting:

#### ❌ Claude API Failed
- Check your API key in `.env`
- Verify key starts with `sk-ant-`
- Check https://console.anthropic.com for credits

#### ❌ Alpaca API Failed
- Verify you're using **paper trading** keys (not live)
- Check keys are copied correctly (no extra spaces)
- Ensure `ALPACA_BASE_URL=https://paper-api.alpaca.markets`

#### ⚠️ Reddit API Optional (Not Configured)
- This is fine! Reddit is optional for MVP
- You can test with mock data
- Or follow Step 1.3 to set it up

---

## Step 5: You're Ready! 🎉

Your development environment is set up. Next steps:

1. **Start Phase 2:** Build the Claude orchestrator
2. **Check the plan:** See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)

### Quick Commands Reference:

```bash
# Activate virtual environment
source venv/bin/activate

# Test API connections
python backend/test_setup.py

# Start backend (later)
cd backend
uvicorn main:app --reload

# Start frontend (later)
cd frontend
npm run dev
```

---

## 📊 Phase 1 Complete! ✅

**What you've accomplished:**
- ✅ Created project structure
- ✅ Installed Python dependencies
- ✅ Got API keys (Anthropic + Alpaca)
- ✅ Configured environment variables
- ✅ Tested API connections
- ✅ Ready to code!

**Time spent:** ~10 minutes
**Progress:** 4% complete (2 hours of 48)

---

## 🚀 Next Steps

Ready to start Phase 2? Let's build the AI orchestrator!

```bash
# Continue to Phase 2
# See IMPLEMENTATION_PLAN.md - Phase 2: Claude Orchestration Core
```

**Estimated time for Phase 2:** 4 hours
**Goal:** Claude AI that can understand requests and call tools

---

## 📚 Resources

- **Implementation Plan:** [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)
- **Claude Docs:** https://docs.anthropic.com
- **Alpaca Docs:** https://docs.alpaca.markets
- **Project README:** [README.md](README.md)

---

## 🆘 Need Help?

**Common Issues:**

1. **Virtual environment not activating**
   ```bash
   # Recreate it
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Import errors**
   ```bash
   # Reinstall dependencies
   pip install -r backend/requirements.txt
   ```

3. **API keys not working**
   - Check `.env` file format (no quotes, no spaces)
   - Verify keys are valid in respective dashboards
   - Try regenerating keys

4. **Still stuck?**
   - Check [README.md](README.md)
   - Review [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)
   - Google the specific error message

---

**You're all set! Let's build something amazing! 🚀**
