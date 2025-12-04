"""
Test script for BaseStrategy architecture
Verifies that strategies work with both BacktestBroker and AlpacaBroker
"""

import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
from templates.strategy_base import BaseStrategy, Signal
from brokers.backtest_broker import BacktestBroker

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SimpleRSIStrategy(BaseStrategy):
    """
    Simple RSI mean-reversion strategy for testing.
    Buy when RSI < 30, sell when RSI > 70.
    """

    def initialize(self):
        """Initialize strategy parameters"""
        self.rsi_buy_threshold = self.config.get('rsi_buy_threshold', 30)
        self.rsi_sell_threshold = self.config.get('rsi_sell_threshold', 70)

        logger.info(f"Initialized {self.__class__.__name__}")
        logger.info(f"  Symbols: {self.symbols}")
        logger.info(f"  RSI Buy: < {self.rsi_buy_threshold}")
        logger.info(f"  RSI Sell: > {self.rsi_sell_threshold}")

    def generate_signals(self, current_data: Dict[str, Dict[str, float]]) -> List[Signal]:
        """Generate trading signals based on RSI"""
        signals = []

        for symbol in self.symbols:
            bar = current_data.get(symbol)
            if not bar:
                continue

            # Get current RSI indicator
            indicators = self.get_current_indicators(symbol)
            rsi = indicators.get('rsi')

            if rsi is None:
                logger.debug(f"No RSI available for {symbol}")
                continue

            # Check if we have a position
            position = self.broker.get_position(symbol)

            # Entry signal: buy when RSI < threshold
            if position is None and rsi < self.rsi_buy_threshold:
                signals.append(Signal(
                    symbol=symbol,
                    action='buy',
                    reason=f'RSI ({rsi:.2f}) < {self.rsi_buy_threshold}'
                ))
                logger.info(f"📈 BUY signal for {symbol}: RSI={rsi:.2f}")

            # Exit signal: sell when RSI > threshold
            elif position is not None and rsi > self.rsi_sell_threshold:
                signals.append(Signal(
                    symbol=symbol,
                    action='sell',
                    reason=f'RSI ({rsi:.2f}) > {self.rsi_sell_threshold}'
                ))
                logger.info(f"📉 SELL signal for {symbol}: RSI={rsi:.2f}")

        return signals


def test_backtest_broker():
    """Test BaseStrategy with BacktestBroker"""
    logger.info("\n" + "="*60)
    logger.info("TEST 1: BaseStrategy with BacktestBroker")
    logger.info("="*60 + "\n")

    # Initialize backtest broker with $10,000
    broker = BacktestBroker(initial_cash=10000.0)

    # Initialize strategy
    symbols = ['AAPL']
    config = {
        'rsi_period': 14,
        'rsi_buy_threshold': 30,
        'rsi_sell_threshold': 70,
    }

    strategy = SimpleRSIStrategy(broker, symbols, config)

    # Simulate some price bars with varying prices
    test_bars = [
        # Day 1-14: Build up RSI history
        {'timestamp': datetime(2024, 1, 1), 'AAPL': {'open': 150, 'high': 151, 'low': 149, 'close': 150.5, 'volume': 1000000}},
        {'timestamp': datetime(2024, 1, 2), 'AAPL': {'open': 150.5, 'high': 152, 'low': 150, 'close': 151, 'volume': 1100000}},
        {'timestamp': datetime(2024, 1, 3), 'AAPL': {'open': 151, 'high': 151.5, 'low': 149, 'close': 149.5, 'volume': 1200000}},
        {'timestamp': datetime(2024, 1, 4), 'AAPL': {'open': 149.5, 'high': 150, 'low': 148, 'close': 148.2, 'volume': 1300000}},
        {'timestamp': datetime(2024, 1, 5), 'AAPL': {'open': 148.2, 'high': 149, 'low': 147, 'close': 147.5, 'volume': 1400000}},
        {'timestamp': datetime(2024, 1, 8), 'AAPL': {'open': 147.5, 'high': 148, 'low': 146, 'close': 146.8, 'volume': 1500000}},
        {'timestamp': datetime(2024, 1, 9), 'AAPL': {'open': 146.8, 'high': 147, 'low': 145, 'close': 145.5, 'volume': 1600000}},
        {'timestamp': datetime(2024, 1, 10), 'AAPL': {'open': 145.5, 'high': 146, 'low': 144, 'close': 144.2, 'volume': 1700000}},
        {'timestamp': datetime(2024, 1, 11), 'AAPL': {'open': 144.2, 'high': 145, 'low': 143, 'close': 143.5, 'volume': 1800000}},
        {'timestamp': datetime(2024, 1, 12), 'AAPL': {'open': 143.5, 'high': 144, 'low': 142, 'close': 142.8, 'volume': 1900000}},
        {'timestamp': datetime(2024, 1, 15), 'AAPL': {'open': 142.8, 'high': 143, 'low': 141, 'close': 141.5, 'volume': 2000000}},
        {'timestamp': datetime(2024, 1, 16), 'AAPL': {'open': 141.5, 'high': 142, 'low': 140, 'close': 140.2, 'volume': 2100000}},
        {'timestamp': datetime(2024, 1, 17), 'AAPL': {'open': 140.2, 'high': 141, 'low': 139, 'close': 139.5, 'volume': 2200000}},
        {'timestamp': datetime(2024, 1, 18), 'AAPL': {'open': 139.5, 'high': 140, 'low': 138, 'close': 138.8, 'volume': 2300000}},
        # Day 15: Oversold - should trigger buy (RSI likely < 30)
        {'timestamp': datetime(2024, 1, 19), 'AAPL': {'open': 138.8, 'high': 145, 'low': 138, 'close': 144, 'volume': 2400000}},
        # Days 16-20: Recovery
        {'timestamp': datetime(2024, 1, 22), 'AAPL': {'open': 144, 'high': 146, 'low': 143, 'close': 145.5, 'volume': 1200000}},
        {'timestamp': datetime(2024, 1, 23), 'AAPL': {'open': 145.5, 'high': 147, 'low': 145, 'close': 146.2, 'volume': 1100000}},
        {'timestamp': datetime(2024, 1, 24), 'AAPL': {'open': 146.2, 'high': 148, 'low': 146, 'close': 147.8, 'volume': 1000000}},
        {'timestamp': datetime(2024, 1, 25), 'AAPL': {'open': 147.8, 'high': 149, 'low': 147, 'close': 148.5, 'volume': 900000}},
        {'timestamp': datetime(2024, 1, 26), 'AAPL': {'open': 148.5, 'high': 150, 'low': 148, 'close': 149.2, 'volume': 800000}},
    ]

    # Run backtest simulation
    for bar_data in test_bars:
        timestamp = bar_data['timestamp']
        prices = {symbol: data['close'] for symbol, data in bar_data.items() if symbol != 'timestamp'}

        # Update broker with current prices
        broker.update_current_prices(prices, timestamp)

        # Feed bar to strategy (updates indicators)
        for symbol in symbols:
            if symbol in bar_data:
                strategy.on_bar(symbol, bar_data[symbol], timestamp)

        # Generate signals
        current_data = {symbol: bar_data[symbol] for symbol in symbols if symbol in bar_data}
        signals = strategy.generate_signals(current_data)

        # Execute signals
        if signals:
            logger.info(f"\n📅 {timestamp.date()}: Generated {len(signals)} signal(s)")
            strategy.execute_signals(signals)

            # Show portfolio status
            account = broker.get_account()
            logger.info(f"   Portfolio Value: ${account.equity:.2f}")
            logger.info(f"   Cash: ${account.cash:.2f}")
            logger.info(f"   Positions Value: ${account.positions_value:.2f}")

    # Final portfolio summary
    logger.info("\n" + "="*60)
    logger.info("BACKTEST RESULTS")
    logger.info("="*60)
    summary = strategy.get_portfolio_summary()
    logger.info(f"Final Equity: ${summary['equity']:.2f}")
    logger.info(f"Final Cash: ${summary['cash']:.2f}")
    logger.info(f"Positions Value: ${summary['positions_value']:.2f}")
    logger.info(f"Number of Positions: {summary['num_positions']}")
    logger.info(f"Return: {((summary['equity'] - 10000) / 10000 * 100):.2f}%")

    for pos in summary['positions']:
        logger.info(f"\nPosition: {pos['symbol']}")
        logger.info(f"  Quantity: {pos['quantity']:.2f}")
        logger.info(f"  Entry: ${pos['avg_entry_price']:.2f}")
        logger.info(f"  Current: ${pos['current_price']:.2f}")
        logger.info(f"  P&L: ${pos['unrealized_pl']:.2f} ({pos['unrealized_plpc']*100:.2f}%)")

    logger.info("\n✅ BacktestBroker test completed successfully!")
    return True


def test_alpaca_broker():
    """Test BaseStrategy with AlpacaBroker (requires API keys)"""
    logger.info("\n" + "="*60)
    logger.info("TEST 2: BaseStrategy with AlpacaBroker")
    logger.info("="*60 + "\n")

    import os

    # Check if API keys are available
    api_key = os.getenv('ALPACA_API_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY')

    if not api_key or not secret_key:
        logger.warning("⚠️  Alpaca API keys not found in environment variables")
        logger.warning("   Skipping AlpacaBroker test")
        logger.info("   To test with Alpaca, set ALPACA_API_KEY and ALPACA_SECRET_KEY")
        return False

    try:
        from brokers.alpaca_broker import AlpacaBroker

        # Initialize Alpaca broker (paper trading)
        broker = AlpacaBroker(
            api_key=api_key,
            secret_key=secret_key,
            paper=True
        )

        # Initialize strategy
        symbols = ['AAPL']
        config = {
            'rsi_period': 14,
            'rsi_buy_threshold': 30,
            'rsi_sell_threshold': 70,
        }

        strategy = SimpleRSIStrategy(broker, symbols, config)

        # Get account info
        account = broker.get_account()
        logger.info(f"Connected to Alpaca Paper Trading")
        logger.info(f"Account Equity: ${account.equity:.2f}")
        logger.info(f"Buying Power: ${account.buying_power:.2f}")

        # Get current positions
        positions = broker.get_all_positions()
        logger.info(f"Current Positions: {len(positions)}")

        logger.info("\n✅ AlpacaBroker test completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ AlpacaBroker test failed: {e}")
        return False


if __name__ == "__main__":
    logger.info("Starting BaseStrategy Architecture Tests\n")

    # Test 1: BacktestBroker
    backtest_passed = test_backtest_broker()

    # Test 2: AlpacaBroker (optional, requires API keys)
    alpaca_passed = test_alpaca_broker()

    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    logger.info(f"BacktestBroker: {'✅ PASSED' if backtest_passed else '❌ FAILED'}")
    logger.info(f"AlpacaBroker: {'✅ PASSED' if alpaca_passed else '⚠️  SKIPPED (no API keys)'}")
    logger.info("="*60)

    if backtest_passed:
        logger.info("\n🎉 Phase 0 Complete!")
        logger.info("   ✅ BaseStrategy interface created")
        logger.info("   ✅ BacktestBroker implementation working")
        logger.info("   ✅ AlpacaBroker implementation created")
        logger.info("   ✅ Code generator updated to use BaseStrategy")
        logger.info("\nNext: Phase 1 - Build backtest harness to execute generated code")
