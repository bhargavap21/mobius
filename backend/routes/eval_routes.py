"""
Evaluation API routes

Provides endpoints for running strategy evaluations.
"""
from fastapi import APIRouter, HTTPException, status
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
import logging

from evals import (
    StrategyParameterEvaluator,
    BacktestCorrectnessEvaluator,
    OutputSchemaEvaluator,
    EvaluationResult,
)
from evals.base import EvaluatorRunner, EvaluationSuite

# Import tracing (optional)
try:
    from services.tracing import log_evaluation_result, add_span_attributes
    TRACING_AVAILABLE = True
except ImportError:
    TRACING_AVAILABLE = False

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/evals", tags=["evaluations"])


# Request/Response models
class StrategyEvalRequest(BaseModel):
    """Request for strategy parameter evaluation."""
    user_input: str
    parsed_strategy: Dict[str, Any]


class BacktestEvalRequest(BaseModel):
    """Request for backtest correctness evaluation."""
    strategy: Dict[str, Any]
    backtest_result: Dict[str, Any]
    trades: Optional[List[Dict[str, Any]]] = None


class SchemaEvalRequest(BaseModel):
    """Request for schema evaluation."""
    parsed_strategy: Dict[str, Any]


class FullEvalRequest(BaseModel):
    """Request for full evaluation suite."""
    user_input: str
    parsed_strategy: Dict[str, Any]
    backtest_result: Optional[Dict[str, Any]] = None
    trades: Optional[List[Dict[str, Any]]] = None


class EvalResponse(BaseModel):
    """Standard evaluation response."""
    passed: bool
    score: Optional[float]
    errors: List[str]
    warnings: List[str]
    details: Dict[str, Any]
    evaluator_name: str


class SuiteResponse(BaseModel):
    """Evaluation suite response."""
    all_passed: bool
    pass_rate: float
    average_score: float
    total_evaluations: int
    failed_evaluators: List[str]
    all_errors: List[str]
    all_warnings: List[str]
    results: List[Dict[str, Any]]


def _log_to_tracing(result: EvaluationResult):
    """Log evaluation result to Phoenix tracing."""
    if TRACING_AVAILABLE:
        try:
            log_evaluation_result(
                evaluator_name=result.evaluator_name,
                passed=result.passed,
                score=result.score,
                details=result.details,
            )
        except Exception as e:
            logger.debug(f"Failed to log to tracing: {e}")


@router.post("/strategy", response_model=EvalResponse)
async def evaluate_strategy_parameters(request: StrategyEvalRequest):
    """
    Evaluate that strategy parameters match user intent.

    Checks:
    - Asset extraction
    - Entry condition signals
    - Exit condition parameters
    - Partial exit percentages
    - Formatting consistency
    """
    try:
        evaluator = StrategyParameterEvaluator()
        result = evaluator.safe_evaluate(
            user_input=request.user_input,
            parsed_strategy=request.parsed_strategy,
        )

        _log_to_tracing(result)

        return EvalResponse(
            passed=result.passed,
            score=result.score,
            errors=result.errors,
            warnings=result.warnings,
            details=result.details,
            evaluator_name=result.evaluator_name,
        )
    except Exception as e:
        logger.error(f"Strategy evaluation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {str(e)}"
        )


@router.post("/backtest", response_model=EvalResponse)
async def evaluate_backtest_correctness(request: BacktestEvalRequest):
    """
    Evaluate backtest execution correctness.

    Checks:
    - Partial exit triggered exactly once
    - No cascading exits
    - Trailing stop logic
    - Trade consistency
    - Metrics accuracy
    """
    try:
        evaluator = BacktestCorrectnessEvaluator()
        result = evaluator.safe_evaluate(
            strategy=request.strategy,
            backtest_result=request.backtest_result,
            trades=request.trades,
        )

        _log_to_tracing(result)

        return EvalResponse(
            passed=result.passed,
            score=result.score,
            errors=result.errors,
            warnings=result.warnings,
            details=result.details,
            evaluator_name=result.evaluator_name,
        )
    except Exception as e:
        logger.error(f"Backtest evaluation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {str(e)}"
        )


@router.post("/schema", response_model=EvalResponse)
async def evaluate_schema(request: SchemaEvalRequest):
    """
    Evaluate strategy schema compliance.

    Checks:
    - Required fields present
    - Correct data types
    - Values within ranges
    - Entry/exit schema validity
    """
    try:
        evaluator = OutputSchemaEvaluator()
        result = evaluator.safe_evaluate(
            parsed_strategy=request.parsed_strategy,
        )

        _log_to_tracing(result)

        return EvalResponse(
            passed=result.passed,
            score=result.score,
            errors=result.errors,
            warnings=result.warnings,
            details=result.details,
            evaluator_name=result.evaluator_name,
        )
    except Exception as e:
        logger.error(f"Schema evaluation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {str(e)}"
        )


@router.post("/full", response_model=SuiteResponse)
async def evaluate_full(request: FullEvalRequest):
    """
    Run full evaluation suite on strategy.

    Runs all available evaluators and returns aggregated results.
    """
    try:
        # Create evaluator runner
        runner = EvaluatorRunner()
        runner.add_evaluator(StrategyParameterEvaluator())
        runner.add_evaluator(OutputSchemaEvaluator())

        # Build kwargs
        kwargs = {
            "user_input": request.user_input,
            "parsed_strategy": request.parsed_strategy,
        }

        # Add backtest evaluator if backtest results provided
        if request.backtest_result:
            runner.add_evaluator(BacktestCorrectnessEvaluator())
            kwargs["strategy"] = request.parsed_strategy
            kwargs["backtest_result"] = request.backtest_result
            kwargs["trades"] = request.trades

        # Run all evaluators
        suite = runner.run_all(**kwargs)

        # Log to tracing
        if TRACING_AVAILABLE:
            try:
                add_span_attributes({
                    "eval.suite.all_passed": suite.all_passed,
                    "eval.suite.pass_rate": suite.pass_rate,
                    "eval.suite.average_score": suite.average_score,
                    "eval.suite.failed": ",".join(suite.failed_evaluators),
                })
            except Exception as e:
                logger.debug(f"Failed to log suite to tracing: {e}")

        return SuiteResponse(
            all_passed=suite.all_passed,
            pass_rate=suite.pass_rate,
            average_score=suite.average_score,
            total_evaluations=len(suite.results),
            failed_evaluators=suite.failed_evaluators,
            all_errors=suite.all_errors,
            all_warnings=suite.all_warnings,
            results=[r.to_dict() for r in suite.results],
        )
    except Exception as e:
        logger.error(f"Full evaluation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {str(e)}"
        )


@router.get("/health")
async def eval_health():
    """Health check for evaluation service."""
    return {
        "status": "healthy",
        "evaluators": [
            "StrategyParameterEvaluator",
            "BacktestCorrectnessEvaluator",
            "OutputSchemaEvaluator",
        ],
        "tracing_enabled": TRACING_AVAILABLE,
    }
