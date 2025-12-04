# Evaluator Data Reference

## Complete Context Available to All Evaluators

Every evaluator receives comprehensive data about the strategy, its execution, and what was shown to the user. This allows for thorough validation of system correctness.

---

## 📝 User Intent Data

### `user_input` (string)
**Original user query before clarification**

Example:
```
"Buy AAPL when RSI < 30"
```

**Use for:** Understanding what the user initially asked for

---

### `enriched_query` (string) ✨ **NEW**
**Clarified query after clarification agent filled in missing parameters**

Example:
```
"Buy AAPL when RSI drops below 30. Sell 50% of position when RSI goes above 70.
Use 2% stop loss. Backtest over 180 days with $10,000 initial capital."
```

**Use for:**
- Validating the system implemented what user ACTUALLY wanted (after clarifications)
- Checking partial exit percentages were correctly interpreted
- Verifying time periods and position sizing match user intent

---

## 🎯 Strategy Implementation

### `strategy` / `parsed_strategy` (dict)
**Parsed strategy configuration**

Structure:
```python
{
    "name": "RSI Mean Reversion Strategy",
    "asset": "AAPL",
    "indicators": {
        "rsi": {
            "period": 14,
            "overbought": 70,
            "oversold": 30
        }
    },
    "entry_conditions": [
        {"type": "indicator", "indicator": "rsi", "operator": "<", "value": 30}
    ],
    "exit_conditions": [
        {"type": "indicator", "indicator": "rsi", "operator": ">", "value": 70, "pct_shares": 0.5},
        {"type": "stop_loss", "value": 0.02, "pct_shares": 1.0}
    ],
    "position_size": 1.0,
    "max_positions": 1
}
```

**Use for:**
- Schema validation (OutputSchemaEvaluator)
- Parameter validation (StrategyParameterEvaluator)
- Logic coherence checking (StrategyCoherenceEvaluator)
- Comparing config to user intent (UserIntentMatchEvaluator)

---

### `generated_code` (string) ✨ **NEW**
**Full Python code generated for the strategy**

Example:
```python
class RSIMeanReversionStrategy(BaseStrategy):
    def __init__(self):
        self.rsi_period = 14
        # ... full implementation

    def calculate_signals(self, data):
        # ... entry/exit logic
        pass
```

**Use for:**
- Code quality checks
- Verify implementation matches configuration
- Check for common coding errors
- Validate partial exit logic in code

---

## 📊 Backtest Execution Data

### `backtest_results` (dict)
**Complete backtest results including all trades and metrics**

Structure:
```python
{
    "summary": {
        "total_trades": 10,
        "win_rate": 70.0,
        "total_return": 15.5,
        "sharpe_ratio": 1.2,
        "max_drawdown": -8.3,
        "buy_hold_return": 12.0,  # Benchmark comparison
        "total_pnl": 1550.0
    },
    "trades": [
        {
            "symbol": "AAPL",
            "side": "buy",
            "qty": 100,
            "price": 150.0,
            "timestamp": "2024-01-15T09:30:00",
            "reason": "RSI < 30 (28.5)"
        },
        {
            "symbol": "AAPL",
            "side": "sell",
            "qty": 50,
            "price": 155.0,
            "timestamp": "2024-01-20T15:45:00",
            "reason": "RSI > 70 (72.1) - partial exit 50%"
        }
    ],
    "equity_curve": [...],  # Portfolio value over time
    "insights_data": {...}  # Chart data (see below)
}
```

**Use for:**
- Trade validation (BacktestCorrectnessEvaluator)
- Performance vs benchmark comparison
- Trade execution validation against signals

---

### `trades` (list)
**Extracted from backtest_results for convenience**

Same as `backtest_results['trades']`

**Use for:** Iterating through trades without accessing nested dict

---

### `indicator_data` (dict)
**Time series of indicator values during backtest**

Structure:
```python
{
    "rsi": [
        {"timestamp": "2024-01-15T09:30:00", "value": 28.5},
        {"timestamp": "2024-01-15T10:00:00", "value": 29.1},
        {"timestamp": "2024-01-20T15:45:00", "value": 72.1},
        # ... full time series
    ],
    "macd": [...],
    "price": [
        {"timestamp": "2024-01-15T09:30:00", "close": 150.0},
        # ... full price history
    ]
}
```

**Use for:**
- **TradeExecutionValidatorEvaluator** - Cross-reference trades with indicator signals
- Verify trades happened when indicators triggered
- Check if partial exits executed on EVERY signal or just once

---

## 📈 Visualization Data ✨ **NEW**

### `insights_config` (dict)
**Configuration of what charts/visualizations were shown to user**

Structure:
```python
{
    "visualizations": [
        {
            "type": "indicator_overlay",
            "title": "RSI Indicator with Buy/Sell Signals",
            "indicators": ["rsi"],
            "thresholds": {"rsi": {"buy": 30, "sell": 70}},
            "show_trades": True
        },
        {
            "type": "equity_curve",
            "title": "Portfolio Value Over Time",
            "compare_benchmark": True
        },
        {
            "type": "trade_distribution",
            "title": "Win/Loss Distribution"
        }
    ],
    "insights": [
        "RSI oscillated between 25-80 during backtest period",
        "Most profitable trades occurred when RSI < 25"
    ]
}
```

**Use for:**
- Validate appropriate charts were shown for strategy type
- Check if key metrics are visualized
- Verify thresholds displayed match strategy config

---

### `insights_data` (dict)
**Actual data points used to render the charts**

Structure:
```python
{
    "rsi": {
        "timestamps": ["2024-01-15T09:30:00", "2024-01-15T10:00:00", ...],
        "values": [28.5, 29.1, 31.2, ...],
        "buy_signals": [{"timestamp": "2024-01-15T09:30:00", "value": 28.5}],
        "sell_signals": [{"timestamp": "2024-01-20T15:45:00", "value": 72.1}]
    },
    "equity_curve": {
        "timestamps": [...],
        "portfolio_values": [10000, 10050, 10100, ...],
        "benchmark_values": [10000, 10030, 10080, ...]
    },
    "price": {
        "timestamps": [...],
        "close": [150.0, 151.2, ...]
    }
}
```

**Use for:**
- Detect data quality issues (e.g., all zeros, NaN values)
- Validate chart data matches trade execution
- Check for anomalies in visualizations (missing data, gaps)
- Verify signals shown on chart align with actual trades

---

## 🎯 Complete Evaluation Use Cases

### Example 1: Validate Partial Exits Work Correctly

```python
# TradeExecutionValidatorEvaluator can check:

enriched_query: "sell 50% when RSI > 70"
strategy.exit_conditions: [{"indicator": "rsi", "operator": ">", "value": 70, "pct_shares": 0.5}]

indicator_data.rsi: [
    {"timestamp": "2024-01-20T15:45:00", "value": 72.1},
    {"timestamp": "2024-01-25T11:30:00", "value": 73.5},  # RSI > 70 AGAIN
    {"timestamp": "2024-02-01T14:00:00", "value": 71.2},  # RSI > 70 AGAIN
]

trades: [
    {"timestamp": "2024-01-20T15:45:00", "side": "sell", "qty": 50},  # Good
    {"timestamp": "2024-01-25T11:30:00", "side": "sell", "qty": 25},  # Should this fire?
    {"timestamp": "2024-02-01T14:00:00", "side": "sell", "qty": 12},  # And this?
]

# VALIDATION: If user said "sell 50% EACH TIME RSI > 70", all 3 should execute
# If user said "sell 50% WHEN RSI first goes above 70", only 1 should execute
```

### Example 2: Validate Visualizations Match Strategy

```python
# Check if RSI chart shows correct thresholds:

strategy.indicators.rsi: {"period": 14, "overbought": 70, "oversold": 30}

insights_config.visualizations: [
    {
        "type": "indicator_overlay",
        "indicators": ["rsi"],
        "thresholds": {"rsi": {"buy": 30, "sell": 70}}  # ✅ Matches!
    }
]

# If thresholds were {"buy": 25, "sell": 75} → MISMATCH → Flag error
```

### Example 3: Detect Data Quality Issues

```python
# Check for missing or invalid chart data:

insights_data.rsi.values: [28.5, 0, 0, 0, 0, ...]  # ❌ All zeros after first value

# Flag: "RSI chart data is mostly zeros - indicator calculation may have failed"
```

---

## Summary Table

| Data Field | Type | Contains | Primary Use |
|------------|------|----------|-------------|
| `user_input` | str | Original query | Compare to final implementation |
| `enriched_query` ✨ | str | Clarified intent | Source of truth for validation |
| `strategy` | dict | Parsed config | Schema + logic validation |
| `generated_code` ✨ | str | Python code | Code quality checks |
| `trades` | list | All executed trades | Trade execution validation |
| `indicator_data` | dict | Indicator time series | Cross-reference with trades |
| `backtest_results` | dict | Full backtest data | Performance metrics |
| `insights_config` ✨ | dict | Chart configurations | Visual validation |
| `insights_data` ✨ | dict | Chart data points | Data quality checks |

✨ = Newly added for comprehensive validation

---

## How Evaluators Access This Data

All data is passed as `**kwargs` to every evaluator's `evaluate()` method:

```python
class MyEvaluator(BaseEvaluator):
    def evaluate(self, **kwargs) -> EvaluationResult:
        # Access any data:
        user_input = kwargs.get('user_input')
        enriched_query = kwargs.get('enriched_query')
        strategy = kwargs.get('strategy')
        generated_code = kwargs.get('generated_code')
        trades = kwargs.get('trades', [])
        indicator_data = kwargs.get('indicator_data', {})
        insights_config = kwargs.get('insights_config', {})
        insights_data = kwargs.get('insights_data', {})

        # Perform validation...
        return EvaluationResult(...)
```

Evaluators can use ANY combination of this data to validate system correctness.
