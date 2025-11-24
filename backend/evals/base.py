"""
Base Evaluator Classes

Provides the foundation for all evaluators in the system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class EvaluationStatus(Enum):
    """Status of an evaluation run."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class EvaluationResult:
    """
    Result of a single evaluation.

    Attributes:
        evaluator_name: Name of the evaluator that produced this result
        status: Overall status (passed/failed/warning/skipped/error)
        passed: Boolean indicating if evaluation passed
        score: Optional numeric score (0.0 - 1.0)
        details: Dictionary with detailed evaluation information
        errors: List of error messages
        warnings: List of warning messages
        timestamp: When the evaluation was run
        metadata: Additional metadata about the evaluation
    """
    evaluator_name: str
    status: EvaluationStatus
    passed: bool
    score: Optional[float] = None
    details: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "evaluator_name": self.evaluator_name,
            "status": self.status.value,
            "passed": self.passed,
            "score": self.score,
            "details": self.details,
            "errors": self.errors,
            "warnings": self.warnings,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def success(
        cls,
        evaluator_name: str,
        details: Optional[Dict[str, Any]] = None,
        score: float = 1.0,
        warnings: Optional[List[str]] = None
    ) -> "EvaluationResult":
        """Create a successful evaluation result."""
        return cls(
            evaluator_name=evaluator_name,
            status=EvaluationStatus.PASSED,
            passed=True,
            score=score,
            details=details or {},
            warnings=warnings or [],
        )

    @classmethod
    def failure(
        cls,
        evaluator_name: str,
        errors: List[str],
        details: Optional[Dict[str, Any]] = None,
        score: float = 0.0,
    ) -> "EvaluationResult":
        """Create a failed evaluation result."""
        return cls(
            evaluator_name=evaluator_name,
            status=EvaluationStatus.FAILED,
            passed=False,
            score=score,
            details=details or {},
            errors=errors,
        )

    @classmethod
    def warning(
        cls,
        evaluator_name: str,
        warnings: List[str],
        details: Optional[Dict[str, Any]] = None,
        score: float = 0.5,
    ) -> "EvaluationResult":
        """Create a warning evaluation result."""
        return cls(
            evaluator_name=evaluator_name,
            status=EvaluationStatus.WARNING,
            passed=True,  # Warnings still pass
            score=score,
            details=details or {},
            warnings=warnings,
        )

    @classmethod
    def error(
        cls,
        evaluator_name: str,
        error_message: str,
    ) -> "EvaluationResult":
        """Create an error evaluation result (evaluator itself failed)."""
        return cls(
            evaluator_name=evaluator_name,
            status=EvaluationStatus.ERROR,
            passed=False,
            score=0.0,
            errors=[f"Evaluator error: {error_message}"],
        )

    @classmethod
    def skipped(
        cls,
        evaluator_name: str,
        reason: str,
    ) -> "EvaluationResult":
        """Create a skipped evaluation result."""
        return cls(
            evaluator_name=evaluator_name,
            status=EvaluationStatus.SKIPPED,
            passed=True,
            details={"skip_reason": reason},
        )


class BaseEvaluator(ABC):
    """
    Base class for all evaluators.

    Evaluators check specific aspects of strategy generation
    and backtest execution to ensure correctness.
    """

    def __init__(self, name: Optional[str] = None):
        """
        Initialize evaluator.

        Args:
            name: Optional custom name for the evaluator
        """
        self.name = name or self.__class__.__name__
        self.logger = logging.getLogger(f"evals.{self.name}")

    @abstractmethod
    def evaluate(self, **kwargs) -> EvaluationResult:
        """
        Run the evaluation.

        This method should be implemented by subclasses to perform
        the actual evaluation logic.

        Returns:
            EvaluationResult with evaluation outcome
        """
        pass

    def safe_evaluate(self, **kwargs) -> EvaluationResult:
        """
        Run evaluation with error handling.

        Catches any exceptions and returns an error result instead
        of propagating the exception.
        """
        try:
            return self.evaluate(**kwargs)
        except Exception as e:
            self.logger.error(f"Evaluator {self.name} failed: {e}", exc_info=True)
            return EvaluationResult.error(self.name, str(e))

    def _check_required_fields(
        self,
        data: Dict[str, Any],
        required_fields: List[str]
    ) -> List[str]:
        """
        Check if required fields are present.

        Returns list of missing field names.
        """
        return [f for f in required_fields if f not in data or data[f] is None]


@dataclass
class EvaluationSuite:
    """
    Collection of evaluation results from multiple evaluators.

    Provides aggregate statistics and easy access to results.
    """
    results: List[EvaluationResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def all_passed(self) -> bool:
        """Check if all evaluations passed."""
        return all(r.passed for r in self.results)

    @property
    def pass_rate(self) -> float:
        """Calculate pass rate as percentage."""
        if not self.results:
            return 0.0
        return sum(1 for r in self.results if r.passed) / len(self.results)

    @property
    def average_score(self) -> float:
        """Calculate average score across all evaluations."""
        scores = [r.score for r in self.results if r.score is not None]
        if not scores:
            return 0.0
        return sum(scores) / len(scores)

    @property
    def failed_evaluators(self) -> List[str]:
        """Get list of failed evaluator names."""
        return [r.evaluator_name for r in self.results if not r.passed]

    @property
    def all_errors(self) -> List[str]:
        """Get all errors across all evaluations."""
        errors = []
        for r in self.results:
            for e in r.errors:
                errors.append(f"[{r.evaluator_name}] {e}")
        return errors

    @property
    def all_warnings(self) -> List[str]:
        """Get all warnings across all evaluations."""
        warnings = []
        for r in self.results:
            for w in r.warnings:
                warnings.append(f"[{r.evaluator_name}] {w}")
        return warnings

    def add(self, result: EvaluationResult):
        """Add an evaluation result to the suite."""
        self.results.append(result)

    def get_result(self, evaluator_name: str) -> Optional[EvaluationResult]:
        """Get result for a specific evaluator."""
        for r in self.results:
            if r.evaluator_name == evaluator_name:
                return r
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "all_passed": self.all_passed,
            "pass_rate": self.pass_rate,
            "average_score": self.average_score,
            "total_evaluations": len(self.results),
            "failed_evaluators": self.failed_evaluators,
            "all_errors": self.all_errors,
            "all_warnings": self.all_warnings,
            "results": [r.to_dict() for r in self.results],
            "metadata": self.metadata,
        }

    def summary(self) -> str:
        """Generate human-readable summary."""
        status = "✅ PASSED" if self.all_passed else "❌ FAILED"
        lines = [
            f"Evaluation Suite: {status}",
            f"Pass Rate: {self.pass_rate:.0%} ({sum(1 for r in self.results if r.passed)}/{len(self.results)})",
            f"Average Score: {self.average_score:.2f}",
        ]

        if self.failed_evaluators:
            lines.append(f"Failed: {', '.join(self.failed_evaluators)}")

        if self.all_errors:
            lines.append("Errors:")
            for e in self.all_errors[:5]:  # Show first 5
                lines.append(f"  - {e}")
            if len(self.all_errors) > 5:
                lines.append(f"  ... and {len(self.all_errors) - 5} more")

        return "\n".join(lines)


class EvaluatorRunner:
    """
    Runs multiple evaluators and collects results.
    """

    def __init__(self, evaluators: Optional[List[BaseEvaluator]] = None):
        """
        Initialize runner with list of evaluators.

        Args:
            evaluators: List of evaluator instances to run
        """
        self.evaluators = evaluators or []
        self.logger = logging.getLogger("evals.runner")

    def add_evaluator(self, evaluator: BaseEvaluator):
        """Add an evaluator to the runner."""
        self.evaluators.append(evaluator)

    def run_all(self, **kwargs) -> EvaluationSuite:
        """
        Run all evaluators and return suite of results.

        All kwargs are passed to each evaluator.
        """
        suite = EvaluationSuite()

        for evaluator in self.evaluators:
            self.logger.debug(f"Running evaluator: {evaluator.name}")
            result = evaluator.safe_evaluate(**kwargs)
            suite.add(result)

            if result.passed:
                self.logger.debug(f"  ✅ {evaluator.name}: PASSED")
            else:
                self.logger.warning(f"  ❌ {evaluator.name}: FAILED - {result.errors}")

        return suite
