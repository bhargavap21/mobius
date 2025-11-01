# WebSocket & Agent Logs Code Review

## Executive Summary

The WebSocket and agent logging system is **well-architected** with good patterns for real-time progress tracking, but has several **critical issues** that need attention:

- ✅ **Good**: Event buffering, completion handling, heartbeat mechanism
- ⚠️ **Issues**: HTTPS→WSS conversion, session cleanup, memory leaks, missing error recovery
- 🔧 **Improvements**: Reconnection logic, better error messages, connection state management

---

## Architecture Overview

### Components

1. **ProgressManager** (`backend/progress_manager.py`)
   - Manages session queues and event history
   - Provides typed event emission methods
   - Singleton pattern (global instance)

2. **WebSocket Endpoint** (`backend/main.py:465`)
   - `/ws/strategy/progress/{session_id}`
   - Streams events from queue to client
   - Handles buffered events for late joiners

3. **Frontend Component** (`frontend/frontend/src/components/AgentActivityLogWS.jsx`)
   - React component that connects to WebSocket
   - Displays phase status and event log
   - Handles completion callback

4. **Job Storage** (`backend/job_storage.py`)
   - In-memory storage for completed results
   - Allows result retrieval after connection drops

---

## Critical Issues

### 1. ❌ **HTTPS→WSS Conversion Bug** (HIGH PRIORITY)

**Location**: `frontend/frontend/src/config.js:17`

```javascript
export const WS_URL = API_URL.replace(/^http/, 'ws')
```

**Problem**: 
- Replaces `http` with `ws` but doesn't handle `https` → `wss`
- In production (HTTPS), this creates `ws://` URLs which fail
- Should be: `API_URL.replace(/^https?/, (match) => match === 'https' ? 'wss' : 'ws')`

**Impact**: WebSocket connections fail in production

**Fix**:
```javascript
export const WS_URL = API_URL.replace(/^https?/, (match) => 
  match === 'https' ? 'wss' : 'ws'
)
```

---

### 2. ⚠️ **Session Cleanup Race Condition** (MEDIUM PRIORITY)

**Location**: `backend/progress_manager.py:23-26`

```python
def close_session(self, session_id: str):
    """Close and cleanup a progress session"""
    if session_id in self.sessions:
        del self.sessions[session_id]
```

**Problem**:
- Only removes from `sessions` dict, not `event_history`
- Event history grows unbounded (memory leak)
- Multiple WebSocket connections to same session can cause issues

**Impact**: Memory leaks over time, especially with many sessions

**Fix**:
```python
def close_session(self, session_id: str):
    """Close and cleanup a progress session"""
    if session_id in self.sessions:
        del self.sessions[session_id]
    # Optionally keep event_history for later retrieval, but limit size
    # Or delete after TTL: self.event_history.pop(session_id, None)
```

---

### 3. ⚠️ **No Reconnection Logic** (MEDIUM PRIORITY)

**Location**: `frontend/frontend/src/components/AgentActivityLogWS.jsx:24-94`

**Problem**:
- If WebSocket disconnects, component shows error but doesn't reconnect
- User must manually refresh page
- No exponential backoff or retry logic

**Impact**: Poor UX, workflow failures on transient network issues

**Fix**: Add reconnection logic with exponential backoff:
```javascript
const reconnectWithBackoff = (attempt = 0) => {
  const delay = Math.min(1000 * Math.pow(2, attempt), 30000) // Max 30s
  setTimeout(() => {
    if (!cleanedUp && !isCompleteRef.current) {
      console.log(`[AgentActivityLogWS] Reconnecting (attempt ${attempt + 1})...`)
      connectWS()
    }
  }, delay)
}
```

---

### 4. ⚠️ **Missing Error Details** (LOW PRIORITY)

**Location**: `frontend/frontend/src/components/AgentActivityLogWS.jsx:78-83`

**Problem**:
- Generic error message: "Connection error. Please refresh the page."
- Doesn't differentiate between network errors, server errors, auth errors
- No error code or details exposed to user

**Impact**: Difficult to debug issues in production

**Fix**: Add error type detection and more informative messages

---

### 5. ⚠️ **Memory Leak in Event History** (MEDIUM PRIORITY)

**Location**: `backend/progress_manager.py:47-49`

```python
if session_id not in self.event_history:
    self.event_history[session_id] = []
self.event_history[session_id].append(event)
```

**Problem**:
- `event_history` grows indefinitely
- No cleanup mechanism
- Old sessions accumulate in memory

**Impact**: Memory usage grows over time, potential OOM errors

**Fix**: Add TTL-based cleanup or limit history size per session

---

### 6. ⚠️ **Heartbeat Timeout Too Long** (LOW PRIORITY)

**Location**: `backend/main.py:506`

```python
event = await asyncio.wait_for(queue.get(), timeout=300.0)  # 5 minutes
```

**Problem**:
- 5-minute timeout is very long
- Heartbeat only sent on timeout, not proactively
- Client may think connection is dead during long operations

**Impact**: Poor UX during long-running workflows

**Fix**: Send proactive heartbeats every 30 seconds regardless of events

---

## Code Quality Issues

### 1. **Inconsistent Error Handling**

**Location**: `backend/main.py:515-522`

- Some errors are caught and logged, others raise
- `WebSocketDisconnect` is handled, but other exceptions may not be
- No centralized error handling strategy

### 2. **Magic Numbers**

- `300.0` (timeout) - should be configurable
- `0.5` (sleep delay) - should be configurable
- `24` (TTL hours) - should be configurable

### 3. **Missing Type Hints**

Some methods in `progress_manager.py` lack proper type hints:
```python
async def emit_event(self, session_id: str, event: Dict[str, Any]):
    # event should have a TypedDict or Pydantic model
```

---

## Strengths

### ✅ **Event Buffering**
- Stores events in `event_history` for late joiners
- Sends buffered events when WebSocket connects
- Prevents missing events if client connects late

### ✅ **Completion Handling**
- 500ms delay before closing WebSocket ensures client receives final event
- Uses refs in React to avoid race conditions
- Proper cleanup on component unmount

### ✅ **Heartbeat Mechanism**
- Prevents connection timeout during long operations
- Keeps connection alive even when no events

### ✅ **Job Storage Fallback**
- Allows result retrieval via HTTP if WebSocket fails
- Good backup mechanism for reliability

### ✅ **Phase Status Tracking**
- Visual phase indicators in UI
- Shows which agent is currently active
- Clear user feedback

---

## Recommendations

### High Priority Fixes

1. **Fix HTTPS→WSS conversion** (Production blocker)
2. **Add session cleanup** (Memory leak)
3. **Add reconnection logic** (UX improvement)

### Medium Priority Improvements

1. **Add proactive heartbeats** (Better UX)
2. **Limit event history size** (Memory management)
3. **Add error type detection** (Better debugging)

### Low Priority Enhancements

1. **Configuration for timeouts** (Flexibility)
2. **Typed event schemas** (Type safety)
3. **Connection state indicators** (UX)

---

## Testing Recommendations

1. **Test HTTPS→WSS conversion** in production-like environment
2. **Test reconnection** with network interruption simulation
3. **Load test** with many concurrent sessions
4. **Memory leak test** with long-running sessions
5. **Error scenarios**: Server restart, network drop, timeout

---

## Code Examples

### Fixed WebSocket URL Configuration

```javascript
// frontend/frontend/src/config.js
const getWsUrl = () => {
  const apiUrl = getApiUrl()
  if (apiUrl.startsWith('https')) {
    return apiUrl.replace(/^https/, 'wss')
  }
  return apiUrl.replace(/^http/, 'ws')
}

export const WS_URL = getWsUrl()
```

### Improved Session Cleanup

```python
# backend/progress_manager.py
def close_session(self, session_id: str):
    """Close and cleanup a progress session"""
    if session_id in self.sessions:
        del self.sessions[session_id]
    
    # Cleanup event history after TTL (24 hours)
    # Or implement per-session cleanup based on completion
    # Keep for job_storage retrieval, but limit size
    if session_id in self.event_history:
        events = self.event_history[session_id]
        if len(events) > 1000:  # Limit to last 1000 events
            self.event_history[session_id] = events[-1000:]
```

### Reconnection Logic

```javascript
// frontend/frontend/src/components/AgentActivityLogWS.jsx
const MAX_RECONNECT_ATTEMPTS = 5
const reconnectWithBackoff = (attempt = 0) => {
  if (attempt >= MAX_RECONNECT_ATTEMPTS) {
    setError('Failed to reconnect after multiple attempts. Please refresh.')
    return
  }
  
  const delay = Math.min(1000 * Math.pow(2, attempt), 30000)
  setTimeout(() => {
    if (!cleanedUp && !isCompleteRef.current) {
      console.log(`[AgentActivityLogWS] Reconnecting (attempt ${attempt + 1})...`)
      connectWS()
    }
  }, delay)
}

ws.onclose = () => {
  console.log('[AgentActivityLogWS] 🔌 WebSocket connection closed')
  if (!cleanedUp && !isCompleteRef.current) {
    reconnectWithBackoff()
  }
}
```

---

## Summary

The WebSocket implementation is **solid** but has **critical production issues** that need immediate attention:

1. ✅ **Architecture**: Well-designed with good separation of concerns
2. ❌ **Production Readiness**: HTTPS→WSS bug blocks production
3. ⚠️ **Reliability**: Missing reconnection and cleanup logic
4. ✅ **User Experience**: Good visual feedback, but could be improved with reconnection

**Priority**: Fix HTTPS→WSS conversion first, then add reconnection logic, then memory management.

