# Multi-Bot Tracking on Single Alpaca Account

## Problem Statement

You have **1 Alpaca paper trading account** but want to track **multiple bots/deployments** independently. Currently, all bots share:
- Same cash pool
- Same positions
- Same portfolio value

This makes it impossible to track individual bot performance.

## Current Implementation Issues

### ✅ What Works
1. **Trade Attribution**: Each trade is logged with `deployment_id` ✅
2. **Trade History**: Can query trades per deployment ✅
3. **Alpaca Order ID**: Links trades to Alpaca orders ✅

### ❌ What's Broken
1. **Performance Metrics**: All deployments show same portfolio value (they all read from same Alpaca account)
2. **Position Tracking**: All deployments see ALL positions, not just their own
3. **Capital Allocation**: No virtual capital allocation per deployment
4. **P&L Calculation**: Can't calculate individual bot P&L accurately

## Solution: Virtual Portfolio Tracking

### Approach 1: Virtual Capital Allocation (Recommended) ⭐

**Concept**: Each deployment gets a "virtual" capital allocation, tracked separately from the real Alpaca account.

#### How It Works

1. **Virtual Capital Per Deployment**
   - Each deployment has `initial_capital` (e.g., $10,000)
   - Track `virtual_cash` and `virtual_positions` per deployment
   - Real Alpaca account is just the execution layer

2. **Trade Attribution**
   - When deployment makes trade → Log it with `deployment_id`
   - Track which deployment owns which positions
   - Calculate P&L based on virtual capital, not account total

3. **Position Ownership**
   - Track `deployment_positions` table (already exists!)
   - Each position linked to specific `deployment_id`
   - Calculate unrealized P&L per deployment

4. **Performance Calculation**
   - `deployment_pnl = sum(trade_realized_pnl) + sum(position_unrealized_pnl)`
   - `deployment_return = deployment_pnl / initial_capital`
   - Independent of other deployments

#### Implementation Changes Needed

```python
# Current (WRONG):
async def _update_metrics(self, deployment_id: str):
    account = await alpaca_service.get_account()  # ❌ Shared account
    portfolio_value = float(account['portfolio_value'])  # ❌ Same for all
    
# Fixed (CORRECT):
async def _update_metrics(self, deployment_id: str):
    # Get only THIS deployment's trades
    trades = await self.deployment_repo.get_deployment_trades(deployment_id)
    
    # Get only THIS deployment's positions
    positions = await self.deployment_repo.get_deployment_positions(deployment_id)
    
    # Calculate virtual portfolio value
    virtual_cash = deployment.initial_capital - sum(trade.total_value for trade in trades if trade.side == 'buy')
    virtual_positions_value = sum(pos.market_value for pos in positions)
    virtual_portfolio_value = virtual_cash + virtual_positions_value
    
    # Calculate deployment-specific P&L
    realized_pnl = sum(trade.realized_pnl for trade in trades if trade.realized_pnl)
    unrealized_pnl = sum(pos.unrealized_pnl for pos in positions)
    total_pnl = realized_pnl + unrealized_pnl
    total_return_pct = (total_pnl / deployment.initial_capital) * 100
```

### Approach 2: Position Allocation (Alternative)

**Concept**: When multiple deployments trade same symbol, allocate shares proportionally.

**Example**:
- Deployment A buys 10 AAPL
- Deployment B buys 5 AAPL
- Alpaca account has 15 AAPL total
- Track: Deployment A owns 10/15 = 66.7%, Deployment B owns 5/15 = 33.3%

**Pros**: More accurate for shared positions
**Cons**: Complex allocation logic, harder to implement

### Approach 3: Separate Alpaca Accounts (Not Recommended)

**Concept**: Create separate Alpaca paper accounts per deployment.

**Pros**: True isolation
**Cons**: 
- Alpaca limits (usually 1 paper account per user)
- More API keys to manage
- Can't easily compare performance

## Recommended Implementation Plan

### Phase 1: Fix Position Tracking ✅ (Partially Done)

**Current State**: `deployment_positions` table exists but not properly used

**Fix**:
1. When trade executes → Update `deployment_positions` table
2. Track position ownership per deployment
3. Calculate unrealized P&L per deployment

### Phase 2: Fix Performance Metrics ⚠️ (Critical)

**Current State**: All deployments show same portfolio value

**Fix**:
1. Calculate virtual portfolio per deployment
2. Track realized P&L from trades
3. Track unrealized P&L from positions
4. Calculate return % independently

### Phase 3: Virtual Capital Management

**Enhancement**:
1. Track `virtual_cash` per deployment
2. Enforce position limits per deployment
3. Prevent over-allocation

## Database Schema (Already Good!)

Your schema already supports this:

```sql
-- deployment_trades: Tracks which deployment made which trade ✅
deployment_id, alpaca_order_id, symbol, side, quantity, filled_avg_price, realized_pnl

-- deployment_positions: Tracks positions per deployment ✅
deployment_id, symbol, quantity, average_entry_price, current_price, unrealized_pnl

-- deployment_metrics: Tracks performance per deployment ✅
deployment_id, portfolio_value, total_return_pct, realized_pnl, unrealized_pnl
```

## Code Changes Needed

### 1. Fix `_update_metrics()` Function

**File**: `backend/services/live_trading_engine.py`

**Current Issue**: Uses shared Alpaca account for all deployments

**Fix**: Calculate metrics from deployment-specific trades and positions

### 2. Fix Position Tracking

**File**: `backend/services/live_trading_engine.py` → `_process_signal()`

**Current Issue**: Updates all positions, not deployment-specific

**Fix**: Only update positions for the specific deployment

### 3. Add Trade Matching Logic

**New Feature**: Match Alpaca orders to deployments

**Why**: When you query Alpaca for all positions, need to know which deployment owns which shares

## Example: How It Should Work

### Scenario: 2 Deployments, Same Symbol

**Deployment A**:
- Initial Capital: $10,000
- Buys 10 AAPL @ $150 = $1,500
- Virtual Cash: $8,500
- Virtual Positions: 10 AAPL @ $150

**Deployment B**:
- Initial Capital: $10,000  
- Buys 5 AAPL @ $150 = $750
- Virtual Cash: $9,250
- Virtual Positions: 5 AAPL @ $150

**Alpaca Account** (Real):
- Cash: $18,250
- Positions: 15 AAPL @ $150 avg

**Performance Tracking**:
- Deployment A: Tracks its own 10 AAPL, calculates P&L independently
- Deployment B: Tracks its own 5 AAPL, calculates P&L independently
- No interference between deployments

## Next Steps

1. **Fix `_update_metrics()`** to use deployment-specific data
2. **Fix position tracking** to be deployment-specific
3. **Add trade matching** logic for position attribution
4. **Test** with multiple deployments on same symbol

Would you like me to implement these fixes?

