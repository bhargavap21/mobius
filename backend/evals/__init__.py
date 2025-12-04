"""
Evaluation Framework for Mobius Trading Bot

Provides deterministic and LLM-based evaluators to ensure
agents correctly implement user requirements.

Phase 2: Deterministic Evaluators
- StrategyParameterEvaluator: Verifies strategy params match user intent
- BacktestCorrectnessEvaluator: Catches cascading exits, trade consistency
- OutputSchemaEvaluator: Validates Pydantic schema compliance

Phase 3: LLM-as-a-Judge Evaluators
- TradeExecutionValidatorEvaluator: Cross-references trades with indicator data
- UserIntentMatchEvaluator: Semantic match of user query vs output
- StrategyCoherenceEvaluator: Checks strategy logic makes sense
"""

from .base import BaseEvaluator, EvaluationResult, EvaluationSuite, EvaluatorRunner
from .strategy_evaluator import StrategyParameterEvaluator
from .backtest_evaluator import BacktestCorrectnessEvaluator
from .schema_evaluator import OutputSchemaEvaluator
from .execution_divergence_evaluator import ExecutionDivergenceEvaluator

# LLM-as-a-Judge evaluators (Phase 3)
from .llm_judge_base import LLMJudgeEvaluator
from .trade_execution_evaluator import TradeExecutionValidatorEvaluator
from .user_intent_evaluator import UserIntentMatchEvaluator
from .strategy_coherence_evaluator import StrategyCoherenceEvaluator

__all__ = [
    # Base classes
    "BaseEvaluator",
    "EvaluationResult",
    "EvaluationSuite",
    "EvaluatorRunner",
    "LLMJudgeEvaluator",
    # Deterministic evaluators (Phase 2)
    "StrategyParameterEvaluator",
    "BacktestCorrectnessEvaluator",
    "OutputSchemaEvaluator",
    "ExecutionDivergenceEvaluator",
    # LLM-as-a-Judge evaluators (Phase 3)
    "TradeExecutionValidatorEvaluator",
    "UserIntentMatchEvaluator",
    "StrategyCoherenceEvaluator",
]
