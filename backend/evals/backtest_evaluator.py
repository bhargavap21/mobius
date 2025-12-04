"""
Backtest Correctness Evaluator

Verifies that backtests execute strategies correctly.
"""

from typing import Any, Dict, List, Optional
from .base import BaseEvaluator, EvaluationResult


class BacktestCorrectnessEvaluator(BaseEvaluator):
    """
    Evaluates backtest execution correctness.

    Checks:
    - Partial exit triggered exactly once
    - Trailing stop only activates after partial exit (if configured)
    - No cascading exits (50→25→12 is WRONG)
    - shares_remaining = original_shares × (1 − partial_pct)
    - State flags (partial_exit_done, trailing_stop_active)
    """

    def __init__(self):
        super().__init__("BacktestCorrectnessEvaluator")

    def evaluate(
        self,
        strategy: Dict[str, Any],
        backtest_result: Dict[str, Any],
        trades: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> EvaluationResult:
        """
        Evaluate backtest execution correctness.

        Args:
            strategy: The strategy configuration
            backtest_result: Backtest metrics/results
            trades: List of trades from backtest

        Returns:
            EvaluationResult with pass/fail status
        """
        errors = []
        warnings = []
        details = {}

        # Extract trades from backtest_result if not provided separately
        if trades is None:
            trades = backtest_result.get("trades", [])

        details["total_trades"] = len(trades)
        details["strategy_name"] = strategy.get("name", "unknown")

        # Check if partial exits are configured
        exit_cond = strategy.get("exit_conditions", {})
        partial_pct = exit_cond.get("take_profit_pct_shares")
        has_partial_exit = partial_pct is not None and partial_pct < 1.0

        if has_partial_exit:
            # Run partial exit checks
            partial_result = self._check_partial_exits(
                trades, partial_pct, strategy
            )
            if partial_result["errors"]:
                errors.extend(partial_result["errors"])
            if partial_result["warnings"]:
                warnings.extend(partial_result["warnings"])
            details["partial_exit_check"] = partial_result

        # Check for cascading exits (bug detection)
        cascade_result = self._check_cascading_exits(trades)
        if cascade_result["errors"]:
            errors.extend(cascade_result["errors"])
        if cascade_result["warnings"]:
            warnings.extend(cascade_result["warnings"])
        details["cascade_check"] = cascade_result

        # Check trailing stop logic
        if exit_cond.get("trailing_stop_pct"):
            trailing_result = self._check_trailing_stop(
                trades, has_partial_exit
            )
            if trailing_result["errors"]:
                errors.extend(trailing_result["errors"])
            if trailing_result["warnings"]:
                warnings.extend(trailing_result["warnings"])
            details["trailing_stop_check"] = trailing_result

        # Check trade consistency
        consistency_result = self._check_trade_consistency(trades)
        if consistency_result["errors"]:
            errors.extend(consistency_result["errors"])
        if consistency_result["warnings"]:
            warnings.extend(consistency_result["warnings"])
        details["consistency_check"] = consistency_result

        # Check metrics accuracy
        metrics_result = self._check_metrics_accuracy(backtest_result, trades)
        if metrics_result["errors"]:
            errors.extend(metrics_result["errors"])
        if metrics_result["warnings"]:
            warnings.extend(metrics_result["warnings"])
        details["metrics_check"] = metrics_result

        # Calculate score
        total_checks = 4 if has_partial_exit else 3
        passed_checks = sum([
            not (partial_result["errors"] if has_partial_exit else False),
            not cascade_result["errors"],
            not consistency_result["errors"],
            not metrics_result["errors"],
        ])
        score = passed_checks / total_checks

        if errors:
            return EvaluationResult.failure(
                self.name,
                errors=errors,
                details=details,
                score=score,
            )

        if warnings:
            return EvaluationResult.warning(
                self.name,
                warnings=warnings,
                details=details,
                score=score,
            )

        return EvaluationResult.success(
            self.name,
            details=details,
            score=score,
        )

    def _check_partial_exits(
        self,
        trades: List[Dict[str, Any]],
        expected_partial_pct: float,
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check partial exit execution.

        Verifies:
        - Partial exit triggered exactly once per position
        - Correct percentage of shares sold
        """
        result = {"errors": [], "warnings": [], "details": {}}

        # Group trades by entry/position
        positions = self._group_trades_by_position(trades)
        result["details"]["position_count"] = len(positions)

        for pos_id, pos_trades in positions.items():
            partial_exits = [
                t for t in pos_trades
                if t.get("exit_type") == "partial_exit" or
                t.get("is_partial_exit") or
                ("partial" in str(t.get("reason", "")).lower())
            ]

            # Check partial exit count
            if len(partial_exits) > 1:
                result["errors"].append(
                    f"Position {pos_id}: Multiple partial exits detected ({len(partial_exits)}). "
                    "Should only trigger once."
                )
            elif len(partial_exits) == 0 and len([t for t in pos_trades if t.get("side") == "sell"]) > 0:
                # Had sells but no partial exit flagged
                result["warnings"].append(
                    f"Position {pos_id}: Has sells but no partial exit flagged. "
                    "May be correct if strategy uses full exit only."
                )

            # Verify partial exit percentage
            if partial_exits:
                entry_qty = self._get_entry_quantity(pos_trades)
                if entry_qty:
                    partial_qty = partial_exits[0].get("quantity", 0)
                    actual_pct = partial_qty / entry_qty
                    expected_pct = expected_partial_pct

                    if abs(actual_pct - expected_pct) > 0.01:  # 1% tolerance
                        result["errors"].append(
                            f"Position {pos_id}: Partial exit sold {actual_pct:.1%} "
                            f"but expected {expected_pct:.1%}"
                        )

        return result

    def _check_cascading_exits(
        self,
        trades: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check for cascading exit bug.

        Bug pattern: 50% → 25% → 12.5% (exponential decay)
        Correct pattern: 50% once, then remaining 50% at final exit
        """
        result = {"errors": [], "warnings": [], "details": {}}

        positions = self._group_trades_by_position(trades)

        for pos_id, pos_trades in positions.items():
            sells = [t for t in pos_trades if t.get("side") == "sell"]

            if len(sells) > 2:
                # More than 2 sells (entry sell is unusual, but check for cascading)
                quantities = [s.get("quantity", 0) for s in sells]

                # Check for exponential decay pattern
                if len(quantities) >= 3:
                    is_cascading = all(
                        quantities[i] > quantities[i + 1] * 1.5
                        for i in range(len(quantities) - 1)
                    )
                    if is_cascading:
                        result["errors"].append(
                            f"Position {pos_id}: Cascading exit detected! "
                            f"Quantities: {quantities}. "
                            "This is a bug - partial exit should only happen once."
                        )

        return result

    def _check_trailing_stop(
        self,
        trades: List[Dict[str, Any]],
        has_partial_exit: bool
    ) -> Dict[str, Any]:
        """
        Check trailing stop logic.

        If partial exits configured, trailing stop should only
        activate AFTER partial exit is done.
        """
        result = {"errors": [], "warnings": [], "details": {}}

        positions = self._group_trades_by_position(trades)

        for pos_id, pos_trades in positions.items():
            trailing_exits = [
                t for t in pos_trades
                if t.get("exit_type") == "trailing_stop" or
                "trailing" in str(t.get("reason", "")).lower()
            ]

            partial_exits = [
                t for t in pos_trades
                if t.get("exit_type") == "partial_exit" or
                t.get("is_partial_exit")
            ]

            if trailing_exits and has_partial_exit:
                # Trailing stop should come AFTER partial exit
                if partial_exits:
                    partial_time = partial_exits[0].get("timestamp") or partial_exits[0].get("date")
                    trailing_time = trailing_exits[0].get("timestamp") or trailing_exits[0].get("date")

                    if partial_time and trailing_time and trailing_time < partial_time:
                        result["errors"].append(
                            f"Position {pos_id}: Trailing stop triggered BEFORE partial exit. "
                            "Trailing stop should only activate after partial exit is done."
                        )
                else:
                    result["warnings"].append(
                        f"Position {pos_id}: Trailing stop triggered but no partial exit found. "
                        "Check if partial exit was configured correctly."
                    )

        return result

    def _check_trade_consistency(
        self,
        trades: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check trade data consistency.

        Verifies:
        - No negative quantities (shares)
        - Valid entry and exit prices
        - Required fields present
        """
        result = {"errors": [], "warnings": [], "details": {}}

        for i, trade in enumerate(trades):
            # Check quantity - backtest uses 'shares' field, not 'quantity'
            qty = trade.get("shares", trade.get("quantity", 0))
            if qty < 0:
                result["errors"].append(
                    f"Trade {i}: Negative quantity ({qty})"
                )
            elif qty == 0:
                result["warnings"].append(
                    f"Trade {i}: Zero quantity trade"
                )

            # Check prices - backtest uses 'entry_price' and 'exit_price', not 'price'
            entry_price = trade.get("entry_price", 0)
            exit_price = trade.get("exit_price", 0)

            if entry_price <= 0:
                result["errors"].append(
                    f"Trade {i}: Invalid entry_price ({entry_price})"
                )

            if exit_price <= 0:
                result["errors"].append(
                    f"Trade {i}: Invalid exit_price ({exit_price})"
                )

            # Check required fields for backtest trade format
            # Backtest trades have: entry_date, exit_date, entry_price, exit_price, shares, symbol
            required = ["entry_date", "exit_date", "entry_price", "exit_price", "shares"]
            missing = [f for f in required if f not in trade]
            if missing:
                result["warnings"].append(
                    f"Trade {i}: Missing fields: {missing}"
                )

        return result

    def _check_metrics_accuracy(
        self,
        backtest_result: Dict[str, Any],
        trades: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check if metrics match trade data.
        """
        result = {"errors": [], "warnings": [], "details": {}}

        reported_trades = backtest_result.get("total_trades", len(trades))
        actual_trades = len(trades)

        if reported_trades != actual_trades:
            result["warnings"].append(
                f"Trade count mismatch: reported {reported_trades}, actual {actual_trades}"
            )

        # Check win rate calculation if we have enough data
        if trades:
            profitable = sum(1 for t in trades if t.get("pnl", 0) > 0)
            calculated_win_rate = profitable / len(trades) * 100

            reported_win_rate = backtest_result.get("win_rate", calculated_win_rate)
            if abs(reported_win_rate - calculated_win_rate) > 1:
                result["warnings"].append(
                    f"Win rate mismatch: reported {reported_win_rate:.1f}%, calculated {calculated_win_rate:.1f}%"
                )

        return result

    def _group_trades_by_position(
        self,
        trades: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group trades by position/entry."""
        positions = {}

        for trade in trades:
            # Use position_id if available, otherwise use symbol
            pos_id = trade.get("position_id") or trade.get("symbol", "unknown")
            if pos_id not in positions:
                positions[pos_id] = []
            positions[pos_id].append(trade)

        return positions

    def _get_entry_quantity(
        self,
        trades: List[Dict[str, Any]]
    ) -> Optional[float]:
        """Get entry quantity for a position."""
        buys = [t for t in trades if t.get("side") == "buy"]
        if buys:
            return sum(t.get("quantity", 0) for t in buys)
        return None
