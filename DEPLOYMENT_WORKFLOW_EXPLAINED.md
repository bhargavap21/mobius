# Deployment Workflow & Alpaca's Role Explained

## High-Level Overview

**Your System**: Virtual portfolio tracking + Strategy execution engine
**Alpaca**: Execution layer only (order placement & account management)

Think of it like this:
- **Your System** = The brain (decides what to trade, tracks performance)
- **Alpaca** = The hands (executes trades, holds positions)

## Complete Deployment Workflow

### Phase 1: Deployment Creation

```
User → Frontend → POST /deployments
                ↓
        1. Validate bot exists
        2. Get Alpaca account info (check balance, status)
        3. Create deployment record in database
        4. Set initial_capital (virtual allocation)
        5. Auto-activate deployment (if status='running')
                ↓
        Returns: Deployment object
```

**What Happens**:
- ✅ Deployment record created in `deployments` table
- ✅ Initial metrics logged (portfolio_value = initial_capital)
- ✅ Deployment added to trading engine scheduler
- ✅ Alpaca account checked (but no trades yet)

**Alpaca's Role**: 
- Provides account balance/status
- No trades executed yet

---

### Phase 2: Strategy Execution (Scheduled)

```
Trading Engine Scheduler (every 1min/5min/15min/etc.)
                ↓
        _execute_strategy(deployment_id)
                ↓
        1. Load deployment config & strategy code
        2. Run strategy code (Python exec)
        3. Strategy checks entry/exit conditions
        4. Returns signal: {'action': 'buy'/'sell', 'symbol': 'AAPL', 'quantity': 10}
                ↓
        If signal generated:
                ↓
        _process_signal(deployment_id, signal)
```

**What Happens**:
- Strategy code executes (checks RSI, sentiment, etc.)
- Generates buy/sell signal if conditions met
- No Alpaca interaction yet

**Alpaca's Role**: 
- None yet (strategy evaluation only)

---

### Phase 3: Trade Execution

```
_process_signal() receives signal
                ↓
        1. Check position size limits (deployment-specific)
        2. Calculate position size (based on virtual cash)
        3. Place order via Alpaca API
                ↓
        alpaca_service.place_market_order()
                ↓
        Alpaca executes order (real trade)
                ↓
        Order response: {order_id, filled_qty, filled_avg_price, status}
```

**What Happens**:
- ✅ Order placed on Alpaca (real execution)
- ✅ Order logged in `deployment_trades` table
- ✅ Position updated in `deployment_positions` table
- ✅ Metrics updated (virtual portfolio)

**Alpaca's Role**: 
- **Executes the actual trade** (buy/sell shares)
- Returns order details (filled price, quantity, etc.)
- Updates Alpaca account (cash, positions)

---

### Phase 4: Position & Performance Tracking

```
After trade execution:
                ↓
        _update_deployment_position()
                ↓
        1. Update deployment_positions table
        2. Calculate unrealized P&L
        3. Track position ownership per deployment
                ↓
        _update_metrics()
                ↓
        1. Query deployment_trades (this deployment only)
        2. Query deployment_positions (this deployment only)
        3. Calculate virtual portfolio:
           - Virtual Cash = Initial - Buys + Sells
           - Virtual Positions Value = Sum of positions
           - Virtual Portfolio = Cash + Positions
        4. Calculate P&L:
           - Realized P&L = Sum of closed trades
           - Unrealized P&L = Sum of open positions
           - Total Return % = (Total P&L / Initial Capital) × 100
        5. Log metrics to deployment_metrics table
```

**What Happens**:
- ✅ Position tracked per deployment (independent)
- ✅ Performance calculated from deployment's own trades
- ✅ Metrics logged (portfolio_value, return_pct, etc.)

**Alpaca's Role**: 
- Provides current market prices (for unrealized P&L)
- **Does NOT** provide portfolio metrics (we calculate our own)

---

## Alpaca's Role: Execution Layer Only

### What Alpaca Does ✅

1. **Order Execution**
   - Receives buy/sell orders
   - Executes trades on real market (paper trading)
   - Returns fill details (price, quantity, order ID)

2. **Account Management**
   - Holds cash
   - Holds positions (shares)
   - Provides account balance

3. **Market Data** (Optional)
   - Current prices
   - Historical data
   - Market status

### What Alpaca Does NOT Do ❌

1. **Portfolio Tracking**
   - Alpaca doesn't know about your deployments
   - Alpaca sees ONE account, not multiple bots
   - Alpaca doesn't track per-bot performance

2. **Strategy Execution**
   - Alpaca doesn't run your strategies
   - Alpaca doesn't generate signals
   - Alpaca doesn't decide when to trade

3. **Virtual Portfolio Management**
   - Alpaca doesn't allocate capital per deployment
   - Alpaca doesn't track deployment-specific positions
   - Alpaca doesn't calculate per-deployment metrics

---

## The Separation: Virtual vs Real

### Virtual Layer (Your System)

```
Deployment A:
├── Virtual Cash: $8,500
├── Virtual Positions: 10 AAPL @ $150
├── Virtual Portfolio: $9,500
└── Performance: +5% return

Deployment B:
├── Virtual Cash: $9,250
├── Virtual Positions: 5 AAPL @ $150
├── Virtual Portfolio: $10,000
└── Performance: 0% return
```

**Tracked in**: Your database (`deployment_trades`, `deployment_positions`, `deployment_metrics`)

### Real Layer (Alpaca)

```
Alpaca Account:
├── Cash: $17,750
├── Positions: 15 AAPL total
└── Portfolio: $20,000
```

**Tracked in**: Alpaca's system (via API)

---

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR SYSTEM                              │
│                                                             │
│  1. User creates deployment                                 │
│     └─> Database: deployment record created                 │
│                                                             │
│  2. Trading engine schedules execution                      │
│     └─> Runs strategy code (Python exec)                    │
│     └─> Generates signal: {'buy', 'AAPL', 10}              │
│                                                             │
│  3. Process signal                                          │
│     └─> Check virtual cash (deployment-specific)           │
│     └─> Calculate position size                            │
│                                                             │
│  4. Execute trade                                           │
│     └─> Call Alpaca API: place_market_order()              │
│         │                                                  │
│         └──────────────────────────────────────────────┐   │
│                                                        │   │
└────────────────────────────────────────────────────────┼───┼─┘
                                                         │   │
                                                         ▼   │
┌─────────────────────────────────────────────────────────────┐
│                    ALPACA (Execution Layer)                  │
│                                                             │
│  1. Receives order                                          │
│     └─> Executes trade (buy 10 AAPL @ market)              │
│                                                             │
│  2. Updates account                                         │
│     └─> Cash: -$1,500                                       │
│     └─> Positions: +10 AAPL                                 │
│                                                             │
│  3. Returns order details                                   │
│     └─> {order_id, filled_qty, filled_avg_price}          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                                                         │
                                                         │
                                                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    YOUR SYSTEM (Tracking)                    │
│                                                             │
│  1. Log trade                                               │
│     └─> Database: deployment_trades record                  │
│         - deployment_id, symbol, side, quantity             │
│         - alpaca_order_id (links to Alpaca)                │
│                                                             │
│  2. Update position                                         │
│     └─> Database: deployment_positions record               │
│         - deployment_id, symbol, quantity                   │
│         - average_entry_price, unrealized_pnl               │
│                                                             │
│  3. Update metrics                                          │
│     └─> Database: deployment_metrics record                 │
│         - virtual_portfolio_value                           │
│         - total_return_pct                                  │
│         - realized_pnl, unrealized_pnl                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Points

### 1. Alpaca is Just the Execution Layer

- **Your system** decides what to trade
- **Alpaca** executes the trades
- **Your system** tracks performance independently

### 2. Virtual Portfolio Tracking

- Each deployment has its own virtual portfolio
- Calculated from deployment-specific trades/positions
- Independent of other deployments
- Independent of Alpaca account totals

### 3. Single Alpaca Account, Multiple Virtual Portfolios

- All deployments share ONE Alpaca account
- Each deployment has its OWN virtual portfolio
- Performance tracked separately per deployment

### 4. Why This Architecture?

**Benefits**:
- ✅ Track multiple bots independently
- ✅ Compare bot performance
- ✅ Allocate capital per bot
- ✅ Test strategies without separate accounts

**Trade-offs**:
- ⚠️ All bots share same cash pool (in reality)
- ⚠️ Need to manage position conflicts manually
- ⚠️ Virtual tracking vs real account can diverge

---

## Example: Two Deployments Trading Same Symbol

### Deployment A
- **Virtual**: Buys 10 AAPL @ $150 = $1,500
- **Alpaca**: Executes buy order (10 AAPL)
- **Tracking**: Logs trade, updates position, calculates metrics

### Deployment B  
- **Virtual**: Buys 5 AAPL @ $150 = $750
- **Alpaca**: Executes buy order (5 AAPL)
- **Tracking**: Logs trade, updates position, calculates metrics

### Alpaca Account
- **Real**: Has 15 AAPL total (10 + 5)
- **Real**: Cash decreased by $2,250 total
- **Sees**: One account, doesn't know about deployments

### Your System
- **Deployment A**: Tracks its 10 AAPL, calculates its P&L
- **Deployment B**: Tracks its 5 AAPL, calculates its P&L
- **Independent**: Each deployment's performance calculated separately

---

## Summary

**Alpaca's Role**: 
- ✅ Order execution (buy/sell shares)
- ✅ Account management (cash, positions)
- ✅ Market data (prices, status)

**Your System's Role**:
- ✅ Strategy execution (decides what to trade)
- ✅ Virtual portfolio tracking (per deployment)
- ✅ Performance metrics (per deployment)
- ✅ Trade attribution (which deployment made which trade)

**The Separation**:
- Alpaca = Execution layer (real trades)
- Your System = Intelligence layer (strategy + tracking)

This architecture lets you track multiple bots independently while using a single Alpaca account for execution.

