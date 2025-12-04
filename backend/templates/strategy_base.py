"""
Base strategy class for all trading strategies.
Provides unified interface for both backtesting and live trading.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd

try:
    from backend.brokers.base_broker import BaseBroker, OrderSide, OrderType
except ModuleNotFoundError:
    from brokers.base_broker import BaseBroker, OrderSide, OrderType


class Signal:
    """Represents a trading signal"""
    def __init__(self, symbol: str, action: str, quantity: Optional[float] = None, reason: str = ""):
        """
        Initialize a signal.

        Args:
            symbol: Stock ticker symbol
            action: 'buy', 'sell', 'hold', or 'rebalance'
            quantity: Number of shares (optional, can be calculated later)
            reason: Human-readable reason for the signal
        """
        self.symbol = symbol
        self.action = action
        self.quantity = quantity
        self.reason = reason

    def __repr__(self):
        return f"Signal(symbol={self.symbol}, action={self.action}, quantity={self.quantity}, reason={self.reason})"


class BaseStrategy(ABC):
    """
    Base class for all trading strategies.

    Subclasses must implement:
    - initialize(): Set up indicators and strategy state
    - generate_signals(): Generate buy/sell signals based on current data

    Optional methods to override:
    - on_bar(): Called on each new price bar (for custom logic)
    - calculate_position_size(): Custom position sizing logic
    - on_portfolio_rebalance(): Portfolio rebalancing logic
    """

    def __init__(
        self,
        broker: BaseBroker,
        symbols: List[str],
        config: Dict[str, Any],
    ):
        """
        Initialize strategy.

        Args:
            broker: Broker instance (BacktestBroker or AlpacaBroker)
            symbols: List of symbols to trade
            config: Strategy configuration (parameters, indicators, etc.)
        """
        self.broker = broker
        self.symbols = symbols if isinstance(symbols, list) else [symbols]
        self.config = config

        # Strategy state
        self.data: Dict[str, pd.DataFrame] = {}  # Historical data for each symbol
        self.indicators: Dict[str, Dict[str, Any]] = {}  # Indicators for each symbol
        self.portfolio_mode = len(self.symbols) > 1

        # Initialize strategy
        self.initialize()

    @abstractmethod
    def initialize(self):
        """
        Initialize strategy (set up indicators, state, etc.).
        Called once when strategy starts.

        Example:
            self.indicators['AAPL'] = {
                'rsi_period': 14,
                'sma_period': 50,
            }
        """
        pass

    @abstractmethod
    def generate_signals(self, current_data: Dict[str, Dict[str, float]]) -> List[Signal]:
        """
        Generate trading signals based on current market data.

        Args:
            current_data: Dict mapping symbol to current bar data
                         Example: {'AAPL': {'open': 150, 'high': 152, 'low': 149, 'close': 151, 'volume': 1000000}}

        Returns:
            List of Signal objects

        Example:
            signals = []
            for symbol in self.symbols:
                bar = current_data.get(symbol)
                if bar and self._should_buy(symbol, bar):
                    signals.append(Signal(symbol, 'buy', reason='RSI < 30'))
                elif bar and self._should_sell(symbol, bar):
                    signals.append(Signal(symbol, 'sell', reason='RSI > 70'))
            return signals
        """
        pass

    def on_bar(self, symbol: str, bar: Dict[str, float], timestamp: datetime):
        """
        Called on each new price bar for a symbol.
        Override this for custom per-bar logic.

        Args:
            symbol: Stock ticker symbol
            bar: OHLCV data {'open': X, 'high': X, 'low': X, 'close': X, 'volume': X}
            timestamp: Bar timestamp
        """
        # Update data history
        if symbol not in self.data:
            self.data[symbol] = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

        new_row = pd.DataFrame([{
            'timestamp': timestamp,
            'open': bar['open'],
            'high': bar['high'],
            'low': bar['low'],
            'close': bar['close'],
            'volume': bar['volume'],
        }])
        self.data[symbol] = pd.concat([self.data[symbol], new_row], ignore_index=True)

        # Update indicators (subclasses can override to add custom indicators)
        self._update_indicators(symbol)

    def _update_indicators(self, symbol: str):
        """
        Update technical indicators for a symbol.
        Override this to calculate custom indicators.

        Args:
            symbol: Stock ticker symbol
        """
        if symbol not in self.data or len(self.data[symbol]) == 0:
            return

        df = self.data[symbol]

        # Initialize indicators dict if needed
        if symbol not in self.indicators:
            self.indicators[symbol] = {}

        # Calculate RSI if configured
        rsi_period = self.config.get('rsi_period', 14)
        if len(df) >= rsi_period:
            self.indicators[symbol]['rsi'] = self._calculate_rsi(df['close'], rsi_period)

        # Calculate SMA if configured
        sma_period = self.config.get('sma_period')
        if sma_period and len(df) >= sma_period:
            self.indicators[symbol]['sma'] = df['close'].rolling(window=sma_period).mean().iloc[-1]

        # Calculate EMA if configured
        ema_period = self.config.get('ema_period')
        if ema_period and len(df) >= ema_period:
            self.indicators[symbol]['ema'] = df['close'].ewm(span=ema_period).mean().iloc[-1]

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI indicator."""
        if len(prices) < period + 1:
            return 50.0  # Neutral RSI if not enough data

        deltas = prices.diff()
        gains = deltas.where(deltas > 0, 0)
        losses = -deltas.where(deltas < 0, 0)

        avg_gain = gains.rolling(window=period).mean()
        avg_loss = losses.rolling(window=period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50.0

    def calculate_position_size(self, symbol: str, signal: Signal) -> float:
        """
        Calculate position size for a signal.
        Override this for custom position sizing logic.

        Args:
            symbol: Stock ticker symbol
            signal: Trading signal

        Returns:
            Number of shares to buy/sell
        """
        if signal.quantity is not None:
            return signal.quantity

        account = self.broker.get_account()
        current_price = self.broker.get_current_price(symbol)

        if current_price == 0:
            return 0

        if signal.action == 'buy':
            if self.portfolio_mode:
                # Equal weight allocation
                target_allocation = account.equity / len(self.symbols)
                position_value = target_allocation
            else:
                # Use all available buying power
                position_value = account.buying_power

            shares = int(position_value / current_price)
            return shares

        elif signal.action == 'sell':
            position = self.broker.get_position(symbol)
            if position:
                return position.quantity
            return 0

        return 0

    def on_portfolio_rebalance(self, target_weights: Dict[str, float]):
        """
        Rebalance portfolio to target weights.
        Override this for custom rebalancing logic.

        Args:
            target_weights: Dict mapping symbol to target weight (0.0 to 1.0)
                          Example: {'AAPL': 0.5, 'GOOG': 0.5}
        """
        account = self.broker.get_account()
        total_value = account.equity

        for symbol, target_weight in target_weights.items():
            target_value = total_value * target_weight
            current_price = self.broker.get_current_price(symbol)

            if current_price == 0:
                continue

            target_shares = int(target_value / current_price)

            # Get current position
            position = self.broker.get_position(symbol)
            current_shares = position.quantity if position else 0

            # Calculate difference
            shares_to_trade = target_shares - current_shares

            if shares_to_trade > 0:
                # Buy more shares
                self.broker.submit_order(
                    symbol=symbol,
                    quantity=shares_to_trade,
                    side=OrderSide.BUY,
                    order_type=OrderType.MARKET,
                )
            elif shares_to_trade < 0:
                # Sell shares
                self.broker.submit_order(
                    symbol=symbol,
                    quantity=abs(shares_to_trade),
                    side=OrderSide.SELL,
                    order_type=OrderType.MARKET,
                )

    def execute_signals(self, signals: List[Signal]):
        """
        Execute a list of trading signals.

        Args:
            signals: List of Signal objects
        """
        for signal in signals:
            if signal.action == 'buy':
                quantity = self.calculate_position_size(signal.symbol, signal)
                if quantity > 0:
                    self.broker.submit_order(
                        symbol=signal.symbol,
                        quantity=quantity,
                        side=OrderSide.BUY,
                        order_type=OrderType.MARKET,
                    )

            elif signal.action == 'sell':
                quantity = self.calculate_position_size(signal.symbol, signal)
                if quantity > 0:
                    self.broker.submit_order(
                        symbol=signal.symbol,
                        quantity=quantity,
                        side=OrderSide.SELL,
                        order_type=OrderType.MARKET,
                    )

            elif signal.action == 'rebalance':
                # Trigger portfolio rebalance
                if self.portfolio_mode:
                    # Equal weight by default
                    target_weights = {sym: 1.0 / len(self.symbols) for sym in self.symbols}
                    self.on_portfolio_rebalance(target_weights)

    def get_current_indicators(self, symbol: str) -> Dict[str, Any]:
        """
        Get current indicator values for a symbol.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dict of indicator values
        """
        return self.indicators.get(symbol, {})

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """
        Get portfolio summary.

        Returns:
            Dict with portfolio metrics
        """
        account = self.broker.get_account()
        positions = self.broker.get_all_positions()

        return {
            'equity': account.equity,
            'cash': account.cash,
            'positions_value': account.positions_value,
            'positions': [pos.to_dict() for pos in positions],
            'num_positions': len(positions),
        }
