"""
Suggestion Analyzer Agent - Generates AI-powered actionable suggestions for strategy improvement
"""
import logging
from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from orchestrator import get_orchestrator
from tools.backtest_analyzer import BacktestAnalyzer

logger = logging.getLogger(__name__)


class SuggestionAnalyzerAgent(BaseAgent):
    """
    Analyzes backtest results and generates specific, actionable suggestions

    Responsibilities:
    - Analyze backtest performance metrics
    - Generate data-driven, specific recommendations
    - Provide one-click applicable suggestions
    - Track suggestion effectiveness
    """

    def __init__(self):
        super().__init__("SuggestionAnalyzer")
        self.orchestrator = get_orchestrator()
        self.backtest_analyzer = BacktestAnalyzer()

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI-powered suggestions based on backtest results

        Args:
            input_data: {
                'backtest_results': {...},
                'strategy': {...},
                'user_query': str (optional),
                'current_code': str (optional)
            }

        Returns:
            {
                'success': bool,
                'suggestions': [
                    {
                        'id': str,
                        'category': 'entry'|'exit'|'risk'|'timeframe'|'portfolio',
                        'title': str,
                        'description': str,
                        'rationale': str,
                        'impact': 'high'|'medium'|'low',
                        'changes': {
                            'parameter': str,
                            'current_value': any,
                            'suggested_value': any
                        },
                        'applicable': bool
                    }
                ],
                'summary': str,
                'metrics_analysis': {...}
            }
        """
        backtest_results = input_data.get('backtest_results', {})
        strategy = input_data.get('strategy', {})
        user_query = input_data.get('user_query', '')

        if not backtest_results or not backtest_results.get('summary'):
            return {
                'success': False,
                'error': 'No backtest results available to analyze'
            }

        summary = backtest_results.get('summary', {})
        trades = backtest_results.get('trades', [])
        additional_info = backtest_results.get('additional_info', [])

        # Analyze data distributions for data-driven suggestions
        data_analysis = self.backtest_analyzer.analyze_data_distribution(additional_info)

        # Generate AI-powered suggestions
        suggestions = await self._generate_suggestions(
            summary, trades, additional_info, strategy, data_analysis
        )

        # Create summary
        summary_text = self._create_summary(summary, suggestions)

        return {
            'success': True,
            'suggestions': suggestions,
            'summary': summary_text,
            'metrics_analysis': {
                'total_trades': summary.get('total_trades', 0),
                'win_rate': summary.get('win_rate', 0),
                'total_return': summary.get('total_return', 0),
                'sharpe_ratio': summary.get('sharpe_ratio', 0),
                'max_drawdown': summary.get('max_drawdown', 0),
                'profit_factor': summary.get('profit_factor', 0)
            },
            'data_distributions': data_analysis
        }

    async def _generate_suggestions(
        self,
        summary: Dict[str, Any],
        trades: List[Dict[str, Any]],
        additional_info: List[Dict[str, Any]],
        strategy: Dict[str, Any],
        data_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate specific, actionable suggestions"""
        suggestions = []

        # Extract key metrics
        total_trades = summary.get('total_trades', 0)
        win_rate = summary.get('win_rate', 0)
        total_return = summary.get('total_return', 0)
        buy_hold_return = summary.get('buy_hold_return', 0)
        sharpe_ratio = summary.get('sharpe_ratio', 0)
        max_drawdown = summary.get('max_drawdown', 0)
        profit_factor = summary.get('profit_factor', 0)
        avg_days_held = summary.get('avg_days_held', 0)

        # Get current strategy parameters
        entry_conditions = strategy.get('entry_conditions', {})
        exit_conditions = strategy.get('exit_conditions', {})
        entry_params = entry_conditions.get('parameters', {})

        # 1. LOW TRADE COUNT SUGGESTIONS
        if total_trades < 5:
            suggestions.extend(self._suggest_low_trade_fixes(
                total_trades, entry_params, data_analysis, strategy
            ))

        # 2. LOW WIN RATE SUGGESTIONS
        if 0 < win_rate < 40 and total_trades >= 3:
            suggestions.extend(self._suggest_win_rate_improvements(
                win_rate, entry_params, exit_conditions, trades
            ))

        # 3. UNDERPERFORMING VS BUY & HOLD
        if total_return < buy_hold_return and total_trades >= 3:
            suggestions.extend(self._suggest_performance_improvements(
                total_return, buy_hold_return, profit_factor, strategy
            ))

        # 4. RISK MANAGEMENT SUGGESTIONS
        if max_drawdown > 20 or sharpe_ratio < 1.0:
            suggestions.extend(self._suggest_risk_improvements(
                max_drawdown, sharpe_ratio, exit_conditions, avg_days_held
            ))

        # 5. PORTFOLIO OPTIMIZATION (if strong performance in specific sectors)
        if total_trades >= 5 and win_rate >= 50:
            suggestions.extend(self._suggest_portfolio_optimizations(
                trades, summary, strategy
            ))

        # 6. AI-POWERED CONTEXTUAL SUGGESTIONS
        ai_suggestions = await self._get_ai_suggestions(
            summary, trades, strategy, data_analysis
        )
        suggestions.extend(ai_suggestions)

        # Filter out already-applied suggestions (where current_value == suggested_value)
        filtered_suggestions = []
        for suggestion in suggestions:
            changes = suggestion.get('changes', {})
            current = changes.get('current_value')
            suggested = changes.get('suggested_value')

            # Skip if already applied (current value matches suggested value)
            if current == suggested:
                logger.info(f"⏭️  Skipping already-applied suggestion: {suggestion.get('title')}")
                continue

            filtered_suggestions.append(suggestion)

        # Add IDs and sort by impact
        for i, suggestion in enumerate(filtered_suggestions):
            suggestion['id'] = f"sug_{i+1}"

        # Sort: high impact first
        impact_order = {'high': 0, 'medium': 1, 'low': 2}
        filtered_suggestions.sort(key=lambda x: impact_order.get(x.get('impact', 'low'), 3))

        return filtered_suggestions[:8]  # Return top 8 suggestions

    def _suggest_low_trade_fixes(
        self,
        total_trades: int,
        entry_params: Dict[str, Any],
        data_analysis: Dict[str, Any],
        strategy: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate suggestions for low trade count"""
        suggestions = []

        # Analyze sentiment threshold if present
        sentiment_threshold = entry_params.get('sentiment_threshold') or entry_params.get('threshold')
        if sentiment_threshold and sentiment_threshold > 0.2:
            sentiment_stats = data_analysis.get('sentiment', {})
            typical_positive = sentiment_stats.get('p75', 0.15)

            suggestions.append({
                'category': 'entry',
                'title': f'Lower sentiment threshold from {sentiment_threshold} to {typical_positive:.2f}',
                'description': f'Only {total_trades} trades executed. Your sentiment threshold is too high.',
                'rationale': f'Data shows 75% of positive sentiment values are below {typical_positive:.2f}. Current threshold of {sentiment_threshold} is rarely reached.',
                'impact': 'high',
                'changes': {
                    'parameter': 'sentiment_threshold',
                    'current_value': sentiment_threshold,
                    'suggested_value': round(typical_positive, 2),
                    'parameter_path': 'entry_conditions.parameters.sentiment_threshold'
                },
                'applicable': True
            })

        # Analyze RSI threshold if present (check 'threshold' field when entry signal is RSI)
        entry_conditions = strategy.get('entry_conditions', {})
        if entry_conditions.get('type') == 'rsi' or entry_conditions.get('signal') == 'rsi':
            rsi_threshold = entry_params.get('threshold') or strategy.get('rsi_oversold', 30)

            if rsi_threshold <= 35:  # Only suggest if threshold is restrictive
                rsi_stats = data_analysis.get('rsi', {})
                typical_low = rsi_stats.get('p25', 35)

                # Only suggest if typical_low is actually higher
                if typical_low > rsi_threshold:
                    suggestions.append({
                        'category': 'entry',
                        'title': f'Increase RSI oversold threshold from {rsi_threshold} to {int(typical_low)}',
                        'description': f'Only {total_trades} trades triggered. RSI rarely drops below {rsi_threshold}.',
                        'rationale': f'Historical data shows RSI stays above 30 most of the time. Try {int(typical_low)} for more opportunities.',
                        'impact': 'high',
                        'changes': {
                            'parameter': 'rsi_oversold',
                            'current_value': rsi_threshold,
                            'suggested_value': int(typical_low),
                            'parameter_path': 'rsi_oversold'
                        },
                        'applicable': True
                    })

        # Suggest timeframe extension only if current timeframe is less than 360
        current_backtest_days = strategy.get('backtest_days', 180)
        if current_backtest_days < 360:
            suggestions.append({
                'category': 'timeframe',
                'title': f'Extend backtest period from {current_backtest_days} to 360 days',
                'description': f'Only {total_trades} trades in current {current_backtest_days}-day timeframe.',
                'rationale': 'Longer timeframes provide more data points and trading opportunities.',
                'impact': 'medium',
                'changes': {
                    'parameter': 'backtest_days',
                    'current_value': current_backtest_days,
                    'suggested_value': 360,
                    'parameter_path': 'backtest_days'
                },
                'applicable': True
            })

        return suggestions

    def _suggest_win_rate_improvements(
        self,
        win_rate: float,
        entry_params: Dict[str, Any],
        exit_conditions: Dict[str, Any],
        trades: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate suggestions for improving win rate"""
        suggestions = []

        current_stop_loss = exit_conditions.get('stop_loss', 2.0)
        current_take_profit = exit_conditions.get('take_profit', 5.0)

        # Analyze losing trades
        losing_trades = [t for t in trades if t.get('pnl', 0) < 0]
        if losing_trades:
            avg_loss_pct = abs(sum(t.get('pnl_pct', 0) for t in losing_trades) / len(losing_trades))

            if avg_loss_pct > current_stop_loss * 0.8:
                suggested_stop = round(current_stop_loss * 0.75, 1)
                suggestions.append({
                    'category': 'risk',
                    'title': f'Tighten stop loss from {current_stop_loss}% to {suggested_stop}%',
                    'description': f'Win rate is {win_rate:.1f}%. Average loss is {avg_loss_pct:.1f}%.',
                    'rationale': f'Tighter stop loss cuts losses earlier and improves win rate.',
                    'impact': 'high',
                    'changes': {
                        'parameter': 'stop_loss',
                        'current_value': current_stop_loss,
                        'suggested_value': suggested_stop,
                        'parameter_path': 'stop_loss'
                    },
                    'applicable': True
                })

        return suggestions

    def _suggest_performance_improvements(
        self,
        total_return: float,
        buy_hold_return: float,
        profit_factor: float,
        strategy: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate suggestions for underperformance vs buy & hold"""
        suggestions = []

        underperformance = buy_hold_return - total_return

        if profit_factor < 1.5:
            suggestions.append({
                'category': 'portfolio',
                'title': f'Strategy underperforms buy & hold by {underperformance:.1f}%',
                'description': f'Consider passive strategy or different approach.',
                'rationale': f'Profit factor of {profit_factor:.2f} suggests trading costs outweigh gains.',
                'impact': 'high',
                'changes': {
                    'parameter': 'strategy_type',
                    'current_value': 'active',
                    'suggested_value': 'Consider buy & hold or different indicators'
                },
                'applicable': False  # Requires manual review
            })

        return suggestions

    def _suggest_risk_improvements(
        self,
        max_drawdown: float,
        sharpe_ratio: float,
        exit_conditions: Dict[str, Any],
        avg_days_held: float
    ) -> List[Dict[str, Any]]:
        """Generate suggestions for risk management"""
        suggestions = []

        if max_drawdown > 20:
            current_stop = exit_conditions.get('stop_loss', 2.0)
            suggested_stop = round(current_stop * 0.7, 1)

            suggestions.append({
                'category': 'risk',
                'title': f'Reduce max drawdown from {max_drawdown:.1f}% with tighter stop loss',
                'description': f'Set stop loss to {suggested_stop}% (currently {current_stop}%)',
                'rationale': 'High drawdown increases risk. Tighter stops protect capital.',
                'impact': 'high',
                'changes': {
                    'parameter': 'stop_loss',
                    'current_value': current_stop,
                    'suggested_value': suggested_stop,
                    'parameter_path': 'stop_loss'
                },
                'applicable': True
            })

        if sharpe_ratio < 1.0 and avg_days_held > 10:
            suggestions.append({
                'category': 'exit',
                'title': 'Reduce holding period to improve risk-adjusted returns',
                'description': f'Average {avg_days_held:.0f} days held with Sharpe {sharpe_ratio:.2f}',
                'rationale': 'Shorter holds reduce exposure to volatility.',
                'impact': 'medium',
                'changes': {
                    'parameter': 'take_profit',
                    'current_value': exit_conditions.get('take_profit', 5.0),
                    'suggested_value': round(exit_conditions.get('take_profit', 5.0) * 0.7, 1),
                    'parameter_path': 'take_profit'
                },
                'applicable': True
            })

        return suggestions

    def _suggest_portfolio_optimizations(
        self,
        trades: List[Dict[str, Any]],
        summary: Dict[str, Any],
        strategy: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate portfolio optimization suggestions"""
        suggestions = []

        # Analyze if certain symbols performed better
        symbol = summary.get('symbol')
        if symbol and trades:
            winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
            win_rate = len(winning_trades) / len(trades) * 100 if trades else 0

            if win_rate >= 55:
                # Suggest expanding to similar stocks
                tech_stocks = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'META']
                if symbol in tech_stocks:
                    other_tech = [s for s in tech_stocks if s != symbol][:3]
                    suggestions.append({
                        'category': 'portfolio',
                        'title': f'Strong performance in {symbol}. Create tech portfolio',
                        'description': f'Win rate of {win_rate:.1f}% suggests this strategy works well for tech stocks.',
                        'rationale': f'Consider diversifying across {", ".join(other_tech)}',
                        'impact': 'medium',
                        'changes': {
                            'parameter': 'asset',
                            'current_value': symbol,
                            'suggested_value': [symbol] + other_tech
                        },
                        'applicable': True
                    })

        return suggestions

    async def _get_ai_suggestions(
        self,
        summary: Dict[str, Any],
        trades: List[Dict[str, Any]],
        strategy: Dict[str, Any],
        data_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get AI-powered contextual suggestions"""

        # Build context for AI
        prompt = f"""Analyze this trading strategy backtest and provide 2-3 specific, actionable suggestions.

PERFORMANCE METRICS:
- Total Trades: {summary.get('total_trades', 0)}
- Win Rate: {summary.get('win_rate', 0):.1f}%
- Total Return: {summary.get('total_return', 0):.1f}%
- Buy & Hold: {summary.get('buy_hold_return', 0):.1f}%
- Sharpe Ratio: {summary.get('sharpe_ratio', 0):.2f}
- Max Drawdown: {summary.get('max_drawdown', 0):.1f}%
- Profit Factor: {summary.get('profit_factor', 0):.2f}

STRATEGY CONFIGURATION:
{strategy}

DATA ANALYSIS:
{data_analysis}

Provide suggestions in this format:
SUGGESTION 1:
TITLE: [Specific action]
DESCRIPTION: [One sentence]
RATIONALE: [Why this helps]
IMPACT: [high/medium/low]

Focus on:
- Specific parameter changes with exact numbers
- Data-driven recommendations
- Actionable improvements users can apply immediately"""

        try:
            result = await self.orchestrator.chat(prompt)
            if result.get('success'):
                return self._parse_ai_suggestions(result.get('response', ''))
        except Exception as e:
            logger.error(f"Error getting AI suggestions: {e}")

        return []

    def _parse_ai_suggestions(self, response: str) -> List[Dict[str, Any]]:
        """Parse AI response into structured suggestions"""
        suggestions = []
        current_suggestion = {}

        lines = response.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                if current_suggestion:
                    suggestions.append(current_suggestion)
                    current_suggestion = {}
                continue

            if line.startswith('TITLE:'):
                current_suggestion['title'] = line.replace('TITLE:', '').strip()
                current_suggestion['category'] = 'ai_insight'
                current_suggestion['applicable'] = False
            elif line.startswith('DESCRIPTION:'):
                current_suggestion['description'] = line.replace('DESCRIPTION:', '').strip()
            elif line.startswith('RATIONALE:'):
                current_suggestion['rationale'] = line.replace('RATIONALE:', '').strip()
            elif line.startswith('IMPACT:'):
                impact = line.replace('IMPACT:', '').strip().lower()
                current_suggestion['impact'] = impact if impact in ['high', 'medium', 'low'] else 'medium'

        if current_suggestion:
            suggestions.append(current_suggestion)

        return suggestions

    def _create_summary(self, summary: Dict[str, Any], suggestions: List[Dict[str, Any]]) -> str:
        """Create a summary of the analysis"""
        total_trades = summary.get('total_trades', 0)
        win_rate = summary.get('win_rate', 0)
        total_return = summary.get('total_return', 0)

        high_impact = len([s for s in suggestions if s.get('impact') == 'high'])

        if total_trades == 0:
            return f"Strategy generated 0 trades. {high_impact} high-impact suggestions to fix entry conditions."
        elif total_return < 0:
            return f"Strategy lost {abs(total_return):.1f}%. {high_impact} suggestions to improve performance."
        elif win_rate < 40:
            return f"Low win rate of {win_rate:.1f}%. {high_impact} suggestions to tighten risk management."
        else:
            return f"Strategy performing well with {total_return:.1f}% return. {len(suggestions)} optimization suggestions available."
