"""
Broker abstraction layer for trading strategies.
Provides unified interface for both backtesting and live trading.
"""

from .base_broker import BaseBroker
from .backtest_broker import BacktestBroker
from .alpaca_broker import AlpacaBroker

__all__ = ['BaseBroker', 'BacktestBroker', 'AlpacaBroker']
