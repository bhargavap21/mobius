"""
Backtest Runner Agent - Executes backtests and validates results

Now uses containerized execution for security and isolation.
"""
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from agents.base_agent import BaseAgent
from tools.backtester import backtest_strategy
from tools.run_backtest import run_backtest_from_code

logger = logging.getLogger(__name__)

# Try to import code executor, gracefully fallback if Docker not available
try:
    from services.code_executor import execute_strategy_in_container
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    logger.warning("⚠️  Docker Python SDK not available - containerized execution disabled")


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
        # Only use containerized execution if Docker is available
        self.use_containerized_execution = DOCKER_AVAILABLE

    def _format_trades_with_pnl(self, raw_trades: list) -> list:
        """
        Convert raw buy/sell signals into round-trip trades with P&L.

        Args:
            raw_trades: List of individual buy/sell actions

        Returns:
            List of completed trades with entry/exit/pnl information
        """
        formatted_trades = []
        open_position = None
        buy_count = 0
        sell_count = 0

        for trade in raw_trades:
            if trade['action'] == 'buy':
                buy_count += 1
                # Store entry
                open_position = trade
            elif trade['action'] == 'sell' and open_position:
                sell_count += 1
                # Calculate P&L for completed round trip
                entry_price = open_position['price']
                exit_price = trade['price']
                pnl = exit_price - entry_price
                pnl_pct = (pnl / entry_price) * 100

                # Calculate days held
                from datetime import datetime
                try:
                    entry_date = datetime.fromisoformat(open_position['date'].replace('Z', '+00:00'))
                    exit_date = datetime.fromisoformat(trade['date'].replace('Z', '+00:00'))
                    days_held = (exit_date - entry_date).days
                except:
                    days_held = 0

                formatted_trades.append({
                    'symbol': trade['symbol'],
                    'trade_number': len(formatted_trades) + 1,
                    'entry_date': open_position['date'],
                    'exit_date': trade['date'],
                    'entry_price': round(entry_price, 2),
                    'exit_price': round(exit_price, 2),
                    'shares': open_position.get('quantity', 0),
                    'pnl': round(pnl * open_position.get('quantity', 1), 2),
                    'pnl_pct': round(pnl_pct, 2),
                    'days_held': days_held,
                    'entry_reason': open_position.get('reason', ''),
                    'exit_reason': trade.get('reason', ''),
                })
                open_position = None

        logger.info(f"📊 Trade pairing: {buy_count} buys, {sell_count} sells, {len(formatted_trades)} completed pairs")
        return formatted_trades

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run backtest for strategy

        Args:
            input_data: {
                'strategy': dict,
                'feedback': dict (optional - contains suggestions for timeframe),
                'iteration': int,
                'days': int (optional),
                'initial_capital': float (optional),
                'generated_code': str (optional - if provided, uses code execution)
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
        generated_code = input_data.get('generated_code')
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
            # PHASE 3/4: ALWAYS use actual code execution (no fallback)
            if not generated_code:
                logger.error("❌ No generated code provided - cannot run backtest")
                return {
                    'success': False,
                    'error': 'Generated code is required for backtest execution. Simulation-only mode has been removed.'
                }

            logger.info("🐳 Using containerized code execution (Phase 3/4)")
            results = await self.execute_with_generated_code(
                code=generated_code,
                strategy=strategy,
                days=days,
                initial_capital=initial_capital,
                use_container=self.use_containerized_execution
            )

            # VALIDATION: Run legacy simulation in parallel for comparison
            # This helps detect divergence between expected vs actual behavior
            try:
                logger.info("🔍 Running legacy simulation for validation comparison...")
                simulation_results = backtest_strategy(
                    strategy=strategy,
                    days=days,
                    initial_capital=initial_capital,
                    session_id=session_id
                )

                # Store simulation results for evaluator comparison
                if simulation_results and simulation_results.get('success'):
                    results['validation_simulation'] = {
                        'summary': simulation_results.get('summary', {}),
                        'total_return': simulation_results.get('summary', {}).get('total_return', 0),
                        'total_trades': simulation_results.get('summary', {}).get('total_trades', 0),
                    }
                    logger.info(f"✅ Validation simulation complete: {simulation_results.get('summary', {}).get('total_return', 0):.2f}% return")
                else:
                    logger.warning("⚠️  Validation simulation failed - skipping comparison")

            except Exception as e:
                logger.warning(f"⚠️  Validation simulation error (non-critical): {e}")
                # Don't fail the main backtest if validation fails

            if not results or not results.get('success'):
                return {
                    'success': False,
                    'error': results.get('error', 'Backtest returned no results') if results else 'Backtest returned no results'
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

    async def execute_with_generated_code(
        self,
        code: str,
        strategy: Dict[str, Any],
        days: int,
        initial_capital: float,
        use_container: bool = True
    ) -> Dict[str, Any]:
        """
        Execute backtest using actual generated code (Phase 1/2 integration).

        Args:
            code: Generated Python code
            strategy: Strategy configuration
            days: Number of days to backtest
            initial_capital: Starting capital
            use_container: Whether to use containerized execution

        Returns:
            Backtest results with execution details
        """
        logger.info(f"🚀 Executing backtest with generated code (container: {use_container})")

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Extract symbols from strategy
        symbols = strategy.get('assets') or [strategy.get('asset', 'AAPL')]
        if not isinstance(symbols, list):
            symbols = [symbols]

        # Build config - consolidate rsi_threshold from multiple possible sources
        entry_params = strategy.get('entry_conditions', {}).get('parameters', {})
        # Prioritize rsi_threshold over generic threshold for clarity
        rsi_buy_value = entry_params.get('rsi_threshold') or entry_params.get('threshold', 30)

        config = {
            'rsi_period': entry_params.get('rsi_period', 14),
            'rsi_threshold': rsi_buy_value,  # Single source of truth for buy threshold
            'rsi_exit_threshold': entry_params.get('rsi_exit_threshold', 70),
        }

        try:
            if use_container and DOCKER_AVAILABLE:
                # Use containerized execution (secure)
                logger.info("  Using containerized execution (CodeExecutor)")
                result = execute_strategy_in_container(
                    code=code,
                    symbols=symbols,
                    config=config,
                    start_date=start_date,
                    end_date=end_date,
                    initial_cash=initial_capital,
                )

                if not result['success']:
                    return {
                        'success': False,
                        'error': result.get('error', 'Container execution failed'),
                        'execution_method': 'container'
                    }

                backtest_results = result['results']

            else:
                # Direct execution (faster, less secure)
                if use_container and not DOCKER_AVAILABLE:
                    logger.warning("  ⚠️ Container requested but Docker not available - using direct execution")
                logger.info("  Using direct execution (run_backtest)")
                backtest_results = run_backtest_from_code(
                    code=code,
                    symbols=symbols,
                    config=config,
                    start_date=start_date,
                    end_date=end_date,
                    initial_cash=initial_capital,
                    data_source='yfinance',
                    verbose=False,
                )

            # Format results to match expected structure
            metrics = backtest_results.get('metrics', {})
            trades = backtest_results.get('trades', [])

            # DEBUG: Log trade count
            logger.info(f"📊 Raw trades from backtest: {len(trades)}")
            logger.info(f"📊 Metrics total_trades: {metrics.get('total_trades', 0)}")

            # Calculate profit factor
            avg_win = metrics.get('avg_win', 0)
            avg_loss = metrics.get('avg_loss', 0)
            winning_trades = metrics.get('winning_trades', 0)
            losing_trades = metrics.get('losing_trades', 0)

            if avg_loss > 0 and losing_trades > 0:
                profit_factor = (avg_win * winning_trades) / (avg_loss * losing_trades)
            else:
                # Use None instead of float('inf') to ensure JSON serialization compatibility
                profit_factor = 0 if avg_win == 0 else None

            # Convert raw trades to round-trip trades with P&L
            formatted_trades = self._format_trades_with_pnl(trades)
            logger.info(f"📊 Formatted trades: {len(formatted_trades)}")

            # Transform equity curve for frontend chart
            equity_curve_raw = backtest_results.get('equity_curve', [])
            portfolio_history = []

            # Use actual buy & hold equity from backtest if available
            for point in equity_curve_raw:
                current_equity = point.get('equity', initial_capital)
                # Use actual buy_hold_equity if available, otherwise use strategy equity
                buy_hold_value = point.get('buy_hold_equity', current_equity)

                portfolio_history.append({
                    'date': point.get('date', ''),
                    'portfolio_value': round(current_equity, 2),
                    'buy_hold_value': round(buy_hold_value, 2),
                    'cash': round(point.get('cash', 0), 2),
                    'position_value': round(point.get('positions_value', 0), 2)
                })

            # Convert to expected format (round all numeric values to 2 decimals)
            formatted_results = {
                'summary': {
                    'total_return': round(metrics.get('total_return', 0), 2),
                    'buy_hold_return': round(metrics.get('buy_hold_return', 0), 2),
                    'total_trades': metrics.get('total_trades', 0),
                    'winning_trades': winning_trades,
                    'losing_trades': losing_trades,
                    'win_rate': round(metrics.get('win_rate', 0), 2),
                    'avg_win': round(avg_win, 2),
                    'avg_loss': round(abs(avg_loss), 2),
                    'profit_factor': round(profit_factor, 2) if profit_factor is not None else None,
                    'sharpe_ratio': round(metrics.get('sharpe_ratio', 0), 2),
                    'max_drawdown': round(metrics.get('max_drawdown', 0), 2),
                    'initial_capital': round(metrics.get('initial_equity', initial_capital), 2),
                    'final_capital': round(metrics.get('final_equity', initial_capital), 2),
                    'symbol': symbols[0] if symbols else 'Unknown',
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                },
                'trades': formatted_trades,
                'equity_curve': equity_curve_raw,
                'portfolio_history': portfolio_history,
                'execution_method': 'container' if use_container else 'direct',
                'code_executed': True,
            }

            logger.info(f"✅ Code execution successful")
            logger.info(f"   Return: {metrics.get('total_return', 0):.2f}%")
            logger.info(f"   Trades: {metrics.get('total_trades', 0)}")

            return {
                'success': True,
                'results': formatted_results,
            }

        except Exception as e:
            logger.error(f"❌ Code execution failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'execution_method': 'container' if use_container else 'direct'
            }
