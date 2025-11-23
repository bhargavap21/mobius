"""
Tests for StrategySchema validation and normalization

Run with: pytest backend/tests/test_strategy_schema.py -v
"""

import pytest
from schemas.strategy import (
    StrategySchema,
    ExitConditions,
    EntryConditions,
    RiskManagement,
    validate_strategy,
    EntrySignalType,
)


class TestExitConditionsNormalization:
    """Test unit normalization for exit conditions"""

    def test_stop_loss_negative_percentage(self):
        """stop_loss: -10.0 should become 0.10"""
        exit_cond = ExitConditions(stop_loss=-10.0)
        assert exit_cond.stop_loss == 0.10

    def test_stop_loss_positive_percentage(self):
        """stop_loss: 10.0 should become 0.10"""
        exit_cond = ExitConditions(stop_loss=10.0)
        assert exit_cond.stop_loss == 0.10

    def test_stop_loss_decimal(self):
        """stop_loss: 0.10 should stay 0.10"""
        exit_cond = ExitConditions(stop_loss=0.10)
        assert exit_cond.stop_loss == 0.10

    def test_take_profit_percentage(self):
        """take_profit: 5.0 should become 0.05"""
        exit_cond = ExitConditions(take_profit=5.0)
        assert exit_cond.take_profit == 0.05

    def test_take_profit_decimal(self):
        """take_profit: 0.02 should stay 0.02"""
        exit_cond = ExitConditions(take_profit=0.02)
        assert exit_cond.take_profit == 0.02

    def test_pct_shares_percentage(self):
        """take_profit_pct_shares: 50 should become 0.50"""
        exit_cond = ExitConditions(take_profit_pct_shares=50)
        assert exit_cond.take_profit_pct_shares == 0.50

    def test_pct_shares_decimal(self):
        """take_profit_pct_shares: 0.5 should stay 0.5"""
        exit_cond = ExitConditions(take_profit_pct_shares=0.5)
        assert exit_cond.take_profit_pct_shares == 0.5

    def test_none_values(self):
        """None values should stay None"""
        exit_cond = ExitConditions()
        assert exit_cond.stop_loss is None
        assert exit_cond.take_profit is None


class TestHasTrailingStop:
    """Test has_trailing_stop property detection"""

    def test_two_phase_exit_detected(self):
        """Two-phase exit: stop_loss > 0 AND take_profit_pct_shares < 1.0"""
        exit_cond = ExitConditions(
            stop_loss=0.10,
            take_profit_pct_shares=0.5
        )
        assert exit_cond.has_trailing_stop is True

    def test_no_trailing_stop_full_exit(self):
        """Not two-phase: take_profit_pct_shares = 1.0"""
        exit_cond = ExitConditions(
            stop_loss=0.10,
            take_profit_pct_shares=1.0
        )
        assert exit_cond.has_trailing_stop is False

    def test_no_trailing_stop_no_stop_loss(self):
        """Not two-phase: no stop_loss"""
        exit_cond = ExitConditions(
            take_profit_pct_shares=0.5
        )
        assert exit_cond.has_trailing_stop is False

    def test_trailing_stop_from_percentage_input(self):
        """Two-phase from percentage input: -10% stop, 50% partial"""
        exit_cond = ExitConditions(
            stop_loss=-10.0,  # Should normalize to 0.10
            take_profit_pct_shares=0.5
        )
        assert exit_cond.stop_loss == 0.10
        assert exit_cond.has_trailing_stop is True


class TestFullStrategyValidation:
    """Test complete strategy validation"""

    def test_rsi_mean_reversion_strategy(self):
        """Validate RSI mean-reversion with two-phase exit"""
        raw = {
            "name": "RSI Mean Reversion",
            "asset": "AAPL",
            "entry_conditions": {
                "signal": "rsi",
                "parameters": {
                    "threshold": 30,
                    "rsi_exit_threshold": 70
                }
            },
            "exit_conditions": {
                "stop_loss": -10.0,  # Percentage
                "custom_exit": "RSI above 70",
                "take_profit_pct_shares": 0.5
            }
        }

        strategy = validate_strategy(raw)

        assert strategy.name == "RSI Mean Reversion"
        assert strategy.asset == "AAPL"
        assert strategy.exit_conditions.stop_loss == 0.10
        assert strategy.exit_conditions.take_profit_pct_shares == 0.5
        assert strategy.is_two_phase_exit is True
        assert strategy.entry_conditions.signal == EntrySignalType.RSI

    def test_simple_strategy_defaults(self):
        """Test that defaults are applied correctly"""
        raw = {"name": "Simple Strategy"}

        strategy = validate_strategy(raw)

        assert strategy.asset == "SPY"  # Default
        assert strategy.exit_conditions.take_profit_pct_shares == 1.0  # Default
        assert strategy.risk_management.position_size == 1.0  # Default

    def test_to_dict_conversion(self):
        """Test conversion back to dict"""
        raw = {
            "name": "Test Strategy",
            "asset": "TSLA",
            "exit_conditions": {
                "stop_loss": -5.0
            }
        }

        strategy = validate_strategy(raw)
        result = strategy.to_dict()

        assert result["name"] == "Test Strategy"
        assert result["asset"] == "TSLA"
        assert result["exit_conditions"]["stop_loss"] == 0.05


class TestEntryConditions:
    """Test entry condition parsing"""

    def test_signal_type_normalization(self):
        """Signal types should normalize to enum"""
        entry = EntryConditions(signal="RSI")
        assert entry.signal == EntrySignalType.RSI

        entry = EntryConditions(signal="macd")
        assert entry.signal == EntrySignalType.MACD

    def test_unknown_signal_defaults_to_custom(self):
        """Unknown signal types default to 'custom'"""
        entry = EntryConditions(signal="unknown_indicator")
        assert entry.signal == EntrySignalType.CUSTOM


class TestRiskManagement:
    """Test risk management normalization"""

    def test_position_size_percentage(self):
        """position_size: 50 should become 0.50"""
        risk = RiskManagement(position_size=50)
        assert risk.position_size == 0.50

    def test_position_size_decimal(self):
        """position_size: 0.25 should stay 0.25"""
        risk = RiskManagement(position_size=0.25)
        assert risk.position_size == 0.25


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
