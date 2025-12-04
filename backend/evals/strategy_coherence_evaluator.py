"""
Strategy Coherence Evaluator

Uses LLM to assess whether the strategy logic is internally consistent
and makes sense from a trading perspective.

Catches issues like:
- Contradictory conditions (buy when RSI high AND low)
- Impossible scenarios (100% stop loss with 50% position size)
- Risky configurations (no stop loss on volatile asset)
- Logical gaps (entry defined but no clear exit)
"""

import json
import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from evals.base import EvaluationResult
from evals.llm_judge_base import LLMJudgeEvaluator

logger = logging.getLogger(__name__)


class CoherenceIssue(BaseModel):
    """A coherence issue found in the strategy."""
    severity: str  # "critical", "warning", "info"
    category: str  # "logical", "risk", "configuration"
    description: str
    recommendation: str


class StrategyCoherenceJudgment(BaseModel):
    """LLM judgment on strategy coherence."""
    overall_score: int = Field(ge=1, le=5, description="1-5 score")
    passed: bool
    summary: str
    issues: List[CoherenceIssue] = Field(default_factory=list)
    logical_consistency: bool
    risk_assessment: str
    entry_exit_alignment: bool
    recommendations: List[str] = Field(default_factory=list)


class StrategyCoherenceEvaluator(LLMJudgeEvaluator[StrategyCoherenceJudgment]):
    """
    Evaluates whether a trading strategy is internally coherent.

    Checks:
    - Logical consistency of conditions
    - Risk management appropriateness
    - Entry/exit alignment
    - Common trading pitfalls

    Required kwargs:
    - strategy: Strategy configuration dict
    - user_input: Optional user query for context
    """

    def __init__(self):
        super().__init__(name="StrategyCoherence")

    def get_system_prompt(self) -> str:
        return """You are an expert quantitative trader and strategy analyst. Your job is to review trading strategies for INTERNAL LOGICAL COHERENCE.

CRITICAL: This is a tool to automate user-defined strategies. DO NOT enforce "best practices" the user didn't request.
- If user didn't ask for stop loss, don't flag it as missing
- If user wants 100% position size, validate the logic works, don't criticize the risk
- Focus on whether the IMPLEMENTATION is logically sound, not whether the strategy is profitable

## What to Check

### 1. Logical Consistency (CRITICAL)
- Entry conditions should not contradict exit conditions
- Thresholds should be achievable (RSI can't be 150)
- Conditions should be mutually compatible
- If user says "sell 50% each time RSI > 70", ensure it doesn't sell 50% once then stop

### 2. Implementation Coherence (CRITICAL)
- Does the position sizing logic match what's configured?
- Are partial exits repeatable if user intended them to be?
- Do indicator thresholds make sense for that indicator type?

### 3. Entry/Exit Alignment (CRITICAL)
- Every entry should have a clear exit path
- Exit conditions should be reachable from entry conditions
- Partial exits should sum to 100% eventually

### 4. Common LOGIC Pitfalls (NOT risk management)
- Contradictory conditions (buy when RSI > 70 AND RSI < 30)
- Unreachable thresholds (RSI > 150)
- Conflicting timeframes (daily data with 1-min indicators)
- Impossible exit paths (sell when RSI hits 90 after buying at RSI 30 in downtrend)

## Severity Levels
- **critical**: Strategy implementation is logically broken (contradictions, impossible thresholds)
- **warning**: Logic might not work as user intended (partial exits trigger once when user wanted repeated)
- **info**: Minor implementation detail that could be clearer

## Scoring Rubric (1-5) - IMPLEMENTATION FIDELITY, NOT PROFITABILITY
- 5: Logic is perfectly coherent and implements user intent
- 4: Minor implementation quirks that don't break core logic
- 3: Some logic issues but strategy could execute
- 2: Significant logical contradictions or broken implementation
- 1: Fundamentally broken logic (impossible conditions, contradictory rules)

## Output Format
Return JSON:
```json
{
    "overall_score": <1-5>,
    "passed": <true if score >= 3>,
    "summary": "Brief assessment of LOGIC coherence",
    "issues": [
        {
            "severity": "critical",
            "category": "logical",
            "description": "Exit condition (RSI > 90) unreachable from entry (RSI < 30) in typical mean reversion",
            "recommendation": "Verify exit threshold matches user intent or add alternative exit"
        }
    ],
    "logical_consistency": true,
    "risk_assessment": "Logic is sound - validates user's intended strategy without imposing unasked risk rules",
    "entry_exit_alignment": true,
    "recommendations": [
        "Only suggest LOGIC improvements, not risk management user didn't request"
    ]
}
```

REMEMBER: Only flag LOGICAL/IMPLEMENTATION bugs, not missing "best practices" the user didn't ask for."""

    def get_user_prompt(self, **kwargs) -> str:
        strategy = kwargs.get("strategy", {})
        user_input = kwargs.get("user_input", "")

        strategy_detail = self._format_strategy_detail(strategy)

        context = ""
        if user_input:
            context = f"""
## Original User Request
{user_input}

IMPORTANT: Compare the strategy ONLY against what the user asked for. If the user didn't mention stop loss, don't flag it missing.
"""

        return f"""## Strategy to Analyze
{strategy_detail}
{context}

## Your Task
1. Check if the strategy LOGIC is internally consistent (no contradictions)
2. Verify entry/exit conditions are reachable and align with user intent
3. Validate position sizing and partial exit LOGIC works as user intended
4. Flag IMPLEMENTATION bugs, NOT missing features the user didn't request
5. Return your assessment as JSON

CRITICAL REMINDER: You are evaluating if the TOOL correctly implemented the USER'S strategy, not if the strategy is profitable."""

    def get_response_model(self) -> type[StrategyCoherenceJudgment]:
        return StrategyCoherenceJudgment

    def interpret_judgment(self, judgment: StrategyCoherenceJudgment) -> EvaluationResult:
        """Convert LLM judgment to EvaluationResult."""
        score = self._normalize_score(judgment.overall_score)

        errors = []
        warnings = []

        for issue in judgment.issues:
            msg = f"[{issue.category}] {issue.description}"
            if issue.severity == "critical":
                errors.append(msg)
            elif issue.severity == "warning":
                warnings.append(msg)
            # info level issues are just noted in details

        details = {
            "overall_score": judgment.overall_score,
            "summary": judgment.summary,
            "logical_consistency": judgment.logical_consistency,
            "risk_assessment": judgment.risk_assessment,
            "entry_exit_alignment": judgment.entry_exit_alignment,
            "issue_count": len(judgment.issues),
            "critical_issues": sum(1 for i in judgment.issues if i.severity == "critical"),
            "recommendations": judgment.recommendations,
            "issues": [i.model_dump() for i in judgment.issues],
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
                errors=errors if errors else ["Strategy coherence check failed"],
                details=details,
                score=score
            )

    def _format_strategy_detail(self, strategy: Dict[str, Any]) -> str:
        """Format strategy with full detail for analysis."""
        entry = strategy.get("entry_conditions", {})
        exit_cond = strategy.get("exit_conditions", {})
        risk = strategy.get("risk_management", {})

        return f"""### Basic Info
- Name: {strategy.get('name', 'Unknown')}
- Description: {strategy.get('description', 'None')}
- Asset: {strategy.get('asset', 'Unknown')}
- Portfolio Mode: {strategy.get('portfolio_mode', False)}

### Entry Conditions
- Signal Type: {entry.get('signal', 'Unknown')}
- Description: {entry.get('description', 'None')}
- Parameters:
{json.dumps(entry.get('parameters', {}), indent=4)}

### Exit Conditions
- Stop Loss: {exit_cond.get('stop_loss', 'Not defined')}
- Take Profit: {exit_cond.get('take_profit', 'Not defined')}
- Take Profit % of Shares to Sell: {exit_cond.get('take_profit_pct_shares', 1.0)}
- Stop Loss % of Shares to Sell: {exit_cond.get('stop_loss_pct_shares', 1.0)}
- Custom Exit Logic: {exit_cond.get('custom_exit', 'None')}

### Risk Management
- Position Size: {risk.get('position_size', 1.0)} (1.0 = 100% of capital)
- Max Positions: {risk.get('max_positions', 1)}
- Allocation Strategy: {risk.get('allocation', 'equal')}

### Data Sources
{strategy.get('data_sources', ['price'])}
"""

    def evaluate(self, **kwargs) -> EvaluationResult:
        """Run strategy coherence evaluation."""
        strategy = kwargs.get("strategy", {})

        # Skip if no strategy
        if not strategy:
            return EvaluationResult.skipped(
                self.name,
                "No strategy to evaluate"
            )

        # Run LLM evaluation
        return super().evaluate(**kwargs)
