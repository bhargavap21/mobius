"""
Strategy Debugger - Comprehensive validation and debugging for trading strategies
"""
import logging
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class StrategyDebugger:
    """Validates and debugs trading strategy execution"""

    def __init__(self, strategy: Dict[str, Any], df: pd.DataFrame):
        self.strategy = strategy
        self.df = df
        self.entry_conditions = strategy.get('entry_conditions', [])
        self.exit_conditions = strategy.get('exit_conditions', [])
        self.validation_results = []

    def validate_indicator_calculations(self) -> Dict[str, Any]:
        """Validate that indicators are calculated correctly"""
        results = {
            'indicators_found': [],
            'indicators_missing': [],
            'value_ranges': {}
        }

        # Check which indicators are in the dataframe
        expected_indicators = set()
        for condition in self.entry_conditions + self.exit_conditions:
            indicator = condition.get('indicator')
            if indicator:
                expected_indicators.add(indicator)

        for indicator in expected_indicators:
            if indicator in self.df.columns:
                results['indicators_found'].append(indicator)
                results['value_ranges'][indicator] = {
                    'min': float(self.df[indicator].min()),
                    'max': float(self.df[indicator].max()),
                    'mean': float(self.df[indicator].mean()),
                    'null_count': int(self.df[indicator].isnull().sum())
                }
            else:
                results['indicators_missing'].append(indicator)

        return results

    def validate_entry_signals(self) -> List[Dict[str, Any]]:
        """Find all dates when entry conditions should have triggered"""
        entry_signals = []

        for i, (idx, row) in enumerate(self.df.iterrows()):
            for condition in self.entry_conditions:
                indicator = condition.get('indicator')
                comparator = condition.get('comparator')
                value = condition.get('value')

                if indicator not in self.df.columns:
                    continue

                indicator_value = row[indicator]
                if pd.isna(indicator_value):
                    continue

                # Check if condition met
                triggered = False
                if comparator == '<' and indicator_value < value:
                    triggered = True
                elif comparator == '>' and indicator_value > value:
                    triggered = True
                elif comparator == '<=' and indicator_value <= value:
                    triggered = True
                elif comparator == '>=' and indicator_value >= value:
                    triggered = True
                elif comparator == '==' and indicator_value == value:
                    triggered = True

                if triggered:
                    entry_signals.append({
                        'date': idx.strftime('%Y-%m-%d'),
                        'indicator': indicator,
                        'value': float(indicator_value),
                        'condition': f"{indicator} {comparator} {value}",
                        'price': float(row['close'])
                    })

        return entry_signals

    def validate_exit_signals(self, entry_date: str) -> List[Dict[str, Any]]:
        """Find all dates after entry_date when exit conditions should have triggered"""
        exit_signals = []

        # Find entry index
        entry_idx = None
        for i, (idx, row) in enumerate(self.df.iterrows()):
            if idx.strftime('%Y-%m-%d') == entry_date:
                entry_idx = i
                break

        if entry_idx is None:
            return []

        # Check exit conditions after entry
        for i, (idx, row) in enumerate(self.df.iterrows()):
            if i <= entry_idx:
                continue

            for condition in self.exit_conditions:
                indicator = condition.get('indicator')
                comparator = condition.get('comparator')
                value = condition.get('value')

                if indicator not in self.df.columns:
                    continue

                indicator_value = row[indicator]
                if pd.isna(indicator_value):
                    continue

                # Check if condition met
                triggered = False
                if comparator == '<' and indicator_value < value:
                    triggered = True
                elif comparator == '>' and indicator_value > value:
                    triggered = True
                elif comparator == '<=' and indicator_value <= value:
                    triggered = True
                elif comparator == '>=' and indicator_value >= value:
                    triggered = True
                elif comparator == '==' and indicator_value == value:
                    triggered = True

                if triggered:
                    exit_signals.append({
                        'date': idx.strftime('%Y-%m-%d'),
                        'indicator': indicator,
                        'value': float(indicator_value),
                        'condition': f"{indicator} {comparator} {value}",
                        'price': float(row['close'])
                    })

        return exit_signals

    def generate_debug_report(self, actual_trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive debug report comparing expected vs actual"""

        # 1. Validate indicators
        indicator_validation = self.validate_indicator_calculations()

        # 2. Find expected entry signals
        expected_entries = self.validate_entry_signals()

        # 3. Compare with actual trades
        actual_entry_dates = {t['entry_date'] for t in actual_trades}
        expected_entry_dates = {e['date'] for e in expected_entries}

        missed_entries = expected_entry_dates - actual_entry_dates
        unexpected_entries = actual_entry_dates - expected_entry_dates

        # 4. For each actual trade, validate exit
        exit_validation = []
        for trade in actual_trades:
            entry_date = trade['entry_date']
            actual_exit = trade['exit_date']

            expected_exits = self.validate_exit_signals(entry_date)
            expected_exit_dates = {e['date'] for e in expected_exits}

            exit_validation.append({
                'trade_number': trade.get('trade_number'),
                'entry_date': entry_date,
                'actual_exit': actual_exit,
                'expected_exits': expected_exit_dates,
                'exit_matched': actual_exit in expected_exit_dates
            })

        return {
            'indicator_validation': indicator_validation,
            'expected_entries': len(expected_entries),
            'actual_entries': len(actual_trades),
            'missed_entries': list(missed_entries),
            'unexpected_entries': list(unexpected_entries),
            'expected_entry_details': expected_entries[:20],  # First 20 for brevity
            'exit_validation': exit_validation,
            'summary': {
                'total_expected_entries': len(expected_entries),
                'total_actual_trades': len(actual_trades),
                'entry_capture_rate': len(actual_trades) / len(expected_entries) if expected_entries else 0,
                'missed_count': len(missed_entries),
                'indicators_ok': len(indicator_validation['indicators_missing']) == 0
            }
        }

    def print_report(self, report: Dict[str, Any]):
        """Print formatted debug report"""
        logger.info("=" * 80)
        logger.info("STRATEGY DEBUG REPORT")
        logger.info("=" * 80)

        # Indicators
        logger.info(f"\n📊 INDICATOR VALIDATION:")
        logger.info(f"   ✅ Found: {report['indicator_validation']['indicators_found']}")
        if report['indicator_validation']['indicators_missing']:
            logger.warning(f"   ❌ Missing: {report['indicator_validation']['indicators_missing']}")

        for indicator, ranges in report['indicator_validation']['value_ranges'].items():
            logger.info(f"   {indicator}: min={ranges['min']:.2f}, max={ranges['max']:.2f}, mean={ranges['mean']:.2f}, nulls={ranges['null_count']}")

        # Entry signals
        logger.info(f"\n🎯 ENTRY SIGNAL ANALYSIS:")
        logger.info(f"   Expected entry signals: {report['expected_entries']}")
        logger.info(f"   Actual trades executed: {report['actual_entries']}")
        logger.info(f"   Capture rate: {report['summary']['entry_capture_rate']*100:.1f}%")

        if report['missed_entries']:
            logger.warning(f"\n   ⚠️  MISSED ENTRIES ({len(report['missed_entries'])} dates):")
            for date in sorted(report['missed_entries'])[:10]:  # Show first 10
                logger.warning(f"      {date}")
            if len(report['missed_entries']) > 10:
                logger.warning(f"      ... and {len(report['missed_entries']) - 10} more")

        if report['expected_entry_details']:
            logger.info(f"\n   📋 First 5 expected entry signals:")
            for entry in report['expected_entry_details'][:5]:
                logger.info(f"      {entry['date']}: {entry['condition']} (price=${entry['price']:.2f})")

        # Exit signals
        logger.info(f"\n🚪 EXIT SIGNAL ANALYSIS:")
        for exit_val in report['exit_validation']:
            status = "✅" if exit_val['exit_matched'] else "❌"
            logger.info(f"   {status} Trade #{exit_val['trade_number']}: Entry {exit_val['entry_date']} → Exit {exit_val['actual_exit']}")
            if not exit_val['exit_matched'] and exit_val['expected_exits']:
                logger.info(f"      Expected exits: {sorted(exit_val['expected_exits'])[:5]}")

        logger.info("=" * 80)
