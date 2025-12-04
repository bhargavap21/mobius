"""
Strategy Parameter Evaluator

Verifies that parsed strategies correctly capture user intent.
"""

import re
from typing import Any, Dict, List, Optional
from .base import BaseEvaluator, EvaluationResult


class StrategyParameterEvaluator(BaseEvaluator):
    """
    Evaluates that strategy parameters match user intent.

    Checks:
    - Asset extraction (correct ticker symbol)
    - Entry condition signals (RSI thresholds, etc.)
    - Exit condition parameters (TP, SL, partial exits)
    - Partial exit percentages
    - Stop-loss/take-profit formatting
    """

    def __init__(self):
        super().__init__("StrategyParameterEvaluator")

    def evaluate(
        self,
        user_input: str,
        parsed_strategy: Dict[str, Any],
        **kwargs
    ) -> EvaluationResult:
        """
        Evaluate strategy parameters against user input.

        Args:
            user_input: Original user description
            parsed_strategy: Parsed strategy dictionary

        Returns:
            EvaluationResult with pass/fail status
        """
        errors = []
        warnings = []
        details = {}

        # Extract expected values from user input
        expected = self._extract_expected_values(user_input)
        details["expected_from_input"] = expected

        # Check asset extraction
        asset_result = self._check_asset(user_input, parsed_strategy)
        if asset_result["error"]:
            errors.append(asset_result["error"])
        if asset_result["warning"]:
            warnings.append(asset_result["warning"])
        details["asset_check"] = asset_result

        # Check entry conditions
        entry_result = self._check_entry_conditions(expected, parsed_strategy)
        if entry_result["errors"]:
            errors.extend(entry_result["errors"])
        if entry_result["warnings"]:
            warnings.extend(entry_result["warnings"])
        details["entry_check"] = entry_result

        # Check exit conditions
        exit_result = self._check_exit_conditions(expected, parsed_strategy)
        if exit_result["errors"]:
            errors.extend(exit_result["errors"])
        if exit_result["warnings"]:
            warnings.extend(exit_result["warnings"])
        details["exit_check"] = exit_result

        # Check partial exit configuration
        partial_result = self._check_partial_exits(expected, parsed_strategy)
        if partial_result["errors"]:
            errors.extend(partial_result["errors"])
        if partial_result["warnings"]:
            warnings.extend(partial_result["warnings"])
        details["partial_exit_check"] = partial_result

        # Check formatting consistency
        format_result = self._check_formatting(parsed_strategy)
        if format_result["errors"]:
            errors.extend(format_result["errors"])
        if format_result["warnings"]:
            warnings.extend(format_result["warnings"])
        details["format_check"] = format_result

        # Calculate score
        total_checks = 5
        passed_checks = sum([
            not asset_result["error"],
            not entry_result["errors"],
            not exit_result["errors"],
            not partial_result["errors"],
            not format_result["errors"],
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

    def _extract_expected_values(self, user_input: str) -> Dict[str, Any]:
        """
        Extract expected parameter values from user input.

        Uses regex patterns to find numbers and keywords.
        """
        expected = {}
        lower_input = user_input.lower()

        # Extract ticker symbols (uppercase words 1-5 chars)
        tickers = re.findall(r'\b([A-Z]{1,5})\b', user_input)
        # Filter common words
        common_words = {'RSI', 'SMA', 'EMA', 'MACD', 'TP', 'SL', 'ATR', 'AND', 'THE', 'FOR', 'BUY', 'SELL'}
        tickers = [t for t in tickers if t not in common_words]
        if tickers:
            expected["tickers"] = tickers

        # Extract RSI values
        rsi_patterns = [
            r'rsi\s*(?:below|under|<|<=)\s*(\d+)',
            r'rsi\s*(?:above|over|>|>=)\s*(\d+)',
            r'rsi\s*=\s*(\d+)',
            r'rsi\s+(\d+)',
        ]
        for pattern in rsi_patterns:
            match = re.search(pattern, lower_input)
            if match:
                expected.setdefault("rsi_thresholds", []).append(int(match.group(1)))

        # Extract percentage values
        pct_patterns = [
            r'(\d+(?:\.\d+)?)\s*%',
            r'(\d+(?:\.\d+)?)\s*percent',
        ]
        for pattern in pct_patterns:
            matches = re.findall(pattern, lower_input)
            if matches:
                expected["percentages"] = [float(m) for m in matches]

        # Extract partial exit info
        partial_patterns = [
            r'sell\s+(\d+)\s*%',
            r'exit\s+(\d+)\s*%',
            r'close\s+(\d+)\s*%',
            r'(\d+)\s*%\s+(?:of\s+)?(?:position|shares)',
            r'partial\s+(?:exit|sell|close).*?(\d+)\s*%',
        ]
        for pattern in partial_patterns:
            match = re.search(pattern, lower_input)
            if match:
                expected["partial_exit_pct"] = float(match.group(1))
                break

        # Check for trailing stop mention
        if 'trailing' in lower_input:
            expected["has_trailing_stop"] = True

        # Extract take profit
        tp_patterns = [
            r'take\s*profit\s*(?:at|of|:)?\s*(\d+(?:\.\d+)?)\s*%',
            r'tp\s*(?:at|of|:)?\s*(\d+(?:\.\d+)?)\s*%',
            r'profit\s+(?:target|goal)\s*(?:of)?\s*(\d+(?:\.\d+)?)\s*%',
        ]
        for pattern in tp_patterns:
            match = re.search(pattern, lower_input)
            if match:
                expected["take_profit_pct"] = float(match.group(1))
                break

        # Extract stop loss
        sl_patterns = [
            r'stop\s*loss\s*(?:at|of|:)?\s*(\d+(?:\.\d+)?)\s*%',
            r'sl\s*(?:at|of|:)?\s*(\d+(?:\.\d+)?)\s*%',
        ]
        for pattern in sl_patterns:
            match = re.search(pattern, lower_input)
            if match:
                expected["stop_loss_pct"] = float(match.group(1))
                break

        return expected

    def _check_asset(
        self,
        user_input: str,
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if correct asset was extracted."""
        result = {"error": None, "warning": None, "actual": None, "expected": None}

        # Check for portfolio mode
        portfolio_mode = strategy.get("portfolio_mode", False)

        # Get asset(s) from strategy
        if portfolio_mode:
            actual_assets = strategy.get("assets", [])
            result["actual"] = actual_assets if actual_assets else None
        else:
            actual_asset = strategy.get("asset")
            result["actual"] = actual_asset

        # Extract expected tickers from input
        tickers = re.findall(r'\b([A-Z]{1,5})\b', user_input)
        common_words = {'RSI', 'SMA', 'EMA', 'MACD', 'TP', 'SL', 'ATR', 'AND', 'THE', 'FOR', 'BUY', 'SELL'}
        tickers = [t for t in tickers if t not in common_words]
        result["expected"] = tickers

        # Validate based on mode
        if portfolio_mode:
            if not actual_assets:
                result["error"] = "No assets list found in portfolio strategy"
            elif tickers:
                # Check if all expected tickers are in the assets list
                missing_tickers = [t for t in tickers if t not in actual_assets]
                if missing_tickers:
                    result["warning"] = f"Some tickers missing from assets list: {missing_tickers}"
        else:
            if not result["actual"]:
                result["error"] = "No asset/ticker found in parsed strategy"
            elif tickers and result["actual"] not in tickers:
                result["warning"] = f"Asset '{result['actual']}' not found in user input. Expected one of: {tickers}"

        return result

    def _check_entry_conditions(
        self,
        expected: Dict[str, Any],
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check entry condition parameters."""
        result = {"errors": [], "warnings": [], "details": {}}

        entry = strategy.get("entry_conditions", {})
        result["details"]["parsed_entry"] = entry

        # Check RSI threshold if expected
        if "rsi_thresholds" in expected:
            signal = entry.get("signal", "")
            if "rsi" in signal.lower():
                # Extract RSI value from parsed signal
                match = re.search(r'(\d+)', signal)
                if match:
                    parsed_rsi = int(match.group(1))
                    if parsed_rsi not in expected["rsi_thresholds"]:
                        result["warnings"].append(
                            f"RSI threshold {parsed_rsi} not in expected values {expected['rsi_thresholds']}"
                        )
            else:
                result["warnings"].append(
                    f"Expected RSI-based entry but got: {signal}"
                )

        return result

    def _check_exit_conditions(
        self,
        expected: Dict[str, Any],
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check exit condition parameters."""
        result = {"errors": [], "warnings": [], "details": {}}

        exit_cond = strategy.get("exit_conditions", {})
        result["details"]["parsed_exit"] = exit_cond

        # Check take profit
        if "take_profit_pct" in expected:
            tp = exit_cond.get("take_profit")
            if tp is None:
                result["errors"].append("Take profit expected but not found in strategy")
            else:
                # Convert to percentage for comparison
                tp_pct = tp * 100 if tp < 1 else tp
                expected_tp = expected["take_profit_pct"]
                if abs(tp_pct - expected_tp) > 0.5:  # Allow 0.5% tolerance
                    result["warnings"].append(
                        f"Take profit mismatch: expected {expected_tp}%, got {tp_pct}%"
                    )

        # Check stop loss
        if "stop_loss_pct" in expected:
            sl = exit_cond.get("stop_loss")
            if sl is None:
                result["errors"].append("Stop loss expected but not found in strategy")
            else:
                sl_pct = abs(sl * 100) if abs(sl) < 1 else abs(sl)
                expected_sl = expected["stop_loss_pct"]
                if abs(sl_pct - expected_sl) > 0.5:
                    result["warnings"].append(
                        f"Stop loss mismatch: expected {expected_sl}%, got {sl_pct}%"
                    )

        # Check trailing stop
        if expected.get("has_trailing_stop"):
            if not exit_cond.get("trailing_stop_pct"):
                result["warnings"].append("Trailing stop expected but not found in strategy")

        return result

    def _check_partial_exits(
        self,
        expected: Dict[str, Any],
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check partial exit configuration."""
        result = {"errors": [], "warnings": [], "details": {}}

        exit_cond = strategy.get("exit_conditions", {})
        partial_pct = exit_cond.get("take_profit_pct_shares")
        result["details"]["parsed_partial_pct"] = partial_pct

        if "partial_exit_pct" in expected:
            expected_pct = expected["partial_exit_pct"]
            result["details"]["expected_partial_pct"] = expected_pct

            if partial_pct is None:
                result["errors"].append(
                    f"Partial exit of {expected_pct}% expected but not configured"
                )
            else:
                # Convert to percentage for comparison
                actual_pct = partial_pct * 100 if partial_pct <= 1 else partial_pct
                if abs(actual_pct - expected_pct) > 1:  # Allow 1% tolerance
                    result["errors"].append(
                        f"Partial exit mismatch: expected {expected_pct}%, got {actual_pct}%"
                    )

        return result

    def _check_formatting(
        self,
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check parameter formatting consistency."""
        result = {"errors": [], "warnings": [], "details": {}}

        exit_cond = strategy.get("exit_conditions", {})

        # Check that percentage values are in decimal format (0.0-1.0)
        tp = exit_cond.get("take_profit")
        sl = exit_cond.get("stop_loss")
        partial = exit_cond.get("take_profit_pct_shares")

        if tp is not None and abs(tp) > 1:
            result["errors"].append(
                f"Take profit should be decimal (0.0-1.0), got {tp}. "
                f"Hint: {abs(tp)}% should be {abs(tp)/100}"
            )

        if sl is not None and abs(sl) > 1:
            result["errors"].append(
                f"Stop loss should be decimal (0.0-1.0), got {sl}. "
                f"Hint: {abs(sl)}% should be {abs(sl)/100}"
            )

        if partial is not None and partial > 1:
            result["errors"].append(
                f"Partial exit percentage should be decimal (0.0-1.0), got {partial}. "
                f"Hint: {partial}% should be {partial/100}"
            )

        return result
