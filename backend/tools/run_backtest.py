"""
Backtest Harness - Execute generated strategy code with BacktestBroker

This module loads dynamically generated strategy code, runs it against historical data,
and returns performance metrics. This is the bridge between code generation and evaluation.

Key Features:
- Loads strategy code from file or string
- Fetches historical market data
- Executes strategy with BacktestBroker
- Calculates comprehensive performance metrics
- Returns results in standardized format
"""

import logging
import sys
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from pathlib import Path
import types
import traceback

# Add backend to path for imports
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from brokers.backtest_broker import BacktestBroker
from brokers.base_broker import OrderSide
from templates.strategy_base import BaseStrategy

logger = logging.getLogger(__name__)


class BacktestHarness:
    """
    Harness for executing generated trading strategies in backtest mode.

    This class:
    1. Loads strategy code dynamically
    2. Fetches historical data
    3. Runs strategy with BacktestBroker
    4. Calculates performance metrics
    """

    def __init__(
        self,
        initial_cash: float = 100000.0,
        data_source: str = "alpaca",  # or "yfinance"
    ):
        """
        Initialize backtest harness.

        Args:
            initial_cash: Starting capital for backtest
            data_source: Data provider ("alpaca" or "yfinance")
        """
        self.initial_cash = initial_cash
        self.data_source = data_source
        self.broker = None
        self.strategy = None
        self.historical_data = {}
        self.trades = []
        self.equity_curve = []

    def load_strategy_from_code(
        self,
        code: str,
        symbols: List[str],
        config: Dict[str, Any]
    ) -> BaseStrategy:
        """
        Load strategy class from code string.

        Args:
            code: Python code string
            symbols: List of symbols to trade
            config: Strategy configuration

        Returns:
            Initialized strategy instance
        """
        try:
            logger.info("Loading strategy from code...")

            # Fix import paths for execution
            code = code.replace('from backend.templates.strategy_base', 'from templates.strategy_base')
            code = code.replace('from backend.brokers.base_broker', 'from brokers.base_broker')
            code = code.replace('from backend.brokers', 'from brokers')

            # Create module from code
            module = types.ModuleType("dynamic_strategy")
            module.__dict__['logging'] = logging
            module.__dict__['logger'] = logger

            # Execute code
            exec(code, module.__dict__)

            # Find strategy class
            strategy_class = None
            for name, obj in module.__dict__.items():
                if isinstance(obj, type) and issubclass(obj, BaseStrategy) and obj != BaseStrategy:
                    strategy_class = obj
                    break

            if not strategy_class:
                raise ValueError("No BaseStrategy subclass found in code")

            logger.info(f"✅ Loaded strategy class: {strategy_class.__name__}")

            # Initialize broker
            self.broker = BacktestBroker(initial_cash=self.initial_cash)

            # Initialize strategy
            self.strategy = strategy_class(self.broker, symbols, config)

            logger.info(f"✅ Strategy initialized for symbols: {symbols}")

            return self.strategy

        except Exception as e:
            logger.error(f"❌ Error loading strategy: {e}")
            logger.error(traceback.format_exc())
            raise

    def load_strategy_from_file(
        self,
        file_path: str,
        symbols: List[str],
        config: Dict[str, Any]
    ) -> BaseStrategy:
        """
        Load strategy from Python file.

        Args:
            file_path: Path to strategy file
            symbols: List of symbols to trade
            config: Strategy configuration

        Returns:
            Initialized strategy instance
        """
        logger.info(f"Loading strategy from file: {file_path}")

        with open(file_path, 'r') as f:
            code = f.read()

        return self.load_strategy_from_code(code, symbols, config)

    def fetch_historical_data(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        timeframe: str = "1Day"
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch historical market data for symbols.

        Args:
            symbols: List of symbols
            start_date: Start date
            end_date: End date
            timeframe: Data timeframe

        Returns:
            Dict mapping symbol to DataFrame with OHLCV data
        """
        logger.info(f"Fetching historical data for {symbols}")
        logger.info(f"  Period: {start_date.date()} to {end_date.date()}")
        logger.info(f"  Timeframe: {timeframe}")

        data = {}

        try:
            if self.data_source == "yfinance":
                import yfinance as yf

                for symbol in symbols:
                    logger.info(f"  Downloading {symbol}...")
                    ticker = yf.Ticker(symbol)
                    df = ticker.history(start=start_date, end=end_date, interval="1d")

                    if df.empty:
                        logger.warning(f"  No data found for {symbol}")
                        continue

                    # Reset index first to get Date as a column
                    df.reset_index(inplace=True)

                    # Standardize column names to lowercase
                    df.columns = [col.lower().replace(' ', '_') for col in df.columns]

                    # Rename date column to timestamp
                    if 'date' in df.columns:
                        df.rename(columns={'date': 'timestamp'}, inplace=True)

                    # Make sure timestamp is datetime
                    if 'timestamp' in df.columns:
                        df['timestamp'] = pd.to_datetime(df['timestamp'])

                    data[symbol] = df
                    logger.info(f"  ✅ {symbol}: {len(df)} bars")

            elif self.data_source == "alpaca":
                from alpaca.data.historical import StockHistoricalDataClient
                from alpaca.data.requests import StockBarsRequest
                from alpaca.data.timeframe import TimeFrame

                api_key = os.getenv('ALPACA_API_KEY')
                secret_key = os.getenv('ALPACA_SECRET_KEY')

                if not api_key or not secret_key:
                    raise ValueError("Alpaca API keys not found in environment")

                client = StockHistoricalDataClient(api_key, secret_key)

                request = StockBarsRequest(
                    symbol_or_symbols=symbols,
                    timeframe=TimeFrame.Day,
                    start=start_date,
                    end=end_date,
                )

                bars = client.get_stock_bars(request)

                for symbol in symbols:
                    if symbol not in bars:
                        logger.warning(f"  No data found for {symbol}")
                        continue

                    records = []
                    for bar in bars[symbol]:
                        records.append({
                            'timestamp': bar.timestamp,
                            'open': float(bar.open),
                            'high': float(bar.high),
                            'low': float(bar.low),
                            'close': float(bar.close),
                            'volume': float(bar.volume),
                        })

                    df = pd.DataFrame(records)
                    data[symbol] = df
                    logger.info(f"  ✅ {symbol}: {len(df)} bars")

            else:
                raise ValueError(f"Unknown data source: {self.data_source}")

            self.historical_data = data
            return data

        except Exception as e:
            logger.error(f"❌ Error fetching historical data: {e}")
            raise

    def run_backtest(
        self,
        start_date: datetime,
        end_date: datetime,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Run backtest simulation.

        Args:
            start_date: Backtest start date
            end_date: Backtest end date
            verbose: Print detailed logs

        Returns:
            Backtest results with trades and metrics
        """
        if not self.strategy:
            raise ValueError("No strategy loaded. Call load_strategy_from_code() first")

        if not self.historical_data:
            symbols = self.strategy.symbols
            self.fetch_historical_data(symbols, start_date, end_date)

        logger.info("\n" + "="*70)
        logger.info("RUNNING BACKTEST")
        logger.info("="*70)
        logger.info(f"Strategy: {self.strategy.__class__.__name__}")
        logger.info(f"Symbols: {self.strategy.symbols}")
        logger.info(f"Period: {start_date.date()} to {end_date.date()}")
        logger.info(f"Initial Capital: ${self.initial_cash:,.2f}")
        logger.info("="*70 + "\n")

        # Reset broker
        self.broker.reset(self.initial_cash)
        self.trades = []
        self.equity_curve = []

        # Get date range from data
        all_dates = set()
        for symbol, df in self.historical_data.items():
            all_dates.update(df['timestamp'].dt.date.tolist())

        dates = sorted(all_dates)

        logger.info(f"Backtesting {len(dates)} trading days...")

        # Track buy & hold for comparison (use first symbol)
        buy_hold_symbol = self.strategy.symbols[0] if self.strategy.symbols else None
        buy_hold_initial_price = None
        buy_hold_shares = 0

        # Main backtest loop
        for i, date in enumerate(dates):
            timestamp = datetime.combine(date, datetime.min.time())

            # Get current bar data for all symbols
            current_data = {}
            prices = {}

            for symbol, df in self.historical_data.items():
                day_data = df[df['timestamp'].dt.date == date]

                if day_data.empty:
                    continue

                row = day_data.iloc[0]
                bar = {
                    'open': row['open'],
                    'high': row['high'],
                    'low': row['low'],
                    'close': row['close'],
                    'volume': row['volume'],
                }

                current_data[symbol] = bar
                prices[symbol] = bar['close']

            if not prices:
                continue

            # Initialize buy & hold on first day with data
            if buy_hold_initial_price is None and buy_hold_symbol in prices:
                buy_hold_initial_price = prices[buy_hold_symbol]
                buy_hold_shares = self.initial_cash / buy_hold_initial_price
                logger.debug(f"Buy & Hold initialized: {buy_hold_shares:.2f} shares @ ${buy_hold_initial_price:.2f}")

            # Update broker with current prices
            self.broker.update_current_prices(prices, timestamp)

            # Feed bars to strategy (updates indicators)
            for symbol, bar in current_data.items():
                self.strategy.on_bar(symbol, bar, timestamp)

            # Generate signals
            signals = self.strategy.generate_signals(current_data)

            # Execute signals
            if signals:
                if verbose:
                    logger.info(f"\n📅 {date}: {len(signals)} signal(s)")

                for signal in signals:
                    if verbose:
                        logger.info(f"   {signal.action.upper()} {signal.symbol}: {signal.reason}")

                # Get positions before execution to track quantity changes
                positions_before = {}
                for signal in signals:
                    pos = self.broker.get_position(signal.symbol)
                    positions_before[signal.symbol] = float(pos.quantity) if pos else 0

                # Execute signals
                self.strategy.execute_signals(signals)

                # Record trades with actual executed quantities
                for signal in signals:
                    pos_after = self.broker.get_position(signal.symbol)
                    quantity_after = float(pos_after.quantity) if pos_after else 0
                    quantity_before = positions_before.get(signal.symbol, 0)

                    # Calculate actual quantity traded
                    quantity_traded = abs(quantity_after - quantity_before)

                    trade_record = {
                        'date': timestamp,
                        'symbol': signal.symbol,
                        'action': signal.action,
                        'reason': signal.reason,
                        'price': prices.get(signal.symbol),
                        'quantity': quantity_traded,
                    }

                    self.trades.append(trade_record)

                if verbose:
                    account = self.broker.get_account()
                    logger.info(f"   Portfolio Value: ${account.equity:,.2f}")

            # Record equity curve
            account = self.broker.get_account()

            # Calculate buy & hold equity
            buy_hold_equity = self.initial_cash
            if buy_hold_symbol in prices and buy_hold_shares > 0:
                buy_hold_equity = buy_hold_shares * prices[buy_hold_symbol]

            self.equity_curve.append({
                'date': timestamp,
                'equity': account.equity,
                'cash': account.cash,
                'positions_value': account.positions_value,
                'buy_hold_equity': buy_hold_equity,
            })

        logger.info(f"\n✅ Backtest complete: {len(dates)} days simulated")

        # Calculate final metrics
        metrics = self._calculate_metrics()

        # Get final positions
        final_positions = self.broker.get_all_positions()

        results = {
            'success': True,
            'metrics': metrics,
            'trades': self.trades,
            'equity_curve': self.equity_curve,
            'final_positions': [pos.to_dict() for pos in final_positions],
            'initial_capital': self.initial_cash,
            'final_equity': metrics['final_equity'],
        }

        self._print_results(results)

        return results

    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics from backtest results."""
        if not self.equity_curve:
            return {}

        df = pd.DataFrame(self.equity_curve)

        initial_equity = self.initial_cash
        final_equity = df['equity'].iloc[-1]
        total_return = ((final_equity - initial_equity) / initial_equity) * 100

        # Daily returns
        df['daily_return'] = df['equity'].pct_change()

        # Sharpe ratio (annualized, assuming 252 trading days)
        avg_return = df['daily_return'].mean()
        std_return = df['daily_return'].std()
        sharpe_ratio = (avg_return / std_return * np.sqrt(252)) if std_return > 0 else 0

        # Max drawdown
        df['cummax'] = df['equity'].cummax()
        df['drawdown'] = (df['equity'] - df['cummax']) / df['cummax']
        max_drawdown = df['drawdown'].min() * 100

        # Win rate (based on days)
        winning_days = len(df[df['daily_return'] > 0])
        losing_days = len(df[df['daily_return'] < 0])
        total_days = len(df) - 1  # Exclude first day (NaN)
        win_rate_days = (winning_days / total_days * 100) if total_days > 0 else 0

        # Trade-level statistics
        trades_df = pd.DataFrame(self.trades)
        total_trades = len(self.trades)

        # Calculate buy & hold return
        if not df.empty and 'buy_hold_equity' in df.columns:
            buy_hold_final = df['buy_hold_equity'].iloc[-1]
            buy_hold_return = ((buy_hold_final - initial_equity) / initial_equity) * 100
        else:
            buy_hold_return = 0

        # Trade statistics (calculate from actual trade pairs)
        winning_trades = 0
        losing_trades = 0
        wins = []
        losses = []
        trade_durations = []

        # Pair up buy/sell trades
        open_position = None
        for trade in self.trades:
            if trade['action'] == 'buy':
                open_position = trade
            elif trade['action'] == 'sell' and open_position:
                # Calculate P&L for this round trip
                entry_price = open_position['price']
                exit_price = trade['price']
                pnl = exit_price - entry_price
                pnl_pct = (pnl / entry_price) * 100

                if pnl > 0:
                    winning_trades += 1
                    wins.append(pnl_pct)
                else:
                    losing_trades += 1
                    losses.append(abs(pnl_pct))

                # Calculate duration if dates available
                if 'date' in open_position and 'date' in trade:
                    entry_date = pd.to_datetime(open_position['date'])
                    exit_date = pd.to_datetime(trade['date'])
                    duration = (exit_date - entry_date).days
                    trade_durations.append(duration)

                open_position = None

        # Calculate aggregate statistics
        avg_win = np.mean(wins) if wins else 0
        avg_loss = np.mean(losses) if losses else 0
        max_win = max(wins) if wins else 0
        max_loss = max(losses) if losses else 0
        avg_days_held = np.mean(trade_durations) if trade_durations else 0
        win_rate = (winning_trades / (winning_trades + losing_trades) * 100) if (winning_trades + losing_trades) > 0 else 0

        # Use completed round-trip count, not total buy/sell actions
        completed_trades = winning_trades + losing_trades

        return {
            'initial_equity': initial_equity,
            'final_equity': final_equity,
            'total_return': total_return,
            'buy_hold_return': buy_hold_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'total_trades': completed_trades,  # Use completed round-trips, not all buy/sell actions
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'max_win': max_win,
            'max_loss': max_loss,
            'avg_days_held': avg_days_held,
            'trading_days': len(df),
            'winning_days': winning_days,
            'losing_days': losing_days,
        }

    def _print_results(self, results: Dict[str, Any]):
        """Print backtest results in a formatted way."""
        metrics = results['metrics']

        logger.info("\n" + "="*70)
        logger.info("BACKTEST RESULTS")
        logger.info("="*70)
        logger.info(f"\n📊 Performance Metrics:")
        logger.info(f"  Initial Capital:  ${metrics['initial_equity']:,.2f}")
        logger.info(f"  Final Equity:     ${metrics['final_equity']:,.2f}")
        logger.info(f"  Total Return:     {metrics['total_return']:+.2f}%")
        logger.info(f"  Sharpe Ratio:     {metrics['sharpe_ratio']:.2f}")
        logger.info(f"  Max Drawdown:     {metrics['max_drawdown']:.2f}%")
        logger.info(f"  Win Rate:         {metrics['win_rate']:.2f}%")
        logger.info(f"\n📈 Trading Activity:")
        logger.info(f"  Total Trades:     {metrics['total_trades']}")
        logger.info(f"  Trading Days:     {metrics['trading_days']}")
        logger.info(f"  Winning Days:     {metrics['winning_days']}")
        logger.info(f"  Losing Days:      {metrics['losing_days']}")

        if results['final_positions']:
            logger.info(f"\n💼 Final Positions:")
            for pos in results['final_positions']:
                logger.info(f"  {pos['symbol']}: {pos['quantity']:.0f} shares @ ${pos['avg_entry_price']:.2f}")
                logger.info(f"    Current: ${pos['current_price']:.2f} | P&L: ${pos['unrealized_pl']:,.2f} ({pos['unrealized_plpc']*100:+.2f}%)")

        logger.info("="*70 + "\n")


def run_backtest_from_code(
    code: str,
    symbols: List[str],
    config: Dict[str, Any],
    start_date: datetime,
    end_date: datetime,
    initial_cash: float = 100000.0,
    data_source: str = "yfinance",
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to run backtest from code string.

    Args:
        code: Strategy code string
        symbols: List of symbols to trade
        config: Strategy configuration
        start_date: Backtest start date
        end_date: Backtest end date
        initial_cash: Starting capital
        data_source: Data provider
        verbose: Print detailed logs

    Returns:
        Backtest results
    """
    harness = BacktestHarness(initial_cash=initial_cash, data_source=data_source)
    harness.load_strategy_from_code(code, symbols, config)
    return harness.run_backtest(start_date, end_date, verbose=verbose)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Load test strategy from Phase 0
    test_code_path = "/tmp/generated_strategy.py"

    if os.path.exists(test_code_path):
        logger.info("Running backtest harness test with generated strategy...")

        harness = BacktestHarness(initial_cash=100000.0, data_source="yfinance")

        symbols = ['AAPL']
        config = {
            'rsi_period': 14,
            'rsi_threshold': 30,
            'rsi_buy_threshold': 30,
            'rsi_sell_threshold': 70,
        }

        harness.load_strategy_from_file(test_code_path, symbols, config)

        # Run backtest for last 6 months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)

        results = harness.run_backtest(start_date, end_date, verbose=True)

        logger.info("✅ Backtest harness test complete!")
    else:
        logger.error(f"Test strategy file not found: {test_code_path}")
        logger.info("Run test_phase_0_integration.py first to generate strategy code")
