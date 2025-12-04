"""
Execution Divergence Evaluator

Compares actual code execution results against simulation baseline to detect
implementation bugs, logic errors, or unexpected behavior divergence.

This evaluator helps catch cases where the generated code behaves differently
from the expected simulation-based results.
"""

from typing import Any, Dict, List, Optional
from .base import BaseEvaluator, EvaluationResult, EvaluationStatus
import logging

logger = logging.getLogger(__name__)


class ExecutionDivergenceEvaluator(BaseEvaluator):
    """
    Evaluates divergence between actual code execution and simulation baseline.

    Checks:
    - Return divergence (>10% difference is suspicious)
    - Trade count divergence (signals not matching expectations)
    - Win rate divergence (execution logic issues)
    - Position sizing issues (shares not matching expected allocation)
    """

    # Thresholds for flagging divergence
    RETURN_DIVERGENCE_THRESHOLD = 0.10  # 10% difference
    TRADE_COUNT_DIVERGENCE_THRESHOLD = 0.20  # 20% difference
    WIN_RATE_DIVERGENCE_THRESHOLD = 0.15  # 15% difference

    def __init__(self):
        super().__init__("ExecutionDivergenceEvaluator")

    def evaluate(
        self,
        strategy: Dict[str, Any],
        backtest_result: Dict[str, Any],
        trades: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> EvaluationResult:
        """
        Evaluate divergence between execution and simulation.

        Args:
            strategy: The strategy configuration
            backtest_result: Backtest results including validation_simulation data
            trades: List of trades from actual execution

        Returns:
            EvaluationResult with pass/fail status and divergence details
        """
        errors = []
        warnings = []
        details = {}

        # Check if validation simulation data exists
        validation_sim = backtest_result.get("validation_simulation")
        if not validation_sim:
            logger.info("No validation simulation data - skipping divergence check")
            return EvaluationResult(
                evaluator_name=self.name,
                status=EvaluationStatus.SKIPPED,
                passed=True,
                score=1.0,
                errors=[],
                warnings=["No validation simulation data available"],
                details={"skipped": True}
            )

        # Extract actual execution results
        actual_summary = backtest_result.get("summary", {})
        actual_return = actual_summary.get("total_return", 0)
        actual_trades = actual_summary.get("total_trades", 0)
        actual_win_rate = actual_summary.get("win_rate", 0)

        # Extract simulation results
        sim_summary = validation_sim.get("summary", {})
        sim_return = sim_summary.get("total_return", 0)
        sim_trades = sim_summary.get("total_trades", 0)
        sim_win_rate = sim_summary.get("win_rate", 0)

        details["actual_execution"] = {
            "total_return": actual_return,
            "total_trades": actual_trades,
            "win_rate": actual_win_rate
        }
        details["simulation_baseline"] = {
            "total_return": sim_return,
            "total_trades": sim_trades,
            "win_rate": sim_win_rate
        }

        # Check return divergence
        if sim_return != 0:
            return_divergence = abs(actual_return - sim_return) / abs(sim_return)
        else:
            return_divergence = abs(actual_return - sim_return)

        if return_divergence > self.RETURN_DIVERGENCE_THRESHOLD:
            errors.append(
                f"Return divergence: Actual {actual_return:.2f}% vs Simulation {sim_return:.2f}% "
                f"({return_divergence*100:.1f}% divergence, threshold {self.RETURN_DIVERGENCE_THRESHOLD*100:.0f}%)"
            )
        elif return_divergence > self.RETURN_DIVERGENCE_THRESHOLD / 2:
            warnings.append(
                f"Moderate return divergence: {return_divergence*100:.1f}% difference"
            )

        details["return_divergence_pct"] = return_divergence * 100

        # Check trade count divergence
        if sim_trades > 0:
            trade_divergence = abs(actual_trades - sim_trades) / sim_trades
        else:
            trade_divergence = abs(actual_trades - sim_trades)

        if trade_divergence > self.TRADE_COUNT_DIVERGENCE_THRESHOLD:
            errors.append(
                f"Trade count divergence: Actual {actual_trades} vs Simulation {sim_trades} "
                f"({trade_divergence*100:.1f}% divergence)"
            )
        elif trade_divergence > self.TRADE_COUNT_DIVERGENCE_THRESHOLD / 2:
            warnings.append(
                f"Moderate trade count divergence: {trade_divergence*100:.1f}% difference"
            )

        details["trade_count_divergence_pct"] = trade_divergence * 100

        # Check win rate divergence (only if both have trades)
        if actual_trades > 0 and sim_trades > 0:
            if sim_win_rate > 0:
                win_rate_divergence = abs(actual_win_rate - sim_win_rate) / sim_win_rate
            else:
                win_rate_divergence = abs(actual_win_rate - sim_win_rate)

            if win_rate_divergence > self.WIN_RATE_DIVERGENCE_THRESHOLD:
                errors.append(
                    f"Win rate divergence: Actual {actual_win_rate:.1f}% vs Simulation {sim_win_rate:.1f}% "
                    f"({win_rate_divergence*100:.1f}% divergence)"
                )
            elif win_rate_divergence > self.WIN_RATE_DIVERGENCE_THRESHOLD / 2:
                warnings.append(
                    f"Moderate win rate divergence: {win_rate_divergence*100:.1f}% difference"
                )

            details["win_rate_divergence_pct"] = win_rate_divergence * 100

        # Calculate overall divergence score (lower is better)
        # Perfect match = 1.0, high divergence = 0.0
        avg_divergence = (return_divergence + trade_divergence) / 2
        score = max(0.0, 1.0 - (avg_divergence * 5))  # Scale so 20% divergence = 0 score

        passed = len(errors) == 0

        if not passed:
            details["diagnosis"] = self._diagnose_divergence(
                actual_summary, sim_summary, strategy
            )

        # Determine status based on errors and warnings
        if not passed:
            status = EvaluationStatus.FAILED
        elif warnings:
            status = EvaluationStatus.WARNING
        else:
            status = EvaluationStatus.PASSED

        return EvaluationResult(
            evaluator_name=self.name,
            status=status,
            passed=passed,
            score=score,
            errors=errors,
            warnings=warnings,
            details=details
        )

    def _diagnose_divergence(
        self,
        actual: Dict[str, Any],
        simulation: Dict[str, Any],
        strategy: Dict[str, Any]
    ) -> List[str]:
        """
        Provide diagnostic suggestions for divergence issues.

        Returns:
            List of possible causes and suggestions
        """
        diagnoses = []

        actual_return = actual.get("total_return", 0)
        sim_return = simulation.get("total_return", 0)
        actual_trades = actual.get("total_trades", 0)
        sim_trades = simulation.get("total_trades", 0)

        # Fewer actual trades than simulation
        if actual_trades < sim_trades * 0.8:
            diagnoses.append(
                "Possible cause: Generated code may have stricter entry conditions or "
                "position sizing issues preventing trade execution"
            )

        # More actual trades than simulation
        if actual_trades > sim_trades * 1.2:
            diagnoses.append(
                "Possible cause: Generated code may be generating duplicate signals or "
                "not properly tracking position state"
            )

        # Significantly worse return
        if actual_return < sim_return - 10:
            diagnoses.append(
                "Possible cause: Position sizing errors, incorrect exit logic, or "
                "missing stop loss implementation in generated code"
            )

        # Significantly better return (also suspicious)
        if actual_return > sim_return + 10:
            diagnoses.append(
                "Possible cause: Simulation may not account for all features, or "
                "generated code may have unintended logic that improves performance"
            )

        # Check for common code generation issues
        exit_conditions = strategy.get("exit_conditions", {})
        if exit_conditions.get("stop_loss") and actual_trades < sim_trades:
            diagnoses.append(
                "Check: Stop loss implementation may be triggering prematurely or incorrectly"
            )

        if exit_conditions.get("take_profit_pct_shares"):
            diagnoses.append(
                "Check: Partial exit logic may not match simulation assumptions"
            )

        if not diagnoses:
            diagnoses.append(
                "Divergence detected but cause unclear - review generated code logic and broker integration"
            )

        return diagnoses
