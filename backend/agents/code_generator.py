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

    def _synchronize_strategy_parameters(self, strategy: dict, changes_made: list) -> None:
        """
        Synchronize top-level strategy parameters with nested entry/exit conditions.

        UNIVERSAL SYNC: The backtester reads from nested paths like entry_conditions.parameters.threshold.
        This function ensures ANY parameter changes propagate to where the backtester actually reads them.

        Handles ALL parameter types:
        - RSI thresholds (rsi_oversold → entry_conditions.parameters.threshold)
        - Sentiment thresholds (sentiment_threshold → entry_conditions.parameters.sentiment_threshold)
        - Stop loss/Take profit (top-level ↔ exit_conditions)
        - Any other dual-location parameters

        Args:
            strategy: Strategy dict to synchronize (modified in place)
            changes_made: List to append sync messages to
        """
        entry = strategy.get('entry_conditions', {})
        exit_cond = strategy.get('exit_conditions', {})
        entry_params = entry.setdefault('parameters', {})

        # UNIVERSAL SYNC: RSI oversold → entry threshold
        if strategy.get('rsi_oversold') is not None:
            if entry.get('type') == 'rsi' or entry.get('signal') == 'rsi':
                old_threshold = entry_params.get('threshold')
                new_threshold = strategy['rsi_oversold']

                if old_threshold != new_threshold:
                    entry_params['threshold'] = new_threshold
                    logger.info(f"  🔄 Synced entry_conditions.parameters.threshold: {old_threshold} → {new_threshold}")
                    changes_made.append(f"Synced RSI entry threshold to {new_threshold}")

        # UNIVERSAL SYNC: RSI overbought → exit threshold
        if strategy.get('rsi_overbought') is not None:
            # Pattern 1: exit_conditions has type/signal = 'rsi'
            if exit_cond.get('type') == 'rsi' or exit_cond.get('signal') == 'rsi':
                exit_params = exit_cond.setdefault('parameters', {})
                old_threshold = exit_params.get('threshold')
                new_threshold = strategy['rsi_overbought']

                if old_threshold != new_threshold:
                    exit_params['threshold'] = new_threshold
                    logger.info(f"  🔄 Synced exit_conditions.parameters.threshold: {old_threshold} → {new_threshold}")
                    changes_made.append(f"Synced RSI exit threshold to {new_threshold}")

            # Pattern 2: custom_exit_conditions array
            custom_exits = strategy.get('custom_exit_conditions', [])
            for exit_condition in custom_exits:
                if exit_condition.get('type') == 'rsi':
                    exit_params = exit_condition.setdefault('parameters', {})
                    old_threshold = exit_params.get('threshold')
                    new_threshold = strategy['rsi_overbought']

                    if old_threshold != new_threshold:
                        exit_params['threshold'] = new_threshold
                        logger.info(f"  🔄 Synced custom_exit_conditions RSI threshold: {old_threshold} → {new_threshold}")
                        changes_made.append(f"Synced RSI exit threshold to {new_threshold}")

        # UNIVERSAL SYNC: Sentiment threshold
        if strategy.get('sentiment_threshold') is not None:
            old_val = entry_params.get('sentiment_threshold')
            new_val = strategy['sentiment_threshold']
            if old_val != new_val:
                entry_params['sentiment_threshold'] = new_val
                logger.info(f"  🔄 Synced entry_conditions.parameters.sentiment_threshold: {old_val} → {new_val}")

        # UNIVERSAL SYNC: Take profit and stop loss (bidirectional)
        if exit_cond.get('take_profit') is not None and strategy.get('take_profit') is None:
            strategy['take_profit'] = exit_cond['take_profit']
        elif strategy.get('take_profit') is not None and exit_cond.get('take_profit') != strategy['take_profit']:
            old_tp = exit_cond.get('take_profit')
            exit_cond['take_profit'] = strategy['take_profit']
            logger.info(f"  🔄 Synced exit_conditions.take_profit: {old_tp} → {strategy['take_profit']}")

        if exit_cond.get('stop_loss') is not None and strategy.get('stop_loss') is None:
            strategy['stop_loss'] = exit_cond['stop_loss']
        elif strategy.get('stop_loss') is not None and exit_cond.get('stop_loss') != strategy['stop_loss']:
            old_sl = exit_cond.get('stop_loss')
            exit_cond['stop_loss'] = strategy['stop_loss']
            logger.info(f"  🔄 Synced exit_conditions.stop_loss: {old_sl} → {strategy['stop_loss']}")

    async def refine_existing_code(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Refine existing strategy code based on user's refinement instructions

        NEW APPROACH: Ask Claude for a small JSON diff instead of full strategy.
        This prevents JSON truncation/parsing errors and is much more reliable.

        Args:
            input_data: {
                'current_strategy': dict,
                'current_code': str,
                'refinement_instructions': str,
                'iteration': int (optional),
                'use_intelligent_analysis': bool (optional)
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
        iteration = input_data.get('iteration', 1)

        logger.info(f"🔧 Refining strategy (iteration {iteration}): {refinement_instructions[:100]}")

        try:
            from anthropic import Anthropic
            import os
            import json
            import re
            import copy

            client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

            # Extract key strategy parameters for the prompt (summary only, not full JSON)
            asset = current_strategy.get('asset', 'Unknown')
            strategy_type = current_strategy.get('strategy_type', 'Unknown')

            # Build parameter summary
            param_summary = []
            if current_strategy.get('rsi_period'):
                param_summary.append(f"RSI Period: {current_strategy['rsi_period']}")
            if current_strategy.get('rsi_oversold'):
                param_summary.append(f"RSI Oversold: {current_strategy['rsi_oversold']}")
            if current_strategy.get('rsi_overbought'):
                param_summary.append(f"RSI Overbought: {current_strategy['rsi_overbought']}")

            entry = current_strategy.get('entry_conditions', {})
            if entry.get('signal'):
                params = entry.get('parameters', {})
                param_summary.append(f"Entry Signal: {entry['signal']}, Threshold: {params.get('threshold')}")

            exit_cond = current_strategy.get('exit_conditions', {})
            if exit_cond.get('stop_loss'):
                param_summary.append(f"Stop Loss: {exit_cond['stop_loss']*100:.1f}%")
            if exit_cond.get('take_profit'):
                param_summary.append(f"Take Profit: {exit_cond['take_profit']*100:.1f}%")

            # Compact system prompt for diff-based changes
            system_prompt = """You are a trading strategy refinement agent. Respond with ONLY valid JSON, no markdown, no backticks, no prose.

OUTPUT SCHEMA:
{
  "parameter_changes": [
    {
      "path": "rsi_oversold",
      "new_value": 40,
      "reason": "Loosen oversold threshold as requested"
    }
  ],
  "backtest_days": 360,
  "notes": "Brief explanation of changes"
}

RULES:
1. "path" uses dot notation for nested fields or simple field name for top-level
2. "new_value" must be correctly typed (int, float, bool, string)
3. "parameter_changes" can be empty array if no parameter changes needed
4. "backtest_days" is optional - only include if user mentions backtest period/timeframe
5. Output ONLY valid JSON - no text before or after, no code fences

COMMON PARAMETERS (use top-level paths, sync handles nested):
- RSI: "rsi_oversold" (20-40), "rsi_overbought" (60-80), "rsi_period" (int)
- Sentiment: "sentiment_threshold" (decimals like 0.1, 0.2)
- Risk: "exit_conditions.stop_loss" (decimals: 0.01 = 1%), "exit_conditions.take_profit" (decimals)
- Asset: "asset" (string ticker like "AAPL")
- Backtest: "backtest_days" (integer)

CRITICAL: For RSI/sentiment thresholds, ONLY change top-level fields (rsi_oversold, sentiment_threshold).
Do NOT include nested paths like entry_conditions.parameters.* - synchronization handles that automatically."""

            user_prompt = f"""CURRENT STRATEGY SUMMARY:
Asset: {asset}
Type: {strategy_type}
Parameters:
{chr(10).join(f"  - {p}" for p in param_summary)}

USER REQUEST:
{refinement_instructions}

Identify which parameters to change and output ONLY the JSON diff."""

            logger.info(f"🤖 Calling Claude for parameter diff...")
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,  # Much smaller - we only need a diff
                temperature=0.1,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }]
            )

            response_text = response.content[0].text.strip()
            logger.info(f"📝 Claude response ({len(response_text)} chars): {response_text[:200]}...")

            # Simple JSON extraction - strip code fences if present
            if response_text.startswith("```"):
                response_text = re.sub(r"^```[a-zA-Z0-9]*\s*", "", response_text)
                response_text = re.sub(r"```$", "", response_text).strip()

            # Parse JSON
            try:
                diff_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"❌ Invalid JSON from Claude: {e}")
                logger.error(f"Raw response: {response_text}")
                return {
                    'success': False,
                    'error': f'LLM returned invalid JSON: {e}',
                    'raw_response': response_text[:500]
                }

            # Extract diff components
            parameter_changes = diff_data.get('parameter_changes', [])
            backtest_days = diff_data.get('backtest_days')
            notes = diff_data.get('notes', '')

            logger.info(f"✅ Parsed diff: {len(parameter_changes)} parameter changes")

            # Apply diff to strategy
            updated_strategy = copy.deepcopy(current_strategy)
            changes_made = []

            def apply_path(obj: dict, path: str, value: Any):
                """Apply a value to a nested dict using dot-notation path"""
                parts = path.split('.')
                current = obj
                for key in parts[:-1]:
                    if key not in current or not isinstance(current.get(key), dict):
                        current[key] = {}
                    current = current[key]
                current[parts[-1]] = value

            # Apply each parameter change
            for change in parameter_changes:
                path = change.get('path')
                new_value = change.get('new_value')
                reason = change.get('reason', '')

                if path and new_value is not None:
                    # Get old value for logging
                    try:
                        parts = path.split('.')
                        old_val = current_strategy
                        for part in parts:
                            old_val = old_val.get(part)
                    except:
                        old_val = None

                    # Apply the change
                    apply_path(updated_strategy, path, new_value)

                    # Log the change
                    change_desc = f"Set {path}: {old_val} → {new_value}"
                    if reason:
                        change_desc += f" ({reason})"
                    changes_made.append(change_desc)
                    logger.info(f"  ✓ {change_desc}")

            # Apply backtest_days if specified
            if backtest_days:
                updated_strategy['backtest_days'] = backtest_days
                changes_made.append(f"Set backtest period: {backtest_days} days")
                logger.info(f"  ✓ Set backtest_days: {backtest_days}")

            if not changes_made:
                changes_made = ["No parameter changes identified"]
                logger.info("  ℹ️ No changes made")

            # CRITICAL: Synchronize top-level RSI fields with entry/exit conditions
            # The backtester reads from entry_conditions.parameters.threshold, not top-level rsi_oversold
            logger.info("🔄 Synchronizing strategy parameters...")
            self._synchronize_strategy_parameters(updated_strategy, changes_made)

            # Regenerate code from updated strategy
            logger.info("🔨 Regenerating code from updated strategy...")
            code_result = generate_trading_bot_code(updated_strategy)
            if not code_result.get('success'):
                return {
                    'success': False,
                    'error': code_result.get('error', 'Failed to generate code from updated strategy')
                }

            logger.info(f"✅ Refinement complete: {len(changes_made)} changes applied")

            return {
                'success': True,
                'strategy': updated_strategy,
                'code': code_result.get('code'),
                'changes_made': changes_made,
                'explanation': notes
            }

        except Exception as e:
            logger.error(f"❌ Error refining code: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
