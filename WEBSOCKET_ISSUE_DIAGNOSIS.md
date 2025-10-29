# WebSocket Premature Closure - Root Cause Analysis

## The Problem
WebSocket connections are closing before the `complete` event is delivered to the frontend, showing "Connection closed unexpectedly" error.

## Root Cause Identified

**The WebSocket has a 30-second timeout** (line 486 in main.py):
```python
event = await asyncio.wait_for(queue.get(), timeout=30.0)
```

**The workflow blocks for too long** between the last regular event and the complete event:
1. Supervisor finishes processing (~2min for backtest)
2. Control returns to `_run_multi_agent_workflow()`
3. **Database save happens** (lines 384-400) - This is BLOCKING and slow
4. **Result storage happens** (line 404)
5. **Complete event is finally emitted** (line 422)

During step 3-5, **NO events are in the queue** for 30+ seconds, so the WebSocket timeout fires and closes the connection.

## Why The Previous Fixes Didn't Work

1. ❌ **Adding `asyncio.sleep()` after emit** - Event was never retrieved by WebSocket because it closed before emit
2. ❌ **Adding delay before closing WS after sending** - Client disconnected BEFORE server could send
3. ❌ **Moving emit_complete to after job_storage** - Still too slow, WebSocket timeout already fired

## The Architectural Fix Required

**Move slow operations to background task:**

```python
# BEFORE (BROKEN):
supervisor.process()  # 2min, sends events regularly
# [30+ seconds of silence while doing database operations]
database_save()  # BLOCKING - no events during this time
job_storage.store()
emit_complete()  # Too late - WebSocket timed out 30 seconds ago!

# AFTER (FIXED):
supervisor.process()  # 2min, sends events regularly
job_storage.store()  # Fast, synchronous
emit_complete()  # Immediate - WebSocket still alive!
asyncio.create_task(database_save())  # Background - doesn't block
```

## The Fix

In `/Users/bhargavap/dubhacks25/backend/main.py` lines 384-432:

1. **Store result in job_storage FIRST** (it's fast, synchronous)
2. **Emit complete event IMMEDIATELY**
3. **Move database save to background task** using `asyncio.create_task()`

This ensures:
- ✅ Complete event emitted within seconds of supervisor finishing
- ✅ WebSocket doesn't timeout (events flowing regularly)
- ✅ Result available when frontend receives complete event
- ✅ Database save still happens, just in background

## Implementation
See the Edit command above for the exact code change needed.
