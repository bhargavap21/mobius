"""
User Intent Match Evaluator

Uses LLM to verify that the generated strategy and backtest results
actually match what the user requested.

Catches issues like:
- Wrong asset (user asked for AAPL, got NVDA)
- Wrong indicator (user asked for RSI, got MACD)
- Wrong thresholds (user said RSI < 30, system used RSI < 25)
- Missing conditions (user wanted trailing stop, it's not there)
- Added conditions (system added take-profit user didn't ask for)
"""

import json
import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from evals.base import EvaluationResult
from evals.llm_judge_base import LLMJudgeEvaluator

logger = logging.getLogger(__name__)


class IntentComponent(BaseModel):
    """A single component of user intent."""
    component: str  # e.g., "asset", "entry_condition", "exit_condition"
    user_requested: str  # What user asked for
    system_implemented: str  # What system did
    matches: bool
    discrepancy: Optional[str] = None


class UserIntentJudgment(BaseModel):
    """LLM judgment on user intent matching."""
    overall_score: int = Field(ge=1, le=5, description="1-5 score")
    passed: bool
    summary: str
    components: List[IntentComponent] = Field(default_factory=list)
    missing_requirements: List[str] = Field(default_factory=list)
    extra_features: List[str] = Field(default_factory=list)
    misinterpretations: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1, description="Confidence in assessment")


class UserIntentMatchEvaluator(LLMJudgeEvaluator[UserIntentJudgment]):
    """
    Validates that generated strategy matches user's original request.

    Performs semantic analysis to catch:
    - Literal mismatches (wrong ticker, wrong numbers)
    - Interpretation errors (50% of initial vs 50% of current)
    - Missing components (forgot trailing stop)
    - Hallucinated features (added features user didn't ask for)

    Required kwargs:
    - user_input: Original user query
    - strategy: Generated strategy configuration
    - backtest_result: Optional backtest results for context
    """

    def __init__(self):
        super().__init__(name="UserIntentMatch")

    def get_system_prompt(self) -> str:
        return """You are an expert at understanding user intent and verifying that AI systems correctly interpret requests.

Your task is to compare a user's trading strategy request with the strategy that was generated, and determine if they match.

## What to Check

### 1. Asset/Ticker
- Did the system use the correct stock/crypto?
- Watch for typos or similar tickers (GOOGL vs GOOG)

### 2. Entry Conditions
- Correct indicator (RSI, MACD, SMA, etc.)
- Correct threshold values (RSI < 30, not RSI < 25)
- Correct comparison direction (below vs above)
- Correct timeframe (daily vs hourly)

### 3. Exit Conditions
- Stop loss percentage/price
- Take profit conditions
- Trailing stop if requested
- Partial exits (sell 50%, etc.)

### 4. Position Sizing
- Percentage of portfolio to use
- Number of shares if specified

### 5. Timeframe
- Daily, hourly, 15-minute, etc.
- Backtest period if specified

### 6. Special Instructions
- Any custom logic the user specified
- Edge cases they mentioned

## Common Misinterpretations to Watch For

1. "Sell 50% when X" could mean:
   - Sell 50% of initial position (wrong interpretation often)
   - Sell 50% of current position (usually what user means)

2. "Use 100% of portfolio" could mean:
   - All available cash on one trade
   - All available cash across all positions

3. "RSI below 30" vs "RSI crosses below 30":
   - One triggers while below, other only on the cross

## Scoring Rubric (1-5)
- 5: Perfect match, all components correctly interpreted
- 4: Minor discrepancies that don't affect core logic
- 3: Some misinterpretations but main idea captured
- 2: Significant mismatches in key parameters
- 1: Fundamentally different strategy than requested

## Output Format
Return JSON:
```json
{
    "overall_score": <1-5>,
    "passed": <true if score >= 3>,
    "summary": "Brief assessment of match quality",
    "components": [
        {
            "component": "asset",
            "user_requested": "AAPL",
            "system_implemented": "AAPL",
            "matches": true,
            "discrepancy": null
        },
        {
            "component": "entry_condition",
            "user_requested": "RSI drops below 30",
            "system_implemented": "RSI < 30",
            "matches": true,
            "discrepancy": null
        }
    ],
    "missing_requirements": [
        "User asked for trailing stop, not implemented"
    ],
    "extra_features": [
        "System added 5% take-profit that user didn't request"
    ],
    "misinterpretations": [
        "User said 'sell 50% each time RSI > 70' but system only sells 50% once"
    ],
    "confidence": 0.9
}
```

Focus on what MATTERS for trading outcomes. Minor wording differences are fine if the logic is correct."""

    def get_user_prompt(self, **kwargs) -> str:
        user_input = kwargs.get("user_input", "")
        strategy = kwargs.get("strategy", {})
        backtest_result = kwargs.get("backtest_result", {})

        # Format strategy for comparison
        strategy_summary = self._format_strategy_for_comparison(strategy)

        # Get backtest context if available
        backtest_context = ""
        if backtest_result:
            summary = backtest_result.get("summary", {})
            trades = backtest_result.get("trades", [])
            backtest_context = f"""
## Backtest Results (for context)
- Total Trades: {summary.get('total_trades', len(trades))}
- Win Rate: {summary.get('win_rate', 'N/A')}%
- Total Return: {summary.get('total_return', 'N/A')}%
- Sample trades: {len(trades)} executed
"""

        return f"""## User's Original Request
{user_input}

## Generated Strategy
{strategy_summary}
{backtest_context}

## Your Task
1. Extract every specific requirement from the user's request
2. Check if each requirement is correctly implemented in the strategy
3. Identify any missing requirements
4. Identify any features added that user didn't ask for
5. Note any misinterpretations of ambiguous requests
6. Return your assessment as JSON"""

    def get_response_model(self) -> type[UserIntentJudgment]:
        return UserIntentJudgment

    def interpret_judgment(self, judgment: UserIntentJudgment) -> EvaluationResult:
        """Convert LLM judgment to EvaluationResult."""
        score = self._normalize_score(judgment.overall_score)

        errors = []
        warnings = []

        # Mismatched components are errors
        for comp in judgment.components:
            if not comp.matches and comp.discrepancy:
                errors.append(f"{comp.component}: {comp.discrepancy}")

        # Missing requirements are errors
        for missing in judgment.missing_requirements:
            errors.append(f"Missing: {missing}")

        # Misinterpretations are errors
        for misinterp in judgment.misinterpretations:
            errors.append(f"Misinterpretation: {misinterp}")

        # Extra features are warnings (not necessarily bad)
        for extra in judgment.extra_features:
            warnings.append(f"Added feature: {extra}")

        details = {
            "overall_score": judgment.overall_score,
            "summary": judgment.summary,
            "confidence": judgment.confidence,
            "components_checked": len(judgment.components),
            "components_matched": sum(1 for c in judgment.components if c.matches),
            "missing_requirements": judgment.missing_requirements,
            "extra_features": judgment.extra_features,
            "misinterpretations": judgment.misinterpretations,
            "component_details": [c.model_dump() for c in judgment.components],
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

    def _format_strategy_for_comparison(self, strategy: Dict[str, Any]) -> str:
        """Format strategy in a clear way for comparison."""
        entry = strategy.get("entry_conditions", {})
        exit_cond = strategy.get("exit_conditions", {})
        risk = strategy.get("risk_management", {})

        lines = [
            f"Name: {strategy.get('name', 'Unknown')}",
            f"Description: {strategy.get('description', 'None')}",
            f"Asset: {strategy.get('asset', 'Unknown')}",
            "",
            "### Entry Conditions",
            f"Signal Type: {entry.get('signal', 'Unknown')}",
            f"Description: {entry.get('description', 'None')}",
            f"Parameters: {json.dumps(entry.get('parameters', {}), indent=2)}",
            "",
            "### Exit Conditions",
            f"Stop Loss: {exit_cond.get('stop_loss', 'None')}",
            f"Take Profit: {exit_cond.get('take_profit', 'None')}",
            f"Take Profit % of Shares: {exit_cond.get('take_profit_pct_shares', 1.0)}",
            f"Custom Exit: {exit_cond.get('custom_exit', 'None')}",
            "",
            "### Risk Management",
            f"Position Size: {risk.get('position_size', 1.0)} (1.0 = 100%)",
            f"Max Positions: {risk.get('max_positions', 1)}",
        ]

        return "\n".join(lines)

    def evaluate(self, **kwargs) -> EvaluationResult:
        """Run user intent matching evaluation."""
        user_input = kwargs.get("user_input", "")
        strategy = kwargs.get("strategy", {})

        # Skip if no user input
        if not user_input:
            return EvaluationResult.skipped(
                self.name,
                "No user input to compare against"
            )

        # Skip if no strategy
        if not strategy:
            return EvaluationResult.skipped(
                self.name,
                "No strategy to evaluate"
            )

        # Run LLM evaluation
        return super().evaluate(**kwargs)
