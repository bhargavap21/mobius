"""
Backtest Runner Agent - Executes backtests and validates results
"""
import logging
from typing import Dict, Any
from agents.base_agent import BaseAgent
from tools.backtester import backtest_strategy

logger = logging.getLogger(__name__)


class BacktestRunnerAgent(BaseAgent):
    """
    Runs backtests and validates results

    Responsibilities:
    - Execute backtests with appropriate parameters
    - Validate backtest results
    - Adjust timeframes based on feedback
    - Return structured results
    """

    def __init__(self):
        super().__init__("BacktestRunner")
        self.default_days = 180
        self.default_capital = 10000

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run backtest for strategy

        Args:
            input_data: {
                'strategy': dict,
                'feedback': dict (optional - contains suggestions for timeframe),
                'iteration': int,
                'days': int (optional),
                'initial_capital': float (optional)
            }

        Returns:
            {
                'success': bool,
                'results': dict,
                'days_used': int,
                'warnings': list[str]
            }
        """
        strategy = input_data.get('strategy', {})
        feedback = input_data.get('feedback')
        iteration = input_data.get('iteration', 1)
        days = input_data.get('days') or self.default_days  # Use 'or' to handle None
        initial_capital = input_data.get('initial_capital') or self.default_capital  # Use 'or' to handle None
        session_id = input_data.get('session_id')  # For dataset persistence

        warnings = []

        # Adjust days based on feedback
        if feedback:
            suggestions = feedback.get('suggestions', [])
            for suggestion in suggestions:
                if '360' in suggestion and 'timeframe' in suggestion.lower():
                    days = 360
                    warnings.append(f"Increased backtest timeframe to {days} days based on analyst feedback")
                elif '720' in suggestion or 'year' in suggestion.lower():
                    days = 720
                    warnings.append(f"Increased backtest timeframe to {days} days (2 years) based on analyst feedback")

        # Also auto-increase if previous iteration had too few trades
        if feedback and feedback.get('metrics', {}).get('total_trades', 0) < 3:
            if days < 360:
                days = 360
                warnings.append(f"Auto-increased timeframe to {days} days due to insufficient trades")
            elif days < 720:
                days = 720
                warnings.append(f"Auto-increased timeframe to {days} days (2 years) due to insufficient trades")

        logger.info(f"Running backtest (iteration {iteration}, {days} days, ${initial_capital} capital)")

        try:
            # Run backtest
            results = backtest_strategy(
                strategy=strategy,
                days=days,
                initial_capital=initial_capital,
                session_id=session_id
            )

            if not results:
                return {
                    'success': False,
                    'error': 'Backtest returned no results'
                }

            # Add to memory
            self.add_to_memory({
                'type': 'backtest',
                'iteration': iteration,
                'days': days,
                'results': results.get('summary', {})
            })

            return {
                'success': True,
                'results': results,
                'days_used': days,
                'warnings': warnings
            }

        except Exception as e:
            logger.error(f"Backtest failed: {str(e)}")
            return {
                'success': False,
                'error': f'Backtest execution failed: {str(e)}'
            }
