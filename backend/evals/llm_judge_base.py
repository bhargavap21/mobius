"""
LLM-as-a-Judge Base Evaluator

Provides foundation for evaluators that use an LLM to assess
qualitative aspects of strategy generation and execution.
"""

import json
import logging
import os
from abc import abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic
from pydantic import BaseModel, ValidationError

from evals.base import BaseEvaluator, EvaluationResult

logger = logging.getLogger(__name__)

# Type variable for judgment response models
T = TypeVar('T', bound=BaseModel)


class JudgmentScore(BaseModel):
    """Standard judgment output format."""
    score: int  # 1-5 scale
    passed: bool
    reasoning: str
    issues: List[str] = []
    suggestions: List[str] = []


class LLMJudgeEvaluator(BaseEvaluator, Generic[T]):
    """
    Base class for LLM-as-a-Judge evaluators.

    Uses Claude to assess qualitative aspects that deterministic
    rules cannot capture.

    Subclasses must implement:
        - get_system_prompt(): Returns the system prompt with evaluation criteria
        - get_user_prompt(**kwargs): Returns the user prompt with data to evaluate
        - get_response_model(): Returns the Pydantic model for parsing response
        - interpret_judgment(judgment): Converts LLM judgment to EvaluationResult
    """

    def __init__(
        self,
        name: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.0,
        max_tokens: int = 2000,
        max_retries: int = 2,
    ):
        """
        Initialize LLM judge evaluator.

        Args:
            name: Evaluator name
            model: Claude model to use
            temperature: Temperature for LLM (0 for deterministic)
            max_tokens: Max response tokens
            max_retries: Number of retries on failure
        """
        super().__init__(name)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self._client = None

    @property
    def client(self):
        """Lazy-load Anthropic client."""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(
                    api_key=os.getenv("ANTHROPIC_API_KEY")
                )
            except ImportError:
                raise ImportError("anthropic package required for LLM judge evaluators")
        return self._client

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt with evaluation criteria and rubric.

        Should include:
        - Role description
        - Evaluation criteria
        - Scoring rubric (1-5 scale)
        - Output format instructions
        """
        pass

    @abstractmethod
    def get_user_prompt(self, **kwargs) -> str:
        """
        Get the user prompt with data to evaluate.

        Args:
            **kwargs: Data passed to evaluate()

        Returns:
            Formatted prompt with all relevant data
        """
        pass

    @abstractmethod
    def get_response_model(self) -> type[T]:
        """
        Get the Pydantic model for parsing LLM response.

        Returns:
            Pydantic model class
        """
        pass

    @abstractmethod
    def interpret_judgment(self, judgment: T) -> EvaluationResult:
        """
        Convert LLM judgment to EvaluationResult.

        Args:
            judgment: Parsed LLM response

        Returns:
            EvaluationResult with pass/fail and details
        """
        pass

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call the LLM with retry logic.

        Args:
            system_prompt: System prompt
            user_prompt: User prompt

        Returns:
            Raw LLM response text
        """
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )
                return response.content[0].text
            except Exception as e:
                last_error = e
                self.logger.warning(f"LLM call attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries:
                    import time
                    time.sleep(1 * (attempt + 1))  # Exponential backoff

        raise last_error

    def _parse_response(self, response_text: str, model_class: type[T]) -> T:
        """
        Parse LLM response into Pydantic model.

        Handles JSON extraction from markdown code blocks.

        Args:
            response_text: Raw LLM response
            model_class: Pydantic model to parse into

        Returns:
            Parsed model instance
        """
        # Extract JSON from markdown code blocks if present
        text = response_text.strip()
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            text = text[start:end].strip()

        try:
            data = json.loads(text)
            return model_class(**data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}\nResponse: {text[:500]}")
        except ValidationError as e:
            raise ValueError(f"Response validation failed: {e}\nData: {data}")

    def evaluate(self, **kwargs) -> EvaluationResult:
        """
        Run the LLM-as-a-Judge evaluation.

        Args:
            **kwargs: Data to evaluate (passed to get_user_prompt)

        Returns:
            EvaluationResult with judgment
        """
        try:
            # Build prompts
            system_prompt = self.get_system_prompt()
            user_prompt = self.get_user_prompt(**kwargs)

            # Call LLM
            self.logger.info(f"Calling LLM for {self.name} evaluation...")
            response_text = self._call_llm(system_prompt, user_prompt)

            # Parse response
            model_class = self.get_response_model()
            judgment = self._parse_response(response_text, model_class)

            # Convert to EvaluationResult
            result = self.interpret_judgment(judgment)
            self.logger.info(f"{self.name} evaluation complete: {'PASSED' if result.passed else 'FAILED'}")

            return result

        except Exception as e:
            self.logger.error(f"{self.name} evaluation failed: {e}")
            return EvaluationResult.error(self.name, str(e))

    def _normalize_score(self, score_1_to_5: int) -> float:
        """Convert 1-5 score to 0.0-1.0 scale."""
        return (score_1_to_5 - 1) / 4.0

    def _format_strategy_summary(self, strategy: Dict[str, Any]) -> str:
        """Format strategy for prompt inclusion."""
        return f"""
Strategy Name: {strategy.get('name', 'Unknown')}
Asset: {strategy.get('asset', 'Unknown')}
Entry Conditions: {json.dumps(strategy.get('entry_conditions', {}), indent=2)}
Exit Conditions: {json.dumps(strategy.get('exit_conditions', {}), indent=2)}
Risk Management: {json.dumps(strategy.get('risk_management', {}), indent=2)}
"""

    def _format_trades_summary(self, trades: List[Dict[str, Any]], limit: int = 20) -> str:
        """Format trades list for prompt inclusion."""
        if not trades:
            return "No trades executed."

        lines = [f"Total trades: {len(trades)}"]
        for i, trade in enumerate(trades[:limit]):
            lines.append(
                f"  {i+1}. {trade.get('type', 'unknown').upper()} {trade.get('shares', 0)} shares "
                f"@ ${trade.get('price', 0):.2f} on {trade.get('date', 'unknown')} "
                f"(reason: {trade.get('reason', 'unknown')})"
            )

        if len(trades) > limit:
            lines.append(f"  ... and {len(trades) - limit} more trades")

        return "\n".join(lines)
