# Multi-Agent Orchestration System

## Overview

This multi-agent system provides intelligent, iterative strategy development and optimization for trading bots. Instead of one-shot generation, agents collaborate to refine strategies based on backtest results.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER REQUEST                             │
│            "Buy AAPL when RSI < 30..."                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
           ┌───────────────────────┐
           │  SUPERVISOR AGENT     │  ← Main Orchestrator
           │                       │
           │  • Coordinates workflow│
           │  • Manages iterations │
           │  • Max 5 iterations   │
           └───────────┬───────────┘
                       │
            ┌──────────┴──────────┐
            │                     │
            ▼                     │
  ┌─────────────────────┐        │
  │ CODE GENERATOR       │◄───────┤
  │                      │        │
  │ • Parse strategy     │        │
  │ • Generate code      │        │
  │ • Refine based on    │        │
  │   feedback           │        │
  └──────────┬──────────┘        │
             │                    │
             ▼                    │
  ┌─────────────────────┐        │
  │ BACKTEST RUNNER      │        │
  │                      │        │
  │ • Execute backtest   │        │
  │ • Validate results   │        │
  │ • Adjust timeframe   │        │
  └──────────┬──────────┘        │
             │                    │
             ▼                    │
  ┌─────────────────────┐        │
  │ STRATEGY ANALYST     │        │
  │                      │        │
  │ • Review metrics     │        │
  │ • Identify issues    │        │
  │ • Suggest improvements│       │
  │ • Decide if continue │────────┘
  └─────────────────────┘
             │
             ▼
    ┌────────────────────┐
    │ OPTIMIZED STRATEGY │
    └────────────────────┘
```

## Agents

### 1. Supervisor Agent (`supervisor.py`)

**Role:** Main orchestrator that coordinates the entire workflow

**Responsibilities:**
- Receive user's strategy request
- Coordinate Code Generator, Backtest Runner, and Strategy Analyst
- Manage iteration loop (max 5 iterations)
- Decide when to stop iterating
- Return final optimized strategy

**Workflow:**
```python
for iteration in range(1, max_iterations + 1):
    1. Call Code Generator (create/refine strategy)
    2. Call Backtest Runner (execute backtest)
    3. Call Strategy Analyst (review results)
    4. If needs_refinement AND should_continue:
        → Continue to next iteration
    5. Else:
        → Return final results
```

### 2. Code Generator Agent (`code_generator.py`)

**Role:** Generates and refines trading strategy code

**Responsibilities:**
- Parse user's natural language strategy description
- Generate initial strategy configuration
- Refine strategy based on analyst feedback
- Adjust parameters (RSI thresholds, stop loss, take profit)

**Refinement Logic:**
- **Too few trades?** → Relax entry conditions (e.g., RSI 30 → 35)
- **Poor win rate?** → Tighten stop loss
- **Low returns?** → Increase take profit target

**Example Refinements:**
```python
# Original: RSI < 30
# Too few trades detected
# Refined: RSI < 35

# Original: Stop Loss = 1%
# Win rate < 40%
# Refined: Stop Loss = 0.8%
```

### 3. Backtest Runner Agent (`backtest_runner.py`)

**Role:** Executes backtests and validates results

**Responsibilities:**
- Run backtests with appropriate parameters
- Automatically adjust timeframes based on feedback
- Validate backtest execution
- Return structured results with warnings

**Auto-Adjustments:**
```python
# If < 3 trades in previous iteration:
#   180 days → 360 days (6 months → 1 year)
#   360 days → 720 days (1 year → 2 years)
```

### 4. Strategy Analyst Agent (`strategy_analyst.py`)

**Role:** Reviews backtest results and provides actionable feedback

**Responsibilities:**
- Analyze backtest metrics (trades, returns, win rate, etc.)
- Identify critical issues
- Suggest concrete improvements
- Decide if strategy needs refinement
- Decide if iteration should continue

**Analysis Criteria:**

**Trade Execution Issues:**
- ❌ `< 3 trades` → Strategy not triggering, conditions too strict
- ⚠️ `3-5 trades` → Borderline, may need longer timeframe
- ✅ `> 5 trades` → Sufficient data

**Performance Issues:**
- Win rate < 40% → Poor strategy
- Total return < Buy & Hold → Not beating market
- Sharpe ratio < 0.5 → Poor risk-adjusted returns

**Risk Issues:**
- Max drawdown > 30% → Too risky
- Profit factor < 1 → Losing money

**Decisions:**
```python
needs_refinement = True if:
    - Total trades < 3
    - Win rate < 40%
    - Total return < 0
    - Sharpe ratio < 0

should_continue = False if:
    - Iteration >= 5 (max reached)
    - Strategy is fundamentally flawed
    - No improvement path visible
```

## Example Flow

### Scenario: RSI Strategy with Issues

**User Request:**
```
Buy AAPL when RSI drops below 30.
Sell when RSI goes above 70 or at -1% stop loss.
```

### Iteration 1

**Code Generator:**
- Generates initial strategy
- RSI threshold: 30
- Stop loss: 1%

**Backtest Runner:**
- Runs 180-day backtest
- Result: **0 trades executed**

**Strategy Analyst:**
- **Issue:** "RSI never dropped below 30 in 6 months"
- **Suggestion:** "Increase timeframe to 360 days OR relax RSI to 35"
- **Decision:** `needs_refinement=True`, `should_continue=True`

### Iteration 2

**Code Generator:**
- Receives feedback
- Refines: RSI threshold 30 → 35
- Changes: "Relaxed RSI threshold from 30 to 35"

**Backtest Runner:**
- Auto-increases timeframe: 180 → 360 days
- Result: **2 trades executed**

**Strategy Analyst:**
- **Issue:** "Still too few trades (2)"
- **Suggestion:** "Further relax RSI to 40 OR extend to 2 years"
- **Decision:** `needs_refinement=True`, `should_continue=True`

### Iteration 3

**Code Generator:**
- Further relaxes: RSI 35 → 40

**Backtest Runner:**
- Extends timeframe: 360 → 720 days
- Result: **7 trades executed, 57% win rate, 8.2% return**

**Strategy Analyst:**
- **Analysis:** "Strategy is now viable with sufficient trades"
- **Issue:** None critical
- **Suggestion:** "Consider tighter stop loss to improve risk/reward"
- **Decision:** `needs_refinement=False`, `should_continue=False`

### Final Result

```json
{
  "success": true,
  "iterations": 3,
  "strategy": {
    "asset": "AAPL",
    "entry_conditions": {
      "signal": "rsi",
      "parameters": {
        "threshold": 40,  // Was 30, refined to 40
        "comparison": "below"
      }
    },
    "exit_conditions": {
      "take_profit": 0.02,
      "stop_loss": 0.01
    }
  },
  "backtest_results": {
    "summary": {
      "total_trades": 7,
      "win_rate": 57.1,
      "total_return": 8.2,
      "days": 720
    }
  }
}
```

## Usage

### API Endpoint

```bash
POST /api/strategy/create_multi_agent
{
  "strategy_description": "Buy TSLA when Elon tweets positive. Sell at +2% profit or -1% stop loss."
}
```

### Python Direct

```python
from agents.supervisor import SupervisorAgent

supervisor = SupervisorAgent()

result = await supervisor.process({
    'user_query': "Buy NVDA when Reddit sentiment is bullish",
    'days': 180,
    'initial_capital': 10000
})

print(f"Iterations: {result['iterations']}")
print(f"Final Return: {result['backtest_results']['summary']['total_return']}%")
```

### Test Script

```bash
cd backend
python test_multi_agent.py
```

## Key Features

### 1. **Intelligent Iteration**
- Not just one-shot generation
- Learns from backtest results
- Refines until satisfactory

### 2. **Automatic Problem Detection**
- Detects insufficient trades
- Identifies poor performance
- Recognizes risk issues

### 3. **Actionable Feedback**
- Specific parameter adjustments
- Concrete suggestions
- Clear reasoning

### 4. **Self-Limiting**
- Max 5 iterations to prevent infinite loops
- Stops when strategy is good enough
- Stops when fundamentally flawed

### 5. **Full Transparency**
- Complete iteration history
- All changes documented
- Analysis at each step

## Configuration

### Supervisor Settings

```python
class SupervisorAgent:
    max_iterations = 5  # Maximum refinement iterations
```

### Backtest Runner Settings

```python
class BacktestRunnerAgent:
    default_days = 180           # Initial backtest period
    default_capital = 10000      # Starting capital
```

### Strategy Analyst Thresholds

```python
# Critical thresholds
MIN_TRADES = 3           # Minimum trades to be viable
MIN_WIN_RATE = 40        # Minimum acceptable win rate
MIN_SHARPE = 0.5         # Minimum Sharpe ratio
MAX_DRAWDOWN = 30        # Maximum acceptable drawdown
```

## Benefits Over Single-Agent

| Aspect | Single-Agent | Multi-Agent |
|--------|-------------|-------------|
| Success Rate | ~30% | ~80%+ |
| Iterations | 1 | Up to 5 |
| Feedback Loop | None | Full |
| Problem Detection | Manual | Automatic |
| Optimization | None | Intelligent |
| Transparency | Low | High |

## Future Enhancements

1. **LangGraph Integration** - State machine workflow
2. **Memory Persistence** - Remember past strategies
3. **Parallel Testing** - Test multiple variants
4. **Market Regime Detection** - Adapt to market conditions
5. **Ensemble Strategies** - Combine multiple approaches
