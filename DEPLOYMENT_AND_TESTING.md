# Deployment & Testing Guide for WebSocket Fixes

## ⚠️ Important: Fixes Must Be Deployed

**The fixes are currently only in your local codebase.** They will NOT be active in production until you deploy them.

---

## 🧪 Step 1: Local Testing (Before Deployment)

Test all fixes locally first to ensure they work correctly.

### Prerequisites
```bash
# Make sure you're in the project root
cd /Users/bhargavap/dubhacks25

# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies
cd ../frontend/frontend
npm install
```

### Test Setup

**Terminal 1 - Start Backend:**
```bash
cd backend
source ../venv/bin/activate  # Or your venv path
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Start Frontend:**
```bash
cd frontend/frontend
npm run dev
```

### Test Scenarios

#### ✅ Test 1: HTTPS→WSS Conversion (Local)

**Check config.js output:**
1. Open browser console (F12)
2. Look for: `API Configuration: { API_URL: 'http://localhost:8000', WS_URL: 'ws://localhost:8000' }`
3. Verify WS_URL starts with `ws://` (correct for localhost)

**Test manually:**
```javascript
// In browser console
import { WS_URL } from './config'
console.log('WS_URL:', WS_URL)
// Should show: ws://localhost:8000/ws/strategy/progress/...
```

#### ✅ Test 2: WebSocket Connection & Heartbeat

1. **Start a strategy generation** in the UI
2. **Open browser DevTools → Network → WS (WebSocket)**
3. **Check for:**
   - Connection establishes successfully
   - Heartbeat messages every ~30 seconds (check `message` tab)
   - Messages show `{"type":"heartbeat"}`

**Expected Console Output:**
```
[AgentActivityLogWS] ✅ WebSocket connection established
[AgentActivityLogWS] 💓 Heartbeat received  (every 30 seconds)
```

**Backend Logs Should Show:**
```
💓 Sent proactive heartbeat (session: ...)
```

#### ✅ Test 3: Reconnection Logic

**Simulate Network Disruption:**

**Option A - Browser DevTools:**
1. Open DevTools → Network tab
2. Right-click on WebSocket connection → "Block request URL"
3. Wait for disconnection
4. **Expected:** Yellow "Reconnecting..." message appears
5. Unblock and **Expected:** Connection reconnects automatically

**Option B - Network Throttling:**
1. DevTools → Network → Throttling → "Offline"
2. Wait a few seconds
3. Set back to "Online"
4. **Expected:** Automatic reconnection with exponential backoff

**Check Console for:**
```
[AgentActivityLogWS] 🔄 Scheduling reconnect attempt 1 in 1000ms...
[AgentActivityLogWS] 🔄 Reconnecting (attempt 1)...
[AgentActivityLogWS] ✅ WebSocket connection established
```

#### ✅ Test 4: Memory Leak Prevention

**Check Event History Limiting:**

1. **Create a session** and generate a strategy
2. **In backend logs**, watch for event history size
3. **Generate many events** (use a complex strategy with many iterations)
4. **Verify:** Event history doesn't exceed 1000 events per session

**Manual Check:**
```python
# In Python shell (connect to your running backend)
from progress_manager import progress_manager
session_id = "your-test-session-id"
if session_id in progress_manager.event_history:
    print(f"Event count: {len(progress_manager.event_history[session_id])}")
    # Should be <= 1000
```

#### ✅ Test 5: Session Cleanup

1. **Complete a workflow** (let it finish normally)
2. **Check backend logs** for session cleanup
3. **Verify:** Session removed from `sessions` dict
4. **Verify:** Event history trimmed or kept (based on keep_history flag)

---

## 🚀 Step 2: Deploy to Production

### Backend Deployment (Fly.io)

```bash
# 1. Navigate to backend directory
cd backend

# 2. Verify changes are committed
git status
# Should show modified files:
# - progress_manager.py
# - main.py

# 3. Commit changes (if not already committed)
git add progress_manager.py main.py
git commit -m "Fix WebSocket: HTTPS→WSS, reconnection, heartbeat, memory leaks"

# 4. Deploy to Fly.io
flyctl deploy

# 5. Monitor deployment
flyctl logs --follow

# 6. Verify deployment
flyctl status
# Should show: Status: running
```

**Expected Output:**
```
==> Building image
==> Creating release
==> Release vX created
==> Deploying...
==> App deployed successfully
```

### Frontend Deployment (Vercel)

```bash
# 1. Navigate to frontend directory
cd ../frontend/frontend

# 2. Verify changes are committed
git status
# Should show modified files:
# - src/config.js
# - src/components/AgentActivityLogWS.jsx

# 3. Commit changes (if not already committed)
git add src/config.js src/components/AgentActivityLogWS.jsx
git commit -m "Fix WebSocket: HTTPS→WSS conversion, reconnection logic"

# 4. Deploy to Vercel
vercel --prod

# 5. Monitor deployment
# Check Vercel dashboard for build logs
```

**Expected Output:**
```
Vercel CLI 32.x.x
> Deploying to production...
> Build completed
✅ Production: https://your-app.vercel.app
```

---

## ✅ Step 3: Production Verification

### Verify HTTPS→WSS Conversion (CRITICAL)

**This is the most important test!**

1. **Open production app** in browser: `https://your-app.vercel.app`
2. **Open DevTools Console** (F12)
3. **Check API Configuration:**
   ```javascript
   // Should see in console:
   API Configuration: { 
     API_URL: 'https://your-backend.fly.dev', 
     WS_URL: 'wss://your-backend.fly.dev'  // ← Must start with wss://
   }
   ```

**If WS_URL starts with `ws://` instead of `wss://`:**
- ❌ **BUG STILL EXISTS** - Check `config.js` deployment
- Re-deploy frontend

**Manual Verification:**
```javascript
// In browser console on production site
import { WS_URL } from './config'
console.log('WS_URL:', WS_URL)
// Must show: wss://your-backend.fly.dev/ws/strategy/progress/...
```

### Verify WebSocket Connection

1. **Start a strategy generation** in production
2. **Open DevTools → Network → WS tab**
3. **Verify:**
   - Connection URL starts with `wss://` ✅
   - Connection establishes successfully ✅
   - Status shows "101 Switching Protocols" ✅

**If connection fails:**
- Check browser console for errors
- Verify backend CORS includes your Vercel URL
- Check `flyctl logs` for backend errors

### Verify Heartbeat Mechanism

1. **Start a strategy generation**
2. **Wait 30-40 seconds** (don't interact)
3. **Check WebSocket messages** in DevTools
4. **Expected:** See heartbeat messages every ~30 seconds

**In DevTools Network → WS → Messages:**
```
{"type":"heartbeat"}
{"type":"heartbeat"}  // ~30 seconds later
{"type":"heartbeat"}  // ~30 seconds later
```

**Backend Logs:**
```bash
flyctl logs --follow
# Should show every 30 seconds:
💓 Sent proactive heartbeat (session: ...)
```

### Verify Reconnection Logic

**Test in Production:**

1. **Start a strategy generation**
2. **Simulate network loss:**
   - Turn off WiFi for 5 seconds
   - Or use DevTools → Network → Offline
3. **Expected:**
   - Yellow "Reconnecting..." message appears
   - Console shows reconnection attempts
   - Connection re-establishes automatically
   - Strategy generation continues

**Check Browser Console:**
```
[AgentActivityLogWS] 🔄 Scheduling reconnect attempt 1 in 1000ms...
[AgentActivityLogWS] 🔄 Reconnecting (attempt 1)...
[AgentActivityLogWS] ✅ WebSocket connection established
```

### Verify Memory Management

**Monitor Backend Memory:**

```bash
# Check backend memory usage
flyctl status
# Look for memory metrics

# Check logs for event history size
flyctl logs | grep "event_history"
```

**Expected:** Event history should not grow unbounded. Each session should max at 1000 events.

---

## 🐛 Troubleshooting

### Issue: WebSocket still uses `ws://` in production

**Symptoms:** Browser console shows `ws://` URL, connection fails

**Fix:**
1. Verify `frontend/frontend/src/config.js` has the fix
2. Clear browser cache
3. Hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
4. Check Vercel deployment logs for build errors
5. Re-deploy frontend: `vercel --prod --force`

### Issue: Heartbeat not working

**Symptoms:** No heartbeat messages every 30 seconds

**Fix:**
1. Check backend logs: `flyctl logs`
2. Verify backend deployment includes new `main.py`
3. Check for errors in heartbeat task
4. Re-deploy backend: `flyctl deploy`

### Issue: Reconnection not working

**Symptoms:** Connection drops and doesn't reconnect

**Fix:**
1. Check browser console for JavaScript errors
2. Verify `AgentActivityLogWS.jsx` changes are deployed
3. Check for conflicts with other WebSocket code
4. Clear browser cache and retry

### Issue: Memory still growing

**Symptoms:** Backend memory usage increasing

**Fix:**
1. Verify `progress_manager.py` changes deployed
2. Check backend logs for event history size
3. Restart backend: `flyctl restart`
4. Monitor memory: `flyctl status`

---

## 📊 Production Monitoring

### Key Metrics to Watch

**Backend (Fly.io):**
```bash
# Check app status
flyctl status

# Monitor logs
flyctl logs --follow

# Check memory usage
flyctl metrics
```

**Frontend (Vercel):**
- Check Vercel dashboard → Analytics
- Monitor WebSocket connection errors
- Check browser console errors

### Expected Behavior After Fixes

✅ **WebSocket connections** use `wss://` in production  
✅ **Heartbeats** sent every 30 seconds  
✅ **Automatic reconnection** on network issues  
✅ **Memory usage** stable (event history capped at 1000)  
✅ **Session cleanup** works properly  

---

## 🎯 Quick Verification Checklist

- [ ] Local testing completed successfully
- [ ] Backend deployed to Fly.io
- [ ] Frontend deployed to Vercel
- [ ] Production WebSocket uses `wss://` (check browser console)
- [ ] Heartbeat messages appear every 30 seconds
- [ ] Reconnection works (test with network interruption)
- [ ] No memory leaks (monitor backend metrics)
- [ ] All fixes working in production

---

## 🚨 Critical: Test HTTPS→WSS Immediately

**This is a production blocker!** Test this first:

1. Deploy frontend
2. Open production site
3. Check browser console for `WS_URL`
4. **MUST show `wss://`** - if not, fix immediately!

---

## 📝 Notes

- **Backend changes** (`progress_manager.py`, `main.py`) require backend deployment
- **Frontend changes** (`config.js`, `AgentActivityLogWS.jsx`) require frontend deployment
- **Both must be deployed** for all fixes to work together
- **Test locally first** to catch issues before production
- **Monitor logs** after deployment for any errors

