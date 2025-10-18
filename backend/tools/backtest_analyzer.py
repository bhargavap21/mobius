"""
Backtest Data Analyzer - Provides detailed analysis of why strategies succeed or fail
"""
import logging
from typing import Dict, Any, List, Optional
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

class BacktestAnalyzer:
    """
    Analyzes backtest results to determine why trades were/weren't executed
    Provides actionable insights for strategy improvement
    """

    def __init__(self):
        self.threshold_recommendations = {
            'sentiment': {'min': -0.3, 'max': 0.3, 'typical': 0.1, 'aggressive': 0.05},
            'rsi': {'oversold': 30, 'overbought': 70, 'typical_buy': 35, 'typical_sell': 65},
            'volume': {'typical_multiplier': 1.5, 'high_volume': 2.0},
            'price_change': {'typical_daily': 0.02, 'volatile': 0.05},
            'news_count': {'typical_threshold': 3, 'high_activity': 10}
        }

    def analyze_data_distribution(self, data_points: List[Dict]) -> Dict[str, Any]:
        """
        Analyze the distribution of data values to recommend thresholds

        Args:
            data_points: List of data points with their values

        Returns:
            Analysis with statistics and recommendations
        """
        if not data_points:
            return {
                'has_data': False,
                'reason': 'No data points provided'
            }

        # Extract different data types
        sentiment_values = []
        rsi_values = []
        volume_values = []
        price_changes = []
        news_counts = []

        for point in data_points:
            if 'sentiment' in point and point['sentiment'] is not None:
                sentiment_values.append(point['sentiment'])
            if 'rsi' in point and point['rsi'] is not None:
                rsi_values.append(point['rsi'])
            if 'volume' in point and point['volume'] is not None:
                volume_values.append(point['volume'])
            if 'price_change' in point and point['price_change'] is not None:
                price_changes.append(point['price_change'])
            if 'news_count' in point and point['news_count'] is not None:
                news_counts.append(point['news_count'])

        analysis = {'has_data': True, 'distributions': {}}

        # Analyze sentiment distribution
        if sentiment_values:
            analysis['distributions']['sentiment'] = self._analyze_values(
                sentiment_values,
                'sentiment',
                threshold_type='sentiment'
            )

        # Analyze RSI distribution
        if rsi_values:
            analysis['distributions']['rsi'] = self._analyze_values(
                rsi_values,
                'rsi',
                threshold_type='rsi'
            )

        # Analyze volume distribution
        if volume_values:
            analysis['distributions']['volume'] = self._analyze_values(
                volume_values,
                'volume',
                threshold_type='volume'
            )

        # Analyze price changes
        if price_changes:
            analysis['distributions']['price_change'] = self._analyze_values(
                price_changes,
                'price_change',
                threshold_type='price_change'
            )

        # Analyze news activity
        if news_counts:
            analysis['distributions']['news_count'] = self._analyze_values(
                news_counts,
                'news_count',
                threshold_type='news_count'
            )

        return analysis

    def _analyze_values(self, values: List[float], name: str, threshold_type: str) -> Dict[str, Any]:
        """Analyze a list of values and recommend thresholds"""
        if not values:
            return {'has_data': False}

        # Calculate statistics
        stats = {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'mean': np.mean(values),
            'median': np.median(values),
            'std': np.std(values),
            'percentiles': {
                '10th': np.percentile(values, 10),
                '25th': np.percentile(values, 25),
                '50th': np.percentile(values, 50),
                '75th': np.percentile(values, 75),
                '90th': np.percentile(values, 90)
            }
        }

        # Get threshold recommendations
        recommendations = self.threshold_recommendations.get(threshold_type, {})

        # Provide specific recommendations based on data
        if threshold_type == 'sentiment':
            # For sentiment, recommend based on actual data distribution
            if stats['max'] < 0.3:
                recommended_buy = stats['percentile']['75th']  # Use 75th percentile for bullish
                recommended_sell = stats['percentile']['25th']  # Use 25th percentile for bearish
            else:
                recommended_buy = max(0.05, stats['percentile']['60th'])
                recommended_sell = min(-0.05, stats['percentile']['40th'])

            stats['recommendations'] = {
                'bullish_threshold': round(recommended_buy, 3),
                'bearish_threshold': round(recommended_sell, 3),
                'reason': f"Based on data distribution (max: {stats['max']:.3f}, 75th percentile: {stats['percentiles']['75th']:.3f})"
            }

        elif threshold_type == 'rsi':
            # For RSI, check if values ever reach traditional thresholds
            oversold_count = sum(1 for v in values if v < 30)
            overbought_count = sum(1 for v in values if v > 70)

            if oversold_count == 0:
                # RSI never goes below 30, adjust threshold
                recommended_buy = stats['percentiles']['25th']
            else:
                recommended_buy = 30

            if overbought_count == 0:
                # RSI never goes above 70, adjust threshold
                recommended_sell = stats['percentiles']['75th']
            else:
                recommended_sell = 70

            stats['recommendations'] = {
                'oversold_threshold': round(recommended_buy, 1),
                'overbought_threshold': round(recommended_sell, 1),
                'oversold_occurrences': oversold_count,
                'overbought_occurrences': overbought_count,
                'reason': f"RSI range: {stats['min']:.1f}-{stats['max']:.1f}, adjust if never reaches extremes"
            }

        elif threshold_type == 'volume':
            # For volume, recommend based on typical multipliers
            avg_volume = stats['mean']
            stats['recommendations'] = {
                'high_volume_threshold': round(avg_volume * 1.5),
                'very_high_volume_threshold': round(avg_volume * 2.0),
                'reason': f"Average volume: {avg_volume:.0f}, use multipliers for signals"
            }

        elif threshold_type == 'price_change':
            # For price changes, use percentiles
            stats['recommendations'] = {
                'bullish_move': round(stats['percentiles']['75th'], 4),
                'bearish_move': round(stats['percentiles']['25th'], 4),
                'extreme_move': round(stats['percentiles']['90th'], 4),
                'reason': f"Daily price changes typically {stats['mean']*100:.2f}%"
            }

        elif threshold_type == 'news_count':
            # For news count, use distribution
            stats['recommendations'] = {
                'high_activity': round(stats['percentiles']['75th']),
                'very_high_activity': round(stats['percentiles']['90th']),
                'reason': f"Average news count: {stats['mean']:.1f} per day"
            }

        stats['has_data'] = True
        return stats

    def analyze_backtest_failure(self, backtest_result: Dict[str, Any],
                                 strategy: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze why a backtest failed to execute trades

        Args:
            backtest_result: The backtest results
            strategy: The strategy configuration

        Returns:
            Detailed analysis with recommendations
        """
        analysis = {
            'success': True,
            'total_trades': backtest_result.get('summary', {}).get('total_trades', 0),
            'data_found': backtest_result.get('summary', {}).get('external_data_found', 0),
            'data_checked': backtest_result.get('summary', {}).get('data_points_checked', 0),
            'issues': [],
            'recommendations': []
        }

        # Check if no trades were executed
        if analysis['total_trades'] == 0:
            analysis['issues'].append('No trades executed')

            # Analyze why based on strategy type
            entry_conditions = strategy.get('entry_conditions', {})
            signal_type = entry_conditions.get('signal', '')
            params = entry_conditions.get('parameters', {})

            if 'sentiment' in signal_type:
                threshold = params.get('threshold', 0.5)
                if threshold > 0.3:
                    analysis['issues'].append(f'Sentiment threshold {threshold} is too high')
                    analysis['recommendations'].append({
                        'type': 'adjust_threshold',
                        'parameter': 'sentiment_threshold',
                        'current': threshold,
                        'suggested': 0.1,
                        'reason': 'Real sentiment rarely exceeds 0.3'
                    })

            elif 'rsi' in signal_type:
                threshold = params.get('rsi_threshold', 30)
                analysis['recommendations'].append({
                    'type': 'check_rsi_range',
                    'parameter': 'rsi_threshold',
                    'current': threshold,
                    'suggested': 'Check if RSI reaches this level',
                    'reason': 'RSI might not reach extreme levels in this period'
                })

            elif 'volume' in signal_type:
                analysis['recommendations'].append({
                    'type': 'adjust_volume',
                    'parameter': 'volume_multiplier',
                    'reason': 'Volume threshold might be too high'
                })

            # Check data availability
            if analysis['data_found'] == 0 and analysis['data_checked'] > 0:
                if 'sentiment' in signal_type or 'news' in signal_type:
                    analysis['issues'].append('No external data found')
                    analysis['recommendations'].append({
                        'type': 'data_issue',
                        'reason': 'APIs may not have data for this period',
                        'suggestion': 'Try different date range or check API keys'
                    })

        # Check if too few trades
        elif analysis['total_trades'] < 5:
            analysis['issues'].append(f'Only {analysis["total_trades"]} trades executed')
            analysis['recommendations'].append({
                'type': 'relax_conditions',
                'reason': 'Entry conditions might be too strict',
                'suggestion': 'Consider relaxing thresholds or combining multiple signals'
            })

        # Add data coverage analysis
        if analysis['data_checked'] > 0:
            data_coverage = (analysis['data_found'] / analysis['data_checked']) * 100
            if data_coverage < 50:
                analysis['issues'].append(f'Low data coverage: {data_coverage:.1f}%')
                analysis['recommendations'].append({
                    'type': 'data_coverage',
                    'coverage_percent': data_coverage,
                    'suggestion': 'Consider strategies that don\'t require external data'
                })

        return analysis

    def suggest_threshold_adjustments(self, strategy: Dict[str, Any],
                                     actual_data_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Suggest specific threshold adjustments based on actual data

        Args:
            strategy: Current strategy configuration
            actual_data_stats: Statistics from actual data

        Returns:
            List of specific adjustment recommendations
        """
        adjustments = []

        # Get current parameters
        entry_conditions = strategy.get('entry_conditions', {})
        params = entry_conditions.get('parameters', {})

        # Check each parameter against actual data
        for param_name, param_value in params.items():
            if param_name in actual_data_stats.get('distributions', {}):
                data_stats = actual_data_stats['distributions'][param_name]

                if data_stats.get('has_data'):
                    recommendations = data_stats.get('recommendations', {})

                    # Create specific adjustment
                    adjustment = {
                        'parameter': param_name,
                        'current_value': param_value,
                        'data_range': f"{data_stats['min']:.3f} to {data_stats['max']:.3f}",
                        'data_mean': data_stats['mean'],
                        'recommendations': recommendations
                    }

                    # Determine if current value is realistic
                    if param_name == 'threshold' and param_value > data_stats['max']:
                        adjustment['issue'] = 'Threshold exceeds maximum observed value'
                        adjustment['suggested_value'] = recommendations.get('bullish_threshold', data_stats['percentiles']['75th'])

                    adjustments.append(adjustment)

        return adjustments