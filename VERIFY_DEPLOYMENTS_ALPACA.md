# How to Verify Deployments Are Working on Alpaca Dashboard

## Quick Checklist

Based on your screenshots showing $0.00 P&L and no trades, here's how to verify and debug:

## 1. Check Alpaca Dashboard Directly

### What to Look For:

**A. Orders Tab** (Most Important)
- Go to Alpaca Dashboard → **"Orders"** or **"Activity"** tab
- Look for:
  - ✅ **Submitted orders** (even if not filled)
  - ✅ **Filled orders** (actual trades executed)
  - ✅ **Rejected orders** (indicates issues)

**B. Positions Tab**
- Go to **"Positions"** tab
- Should show open positions if strategies are buying

**C. Portfolio Value**
- Your portfolio value should change if trades execute
- Currently showing $100,000 (paper trading)
- If strategies buy stocks, cash decreases and positions increase

**D. Activity/History**
- Check **"Activity"** or **"History"** section
- Shows all order submissions, fills, and cancellations

## 2. Verify Deployment Activation Status

### Critical Issue: Deployments Must Be "Activated"

Your deployments show "RUNNING" status, but they might not be **activated** in the trading engine.

**Check if activated:**
```bash
# Check backend logs for activation
fly logs -a mobius-s4cz7q | grep -i "activated\|add_deployment"
```

**Activate a deployment:**
```bash
# Via API (replace DEPLOYMENT_ID and YOUR_TOKEN)
curl -X POST https://mobius-s4cz7q.fly.dev/deployments/{DEPLOYMENT_ID}/activate \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Or via Frontend:**
- Your deployment page should have an "Activate" button
- Click it to add deployment to trading engine

## 3. Check Backend Logs

### What to Look For:

**A. Strategy Execution Logs**
```bash
fly logs -a mobius-s4cz7q | grep -E "Executing strategy|trading signal|order placed"
```

**Expected logs:**
- `🔄 Executing strategy for deployment {id}`
- `📊 No trading signal generated` (if conditions not met)
- `🟢 Entry signal for {symbol}` (if buy signal)
- `📈 BUY order placed` (if order submitted)

**B. Alpaca API Calls**
```bash
fly logs -a mobius-s4cz7q | grep -E "Alpaca|order placed|Failed to place"
```

**C. Errors**
```bash
fly logs -a mobius-s4cz7q | grep -E "ERROR|Error|Failed|Exception"
```

## 4. Common Issues & Solutions

### Issue 1: Deployments Not Activated ✅ MOST LIKELY

**Symptom:** Status shows "RUNNING" but no trades

**Solution:**
1. Check if deployment is in `active_deployments` dict
2. Call `/activate` endpoint
3. Verify in logs: `✅ Added deployment {id} to trading engine`

### Issue 2: Strategies Not Generating Signals

**Symptom:** Logs show "No trading signal generated"

**Possible Causes:**
- Entry conditions not met (RSI, sentiment, etc.)
- Market data unavailable
- Strategy code errors

**Debug:**
```bash
# Check strategy execution logs
fly logs -a mobius-s4cz7q | grep -E "check_entry_conditions|signal"
```

### Issue 3: Market Hours Check

**Symptom:** Strategies only run during market hours

**Current Code:**
```python
# Market check is commented out (line 199-201)
# if not self._is_market_open():
#     return
```

**Status:** ✅ Should work 24/7 (market check disabled)

### Issue 4: Alpaca API Errors

**Symptom:** Orders rejected or API errors

**Check:**
```bash
fly logs -a mobius-s4cz7q | grep -E "Alpaca|API|Failed|rejected"
```

**Common Issues:**
- Invalid API keys
- Account blocked
- Insufficient buying power
- Invalid order parameters

## 5. Manual Testing Steps

### Step 1: Verify Trading Engine Started
```bash
fly logs -a mobius-s4cz7q | grep "Live Trading Engine started"
```

Should see: `✅ Live Trading Engine started`

### Step 2: Check Active Deployments
```bash
fly logs -a mobius-s4cz7q | grep "Added deployment\|active_deployments"
```

### Step 3: Monitor Strategy Execution
```bash
# Watch logs in real-time
fly logs -a mobius-s4cz7q -f | grep -E "Executing|signal|order"
```

### Step 4: Test Alpaca Connection
```bash
# Test API endpoint (if you have one)
curl https://mobius-s4cz7q.fly.dev/api/test/alpaca
```

## 6. Expected Behavior Timeline

### When Deployment is Activated:

1. **Immediate:**
   - Log: `✅ Added deployment {id} to trading engine`
   - Deployment scheduled based on frequency (1min, 5min, etc.)

2. **At Scheduled Time:**
   - Log: `🔄 Executing strategy for deployment {id}`
   - Strategy code runs
   - Entry/exit conditions checked

3. **If Signal Generated:**
   - Log: `🟢 Entry signal for {SYMBOL}` or `🔴 Exit signal`
   - Order placed: `📈 BUY order placed: {qty} shares`
   - **Alpaca Dashboard shows order immediately**

4. **After Order Fill:**
   - Position appears in Alpaca "Positions" tab
   - Portfolio value updates
   - Cash decreases, positions increase

## 7. Quick Diagnostic Script

Create a test endpoint to check deployment status:

```python
# Add to backend/main.py
@app.get("/api/debug/deployments")
async def debug_deployments():
    from services.live_trading_engine import trading_engine
    return {
        "trading_engine_running": trading_engine.scheduler.running,
        "active_deployments": list(trading_engine.active_deployments.keys()),
        "scheduled_jobs": [job.id for job in trading_engine.scheduler.get_jobs()]
    }
```

## 8. Most Likely Issue: Deployments Not Activated

Based on your code, deployments are created but **not automatically activated**. You need to:

1. **Call the activate endpoint** for each deployment
2. **Or modify code** to auto-activate on creation

### Quick Fix: Auto-Activate on Creation

```python
# In backend/routes/deployment_routes.py, after creating deployment:
deployment = await deployment_repo.create_deployment(...)

# Auto-activate
success = await trading_engine.add_deployment(deployment.id)
if success:
    logger.info(f"✅ Auto-activated deployment {deployment.id}")
```

## Summary

**To verify deployments are working:**

1. ✅ **Check Alpaca Dashboard → Orders tab** (most reliable)
2. ✅ **Check backend logs** for execution messages
3. ✅ **Verify deployments are activated** (not just created)
4. ✅ **Monitor logs in real-time** during scheduled execution times

**Most likely issue:** Deployments are created but not activated in the trading engine scheduler.

