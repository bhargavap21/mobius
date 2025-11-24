"""
Output Schema Evaluator

Verifies that strategy output matches expected schema.
"""

from typing import Any, Dict, List, Optional, Type
from .base import BaseEvaluator, EvaluationResult


class OutputSchemaEvaluator(BaseEvaluator):
    """
    Evaluates that strategy output matches expected schema.

    Checks:
    - No missing required fields
    - Correct data types
    - Values within expected ranges
    - Consistent field naming
    """

    # Required top-level fields for a valid strategy
    REQUIRED_FIELDS = ["name", "asset", "entry_conditions", "exit_conditions"]

    # Required entry condition fields
    REQUIRED_ENTRY_FIELDS = ["signal"]

    # Expected field types
    FIELD_TYPES = {
        "name": str,
        "asset": str,
        "timeframe": str,
        "entry_conditions": dict,
        "exit_conditions": dict,
        "risk_management": dict,
        "mode": str,
    }

    # Exit condition field types
    EXIT_FIELD_TYPES = {
        "take_profit": (int, float),
        "stop_loss": (int, float),
        "trailing_stop_pct": (int, float),
        "take_profit_pct_shares": (int, float),
        "signal": str,
    }

    # Valid ranges for percentage fields (as decimals)
    VALID_RANGES = {
        "take_profit": (0.001, 1.0),  # 0.1% to 100%
        "stop_loss": (-1.0, -0.001),  # -100% to -0.1%
        "trailing_stop_pct": (0.001, 0.5),  # 0.1% to 50%
        "take_profit_pct_shares": (0.01, 1.0),  # 1% to 100%
    }

    def __init__(self):
        super().__init__("OutputSchemaEvaluator")

    def evaluate(
        self,
        parsed_strategy: Dict[str, Any],
        **kwargs
    ) -> EvaluationResult:
        """
        Evaluate strategy schema compliance.

        Args:
            parsed_strategy: The parsed strategy dictionary

        Returns:
            EvaluationResult with pass/fail status
        """
        errors = []
        warnings = []
        details = {}

        # Check required fields
        required_result = self._check_required_fields(parsed_strategy)
        if required_result["errors"]:
            errors.extend(required_result["errors"])
        if required_result["warnings"]:
            warnings.extend(required_result["warnings"])
        details["required_fields_check"] = required_result

        # Check field types
        types_result = self._check_field_types(parsed_strategy)
        if types_result["errors"]:
            errors.extend(types_result["errors"])
        if types_result["warnings"]:
            warnings.extend(types_result["warnings"])
        details["field_types_check"] = types_result

        # Check value ranges
        ranges_result = self._check_value_ranges(parsed_strategy)
        if ranges_result["errors"]:
            errors.extend(ranges_result["errors"])
        if ranges_result["warnings"]:
            warnings.extend(ranges_result["warnings"])
        details["value_ranges_check"] = ranges_result

        # Check entry conditions
        entry_result = self._check_entry_schema(parsed_strategy)
        if entry_result["errors"]:
            errors.extend(entry_result["errors"])
        if entry_result["warnings"]:
            warnings.extend(entry_result["warnings"])
        details["entry_schema_check"] = entry_result

        # Check exit conditions
        exit_result = self._check_exit_schema(parsed_strategy)
        if exit_result["errors"]:
            errors.extend(exit_result["errors"])
        if exit_result["warnings"]:
            warnings.extend(exit_result["warnings"])
        details["exit_schema_check"] = exit_result

        # Calculate score
        total_checks = 5
        passed_checks = sum([
            not required_result["errors"],
            not types_result["errors"],
            not ranges_result["errors"],
            not entry_result["errors"],
            not exit_result["errors"],
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

    def _check_required_fields(
        self,
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check that all required fields are present."""
        result = {"errors": [], "warnings": [], "details": {}}

        missing = []
        for field in self.REQUIRED_FIELDS:
            if field not in strategy or strategy[field] is None:
                missing.append(field)

        result["details"]["missing_fields"] = missing

        if missing:
            result["errors"].append(
                f"Missing required fields: {', '.join(missing)}"
            )

        # Check for empty strings
        empty = []
        for field in self.REQUIRED_FIELDS:
            if field in strategy and strategy[field] == "":
                empty.append(field)

        if empty:
            result["warnings"].append(
                f"Empty required fields: {', '.join(empty)}"
            )

        return result

    def _check_field_types(
        self,
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check that fields have correct types."""
        result = {"errors": [], "warnings": [], "details": {}}
        type_mismatches = []

        for field, expected_type in self.FIELD_TYPES.items():
            if field in strategy and strategy[field] is not None:
                value = strategy[field]
                if not isinstance(value, expected_type):
                    type_mismatches.append({
                        "field": field,
                        "expected": expected_type.__name__,
                        "actual": type(value).__name__,
                        "value": str(value)[:50],
                    })

        result["details"]["type_mismatches"] = type_mismatches

        if type_mismatches:
            for mismatch in type_mismatches:
                result["errors"].append(
                    f"Field '{mismatch['field']}' has wrong type: "
                    f"expected {mismatch['expected']}, got {mismatch['actual']}"
                )

        return result

    def _check_value_ranges(
        self,
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check that values are within expected ranges."""
        result = {"errors": [], "warnings": [], "details": {}}
        out_of_range = []

        exit_cond = strategy.get("exit_conditions", {})

        for field, (min_val, max_val) in self.VALID_RANGES.items():
            if field in exit_cond and exit_cond[field] is not None:
                value = exit_cond[field]
                if isinstance(value, (int, float)):
                    # Handle stop_loss which should be negative
                    if field == "stop_loss":
                        if value > 0:  # Should be negative
                            value = -value
                        if not (min_val <= value <= max_val):
                            out_of_range.append({
                                "field": field,
                                "value": value,
                                "expected_range": f"[{min_val}, {max_val}]",
                            })
                    else:
                        if not (min_val <= value <= max_val):
                            out_of_range.append({
                                "field": field,
                                "value": value,
                                "expected_range": f"[{min_val}, {max_val}]",
                            })

        result["details"]["out_of_range"] = out_of_range

        if out_of_range:
            for oor in out_of_range:
                # Check if value looks like a percentage that wasn't normalized
                if oor["value"] > 1 or oor["value"] < -1:
                    result["errors"].append(
                        f"Field '{oor['field']}' value {oor['value']} appears to be a percentage "
                        f"that wasn't normalized to decimal. Expected range: {oor['expected_range']}"
                    )
                else:
                    result["warnings"].append(
                        f"Field '{oor['field']}' value {oor['value']} outside typical range "
                        f"{oor['expected_range']}"
                    )

        return result

    def _check_entry_schema(
        self,
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check entry conditions schema."""
        result = {"errors": [], "warnings": [], "details": {}}

        entry = strategy.get("entry_conditions", {})

        if not entry:
            result["errors"].append("Entry conditions are empty or missing")
            return result

        # Check required entry fields
        for field in self.REQUIRED_ENTRY_FIELDS:
            if field not in entry or entry[field] is None:
                result["errors"].append(f"Missing entry field: {field}")

        # Check signal is not empty
        signal = entry.get("signal", "")
        if signal == "":
            result["errors"].append("Entry signal is empty")
        elif len(signal) < 3:
            result["warnings"].append(
                f"Entry signal seems too short: '{signal}'"
            )

        return result

    def _check_exit_schema(
        self,
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check exit conditions schema."""
        result = {"errors": [], "warnings": [], "details": {}}

        exit_cond = strategy.get("exit_conditions", {})

        if not exit_cond:
            result["warnings"].append(
                "Exit conditions are empty - strategy will only exit on signal"
            )
            return result

        # Check exit field types
        for field, expected_type in self.EXIT_FIELD_TYPES.items():
            if field in exit_cond and exit_cond[field] is not None:
                value = exit_cond[field]
                if not isinstance(value, expected_type):
                    result["errors"].append(
                        f"Exit field '{field}' has wrong type: "
                        f"expected {expected_type}, got {type(value).__name__}"
                    )

        # Check for conflicting exit conditions
        has_tp = exit_cond.get("take_profit") is not None
        has_sl = exit_cond.get("stop_loss") is not None
        has_signal = exit_cond.get("signal") is not None

        if not has_tp and not has_sl and not has_signal:
            result["warnings"].append(
                "No take profit, stop loss, or exit signal defined"
            )

        # Check partial exit configuration consistency
        partial_pct = exit_cond.get("take_profit_pct_shares")
        if partial_pct is not None:
            if not has_tp:
                result["warnings"].append(
                    "Partial exit configured but no take profit level set"
                )
            if partial_pct == 1.0:
                result["warnings"].append(
                    "take_profit_pct_shares is 1.0 (100%), which is a full exit, not partial"
                )

        return result


class StrategySchemaValidator:
    """
    Standalone validator for quick schema checks.

    Can be used independently of the evaluation framework.
    """

    @staticmethod
    def validate(strategy: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate strategy and return validation result.

        Returns:
            Dict with 'valid', 'errors', 'warnings' keys
        """
        evaluator = OutputSchemaEvaluator()
        result = evaluator.evaluate(parsed_strategy=strategy)

        return {
            "valid": result.passed,
            "errors": result.errors,
            "warnings": result.warnings,
            "score": result.score,
        }

    @staticmethod
    def is_valid(strategy: Dict[str, Any]) -> bool:
        """Quick check if strategy is valid."""
        result = StrategySchemaValidator.validate(strategy)
        return result["valid"]
