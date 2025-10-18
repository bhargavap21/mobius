"""
Intelligent Orchestrator - Learns from data and adapts strategies automatically
"""
import logging
from typing import Dict, Any, List, Optional
import numpy as np

logger = logging.getLogger(__name__)


class DataInsight:
    """Represents an insight derived from analyzing actual data"""

    def __init__(self, metric: str, actual_range: tuple, recommended_threshold: float,
                 confidence: float, reasoning: str):
        self.metric = metric
        self.actual_range = actual_range  # (min, max)
        self.recommended_threshold = recommended_threshold
        self.confidence = confidence  # 0-1
        self.reasoning = reasoning


class IntelligentOrchestrator:
    """
    Orchestrates agents with intelligent learning from data

    Key features:
    1. Analyzes actual data distributions from backtests
    2. Learns optimal thresholds based on real data
    3. Passes concrete recommendations between agents
    4. Adapts to ANY strategy type without hardcoding
    """

    def __init__(self):
        self.insights_cache = {}  # Cache insights for reuse
        self.learning_history = []  # Track what we've learned

    def analyze_backtest_data(self, backtest_results: Dict[str, Any],
                               strategy: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze backtest results to understand WHY a strategy succeeded or failed

        Returns:
            Detailed analysis with actionable insights
        """
        insights = []
        # Use additional_info which contains indicator/sentiment data collected during backtest
        data_points = backtest_results.get('additional_info', [])
        summary = backtest_results.get('summary', {})

        # Extract all conditions from strategy (handle both formats)
        buy_conditions = strategy.get('buy_conditions', strategy.get('entry_conditions', []))
        sell_conditions = strategy.get('sell_conditions', strategy.get('exit_conditions', []))

        # Convert dict format to list format if needed
        if isinstance(buy_conditions, dict):
            buy_conditions = [{
                'type': buy_conditions.get('signal', buy_conditions.get('type', '')),
                'params': buy_conditions.get('parameters', buy_conditions.get('params', {}))
            }]
        if isinstance(sell_conditions, dict):
            sell_conditions = [{
                'type': sell_conditions.get('signal', sell_conditions.get('type', '')),
                'params': sell_conditions.get('parameters', sell_conditions.get('params', {}))
            }]

        all_conditions = buy_conditions + sell_conditions

        # Analyze each condition type
        for condition in all_conditions:
            condition_type = condition.get('type')
            params = condition.get('params', {})

            # Get actual data for this condition
            actual_values = self._extract_condition_values(data_points, condition_type, params)

            if actual_values:
                insight = self._generate_insight(
                    condition_type=condition_type,
                    params=params,
                    actual_values=actual_values,
                    total_trades=summary.get('total_trades', 0)
                )
                insights.append(insight)

        # Generate overall analysis
        analysis = {
            'success': True,
            'total_trades': summary.get('total_trades', 0),
            'insights': insights,
            'primary_issue': self._identify_primary_issue(insights, summary),
            'recommendations': self._generate_recommendations(insights, strategy)
        }

        # Cache insights for future use
        strategy_key = self._get_strategy_key(strategy)
        self.insights_cache[strategy_key] = analysis
        self.learning_history.append(analysis)

        return analysis

    def _extract_condition_values(self, data_points: List[Dict],
                                   condition_type: str, params: Dict) -> List[float]:
        """Extract actual values for a specific condition from data points"""
        values = []

        for point in data_points:
            value = None

            if condition_type == 'sentiment':
                source = params.get('source', 'general')
                value = point.get(f'{source}_sentiment', point.get('sentiment'))
            elif condition_type == 'rsi':
                value = point.get('rsi')
            elif condition_type == 'volume_spike':
                value = point.get('volume_ratio', point.get('volume'))
            elif condition_type == 'price_change':
                value = point.get('price_change_pct', point.get('price_change'))
            elif condition_type == 'moving_average':
                ma_type = params.get('period', 20)
                value = point.get(f'ma_{ma_type}', point.get('moving_average'))
            elif condition_type == 'news_volume':
                value = point.get('news_count', point.get('news_volume'))
            elif condition_type == 'volatility':
                value = point.get('volatility', point.get('atr'))
            # Add more condition types as needed

            if value is not None:
                values.append(float(value))

        return values

    def _generate_insight(self, condition_type: str, params: Dict,
                          actual_values: List[float], total_trades: int) -> DataInsight:
        """Generate an insight based on actual data distribution"""
        if not actual_values:
            return None

        # Calculate statistics
        min_val = np.min(actual_values)
        max_val = np.max(actual_values)
        mean_val = np.mean(actual_values)
        std_val = np.std(actual_values)
        percentiles = np.percentile(actual_values, [10, 25, 50, 75, 90])

        # Determine optimal threshold based on data distribution
        current_threshold = params.get('threshold', params.get('value', 0))
        recommended_threshold = self._calculate_optimal_threshold(
            condition_type, actual_values, current_threshold, total_trades
        )

        # Calculate confidence based on data quality
        confidence = min(1.0, len(actual_values) / 100)  # More data = higher confidence

        # Generate reasoning
        reasoning = self._generate_reasoning(
            condition_type, min_val, max_val, mean_val,
            current_threshold, recommended_threshold, total_trades
        )

        return DataInsight(
            metric=condition_type,
            actual_range=(min_val, max_val),
            recommended_threshold=recommended_threshold,
            confidence=confidence,
            reasoning=reasoning
        )

    def _calculate_optimal_threshold(self, condition_type: str, values: List[float],
                                      current_threshold: float, total_trades: int) -> float:
        """
        Calculate optimal threshold based on actual data distribution
        This is the KEY to intelligent adaptation
        """
        if not values:
            return current_threshold

        # Sort values to understand distribution
        sorted_values = sorted(values)

        # If we have zero trades, current threshold is likely too restrictive
        if total_trades == 0:
            # Use percentiles to set more reasonable thresholds
            if condition_type in ['sentiment', 'price_change']:
                # For these, we want to catch the top/bottom movements
                if current_threshold > 0:
                    # Looking for positive signals - use 70th percentile
                    return sorted_values[int(len(sorted_values) * 0.7)]
                else:
                    # Looking for negative signals - use 30th percentile
                    return sorted_values[int(len(sorted_values) * 0.3)]

            elif condition_type == 'rsi':
                # RSI has known ranges
                if current_threshold < 50:  # Oversold
                    return min(35, sorted_values[int(len(sorted_values) * 0.3)])
                else:  # Overbought
                    return max(65, sorted_values[int(len(sorted_values) * 0.7)])

            elif condition_type == 'volume_spike':
                # Volume spikes - use 75th percentile for meaningful spikes
                return sorted_values[int(len(sorted_values) * 0.75)]

            else:
                # Generic approach - use percentiles
                return sorted_values[int(len(sorted_values) * 0.6)]

        # If we have some trades but want more
        elif total_trades < 10:
            # Slightly relax threshold
            adjustment = (sorted_values[int(len(sorted_values) * 0.5)] - current_threshold) * 0.3
            return current_threshold + adjustment

        # If we have too many trades (overtrading)
        elif total_trades > 100:
            # Tighten threshold
            if condition_type in ['sentiment', 'price_change']:
                if current_threshold > 0:
                    return sorted_values[int(len(sorted_values) * 0.85)]
                else:
                    return sorted_values[int(len(sorted_values) * 0.15)]
            else:
                adjustment = (sorted_values[int(len(sorted_values) * 0.75)] - current_threshold) * 0.3
                return current_threshold + adjustment

        # Trades are in reasonable range - minor adjustments only
        else:
            return current_threshold

    def _generate_reasoning(self, condition_type: str, min_val: float, max_val: float,
                            mean_val: float, current_threshold: float,
                            recommended_threshold: float, total_trades: int) -> str:
        """Generate human-readable reasoning for the recommendation"""

        if total_trades == 0:
            if condition_type == 'sentiment':
                return (f"Sentiment data ranges from {min_val:.3f} to {max_val:.3f} "
                        f"(mean: {mean_val:.3f}). Current threshold {current_threshold} "
                        f"is outside this range. Recommend {recommended_threshold:.3f} "
                        f"to capture actual market sentiment.")
            elif condition_type == 'rsi':
                return (f"RSI values range from {min_val:.1f} to {max_val:.1f}. "
                        f"Current threshold {current_threshold} may be too extreme. "
                        f"Recommend {recommended_threshold:.1f} for more signals.")
            else:
                return (f"Data ranges from {min_val:.3f} to {max_val:.3f}. "
                        f"Current threshold {current_threshold} generates no trades. "
                        f"Recommend {recommended_threshold:.3f} based on data distribution.")

        elif total_trades < 10:
            return (f"Only {total_trades} trades executed. Data shows range {min_val:.3f} "
                    f"to {max_val:.3f}. Adjusting threshold from {current_threshold} "
                    f"to {recommended_threshold:.3f} for more opportunities.")

        else:
            return (f"Strategy performing reasonably with {total_trades} trades. "
                    f"Minor adjustment from {current_threshold} to {recommended_threshold:.3f} "
                    f"may improve performance.")

    def _identify_primary_issue(self, insights: List[DataInsight],
                                summary: Dict[str, Any]) -> str:
        """Identify the primary issue preventing success"""

        total_trades = summary.get('total_trades', 0)

        if total_trades == 0:
            # Find the most restrictive condition
            most_restrictive = None
            max_difference = 0

            for insight in insights:
                if insight:
                    # Calculate how far off the threshold is
                    range_size = insight.actual_range[1] - insight.actual_range[0]
                    if range_size > 0:
                        difference = abs(insight.recommended_threshold -
                                       (insight.actual_range[0] + insight.actual_range[1]) / 2)
                        if difference > max_difference:
                            max_difference = difference
                            most_restrictive = insight

            if most_restrictive:
                return f"Zero trades: {most_restrictive.metric} threshold severely misaligned with data"
            else:
                return "Zero trades: Unable to determine specific cause"

        elif total_trades < 5:
            return f"Insufficient trades ({total_trades}): Conditions too restrictive"

        elif summary.get('win_rate', 0) < 40:
            return "Poor win rate: Entry/exit logic may need refinement"

        elif summary.get('total_return', 0) < 0:
            return "Negative returns: Risk management or timing issues"

        else:
            return "Strategy performing adequately"

    def _generate_recommendations(self, insights: List[DataInsight],
                                   strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific, actionable recommendations"""

        recommendations = []

        for insight in insights:
            if insight and abs(insight.recommended_threshold - insight.actual_range[0]) > 0.001:
                recommendations.append({
                    'condition': insight.metric,
                    'action': 'adjust_threshold',
                    'current_value': insight.actual_range,  # Show what we're seeing
                    'recommended_value': insight.recommended_threshold,
                    'confidence': insight.confidence,
                    'reasoning': insight.reasoning
                })

        # Sort by confidence
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)

        return recommendations[:5]  # Return top 5 recommendations

    def _get_strategy_key(self, strategy: Dict[str, Any]) -> str:
        """Generate a unique key for a strategy configuration"""
        conditions = []
        for cond in strategy.get('buy_conditions', []) + strategy.get('sell_conditions', []):
            conditions.append(f"{cond.get('type')}_{cond.get('params', {}).get('threshold', 0)}")
        return "_".join(conditions)

    def generate_refined_strategy(self, original_strategy: Dict[str, Any],
                                   recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a refined strategy based on recommendations
        This is what gets passed to the CodeGenerator
        """
        refined_strategy = original_strategy.copy()

        # Apply recommendations to buy conditions
        for condition in refined_strategy.get('buy_conditions', []):
            for rec in recommendations:
                if rec['condition'] == condition.get('type'):
                    # Apply the recommended threshold
                    if 'threshold' in condition.get('params', {}):
                        condition['params']['threshold'] = rec['recommended_value']
                    elif 'value' in condition.get('params', {}):
                        condition['params']['value'] = rec['recommended_value']

        # Apply recommendations to sell conditions
        for condition in refined_strategy.get('sell_conditions', []):
            for rec in recommendations:
                if rec['condition'] == condition.get('type'):
                    # Apply the recommended threshold
                    if 'threshold' in condition.get('params', {}):
                        condition['params']['threshold'] = rec['recommended_value']
                    elif 'value' in condition.get('params', {}):
                        condition['params']['value'] = rec['recommended_value']

        return refined_strategy