"""
Tests for the evaluation framework.
"""

import pytest
from evals import (
    StrategyParameterEvaluator,
    BacktestCorrectnessEvaluator,
    OutputSchemaEvaluator,
)
from evals.base import EvaluationResult, EvaluationStatus, EvaluatorRunner, EvaluationSuite


# =============================================================================
# Test Base Classes
# =============================================================================

class TestEvaluationResult:
    """Test EvaluationResult dataclass."""

    def test_success_result(self):
        result = EvaluationResult.success(
            evaluator_name="TestEvaluator",
            details={"key": "value"},
            score=0.95
        )
        assert result.passed is True
        assert result.status == EvaluationStatus.PASSED
        assert result.score == 0.95
        assert result.errors == []

    def test_failure_result(self):
        result = EvaluationResult.failure(
            evaluator_name="TestEvaluator",
            errors=["Error 1", "Error 2"],
            score=0.2
        )
        assert result.passed is False
        assert result.status == EvaluationStatus.FAILED
        assert len(result.errors) == 2

    def test_warning_result(self):
        result = EvaluationResult.warning(
            evaluator_name="TestEvaluator",
            warnings=["Warning 1"]
        )
        assert result.passed is True  # Warnings still pass
        assert result.status == EvaluationStatus.WARNING

    def test_to_dict(self):
        result = EvaluationResult.success("Test", score=1.0)
        d = result.to_dict()
        assert "evaluator_name" in d
        assert "status" in d
        assert d["status"] == "passed"


class TestEvaluationSuite:
    """Test EvaluationSuite class."""

    def test_all_passed(self):
        suite = EvaluationSuite()
        suite.add(EvaluationResult.success("Eval1"))
        suite.add(EvaluationResult.success("Eval2"))
        assert suite.all_passed is True

    def test_not_all_passed(self):
        suite = EvaluationSuite()
        suite.add(EvaluationResult.success("Eval1"))
        suite.add(EvaluationResult.failure("Eval2", errors=["Error"]))
        assert suite.all_passed is False

    def test_pass_rate(self):
        suite = EvaluationSuite()
        suite.add(EvaluationResult.success("Eval1"))
        suite.add(EvaluationResult.success("Eval2"))
        suite.add(EvaluationResult.failure("Eval3", errors=["Error"]))
        assert suite.pass_rate == pytest.approx(2/3)

    def test_failed_evaluators(self):
        suite = EvaluationSuite()
        suite.add(EvaluationResult.success("Eval1"))
        suite.add(EvaluationResult.failure("Eval2", errors=["Error"]))
        assert suite.failed_evaluators == ["Eval2"]


# =============================================================================
# Test Strategy Parameter Evaluator
# =============================================================================

class TestStrategyParameterEvaluator:
    """Test StrategyParameterEvaluator."""

    @pytest.fixture
    def evaluator(self):
        return StrategyParameterEvaluator()

    def test_valid_strategy_passes(self, evaluator):
        """Test that a valid strategy passes evaluation."""
        user_input = "Buy AAPL when RSI below 30, sell when RSI above 70, take profit 5%, stop loss 2%"
        parsed_strategy = {
            "name": "RSI Strategy",
            "asset": "AAPL",
            "entry_conditions": {
                "signal": "RSI < 30"
            },
            "exit_conditions": {
                "signal": "RSI > 70",
                "take_profit": 0.05,
                "stop_loss": -0.02
            }
        }

        result = evaluator.evaluate(user_input=user_input, parsed_strategy=parsed_strategy)
        assert result.passed is True

    def test_detects_wrong_formatting(self, evaluator):
        """Test that incorrect percentage formatting is detected."""
        user_input = "Buy AAPL with 5% take profit"
        parsed_strategy = {
            "name": "Test Strategy",
            "asset": "AAPL",
            "entry_conditions": {"signal": "RSI < 30"},
            "exit_conditions": {
                "take_profit": 5.0,  # Wrong! Should be 0.05
                "stop_loss": -2.0    # Wrong! Should be -0.02
            }
        }

        result = evaluator.evaluate(user_input=user_input, parsed_strategy=parsed_strategy)
        assert result.passed is False
        assert any("decimal" in e.lower() for e in result.errors)

    def test_partial_exit_detection(self, evaluator):
        """Test that partial exit percentage is detected from user input."""
        user_input = "Buy TSLA, sell 50% at take profit"
        parsed_strategy = {
            "name": "Partial Exit Strategy",
            "asset": "TSLA",
            "entry_conditions": {"signal": "RSI < 30"},
            "exit_conditions": {
                "take_profit": 0.05,
                "take_profit_pct_shares": 0.50  # Correct - 50%
            }
        }

        result = evaluator.evaluate(user_input=user_input, parsed_strategy=parsed_strategy)
        assert "partial_exit_check" in result.details

    def test_missing_asset_fails(self, evaluator):
        """Test that missing asset is detected."""
        user_input = "Buy AAPL when RSI low"
        parsed_strategy = {
            "name": "Test Strategy",
            "asset": None,  # Missing!
            "entry_conditions": {"signal": "RSI < 30"},
            "exit_conditions": {}
        }

        result = evaluator.evaluate(user_input=user_input, parsed_strategy=parsed_strategy)
        assert result.passed is False
        assert any("asset" in e.lower() for e in result.errors)


# =============================================================================
# Test Output Schema Evaluator
# =============================================================================

class TestOutputSchemaEvaluator:
    """Test OutputSchemaEvaluator."""

    @pytest.fixture
    def evaluator(self):
        return OutputSchemaEvaluator()

    def test_valid_schema_passes(self, evaluator):
        """Test that a valid strategy schema passes."""
        strategy = {
            "name": "RSI Strategy",
            "asset": "AAPL",
            "entry_conditions": {"signal": "RSI < 30"},
            "exit_conditions": {
                "take_profit": 0.05,
                "stop_loss": -0.02
            }
        }

        result = evaluator.evaluate(parsed_strategy=strategy)
        assert result.passed is True

    def test_missing_required_fields_fails(self, evaluator):
        """Test that missing required fields are detected."""
        strategy = {
            "name": "Incomplete Strategy"
            # Missing: asset, entry_conditions, exit_conditions
        }

        result = evaluator.evaluate(parsed_strategy=strategy)
        assert result.passed is False
        assert "missing required fields" in result.errors[0].lower()

    def test_wrong_type_fails(self, evaluator):
        """Test that wrong types are detected."""
        strategy = {
            "name": 123,  # Wrong! Should be string
            "asset": "AAPL",
            "entry_conditions": {"signal": "RSI < 30"},
            "exit_conditions": {}
        }

        result = evaluator.evaluate(parsed_strategy=strategy)
        assert result.passed is False
        assert any("wrong type" in e.lower() for e in result.errors)

    def test_out_of_range_values_detected(self, evaluator):
        """Test that out-of-range percentage values are detected."""
        strategy = {
            "name": "Test Strategy",
            "asset": "AAPL",
            "entry_conditions": {"signal": "RSI < 30"},
            "exit_conditions": {
                "take_profit": 5.0,  # Wrong! Should be 0.05 (decimal)
                "stop_loss": -2.0    # Wrong! Should be -0.02
            }
        }

        result = evaluator.evaluate(parsed_strategy=strategy)
        assert result.passed is False
        assert any("normalized" in e.lower() or "percentage" in e.lower() for e in result.errors)

    def test_empty_entry_conditions_fails(self, evaluator):
        """Test that empty entry conditions are detected."""
        strategy = {
            "name": "Test Strategy",
            "asset": "AAPL",
            "entry_conditions": {},  # Empty!
            "exit_conditions": {"take_profit": 0.05}
        }

        result = evaluator.evaluate(parsed_strategy=strategy)
        assert result.passed is False


# =============================================================================
# Test Backtest Correctness Evaluator
# =============================================================================

class TestBacktestCorrectnessEvaluator:
    """Test BacktestCorrectnessEvaluator."""

    @pytest.fixture
    def evaluator(self):
        return BacktestCorrectnessEvaluator()

    def test_valid_backtest_passes(self, evaluator):
        """Test that a valid backtest passes evaluation."""
        strategy = {
            "name": "Test Strategy",
            "exit_conditions": {}
        }
        backtest_result = {
            "total_trades": 10,
            "win_rate": 60.0,
            "total_return": 15.5,
            "trades": [
                {"side": "buy", "symbol": "AAPL", "quantity": 10, "price": 150.0},
                {"side": "sell", "symbol": "AAPL", "quantity": 10, "price": 155.0, "pnl": 50.0}
            ]
        }

        result = evaluator.evaluate(
            strategy=strategy,
            backtest_result=backtest_result
        )
        assert result.passed is True

    def test_detects_cascading_exits(self, evaluator):
        """Test that cascading exit bug is detected."""
        strategy = {
            "name": "Test Strategy",
            "exit_conditions": {"take_profit_pct_shares": 0.5}
        }
        # Simulate cascading exits: 100 → 50 → 25 → 12.5
        backtest_result = {
            "total_trades": 4,
            "trades": [
                {"side": "buy", "symbol": "AAPL", "quantity": 100, "price": 150.0},
                {"side": "sell", "symbol": "AAPL", "quantity": 50, "price": 155.0},
                {"side": "sell", "symbol": "AAPL", "quantity": 25, "price": 157.0},
                {"side": "sell", "symbol": "AAPL", "quantity": 12, "price": 158.0},
            ]
        }

        result = evaluator.evaluate(
            strategy=strategy,
            backtest_result=backtest_result
        )
        # Note: This tests the cascading detection logic
        assert "cascade_check" in result.details

    def test_invalid_trade_quantity(self, evaluator):
        """Test that negative quantities are detected."""
        strategy = {"name": "Test", "exit_conditions": {}}
        backtest_result = {
            "trades": [
                {"side": "buy", "symbol": "AAPL", "quantity": -10, "price": 150.0}
            ]
        }

        result = evaluator.evaluate(
            strategy=strategy,
            backtest_result=backtest_result
        )
        assert any("negative" in e.lower() for e in result.errors)


# =============================================================================
# Test Evaluator Runner
# =============================================================================

class TestEvaluatorRunner:
    """Test EvaluatorRunner class."""

    def test_run_all_evaluators(self):
        """Test running all evaluators at once."""
        runner = EvaluatorRunner()
        runner.add_evaluator(OutputSchemaEvaluator())
        runner.add_evaluator(StrategyParameterEvaluator())

        strategy = {
            "name": "Test Strategy",
            "asset": "AAPL",
            "entry_conditions": {"signal": "RSI < 30"},
            "exit_conditions": {"take_profit": 0.05}
        }

        suite = runner.run_all(
            parsed_strategy=strategy,
            user_input="Buy AAPL when RSI below 30"
        )

        assert len(suite.results) == 2
        assert isinstance(suite.all_passed, bool)
        assert 0 <= suite.pass_rate <= 1


# =============================================================================
# Integration Tests
# =============================================================================

class TestEvaluatorIntegration:
    """Integration tests for the evaluation framework."""

    def test_full_evaluation_pipeline(self):
        """Test a complete evaluation pipeline."""
        # Create evaluators
        schema_eval = OutputSchemaEvaluator()
        param_eval = StrategyParameterEvaluator()

        # Valid strategy
        user_input = "Create RSI strategy for AAPL, buy when RSI below 30, take profit 5%"
        strategy = {
            "name": "RSI AAPL Strategy",
            "asset": "AAPL",
            "entry_conditions": {"signal": "RSI < 30"},
            "exit_conditions": {
                "signal": "RSI > 70",
                "take_profit": 0.05,
                "stop_loss": -0.02
            }
        }

        # Run evaluations
        schema_result = schema_eval.evaluate(parsed_strategy=strategy)
        param_result = param_eval.evaluate(
            user_input=user_input,
            parsed_strategy=strategy
        )

        # Both should pass for valid input
        assert schema_result.passed is True
        assert param_result.passed is True

    def test_catches_partial_exit_bug(self):
        """
        Test that the evaluation framework would catch the partial exit bug.

        The bug: -10.0 (percentage) being used instead of 0.10 (decimal)
        """
        schema_eval = OutputSchemaEvaluator()

        # Buggy strategy with wrong percentage format
        buggy_strategy = {
            "name": "Buggy Strategy",
            "asset": "AAPL",
            "entry_conditions": {"signal": "RSI < 30"},
            "exit_conditions": {
                "take_profit": 10.0,  # Bug: should be 0.10
                "take_profit_pct_shares": 50.0,  # Bug: should be 0.50
            }
        }

        result = schema_eval.evaluate(parsed_strategy=buggy_strategy)

        # Should FAIL because percentages aren't normalized
        assert result.passed is False
        assert len(result.errors) > 0
