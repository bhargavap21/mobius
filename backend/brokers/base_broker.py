"""
Base broker interface for unified trading across backtest and live environments.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class OrderSide(Enum):
    """Order side (buy or sell)"""
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """Order type"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class TimeInForce(Enum):
    """Time in force for orders"""
    DAY = "day"
    GTC = "gtc"  # Good till cancelled
    IOC = "ioc"  # Immediate or cancel
    FOK = "fok"  # Fill or kill


class OrderStatus(Enum):
    """Order status"""
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class Position:
    """Represents a position in an asset"""
    def __init__(
        self,
        symbol: str,
        quantity: float,
        avg_entry_price: float,
        current_price: float,
        market_value: float,
        cost_basis: float,
        unrealized_pl: float,
        unrealized_plpc: float,
    ):
        self.symbol = symbol
        self.quantity = quantity
        self.avg_entry_price = avg_entry_price
        self.current_price = current_price
        self.market_value = market_value
        self.cost_basis = cost_basis
        self.unrealized_pl = unrealized_pl
        self.unrealized_plpc = unrealized_plpc

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "quantity": self.quantity,
            "avg_entry_price": self.avg_entry_price,
            "current_price": self.current_price,
            "market_value": self.market_value,
            "cost_basis": self.cost_basis,
            "unrealized_pl": self.unrealized_pl,
            "unrealized_plpc": self.unrealized_plpc,
        }


class Order:
    """Represents an order"""
    def __init__(
        self,
        id: str,
        symbol: str,
        quantity: float,
        side: OrderSide,
        order_type: OrderType,
        time_in_force: TimeInForce,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        status: OrderStatus = OrderStatus.PENDING,
        filled_qty: float = 0.0,
        filled_avg_price: Optional[float] = None,
        created_at: Optional[datetime] = None,
        filled_at: Optional[datetime] = None,
    ):
        self.id = id
        self.symbol = symbol
        self.quantity = quantity
        self.side = side
        self.order_type = order_type
        self.time_in_force = time_in_force
        self.limit_price = limit_price
        self.stop_price = stop_price
        self.status = status
        self.filled_qty = filled_qty
        self.filled_avg_price = filled_avg_price
        self.created_at = created_at or datetime.now()
        self.filled_at = filled_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "symbol": self.symbol,
            "quantity": self.quantity,
            "side": self.side.value,
            "order_type": self.order_type.value,
            "time_in_force": self.time_in_force.value,
            "limit_price": self.limit_price,
            "stop_price": self.stop_price,
            "status": self.status.value,
            "filled_qty": self.filled_qty,
            "filled_avg_price": self.filled_avg_price,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "filled_at": self.filled_at.isoformat() if self.filled_at else None,
        }


class Account:
    """Represents account information"""
    def __init__(
        self,
        equity: float,
        cash: float,
        buying_power: float,
        portfolio_value: float,
        positions_value: float,
    ):
        self.equity = equity
        self.cash = cash
        self.buying_power = buying_power
        self.portfolio_value = portfolio_value
        self.positions_value = positions_value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "equity": self.equity,
            "cash": self.cash,
            "buying_power": self.buying_power,
            "portfolio_value": self.portfolio_value,
            "positions_value": self.positions_value,
        }


class Bar:
    """Represents a price bar (OHLCV)"""
    def __init__(
        self,
        symbol: str,
        timestamp: datetime,
        open: float,
        high: float,
        low: float,
        close: float,
        volume: float,
    ):
        self.symbol = symbol
        self.timestamp = timestamp
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat(),
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
        }


class BaseBroker(ABC):
    """
    Base broker interface for unified trading operations.
    Implementations: BacktestBroker (simulation), AlpacaBroker (live trading)
    """

    @abstractmethod
    def get_account(self) -> Account:
        """
        Get current account information.

        Returns:
            Account object with equity, cash, buying power, etc.
        """
        pass

    @abstractmethod
    def get_position(self, symbol: str) -> Optional[Position]:
        """
        Get position for a specific symbol.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Position object if position exists, None otherwise
        """
        pass

    @abstractmethod
    def get_all_positions(self) -> List[Position]:
        """
        Get all open positions.

        Returns:
            List of Position objects
        """
        pass

    @abstractmethod
    def submit_order(
        self,
        symbol: str,
        quantity: float,
        side: OrderSide,
        order_type: OrderType = OrderType.MARKET,
        time_in_force: TimeInForce = TimeInForce.DAY,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
    ) -> Order:
        """
        Submit a new order.

        Args:
            symbol: Stock ticker symbol
            quantity: Number of shares
            side: Buy or sell
            order_type: Market, limit, stop, or stop-limit
            time_in_force: Day, GTC, IOC, or FOK
            limit_price: Limit price (required for limit orders)
            stop_price: Stop price (required for stop orders)

        Returns:
            Order object
        """
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an existing order.

        Args:
            order_id: Order ID to cancel

        Returns:
            True if cancelled successfully, False otherwise
        """
        pass

    @abstractmethod
    def get_order(self, order_id: str) -> Optional[Order]:
        """
        Get order by ID.

        Args:
            order_id: Order ID

        Returns:
            Order object if found, None otherwise
        """
        pass

    @abstractmethod
    def get_bars(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        timeframe: str = "1Day",
    ) -> List[Bar]:
        """
        Get historical price bars.

        Args:
            symbol: Stock ticker symbol
            start: Start date
            end: End date
            timeframe: Bar timeframe (e.g., "1Min", "1Hour", "1Day")

        Returns:
            List of Bar objects
        """
        pass

    @abstractmethod
    def get_current_price(self, symbol: str) -> float:
        """
        Get current price for a symbol.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Current price
        """
        pass

    @abstractmethod
    def close_position(self, symbol: str) -> Optional[Order]:
        """
        Close an existing position (market order to sell all shares).

        Args:
            symbol: Stock ticker symbol

        Returns:
            Order object if position closed, None if no position exists
        """
        pass

    @abstractmethod
    def close_all_positions(self) -> List[Order]:
        """
        Close all open positions.

        Returns:
            List of Order objects for each position closed
        """
        pass
