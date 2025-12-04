"""
Code Validation Evaluator - Validates generated code quality and executability

This evaluator checks that generated trading bot code:
1. Is syntactically valid Python
2. Properly extends BaseStrategy
3. Implements required methods
4. Can be executed without errors
5. Produces reasonable backtest results

This is a CRITICAL evaluator - if code doesn't execute, the strategy is useless.
"""

import logging
import ast
import re
from typing import Dict, Any, List
from datetime import datetime, timedelta
from evals.base import BaseEvaluator, EvaluationResult

logger = logging.getLogger(__name__)


class CodeValidationEvaluator(BaseEvaluator):
    """
    Evaluates generated code for quality and executability.

    Checks:
    - Syntax validity
    - Proper class structure
    - Required method implementation
    - Imports correctness
    - Code execution (via backtest)
    - Result validity
    """

    def __init__(self):
        super().__init__("CodeValidation")
        self.weight = 1.0  # Critical evaluator
        self.required_methods = ['initialize', 'generate_signals']
        self.required_imports = ['BaseStrategy', 'Signal']

    def evaluate(
        self,
        user_input: str = "",
        strategy: Dict[str, Any] = None,
        generated_code: str = "",
        backtest_result: Dict[str, Any] = None,
        **kwargs
    ) -> EvaluationResult:
        """
        Evaluate code quality and executability.

        Args:
            user_input: Original user query
            strategy: Parsed strategy configuration
            generated_code: Generated Python code
            backtest_result: Backtest execution results (optional)
            **kwargs: Additional parameters (ignored)

        Returns:
            EvaluationResult with score and feedback
        """
        # Handle None strategy
        if strategy is None:
            strategy = {}

        # Handle empty code
        if not generated_code:
            return EvaluationResult.skipped(
                self.name,
                "No code provided for validation"
            )

        logger.info(f"🔍 Evaluating code validation...")

        checks = {
            'syntax_valid': self._check_syntax(generated_code),
            'imports_correct': self._check_imports(generated_code),
            'class_structure': self._check_class_structure(generated_code),
            'required_methods': self._check_required_methods(generated_code),
            'proper_inheritance': self._check_inheritance(generated_code),
            'data_validation': self._check_data_validation(generated_code),
        }

        # Add backtest execution check if results provided
        if backtest_result:
            checks['execution_success'] = self._check_execution(backtest_result)
            checks['results_valid'] = self._check_results_validity(backtest_result)

        # Calculate score
        passed_checks = sum(1 for result in checks.values() if result['passed'])
        total_checks = len(checks)
        score = passed_checks / total_checks

        # Generate feedback
        feedback = self._generate_feedback(checks)

        # Determine pass/fail
        passed = score >= 0.8  # 80% of checks must pass

        # Extract errors and warnings
        errors = []
        warnings = []
        for check_name, check_result in checks.items():
            if not check_result['passed']:
                message = check_result.get('message', 'Check failed')
                if check_result.get('severity') == 'warning':
                    warnings.append(f"{check_name}: {message}")
                else:
                    errors.append(f"{check_name}: {message}")

        details = {
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'failed_checks': total_checks - passed_checks,
            'checks': checks,
            'weight': self.weight,
        }

        if passed:
            logger.info(f"✅ Code validation passed: {score:.2%}")
            return EvaluationResult.success(
                evaluator_name=self.name,
                score=score,
                details=details,
                warnings=warnings,
            )
        else:
            logger.warning(f"⚠️  Code validation failed: {score:.2%}")
            return EvaluationResult.failure(
                evaluator_name=self.name,
                score=score,
                errors=errors,
                details=details,
            )

    def _check_syntax(self, code: str) -> Dict[str, Any]:
        """Check if code is syntactically valid Python."""
        try:
            ast.parse(code)
            return {
                'passed': True,
                'message': 'Code is syntactically valid'
            }
        except SyntaxError as e:
            return {
                'passed': False,
                'message': f'Syntax error: {e.msg} (line {e.lineno})',
                'error': str(e)
            }

    def _check_imports(self, code: str) -> Dict[str, Any]:
        """Check if required imports are present."""
        missing_imports = []

        for required in self.required_imports:
            if required not in code:
                missing_imports.append(required)

        if not missing_imports:
            return {
                'passed': True,
                'message': 'All required imports present'
            }
        else:
            return {
                'passed': False,
                'message': f'Missing imports: {", ".join(missing_imports)}',
                'missing': missing_imports
            }

    def _check_class_structure(self, code: str) -> Dict[str, Any]:
        """Check if code defines a strategy class."""
        try:
            tree = ast.parse(code)

            # Find class definitions
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

            if not classes:
                return {
                    'passed': False,
                    'message': 'No class defined in code'
                }

            # Check if any class ends with "Strategy"
            strategy_classes = [cls for cls in classes if cls.name.endswith('Strategy')]

            if not strategy_classes:
                return {
                    'passed': False,
                    'message': 'No strategy class found (class name should end with "Strategy")'
                }

            return {
                'passed': True,
                'message': f'Strategy class found: {strategy_classes[0].name}',
                'class_name': strategy_classes[0].name
            }

        except Exception as e:
            return {
                'passed': False,
                'message': f'Error parsing class structure: {str(e)}'
            }

    def _check_required_methods(self, code: str) -> Dict[str, Any]:
        """Check if required methods are implemented."""
        try:
            tree = ast.parse(code)

            # Find all method definitions
            methods = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    methods.append(node.name)

            # Check for required methods
            missing_methods = [m for m in self.required_methods if m not in methods]

            if not missing_methods:
                return {
                    'passed': True,
                    'message': 'All required methods implemented',
                    'methods_found': self.required_methods
                }
            else:
                return {
                    'passed': False,
                    'message': f'Missing required methods: {", ".join(missing_methods)}',
                    'missing': missing_methods
                }

        except Exception as e:
            return {
                'passed': False,
                'message': f'Error checking methods: {str(e)}'
            }

    def _check_inheritance(self, code: str) -> Dict[str, Any]:
        """Check if class properly inherits from BaseStrategy."""
        try:
            tree = ast.parse(code)

            # Find strategy class
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name.endswith('Strategy'):
                    # Check bases
                    if node.bases:
                        for base in node.bases:
                            base_name = ast.get_source_segment(code, base)
                            if 'BaseStrategy' in base_name:
                                return {
                                    'passed': True,
                                    'message': 'Class properly inherits from BaseStrategy'
                                }

                    return {
                        'passed': False,
                        'message': 'Class does not inherit from BaseStrategy'
                    }

            return {
                'passed': False,
                'message': 'No strategy class found'
            }

        except Exception as e:
            return {
                'passed': False,
                'message': f'Error checking inheritance: {str(e)}'
            }

    def _check_data_validation(self, code: str) -> Dict[str, Any]:
        """Check if code validates data (checks for None values)."""
        # Check for None checks in code
        none_checks = [
            'is None',
            'is not None',
            '!= None',
            'if rsi',
            'if sentiment',
        ]

        has_validation = any(check in code for check in none_checks)

        if has_validation:
            return {
                'passed': True,
                'message': 'Code includes data validation (None checks)'
            }
        else:
            return {
                'passed': False,
                'message': 'Warning: No explicit None checks found in code',
                'severity': 'warning'  # Not critical but recommended
            }

    def _check_execution(self, backtest_results: Dict[str, Any]) -> Dict[str, Any]:
        """Check if code executed successfully."""
        # Handle both formats:
        # 1. {'success': True, 'metrics': {...}} (from execute_with_generated_code wrapper)
        # 2. {'summary': {...}, 'trades': [...]} (from backtest_strategy)

        if 'success' in backtest_results:
            # Format 1: has explicit success flag
            if backtest_results.get('success'):
                return {
                    'passed': True,
                    'message': 'Code executed successfully in backtest'
                }
            else:
                error = backtest_results.get('error', 'Unknown error')
                return {
                    'passed': False,
                    'message': f'Code execution failed: {error}',
                    'error': error
                }
        else:
            # Format 2: if we have summary or metrics, assume success
            if 'summary' in backtest_results or 'metrics' in backtest_results:
                return {
                    'passed': True,
                    'message': 'Code executed successfully in backtest'
                }
            else:
                return {
                    'passed': False,
                    'message': 'Code execution failed: No results found',
                }

    def _check_results_validity(self, backtest_results: Dict[str, Any]) -> Dict[str, Any]:
        """Check if backtest results are valid and reasonable."""
        # Check if execution failed
        if 'success' in backtest_results and not backtest_results.get('success'):
            return {
                'passed': False,
                'message': 'Cannot validate results - execution failed'
            }

        # Get metrics from either 'metrics' or 'summary' key
        metrics = backtest_results.get('metrics') or backtest_results.get('summary', {})

        # Check for required metrics
        required_metrics = ['total_return', 'sharpe_ratio', 'max_drawdown', 'total_trades']
        missing_metrics = [m for m in required_metrics if m not in metrics]

        if missing_metrics:
            return {
                'passed': False,
                'message': f'Missing metrics: {", ".join(missing_metrics)}'
            }

        # Check for unreasonable values
        total_return = metrics.get('total_return', 0)
        sharpe = metrics.get('sharpe_ratio', 0)
        drawdown = metrics.get('max_drawdown', 0)

        warnings = []

        # Sanity checks
        if abs(total_return) > 1000:
            warnings.append(f'Unrealistic return: {total_return:.1f}%')

        if abs(sharpe) > 10:
            warnings.append(f'Unrealistic Sharpe ratio: {sharpe:.2f}')

        if abs(drawdown) > 100:
            warnings.append(f'Invalid drawdown: {drawdown:.1f}%')

        if warnings:
            return {
                'passed': False,
                'message': 'Results contain unrealistic values',
                'warnings': warnings
            }

        return {
            'passed': True,
            'message': 'Results are valid and reasonable',
            'metrics': {
                'return': f'{total_return:.2f}%',
                'sharpe': f'{sharpe:.2f}',
                'drawdown': f'{drawdown:.2f}%',
            }
        }

    def _generate_feedback(self, checks: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate human-readable feedback from check results."""
        feedback = []

        for check_name, result in checks.items():
            if not result['passed']:
                # Format check name
                display_name = check_name.replace('_', ' ').title()
                message = result.get('message', 'Check failed')
                feedback.append(f"❌ {display_name}: {message}")

        if not feedback:
            feedback.append("✅ All code validation checks passed")

        return feedback


# Convenience function
def validate_code(
    code: str,
    user_input: str = "",
    strategy: Dict[str, Any] = None,
    backtest_results: Dict[str, Any] = None
) -> EvaluationResult:
    """
    Validate generated code.

    Args:
        code: Generated Python code
        user_input: Original user query (optional)
        strategy: Parsed strategy (optional)
        backtest_results: Backtest results (optional)

    Returns:
        EvaluationResult
    """
    evaluator = CodeValidationEvaluator()
    return evaluator.evaluate(
        user_input=user_input or "",
        strategy=strategy or {},
        generated_code=code,
        backtest_result=backtest_results
    )


if __name__ == "__main__":
    # Test code validation
    logging.basicConfig(level=logging.INFO)

    # Test with valid code
    valid_code = """
import logging
from typing import Dict, List
from templates.strategy_base import BaseStrategy, Signal

class TestStrategy(BaseStrategy):
    def initialize(self):
        self.threshold = 30

    def generate_signals(self, current_data: Dict[str, Dict[str, float]]) -> List[Signal]:
        signals = []
        for symbol in self.symbols:
            bar = current_data.get(symbol)
            if bar is None:  # Data validation
                continue

            indicators = self.get_current_indicators(symbol)
            rsi = indicators.get('rsi')

            if rsi is not None and rsi < self.threshold:
                signals.append(Signal(symbol, 'buy'))

        return signals
"""

    result = validate_code(valid_code)

    print("\n" + "="*70)
    print("CODE VALIDATION RESULT")
    print("="*70)
    print(f"Passed: {result['passed']}")
    print(f"Score: {result['score']:.2%}")
    print(f"\nFeedback:")
    for msg in result['feedback']:
        print(f"  {msg}")

    print(f"\nChecks:")
    for check_name, check_result in result['checks'].items():
        status = "✅" if check_result['passed'] else "❌"
        print(f"  {status} {check_name}: {check_result['message']}")
