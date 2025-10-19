"""
Code Generator Agent - Generates and refines trading strategy code
"""
import logging
from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from tools.code_generator import parse_strategy, generate_trading_bot_code

logger = logging.getLogger(__name__)


class CodeGeneratorAgent(BaseAgent):
    """
    Generates trading strategy code and refines it based on feedback

    Responsibilities:
    - Parse user's strategy description
    - Generate initial strategy configuration
    - Refine strategy based on analyst feedback
    - Adjust parameters (timeframe, thresholds, conditions)
    """

    def __init__(self):
        super().__init__("CodeGenerator")

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate or refine strategy code

        Args:
            input_data: {
                'user_query': str,
                'feedback': dict (optional - from analyst),
                'previous_strategy': dict (optional),
                'iteration': int,
                'data_insights': dict (optional - data-driven recommendations)
            }

        Returns:
            {
                'success': bool,
                'strategy': dict,
                'code': str,
                'changes_made': list[str]
            }
        """
        user_query = input_data.get('user_query', '')
        feedback = input_data.get('feedback')
        previous_strategy = input_data.get('previous_strategy')
        iteration = input_data.get('iteration', 1)
        data_insights = input_data.get('data_insights')

        changes_made = []

        # If this is a refinement (not first iteration)
        if feedback and previous_strategy:
            logger.info(f"Refining strategy based on feedback (iteration {iteration})")

            # Apply data insights if available (data-driven refinement)
            if data_insights and data_insights.get('recommendations'):
                logger.info(f"🧠 Applying data-driven insights to strategy...")
                strategy = self._apply_data_insights(previous_strategy, data_insights, changes_made)
            else:
                strategy = await self._refine_strategy(user_query, previous_strategy, feedback, changes_made)
        else:
            logger.info(f"Generating initial strategy (iteration {iteration})")
            # Generate initial strategy
            result = parse_strategy(user_query)
            if not result.get('success'):
                return {
                    'success': False,
                    'error': result.get('error', 'Failed to parse strategy')
                }
            strategy = result.get('strategy', {})

        # Generate code
        code_result = generate_trading_bot_code(strategy)
        if not code_result.get('success'):
            return {
                'success': False,
                'error': code_result.get('error', 'Failed to generate code')
            }

        code = code_result.get('code', '')

        # Add to memory
        self.add_to_memory({
            'type': 'code_generation',
            'iteration': iteration,
            'strategy': strategy,
            'changes_made': changes_made
        })

        return {
            'success': True,
            'strategy': strategy,
            'code': code,
            'changes_made': changes_made
        }

    def _extract_user_specified_params(self, user_query: str) -> Dict[str, Any]:
        """
        Extract parameters that the user explicitly specified
        These should NEVER be modified during refinement
        """
        import re

        user_specified = {
            'rsi_threshold': None,
            'rsi_exit_threshold': None,
            'take_profit': None,
            'stop_loss': None,
        }

        query_lower = user_query.lower()

        # Check for explicit RSI thresholds
        rsi_patterns = [
            r'rsi\s+(?:drops?|falls?|goes?|is)?\s*(?:below|under|<)\s*(\d+)',
            r'rsi\s*<\s*(\d+)',
        ]
        for pattern in rsi_patterns:
            match = re.search(pattern, query_lower)
            if match:
                user_specified['rsi_threshold'] = int(match.group(1))
                logger.info(f"🔒 User specified RSI entry threshold: {user_specified['rsi_threshold']}")
                break

        # Check for explicit RSI exit
        rsi_exit_patterns = [
            r'rsi\s+(?:goes?|rises?|exceeds?)?\s*(?:above|over|>)\s*(\d+)',
            r'rsi\s*>\s*(\d+)'
        ]
        for pattern in rsi_exit_patterns:
            match = re.search(pattern, query_lower)
            if match:
                user_specified['rsi_exit_threshold'] = int(match.group(1))
                logger.info(f"🔒 User specified RSI exit threshold: {user_specified['rsi_exit_threshold']}")
                break

        # Check for explicit take profit
        tp_patterns = [
            r'[+]?(\d+(?:\.\d+)?)%\s+(?:profit|take\s*profit|tp)',
            r'(?:take\s*profit|tp)\s+(?:at\s+)?[+]?(\d+(?:\.\d+)?)%',
        ]
        for pattern in tp_patterns:
            match = re.search(pattern, query_lower)
            if match:
                user_specified['take_profit'] = float(match.group(1)) / 100.0
                logger.info(f"🔒 User specified take profit: {user_specified['take_profit']*100}%")
                break

        # Check for explicit stop loss
        sl_patterns = [
            r'[-]?(\d+(?:\.\d+)?)%\s+(?:stop\s*loss|sl)',
            r'(?:stop\s*loss|sl)\s+(?:at\s+)?[-]?(\d+(?:\.\d+)?)%',
        ]
        for pattern in sl_patterns:
            match = re.search(pattern, query_lower)
            if match:
                user_specified['stop_loss'] = float(match.group(1)) / 100.0
                logger.info(f"🔒 User specified stop loss: {user_specified['stop_loss']*100}%")
                break

        return user_specified

    async def _refine_strategy(
        self,
        user_query: str,
        previous_strategy: Dict[str, Any],
        feedback: Dict[str, Any],
        changes_made: list
    ) -> Dict[str, Any]:
        """
        Refine strategy based on analyst feedback
        CRITICAL: Never modify user-specified parameters
        """
        import copy
        strategy = copy.deepcopy(previous_strategy)

        issues = feedback.get('issues', [])
        suggestions = feedback.get('suggestions', [])
        metrics = feedback.get('metrics', {})

        # Extract what the user explicitly specified - these are PROTECTED
        user_specified = self._extract_user_specified_params(user_query)
        protected_params = [k for k, v in user_specified.items() if v is not None]

        logger.info(f"Refining strategy - Issues: {len(issues)}, Suggestions: {len(suggestions)}")
        if protected_params:
            logger.info(f"🔒 Protected user-specified parameters: {protected_params}")

        # Check for trade execution issues
        total_trades = metrics.get('total_trades', 0)

        # Issue: Not enough trades (strategy not triggering)
        if total_trades < 3:
            # Always recommend timeframe increase first
            for suggestion in suggestions:
                if 'timeframe' in suggestion.lower() or '360' in suggestion or '720' in suggestion:
                    changes_made.append("Recommended: Increase backtest timeframe to 360+ days")
                    break

            # NEVER modify user-specified RSI thresholds
            entry_conditions = strategy.get('entry_conditions', {})
            if entry_conditions.get('signal') == 'rsi':
                params = entry_conditions.get('parameters', {})
                threshold = params.get('threshold', 30)
                comparison = params.get('comparison', 'below')

                # Only adjust if user didn't specify this threshold
                if user_specified['rsi_threshold'] is None:
                    if comparison == 'below' and threshold < 35:
                        params['threshold'] = min(threshold + 5, 40)
                        changes_made.append(f"Relaxed RSI entry threshold from {threshold} to {params['threshold']}")
                    elif comparison == 'above' and threshold > 65:
                        params['threshold'] = max(threshold - 5, 60)
                        changes_made.append(f"Relaxed RSI entry threshold from {threshold} to {params['threshold']}")
                else:
                    changes_made.append(f"⚠️ Cannot relax RSI threshold - user specified RSI < {user_specified['rsi_threshold']}")
                    changes_made.append(f"→ Recommendation: Extend backtest timeframe to 360-720 days to find more signals")

        # Issue: Poor performance
        total_return = metrics.get('total_return', 0)
        win_rate = metrics.get('win_rate', 0)

        if total_trades >= 3:  # Only adjust if we have enough data
            # Adjust stop loss if too many losing trades (only if NOT user-specified)
            if win_rate < 40 and user_specified['stop_loss'] is None:
                exit_conditions = strategy.get('exit_conditions', {})
                current_stop_loss = exit_conditions.get('stop_loss', 0.01)
                # Tighten stop loss slightly
                new_stop_loss = max(current_stop_loss * 0.8, 0.005)
                if new_stop_loss != current_stop_loss:
                    exit_conditions['stop_loss'] = new_stop_loss
                    changes_made.append(f"Tightened stop loss from {current_stop_loss*100:.1f}% to {new_stop_loss*100:.1f}%")
            elif win_rate < 40:
                changes_made.append(f"⚠️ Low win rate ({win_rate:.1f}%) but cannot adjust stop loss (user specified {user_specified['stop_loss']*100}%)")

            # Adjust take profit if returns are too low (only if NOT user-specified)
            if total_return < 5 and win_rate > 50 and user_specified['take_profit'] is None:
                exit_conditions = strategy.get('exit_conditions', {})
                current_take_profit = exit_conditions.get('take_profit', 0.02)
                # Let profits run more
                new_take_profit = min(current_take_profit * 1.5, 0.10)
                if new_take_profit != current_take_profit:
                    exit_conditions['take_profit'] = new_take_profit
                    changes_made.append(f"Increased take profit from {current_take_profit*100:.1f}% to {new_take_profit*100:.1f}%")

        if not changes_made:
            changes_made.append("No automated changes made - all key parameters are user-specified or strategy is satisfactory")

        logger.info(f"Strategy refinement complete. Changes: {changes_made}")

        return strategy

    def _apply_data_insights(self, strategy: Dict[str, Any], data_insights: Dict[str, Any],
                              changes_made: List[str]) -> Dict[str, Any]:
        """
        Apply data-driven insights to refine the strategy
        This is the KEY to intelligent adaptation - uses actual data, not guesses
        """
        refined_strategy = strategy.copy()
        recommendations = data_insights.get('recommendations', [])

        for rec in recommendations:
            condition_type = rec['condition']
            new_value = rec['recommended_value']
            confidence = rec['confidence']

            # Only apply high-confidence recommendations
            if confidence < 0.5:
                continue

            # Apply to buy conditions
            for condition in refined_strategy.get('buy_conditions', []):
                if condition.get('type') == condition_type:
                    params = condition.get('params', {})
                    if 'threshold' in params:
                        old_value = params['threshold']
                        params['threshold'] = new_value
                        changes_made.append(
                            f"Adjusted {condition_type} buy threshold from {old_value} to {new_value:.3f} "
                            f"(based on data analysis, confidence: {confidence:.2f})"
                        )
                    elif 'value' in params:
                        old_value = params['value']
                        params['value'] = new_value
                        changes_made.append(
                            f"Adjusted {condition_type} buy value from {old_value} to {new_value:.3f} "
                            f"(based on data analysis, confidence: {confidence:.2f})"
                        )

            # Apply to sell conditions
            for condition in refined_strategy.get('sell_conditions', []):
                if condition.get('type') == condition_type:
                    params = condition.get('params', {})
                    if 'threshold' in params:
                        old_value = params['threshold']
                        # For sell conditions, might need opposite threshold
                        if condition_type == 'sentiment':
                            params['threshold'] = -new_value if new_value > 0 else new_value
                        else:
                            params['threshold'] = new_value
                        changes_made.append(
                            f"Adjusted {condition_type} sell threshold from {old_value} to {params['threshold']:.3f} "
                            f"(based on data analysis, confidence: {confidence:.2f})"
                        )

        if not changes_made:
            changes_made.append("No changes needed based on data analysis")

        return refined_strategy

    async def refine_existing_code(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Refine existing strategy code based on user's refinement instructions
        This modifies the existing code directly rather than regenerating from scratch

        Args:
            input_data: {
                'current_strategy': dict,
                'current_code': str,
                'refinement_instructions': str
            }

        Returns:
            {
                'success': bool,
                'strategy': dict,
                'code': str,
                'changes_made': list[str]
            }
        """
        current_strategy = input_data.get('current_strategy')
        current_code = input_data.get('current_code')
        refinement_instructions = input_data.get('refinement_instructions')

        logger.info(f"Refining existing code: {refinement_instructions[:100]}")

        try:
            # Use Claude to understand refinement instructions and apply them
            from anthropic import Anthropic
            import os
            import json

            client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

            # Build prompt for code refinement
            prompt = f"""You are a trading strategy code refinement expert. You need to modify existing trading strategy code based on user instructions.

CURRENT STRATEGY CONFIG:
{json.dumps(current_strategy, indent=2)}

USER'S REFINEMENT REQUEST:
{refinement_instructions}

CURRENT STRATEGY DESCRIPTION:
- Asset: {current_strategy.get('asset')}
- Strategy Type: {current_strategy.get('strategy_type')}
- Entry Conditions: {current_strategy.get('entry_conditions')}
- Exit Conditions: {current_strategy.get('exit_conditions')}

YOUR TASK:
1. Analyze what the user wants to change
2. Modify the strategy config JSON to implement those changes
3. List all changes made

IMPORTANT RULES:
- Only modify what the user requested
- Preserve all other parameters
- Make minimal changes to achieve the goal
- If the user says "loosen RSI threshold", increase the threshold value
- If the user says "lower sentiment requirement", decrease the threshold value
- If the user says "use OR instead of AND", that means conditions should be less restrictive

Respond in this exact JSON format:
{{
  "updated_strategy": {{ ... the modified strategy config ... }},
  "changes_made": ["change 1", "change 2", ...],
  "explanation": "Brief explanation of what was modified"
}}"""

            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            response_text = response.content[0].text

            # Parse JSON response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                raise Exception("Could not parse refinement response")

            result_data = json.loads(json_match.group(0))

            updated_strategy = result_data.get('updated_strategy')
            changes_made = result_data.get('changes_made', [])

            logger.info(f"✅ Refinement complete. Changes: {changes_made}")

            # Regenerate code from updated strategy
            code_result = generate_trading_bot_code(updated_strategy)
            if not code_result.get('success'):
                return {
                    'success': False,
                    'error': 'Failed to generate code from refined strategy'
                }

            return {
                'success': True,
                'strategy': updated_strategy,
                'code': code_result.get('code'),
                'changes_made': changes_made
            }

        except Exception as e:
            logger.error(f"Error refining code: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
