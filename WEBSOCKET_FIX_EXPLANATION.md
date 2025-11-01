# WebSocket Disconnection & Missing Events Fix

## 🔍 Root Cause Analysis

### The Problem

You were seeing:
1. ✅ WebSocket connects successfully
2. ❌ WebSocket disconnects immediately (causing reconnect)
3. ✅ WebSocket reconnects successfully
4. ✅ Heartbeats work (every 30 seconds)
5. ❌ **NO workflow events received**

### Why This Happened

**The Bug:**
When the WebSocket disconnected, the code was calling `progress_manager.close_session()`, which **deleted the session queue**. Here's what happened:

1. **Session created** → Queue created
2. **WebSocket connects** → Gets queue reference
3. **WebSocket disconnects** → `close_session()` **deletes the queue**
4. **Workflow starts** → Tries to emit events to **deleted queue**
5. **Events go nowhere** → Logged as warning: `⚠️ Session not in active sessions!`
6. **WebSocket reconnects** → Creates **new queue**, but workflow is using **old deleted queue**

**Result:** Events emitted to a non-existent queue, so they never reached the client.

### Why WebSocket Disconnects Initially

The initial disconnect could be caused by:
- Network latency during connection establishment
- Server-side connection timeout
- Load balancer/proxy timeout
- Browser WebSocket connection retry logic

Regardless of the cause, the fix ensures events aren't lost.

---

## ✅ The Fix

### Changes Made

1. **Don't delete session on disconnect** (`backend/main.py:562-578`)
   - Keep session queue alive for reconnections
   - Only close session when workflow completes

2. **Close session only on completion** (`backend/main.py:554-556`)
   - Close session when `complete` or `error` event is sent
   - Keep event history for job_storage retrieval

3. **Auto-create session if missing** (`backend/main.py:663-668`)
   - If workflow starts but session doesn't exist (reconnection case), create it
   - Prevents "Session not found" errors

4. **Better buffered event handling** (`backend/main.py:488-494`)
   - Improved error handling when sending buffered events
   - Prevents connection failures from blocking event delivery

---

## 🧪 Testing the Fix

### Before Fix (What You Saw)
```
[AgentActivityLogWS] 🔄 Reconnecting (attempt 1)...
[AgentActivityLogWS] ✅ WebSocket connection established
[AgentActivityLogWS] 📨 Received event: {type: 'ready'}
[AgentActivityLogWS] 💓 Heartbeat received  (repeatedly)
❌ NO workflow events
```

### After Fix (Expected)
```
[AgentActivityLogWS] ✅ WebSocket connection established
[AgentActivityLogWS] 📨 Received event: {type: 'ready'}
[AgentActivityLogWS] 📨 Received event: {type: 'agent_start', agent: 'Supervisor', ...}
[AgentActivityLogWS] 📨 Received event: {type: 'agent_start', agent: 'CodeGenerator', ...}
[AgentActivityLogWS] 📨 Received event: {type: 'agent_complete', agent: 'CodeGenerator', ...}
... (all workflow events)
```

### Test Steps

1. **Deploy the fix:**
   ```bash
   cd backend
   git add main.py
   git commit -m "Fix WebSocket session cleanup causing missing events"
   flyctl deploy
   ```

2. **Generate a strategy:**
   - Start a strategy generation
   - Watch browser console for events
   - Should see workflow events, not just heartbeats

3. **Test reconnection:**
   - Start a strategy
   - Simulate network drop (DevTools → Network → Offline)
   - Wait for reconnection
   - **Expected:** Reconnects and receives all buffered events

4. **Check backend logs:**
   ```bash
   flyctl logs --follow
   ```
   
   **Look for:**
   - `✅ Session verified/created`
   - `🚀 Launching workflow task`
   - `📡 Attempting to emit event to session`
   - `📥 Event added to queue`

---

## 📊 Expected Behavior After Fix

### Normal Flow
1. ✅ Session created
2. ✅ WebSocket connects
3. ✅ Workflow starts
4. ✅ Events emitted to queue
5. ✅ WebSocket receives events in real-time
6. ✅ Workflow completes
7. ✅ Session closed

### Reconnection Flow
1. ✅ Session created
2. ✅ WebSocket connects
3. ✅ WebSocket disconnects (network issue)
4. ✅ **Session queue kept alive** (NEW!)
5. ✅ Workflow continues emitting to queue
6. ✅ WebSocket reconnects
7. ✅ Receives buffered events from `event_history`
8. ✅ Continues receiving new events from queue
9. ✅ Workflow completes

---

## 🔍 Debugging Commands

### Check if workflow is running:
```bash
flyctl logs | grep "Multi-Agent Workflow Starting"
```

### Check if events are being emitted:
```bash
flyctl logs | grep "Event emitted"
```

### Check session status:
```bash
flyctl logs | grep "Active sessions"
```

### Check for warnings:
```bash
flyctl logs | grep "⚠️"
```

---

## 🚨 If Events Still Missing

If you still don't see events after deploying:

1. **Check workflow is starting:**
   - Look for: `🤖 Multi-Agent Workflow Starting`
   - If missing, workflow might not be launching

2. **Check session exists:**
   - Look for: `✅ Session verified/created`
   - Verify session ID matches

3. **Check events are emitted:**
   - Look for: `📡 Attempting to emit event`
   - Check if session is in active sessions

4. **Check queue has events:**
   - Look for: `📥 Event added to queue (new size: X)`
   - If size stays 0, events aren't being added

5. **Check WebSocket is consuming:**
   - Look for: `📦 Retrieved event from queue`
   - If missing, WebSocket might not be reading from queue

---

## 📝 Summary

**Before:** Session deleted on disconnect → Events lost  
**After:** Session kept alive → Events buffered → Reconnection works

**Key Changes:**
- Session queue persists through disconnections
- Events buffered in `event_history` for late joiners
- Session only closed when workflow completes
- Better error handling and logging

This fix ensures workflow events are never lost, even if the WebSocket disconnects and reconnects multiple times.

