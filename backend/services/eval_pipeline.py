"""
Production Evaluation Pipeline

Automatically runs evaluators after strategy generation
and logs results to Phoenix tracing.
"""

import logging
from typing import Any, Dict, Optional

from evals import (
    StrategyParameterEvaluator,
    BacktestCorrectnessEvaluator,
    OutputSchemaEvaluator,
)
from evals.base import EvaluatorRunner, EvaluationSuite

# Import tracing (optional)
try:
    from services.tracing import log_evaluation_result, add_span_attributes, trace_operation
    TRACING_AVAILABLE = True
except ImportError:
    TRACING_AVAILABLE = False
    trace_operation = None

logger = logging.getLogger(__name__)


class ProductionEvalPipeline:
    """
    Runs all evaluators on strategy generation results.

    Integrates with:
    - Phoenix tracing for observability
    - Supervisor workflow for automatic evaluation
    """

    def __init__(self):
        """Initialize evaluators."""
        self.runner = EvaluatorRunner()
        self.runner.add_evaluator(OutputSchemaEvaluator())
        self.runner.add_evaluator(StrategyParameterEvaluator())
        self.runner.add_evaluator(BacktestCorrectnessEvaluator())

        logger.info("✅ Evaluation pipeline initialized with 3 evaluators")

    def evaluate(
        self,
        user_input: str,
        strategy: Dict[str, Any],
        backtest_results: Optional[Dict[str, Any]] = None,
        trades: Optional[list] = None,
    ) -> EvaluationSuite:
        """
        Run all evaluators on the strategy.

        Args:
            user_input: Original user query
            strategy: Parsed strategy config
            backtest_results: Backtest results (optional)
            trades: List of trades (optional, extracted from backtest_results if not provided)

        Returns:
            EvaluationSuite with all results
        """
        logger.info("🔍 Running evaluation pipeline...")

        # Extract trades from backtest_results if not provided
        if trades is None and backtest_results:
            trades = backtest_results.get('trades', [])

        # Build kwargs for evaluators
        kwargs = {
            "user_input": user_input,
            "parsed_strategy": strategy,
        }

        # Add backtest data if available
        if backtest_results:
            kwargs["strategy"] = strategy
            kwargs["backtest_result"] = backtest_results
            kwargs["trades"] = trades

        # Run all evaluators
        suite = self.runner.run_all(**kwargs)

        # Log to Phoenix tracing
        self._log_to_tracing(suite)

        # Log summary
        if suite.all_passed:
            logger.info(f"✅ All evaluations PASSED ({len(suite.results)} evaluators)")
        else:
            logger.warning(f"❌ Evaluations FAILED: {suite.failed_evaluators}")
            for error in suite.all_errors[:5]:
                logger.warning(f"   - {error}")

        return suite

    def _log_to_tracing(self, suite: EvaluationSuite):
        """Log evaluation results to Phoenix tracing."""
        if not TRACING_AVAILABLE:
            return

        try:
            # Log overall suite metrics
            add_span_attributes({
                "eval.suite.all_passed": suite.all_passed,
                "eval.suite.pass_rate": suite.pass_rate,
                "eval.suite.average_score": suite.average_score,
                "eval.suite.total_evaluators": len(suite.results),
                "eval.suite.failed_evaluators": ",".join(suite.failed_evaluators) if suite.failed_evaluators else "none",
            })

            # Log individual evaluator results
            for result in suite.results:
                log_evaluation_result(
                    evaluator_name=result.evaluator_name,
                    passed=result.passed,
                    score=result.score,
                    details=result.details,
                )

            logger.debug("✅ Evaluation results logged to Phoenix")

        except Exception as e:
            logger.warning(f"⚠️ Failed to log evaluations to tracing: {e}")

    def get_summary(self, suite: EvaluationSuite) -> Dict[str, Any]:
        """
        Get a summary dict suitable for API responses.

        Args:
            suite: Evaluation suite

        Returns:
            Summary dict
        """
        return {
            "all_passed": suite.all_passed,
            "pass_rate": suite.pass_rate,
            "average_score": suite.average_score,
            "failed_evaluators": suite.failed_evaluators,
            "errors": suite.all_errors,
            "warnings": suite.all_warnings,
            "evaluator_count": len(suite.results),
        }


# Singleton instance for easy import
eval_pipeline = ProductionEvalPipeline()


def run_evaluations(
    user_input: str,
    strategy: Dict[str, Any],
    backtest_results: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Convenience function to run evaluations and get summary.

    Args:
        user_input: Original user query
        strategy: Parsed strategy config
        backtest_results: Backtest results

    Returns:
        Evaluation summary dict
    """
    suite = eval_pipeline.evaluate(
        user_input=user_input,
        strategy=strategy,
        backtest_results=backtest_results,
    )
    return eval_pipeline.get_summary(suite)
