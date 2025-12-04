"""
Trade Execution Validator Evaluator

Uses LLM to validate that trades executed during backtest actually align
with the strategy's entry/exit conditions by cross-referencing indicator data.

This catches bugs like:
- Partial exits not triggering on subsequent signals
- Entry conditions triggering at wrong threshold
- Position sizing misinterpretation (50% of initial vs 50% of current)
- Off-by-one timing errors
"""

import json
import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from evals.base import EvaluationResult
from evals.llm_judge_base import LLMJudgeEvaluator

logger = logging.getLogger(__name__)


class TradeValidation(BaseModel):
    """Validation result for a single trade."""
    trade_index: int
    trade_type: str  # "buy" or "sell"
    trade_date: str
    is_valid: bool
    expected_behavior: str
    actual_behavior: str
    indicator_values_at_trade: Dict[str, Any] = Field(default_factory=dict)
    issue: Optional[str] = None


class MissingTrade(BaseModel):
    """A trade that should have happened but didn't."""
    date: str
    expected_action: str
    reason: str
    indicator_values: Dict[str, Any] = Field(default_factory=dict)


class TradeExecutionJudgment(BaseModel):
    """LLM judgment on trade execution validity."""
    overall_score: int = Field(ge=1, le=5, description="1-5 score")
    passed: bool
    summary: str
    trade_validations: List[TradeValidation] = Field(default_factory=list)
    missing_trades: List[MissingTrade] = Field(default_factory=list)
    position_sizing_issues: List[str] = Field(default_factory=list)
    timing_issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class TradeExecutionValidatorEvaluator(LLMJudgeEvaluator[TradeExecutionJudgment]):
    """
    Validates that backtest trades align with strategy conditions.

    Cross-references:
    - Trade timestamps with indicator values at those times
    - Entry conditions with actual buy signals
    - Exit conditions with actual sell signals
    - Position sizing logic (partial exits, etc.)

    Required kwargs:
    - strategy: Strategy configuration dict
    - trades: List of executed trades
    - indicator_data: Dict of indicator time series (e.g., {"rsi": [...], "price": [...]})
    - user_input: Original user query (for intent context)
    """

    def __init__(self):
        super().__init__(name="TradeExecutionValidator")

    def get_system_prompt(self) -> str:
        return """You are an expert trading systems auditor. Your job is to validate that a backtesting system correctly executed trades according to the specified strategy rules.

You will be given:
1. A trading strategy with specific entry/exit conditions
2. The list of trades that were executed during the backtest
3. The indicator data (RSI, price, etc.) over the backtest period
4. The original user request describing their intent

Your task is to cross-reference the trades with the indicator data and verify:

## Entry Validation
- Did BUY trades occur when entry conditions were actually met?
- Were there times when entry conditions were met but no buy occurred?

## Exit Validation
- Did SELL trades occur when exit conditions were actually met?
- Were there times when exit conditions were met but no sell occurred?

## Position Sizing Validation (CRITICAL)
- If strategy says "sell 50% of position", verify the shares sold match 50%
- Watch for this common bug: "sell 50% of initial purchase" vs "sell 50% of current position"
- Example: User owns 100 shares, RSI hits 70 → sell 50 (correct)
           RSI hits 70 again → should sell 25 (50% of remaining 50), but system might sell 0 (bug!)

## Timing Validation
- Trades should execute on the bar where condition was met, not the next bar
- Watch for off-by-one errors in the backtest logic

## Scoring Rubric (1-5):
- 5: All trades perfectly align with strategy rules
- 4: Minor timing issues, but logic is correct
- 3: Some trades are questionable, possible interpretation issues
- 2: Multiple trades don't align with stated conditions
- 1: Systematic errors in trade execution logic

## Output Format
Return a JSON object with this exact structure:
```json
{
    "overall_score": <1-5>,
    "passed": <true if score >= 3>,
    "summary": "Brief summary of findings",
    "trade_validations": [
        {
            "trade_index": 0,
            "trade_type": "buy",
            "trade_date": "2024-01-15",
            "is_valid": true,
            "expected_behavior": "Buy when RSI < 30",
            "actual_behavior": "Bought at RSI = 28",
            "indicator_values_at_trade": {"rsi": 28, "price": 150.00},
            "issue": null
        }
    ],
    "missing_trades": [
        {
            "date": "2024-02-20",
            "expected_action": "Sell 50% of position (25 shares)",
            "reason": "RSI was 72, above 70 threshold",
            "indicator_values": {"rsi": 72}
        }
    ],
    "position_sizing_issues": [
        "Sold 50 shares but should have sold 25 (50% of remaining position)"
    ],
    "timing_issues": [],
    "recommendations": [
        "Fix partial exit logic to track remaining position, not initial position"
    ]
}
```

Be thorough but fair. Focus on actual logical errors, not minor floating-point differences."""

    def get_user_prompt(self, **kwargs) -> str:
        strategy = kwargs.get("strategy", {})
        trades = kwargs.get("trades", [])
        indicator_data = kwargs.get("indicator_data", {})
        user_input = kwargs.get("user_input", "")
        backtest_result = kwargs.get("backtest_result", {})

        # Extract key strategy parameters
        entry_conditions = strategy.get("entry_conditions", {})
        exit_conditions = strategy.get("exit_conditions", {})
        risk_management = strategy.get("risk_management", {})

        # Format trades with details
        trades_formatted = self._format_trades_detailed(trades)

        # Format indicator data (sample key points)
        indicator_summary = self._format_indicator_data(indicator_data, trades)

        # Get backtest summary
        summary = backtest_result.get("summary", {}) if backtest_result else {}

        return f"""## Original User Request
{user_input}

## Strategy Configuration
Asset: {strategy.get('asset', 'Unknown')}
Name: {strategy.get('name', 'Unknown')}

### Entry Conditions
{json.dumps(entry_conditions, indent=2)}

### Exit Conditions
{json.dumps(exit_conditions, indent=2)}

### Risk Management
Position Size: {risk_management.get('position_size', 1.0)} (1.0 = 100% of capital)
Max Positions: {risk_management.get('max_positions', 1)}

## Backtest Summary
- Total Trades: {summary.get('total_trades', len(trades))}
- Win Rate: {summary.get('win_rate', 'N/A')}%
- Total Return: {summary.get('total_return', 'N/A')}%

## Executed Trades
{trades_formatted}

## Indicator Data at Key Points
{indicator_summary}

## Your Task
1. Cross-reference each trade with the indicator values at that time
2. Identify any trades that don't align with the strategy rules
3. Identify any MISSING trades (times when conditions were met but no trade occurred)
4. Pay special attention to partial exit logic and position sizing
5. Return your judgment as JSON"""

    def get_response_model(self) -> type[TradeExecutionJudgment]:
        return TradeExecutionJudgment

    def interpret_judgment(self, judgment: TradeExecutionJudgment) -> EvaluationResult:
        """Convert LLM judgment to EvaluationResult."""
        score = self._normalize_score(judgment.overall_score)

        # Collect all issues
        errors = []
        warnings = []

        # Invalid trades are errors
        invalid_trades = [t for t in judgment.trade_validations if not t.is_valid]
        for trade in invalid_trades:
            errors.append(f"Trade {trade.trade_index} ({trade.trade_type} on {trade.trade_date}): {trade.issue}")

        # Missing trades are errors
        for missing in judgment.missing_trades:
            errors.append(f"Missing trade on {missing.date}: {missing.expected_action} - {missing.reason}")

        # Position sizing issues are errors
        errors.extend(judgment.position_sizing_issues)

        # Timing issues are warnings
        warnings.extend(judgment.timing_issues)

        details = {
            "overall_score": judgment.overall_score,
            "summary": judgment.summary,
            "total_trades_validated": len(judgment.trade_validations),
            "invalid_trade_count": len(invalid_trades),
            "missing_trade_count": len(judgment.missing_trades),
            "position_sizing_issues": len(judgment.position_sizing_issues),
            "timing_issues": len(judgment.timing_issues),
            "recommendations": judgment.recommendations,
            "trade_validations": [t.model_dump() for t in judgment.trade_validations],
            "missing_trades": [m.model_dump() for m in judgment.missing_trades],
        }

        if judgment.passed:
            return EvaluationResult.success(
                evaluator_name=self.name,
                score=score,
                details=details,
                warnings=warnings if warnings else None
            )
        else:
            return EvaluationResult.failure(
                evaluator_name=self.name,
                errors=errors,
                details=details,
                score=score
            )

    def _format_trades_detailed(self, trades: List[Dict[str, Any]]) -> str:
        """Format trades with full details for analysis."""
        if not trades:
            return "No trades were executed during the backtest."

        lines = []
        for i, trade in enumerate(trades):
            lines.append(f"""
Trade #{i + 1}:
  Type: {trade.get('type', 'unknown').upper()}
  Date: {trade.get('date', 'unknown')}
  Shares: {trade.get('shares', 0)}
  Price: ${trade.get('price', 0):.2f}
  Reason: {trade.get('reason', 'not specified')}
  Position After: {trade.get('position_after', 'unknown')} shares
  Portfolio Value: ${trade.get('portfolio_value', 0):.2f}""")

        return "\n".join(lines)

    def _format_indicator_data(
        self,
        indicator_data: Dict[str, Any],
        trades: List[Dict[str, Any]]
    ) -> str:
        """
        Format indicator data, focusing on trade dates and condition thresholds.

        Shows indicator values at:
        - Each trade date
        - Dates where conditions might have been met but no trade occurred
        """
        if not indicator_data:
            return "No indicator data available."

        lines = []

        # Get trade dates for reference
        trade_dates = set()
        for trade in trades:
            date = trade.get('date', '')
            if date:
                # Handle various date formats
                if isinstance(date, str):
                    trade_dates.add(date[:10])  # Get just YYYY-MM-DD

        # Format each indicator
        for indicator_name, data in indicator_data.items():
            if not data:
                continue

            lines.append(f"\n### {indicator_name.upper()}")

            if isinstance(data, list):
                # Time series data
                lines.append(f"Data points: {len(data)}")

                # Show values at trade dates
                if isinstance(data[0], dict) and 'date' in data[0]:
                    lines.append("Values at trade dates:")
                    for point in data:
                        point_date = str(point.get('date', ''))[:10]
                        if point_date in trade_dates:
                            value = point.get('value', point.get(indicator_name, 'N/A'))
                            lines.append(f"  {point_date}: {value}")

                    # Show some threshold crossings
                    lines.append("\nKey threshold crossings (sample):")
                    crossings_shown = 0
                    for i, point in enumerate(data):
                        if crossings_shown >= 10:
                            break
                        value = point.get('value', point.get(indicator_name))
                        if value is not None:
                            # RSI thresholds
                            if indicator_name.lower() == 'rsi':
                                if value < 30 or value > 70:
                                    point_date = str(point.get('date', ''))[:10]
                                    lines.append(f"  {point_date}: RSI = {value:.1f}")
                                    crossings_shown += 1
                elif isinstance(data[0], (int, float)):
                    # Simple list of values
                    lines.append(f"Range: {min(data):.2f} to {max(data):.2f}")
                    lines.append(f"Sample values: {data[:5]}")

            elif isinstance(data, dict):
                # Dictionary format
                lines.append(f"Keys: {list(data.keys())[:10]}")

        return "\n".join(lines) if lines else "Indicator data format not recognized."

    def evaluate(self, **kwargs) -> EvaluationResult:
        """
        Run trade execution validation.

        Falls back to deterministic checks if LLM call fails or
        if there's insufficient data for LLM analysis.
        """
        trades = kwargs.get("trades", [])
        strategy = kwargs.get("strategy", {})
        indicator_data = kwargs.get("indicator_data", {})

        # Skip if no trades to validate
        if not trades:
            return EvaluationResult.skipped(
                self.name,
                "No trades to validate"
            )

        # Skip if no indicator data
        if not indicator_data:
            return EvaluationResult.warning(
                self.name,
                ["No indicator data provided for cross-reference validation"],
                details={"reason": "Cannot validate trades without indicator data"},
                score=0.5
            )

        # Run LLM evaluation
        try:
            return super().evaluate(**kwargs)
        except Exception as e:
            logger.error(f"LLM evaluation failed, running basic checks: {e}")
            return self._run_basic_validation(trades, strategy)

    def _run_basic_validation(
        self,
        trades: List[Dict[str, Any]],
        strategy: Dict[str, Any]
    ) -> EvaluationResult:
        """
        Fallback deterministic validation when LLM fails.

        Checks basic consistency without cross-referencing indicator data.
        """
        errors = []
        warnings = []

        # Check for empty trades
        if not trades:
            return EvaluationResult.skipped(self.name, "No trades to validate")

        # Check trade sequence logic
        position = 0
        for i, trade in enumerate(trades):
            trade_type = trade.get('type', '').lower()
            shares = trade.get('shares', 0)

            if trade_type == 'buy':
                position += shares
            elif trade_type == 'sell':
                if shares > position:
                    errors.append(f"Trade {i}: Sold {shares} shares but only had {position}")
                position -= shares

            # Check for missing reason
            if not trade.get('reason'):
                warnings.append(f"Trade {i}: No reason specified for {trade_type}")

        # Check partial exit logic
        exit_conditions = strategy.get('exit_conditions', {})
        take_profit_pct = exit_conditions.get('take_profit_pct_shares', 1.0)

        if take_profit_pct < 1.0:
            # Strategy uses partial exits - warn that we couldn't validate
            warnings.append(
                f"Strategy uses {take_profit_pct*100:.0f}% partial exits - "
                "LLM validation recommended to verify correct implementation"
            )

        if errors:
            return EvaluationResult.failure(
                self.name,
                errors,
                details={"validation_type": "basic", "trade_count": len(trades)},
                score=0.3
            )
        else:
            return EvaluationResult.success(
                self.name,
                details={"validation_type": "basic", "trade_count": len(trades)},
                score=0.7,  # Lower score for basic validation
                warnings=warnings if warnings else None
            )
