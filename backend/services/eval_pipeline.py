"""
Production Evaluation Pipeline

Automatically runs evaluators after strategy generation
and logs results to Phoenix tracing.

Phase 2: Deterministic evaluators (fast, rule-based)
Phase 3: LLM-as-a-Judge evaluators (thorough, AI-based)
"""

import logging
import os
from typing import Any, Dict, Optional

from evals import (
    # Phase 2: Deterministic
    StrategyParameterEvaluator,
    BacktestCorrectnessEvaluator,
    OutputSchemaEvaluator,
    # Phase 3: LLM-as-a-Judge
    TradeExecutionValidatorEvaluator,
    UserIntentMatchEvaluator,
    StrategyCoherenceEvaluator,
)
from evals.code_validation_evaluator import CodeValidationEvaluator
from evals.execution_divergence_evaluator import ExecutionDivergenceEvaluator
from evals.base import EvaluatorRunner, EvaluationSuite

# Import tracing (optional)
try:
    from services.tracing import log_evaluation_result, add_span_attributes, trace_operation
    TRACING_AVAILABLE = True
except ImportError:
    TRACING_AVAILABLE = False
    trace_operation = None

logger = logging.getLogger(__name__)

# Environment flag to enable/disable LLM evaluators (they cost money)
LLM_EVALS_ENABLED = os.getenv("LLM_EVALS_ENABLED", "true").lower() == "true"


class ProductionEvalPipeline:
    """
    Runs all evaluators on strategy generation results.

    Integrates with:
    - Phoenix tracing for observability
    - Supervisor workflow for automatic evaluation

    Two evaluation modes:
    - Deterministic only: Fast, rule-based checks (always runs)
    - Full (with LLM): Includes LLM-as-a-Judge evaluators (controlled by LLM_EVALS_ENABLED)
    """

    def __init__(self, enable_llm_evals: Optional[bool] = None):
        """
        Initialize evaluators.

        Args:
            enable_llm_evals: Override for LLM evaluator flag (None = use env var)
        """
        self.llm_evals_enabled = enable_llm_evals if enable_llm_evals is not None else LLM_EVALS_ENABLED

        # Deterministic evaluators (Phase 2) - always run
        self.deterministic_runner = EvaluatorRunner()
        self.deterministic_runner.add_evaluator(OutputSchemaEvaluator())
        self.deterministic_runner.add_evaluator(StrategyParameterEvaluator())
        self.deterministic_runner.add_evaluator(BacktestCorrectnessEvaluator())
        self.deterministic_runner.add_evaluator(CodeValidationEvaluator())  # Phase 3: Code validation
        self.deterministic_runner.add_evaluator(ExecutionDivergenceEvaluator())  # Phase 4: Execution validation

        # LLM-as-a-Judge evaluators (Phase 3) - optional
        self.llm_runner = EvaluatorRunner()
        if self.llm_evals_enabled:
            self.llm_runner.add_evaluator(UserIntentMatchEvaluator())
            self.llm_runner.add_evaluator(StrategyCoherenceEvaluator())
            self.llm_runner.add_evaluator(TradeExecutionValidatorEvaluator())
            logger.info("✅ Evaluation pipeline initialized with 5 deterministic + 3 LLM evaluators")
        else:
            logger.info("✅ Evaluation pipeline initialized with 5 deterministic evaluators (LLM evals disabled)")

    def evaluate(
        self,
        user_input: str,
        strategy: Dict[str, Any],
        backtest_results: Optional[Dict[str, Any]] = None,
        trades: Optional[list] = None,
        indicator_data: Optional[Dict[str, Any]] = None,
        generated_code: Optional[str] = None,
        enriched_query: Optional[str] = None,
        insights_config: Optional[Dict[str, Any]] = None,
    ) -> EvaluationSuite:
        """
        Run all evaluators on the strategy.

        Args:
            user_input: Original user query
            enriched_query: Enriched query from clarification agent (optional)
            strategy: Parsed strategy config
            backtest_results: Backtest results (optional)
            trades: List of trades (optional, extracted from backtest_results if not provided)
            indicator_data: Indicator time series for trade validation (optional)
            generated_code: Generated strategy code (optional)
            insights_config: Visualization configuration showing what charts were displayed (optional)

        Returns:
            EvaluationSuite with all results
        """
        logger.info("🔍 Running evaluation pipeline...")

        # Extract trades from backtest_results if not provided
        if trades is None and backtest_results:
            trades = backtest_results.get('trades', [])

        # Extract indicator data from backtest results if not provided
        if indicator_data is None and backtest_results:
            indicator_data = backtest_results.get('indicator_data', {})
            # Also check insights_data which may contain indicator values
            if not indicator_data:
                indicator_data = backtest_results.get('insights_data', {})

        # Extract insights_data (visualization chart data) from backtest results
        insights_data = None
        if backtest_results:
            insights_data = backtest_results.get('insights_data', {})

        # Build kwargs for evaluators
        kwargs = {
            "user_input": user_input,
            "enriched_query": enriched_query or user_input,  # Fallback to user_input if no enriched
            "parsed_strategy": strategy,
            "strategy": strategy,
        }

        # Add backtest data if available
        if backtest_results:
            kwargs["backtest_result"] = backtest_results
            kwargs["trades"] = trades

        # Add indicator data for trade execution validation
        if indicator_data:
            kwargs["indicator_data"] = indicator_data

        # Add generated code for code quality evaluation
        if generated_code:
            kwargs["generated_code"] = generated_code

        # Add visualization data for visual validation
        if insights_config:
            kwargs["insights_config"] = insights_config  # What charts were configured to show
        if insights_data:
            kwargs["insights_data"] = insights_data  # Actual chart data points

        # Run deterministic evaluators first (fast)
        logger.info("  📋 Running deterministic evaluators...")
        suite = self.deterministic_runner.run_all(**kwargs)

        # Run LLM evaluators if enabled (slower, costs money)
        if self.llm_evals_enabled and self.llm_runner.evaluators:
            logger.info("  🤖 Running LLM-as-a-Judge evaluators...")
            llm_suite = self.llm_runner.run_all(**kwargs)
            # Merge results
            for result in llm_suite.results:
                suite.add(result)

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
    generated_code: Optional[str] = None,
    enriched_query: Optional[str] = None,
    insights_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Convenience function to run evaluations and get summary.

    Args:
        user_input: Original user query
        enriched_query: Enriched query from clarification agent
        strategy: Parsed strategy config
        backtest_results: Backtest results
        generated_code: Generated strategy code
        insights_config: Visualization configuration

    Returns:
        Evaluation summary dict
    """
    suite = eval_pipeline.evaluate(
        user_input=user_input,
        enriched_query=enriched_query,
        strategy=strategy,
        backtest_results=backtest_results,
        generated_code=generated_code,
        insights_config=insights_config,
    )
    return eval_pipeline.get_summary(suite)
