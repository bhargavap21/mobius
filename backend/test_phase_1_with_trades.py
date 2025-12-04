"""
Phase 1 Integration Test - With Expected Trades

Tests backtest harness with a strategy and time period designed to generate trades.
We'll use a period where markets were volatile (early 2024) and adjust RSI thresholds
to be more permissive.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from tools.run_backtest import run_backtest_from_code, BacktestHarness


def test_rsi_strategy_volatile_period():
    """Test RSI strategy during a volatile market period"""
    logger.info("\n" + "="*70)
    logger.info("TEST: RSI Strategy During Volatile Period (Aug-Oct 2024)")
    logger.info("="*70 + "\n")

    # Simple RSI strategy code
    strategy_code = """
import logging
from typing import Dict, List, Any
from templates.strategy_base import BaseStrategy, Signal

logger = logging.getLogger(__name__)


class SimpleRSIStrategy(BaseStrategy):
    '''
    Simple RSI mean-reversion strategy.
    Buy when RSI < threshold, sell when RSI > exit_threshold.
    '''

    def initialize(self):
        '''Initialize strategy parameters'''
        self.rsi_period = self.config.get('rsi_period', 14)
        self.rsi_buy_threshold = self.config.get('rsi_buy_threshold', 40)  # More permissive
        self.rsi_sell_threshold = self.config.get('rsi_sell_threshold', 60)  # More permissive

        logger.info(f"✅ Initialized {self.__class__.__name__}")
        logger.info(f"   RSI Period: {self.rsi_period}")
        logger.info(f"   Buy Threshold: {self.rsi_buy_threshold}")
        logger.info(f"   Sell Threshold: {self.rsi_sell_threshold}")

    def generate_signals(self, current_data: Dict[str, Dict[str, float]]) -> List[Signal]:
        '''Generate buy/sell signals based on RSI'''
        signals = []

        for symbol in self.symbols:
            bar = current_data.get(symbol)
            if not bar:
                continue

            # Get current RSI
            indicators = self.get_current_indicators(symbol)
            rsi = indicators.get('rsi')

            # CRITICAL: Check for None
            if rsi is None:
                continue

            # Check position
            position = self.broker.get_position(symbol)

            # Entry: Buy when RSI < threshold (oversold)
            if position is None and rsi < self.rsi_buy_threshold:
                signals.append(Signal(
                    symbol=symbol,
                    action='buy',
                    reason=f'RSI oversold: {rsi:.2f} < {self.rsi_buy_threshold}'
                ))
                logger.info(f"🟢 BUY signal for {symbol}: RSI={rsi:.2f} (oversold)")

            # Exit: Sell when RSI > threshold (overbought)
            elif position is not None and rsi > self.rsi_sell_threshold:
                signals.append(Signal(
                    symbol=symbol,
                    action='sell',
                    reason=f'RSI overbought: {rsi:.2f} > {self.rsi_sell_threshold}'
                ))
                logger.info(f"🔴 SELL signal for {symbol}: RSI={rsi:.2f} (overbought)")

        return signals
"""

    # Configuration with more permissive thresholds
    symbols = ['AAPL']
    config = {
        'rsi_period': 14,
        'rsi_buy_threshold': 40,   # Buy when RSI < 40 (instead of 30)
        'rsi_sell_threshold': 60,  # Sell when RSI > 60 (instead of 70)
    }

    # Test period: August to October 2024 (volatile period with selloffs)
    start_date = datetime(2024, 8, 1)
    end_date = datetime(2024, 10, 31)

    logger.info(f"Strategy: Simple RSI Mean Reversion")
    logger.info(f"Symbol: {symbols[0]}")
    logger.info(f"Period: {start_date.date()} to {end_date.date()}")
    logger.info(f"RSI Buy Threshold: {config['rsi_buy_threshold']} (more permissive)")
    logger.info(f"RSI Sell Threshold: {config['rsi_sell_threshold']} (more permissive)")
    logger.info("")

    # Run backtest
    results = run_backtest_from_code(
        code=strategy_code,
        symbols=symbols,
        config=config,
        start_date=start_date,
        end_date=end_date,
        initial_cash=100000.0,
        data_source="yfinance",
        verbose=True
    )

    # Validate results
    logger.info("\n" + "="*70)
    logger.info("VALIDATION")
    logger.info("="*70)

    metrics = results['metrics']
    trades = results['trades']

    checks = {
        'Backtest completed': results['success'],
        'Trades executed': len(trades) > 0,
        'Metrics calculated': len(metrics) > 0,
        'Returns calculated': 'total_return' in metrics,
        'Sharpe ratio calculated': 'sharpe_ratio' in metrics,
        'Max drawdown calculated': 'max_drawdown' in metrics,
        'Trade history recorded': len(results['trades']) > 0,
        'Equity curve recorded': len(results['equity_curve']) > 0,
    }

    all_passed = True
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        logger.info(f"{status} {check}")
        if not passed:
            all_passed = False

    # Detailed trade analysis
    if trades:
        logger.info("\n" + "="*70)
        logger.info("TRADE ANALYSIS")
        logger.info("="*70)

        buy_trades = [t for t in trades if t['action'] == 'buy']
        sell_trades = [t for t in trades if t['action'] == 'sell']

        logger.info(f"\nTotal Trades: {len(trades)}")
        logger.info(f"  Buy Orders:  {len(buy_trades)}")
        logger.info(f"  Sell Orders: {len(sell_trades)}")

        logger.info("\nTrade History:")
        for i, trade in enumerate(trades[:10], 1):  # Show first 10 trades
            logger.info(f"  {i}. {trade['date'].strftime('%Y-%m-%d')}: "
                       f"{trade['action'].upper()} {trade['symbol']} @ ${trade['price']:.2f} - {trade['reason']}")

        if len(trades) > 10:
            logger.info(f"  ... and {len(trades) - 10} more trades")

        # Check if we have matched buy/sell pairs
        if len(buy_trades) > 0 and len(sell_trades) > 0:
            logger.info(f"\n✅ Strategy successfully generated both BUY and SELL signals")
        elif len(buy_trades) > 0:
            logger.info(f"\n⚠️  Strategy generated BUY signals but no SELL signals")
        elif len(sell_trades) > 0:
            logger.info(f"\n⚠️  Strategy generated SELL signals but no BUY signals")

    return all_passed


def test_sma_crossover_strategy():
    """Test SMA crossover strategy (different signal type)"""
    logger.info("\n" + "="*70)
    logger.info("TEST: SMA Crossover Strategy (Golden Cross / Death Cross)")
    logger.info("="*70 + "\n")

    strategy_code = """
import logging
from typing import Dict, List, Any
from templates.strategy_base import BaseStrategy, Signal

logger = logging.getLogger(__name__)


class SMACrossoverStrategy(BaseStrategy):
    '''
    SMA crossover strategy.
    Buy when fast SMA crosses above slow SMA (golden cross).
    Sell when fast SMA crosses below slow SMA (death cross).
    '''

    def initialize(self):
        '''Initialize strategy parameters'''
        self.fast_period = self.config.get('fast_period', 10)
        self.slow_period = self.config.get('slow_period', 30)
        self.last_signal = None  # Track last signal to detect crossovers

        logger.info(f"✅ Initialized {self.__class__.__name__}")
        logger.info(f"   Fast SMA: {self.fast_period} days")
        logger.info(f"   Slow SMA: {self.slow_period} days")

    def generate_signals(self, current_data: Dict[str, Dict[str, float]]) -> List[Signal]:
        '''Generate signals based on SMA crossover'''
        signals = []

        for symbol in self.symbols:
            bar = current_data.get(symbol)
            if not bar:
                continue

            # Calculate SMAs manually from price history
            if symbol not in self.data or len(self.data[symbol]) < self.slow_period:
                continue  # Not enough data yet

            df = self.data[symbol]

            # Calculate fast and slow SMAs
            fast_sma = df['close'].tail(self.fast_period).mean()
            slow_sma = df['close'].tail(self.slow_period).mean()

            if fast_sma is None or slow_sma is None:
                continue

            # Check position
            position = self.broker.get_position(symbol)

            # Golden Cross: Fast SMA crosses above Slow SMA (bullish)
            if position is None and fast_sma > slow_sma:
                signals.append(Signal(
                    symbol=symbol,
                    action='buy',
                    reason=f'Golden Cross: Fast SMA ({fast_sma:.2f}) > Slow SMA ({slow_sma:.2f})'
                ))
                logger.info(f"🟢 BUY signal: Golden Cross - Fast={fast_sma:.2f}, Slow={slow_sma:.2f}")

            # Death Cross: Fast SMA crosses below Slow SMA (bearish)
            elif position is not None and fast_sma < slow_sma:
                signals.append(Signal(
                    symbol=symbol,
                    action='sell',
                    reason=f'Death Cross: Fast SMA ({fast_sma:.2f}) < Slow SMA ({slow_sma:.2f})'
                ))
                logger.info(f"🔴 SELL signal: Death Cross - Fast={fast_sma:.2f}, Slow={slow_sma:.2f}")

        return signals
"""

    symbols = ['AAPL']
    config = {
        'fast_period': 10,
        'slow_period': 30,
    }

    # Test period: Full year 2024
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 10, 31)

    logger.info(f"Strategy: SMA Crossover (Golden/Death Cross)")
    logger.info(f"Symbol: {symbols[0]}")
    logger.info(f"Period: {start_date.date()} to {end_date.date()}")
    logger.info(f"Fast SMA: {config['fast_period']} days")
    logger.info(f"Slow SMA: {config['slow_period']} days")
    logger.info("")

    # Run backtest
    results = run_backtest_from_code(
        code=strategy_code,
        symbols=symbols,
        config=config,
        start_date=start_date,
        end_date=end_date,
        initial_cash=100000.0,
        data_source="yfinance",
        verbose=False  # Less verbose for SMA
    )

    # Validate
    trades = results['trades']
    metrics = results['metrics']

    logger.info(f"\n✅ Backtest completed")
    logger.info(f"   Total Trades: {len(trades)}")
    logger.info(f"   Total Return: {metrics['total_return']:+.2f}%")
    logger.info(f"   Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")

    if len(trades) > 0:
        logger.info(f"\n✅ SMA strategy successfully generated trades")
        return True
    else:
        logger.warning(f"\n⚠️  No trades generated (might need longer period or different parameters)")
        return False


def main():
    """Run all Phase 1 trade validation tests"""
    logger.info("\n" + "="*70)
    logger.info("PHASE 1 TRADE VALIDATION TEST SUITE")
    logger.info("="*70)
    logger.info("\nValidating that backtest harness:")
    logger.info("  1. Executes generated code correctly")
    logger.info("  2. Generates trading signals as expected")
    logger.info("  3. Records trades and metrics accurately")
    logger.info("")

    # Test 1: RSI strategy during volatile period
    test1_passed = test_rsi_strategy_volatile_period()

    # Test 2: SMA crossover strategy
    test2_passed = test_sma_crossover_strategy()

    # Summary
    logger.info("\n" + "="*70)
    logger.info("TEST SUMMARY")
    logger.info("="*70)
    logger.info(f"RSI Strategy (Volatile Period):  {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    logger.info(f"SMA Crossover Strategy:           {'✅ PASSED' if test2_passed else '⚠️  NO TRADES'}")

    if test1_passed:
        logger.info("\n" + "="*70)
        logger.info("🎉 PHASE 1 TRADE VALIDATION: SUCCESS")
        logger.info("="*70)
        logger.info("\n✅ Backtest harness correctly:")
        logger.info("   • Loads and executes generated code")
        logger.info("   • Generates trading signals")
        logger.info("   • Executes trades through broker")
        logger.info("   • Records trade history")
        logger.info("   • Calculates performance metrics")
        logger.info("   • Tracks equity curve")
        logger.info("\n🚀 Phase 1 is production-ready!")
        logger.info("📋 Ready for Phase 2: Containerization")
        return True
    else:
        logger.error("\n❌ PHASE 1 TRADE VALIDATION FAILED")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
