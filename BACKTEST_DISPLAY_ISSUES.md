# Backtest Display Issues

## 1. Precision and Formatting Issues
**Problem**: Numbers are not consistently rounded to 2 decimal places
- Total Return shows: `+8.71599258422851607%` (should be `+8.72%`)
- Take Profit shows: `+NaN%`
- Trade prices show excessive precision (e.g., `$186.037521362304`)

**Location**: Frontend display components
**Fix Required**: Round all numeric values to 2 decimal places in BacktestResults.jsx

---

## 2. Missing Portfolio Value Over Time Graph
**Problem**: "Portfolio Value Over Time" section exists but shows no chart/graph
- Section header is present
- No visual equity curve chart is rendered
- User cannot see portfolio growth over the backtest period

**Location**: BacktestResults.jsx - equity curve visualization
**Fix Required**: Implement chart component (likely using Chart.js or Recharts) to visualize equity_curve data

---

## 3. Missing Benchmark Comparison in Graph
**Problem**: No benchmark (Buy & Hold) line in the portfolio chart
- Backend calculates `buy_hold_return` (0%)
- Frontend shows "Outperformed by 8.72%" text
- But no visual comparison in the chart itself

**Location**: BacktestResults.jsx - chart should show both strategy and benchmark lines
**Fix Required**: Add benchmark equity curve data and render it alongside strategy performance

---

## 4. Strategy Evaluation Errors
**Problem**: Multiple validation errors in Strategy Evaluation section (Score: 0.78/1.0)

### Errors:
1. **[UserIntentMatch] entry_condition**: Parameters show 'threshold': 35 which conflicts with 'rsi_threshold': 30.0
2. **[UserIntentMatch] Misinterpretation**: Critical confusion in entry threshold - parameters show both 'threshold': 35 and 'rsi_threshold': 30.0, creating ambiguity about actual trigger level
3. **[UserIntentMatch] Misinterpretation**: Parameter structure includes many irrelevant fields that don't apply to RSI strategy
4. **[StrategyCoherence] [logical]**: Entry condition contradicts parameters: description says 'RSI drops below 30' but threshold parameter is set to 35, creating ambiguous trigger condition
5. **[StrategyCoherence] [logical]**: Redundant RSI exit thresholds: both 'rsi_exit_threshold': 70.0 in parameters AND 'Custom Exit Logic: RSI rises above 70' - unclear which takes precedence

### Warnings:
1. **[OutputSchemaEvaluator]**: Partial exit configured but no take profit level set
2. **[OutputSchemaEvaluator]**: take_profit_pct_shares is 1.0 (100%), which is a full exit, not partial

**Location**:
- Backend strategy schema generation (clarification_agent.py or code_generator.py)
- Evaluation pipeline (backend/evals/)
- Strategy metadata structure

**Fix Required**:
- Clean up parameter passing to avoid duplicate/conflicting thresholds
- Ensure user intent (RSI < 30) matches actual parameters
- Fix schema to properly represent full vs partial exits

---

## 5. Missing Trade Details
**Problem**: Trade history shows `$NaN` for multiple fields
- **Shares**: Shows `$NaN` (should show quantity like "58 shares")
- **Value**: Shows `$NaN` for both entry and exit (should show total position value)
- **Days Held**: Shows text "days held" but no actual number

**Example from Trade #1**:
```
Entry:
Date: 2025-02-20T00:00:00
Price: $186.037521362304
Shares: $NaN  ← MISSING
Value: $NaN   ← MISSING

Exit:
Date: 2025-02-26T00:00:00
Price: $174.136062620703
Shares: $NaN  ← MISSING
Value: $NaN   ← MISSING

days held     ← NO NUMBER
```

**Location**:
- Backend trade formatting in backtest_runner.py (`_format_trades_with_pnl()`)
- Frontend rendering in BacktestResults.jsx

**Fix Required**:
- Backend: Add `quantity` and `value` fields to formatted trades
- Backend: Calculate `days_held` from entry_date to exit_date
- Frontend: Display these fields properly (remove $ from shares, format value as currency)

---

## Priority Order (Suggested):
1. **Fix #5 (Missing Trade Details)** - Critical data missing from trades
2. **Fix #1 (Number Formatting)** - Easy fix, improves UX significantly
3. **Fix #2 (Portfolio Graph)** - Core visualization feature
4. **Fix #3 (Benchmark in Graph)** - Enhances graph with comparison
5. **Fix #4 (Strategy Evaluation)** - Most complex, requires schema/validation changes
