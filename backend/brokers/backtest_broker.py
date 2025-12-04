"""
Backtest broker implementation for simulated trading.
"""

from typing import Dict, List, Optional
from datetime import datetime
import uuid

from .base_broker import (
    BaseBroker, Account, Position, Order, Bar,
    OrderSide, OrderType, OrderStatus, TimeInForce
)


class BacktestBroker(BaseBroker):
    """
    Simulated broker for backtesting strategies.
    Maintains positions, cash, and executes orders against historical data.
    """

    def __init__(self, initial_cash: float = 100000.0):
        """
        Initialize backtest broker.

        Args:
            initial_cash: Starting cash balance
        """
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: Dict[str, Position] = {}
        self.orders: Dict[str, Order] = {}
        self.current_prices: Dict[str, float] = {}
        self.current_datetime: Optional[datetime] = None

    def update_current_prices(self, prices: Dict[str, float], timestamp: datetime):
        """
        Update current market prices (called during backtest loop).

        Args:
            prices: Dict mapping symbol to current price
            timestamp: Current datetime in backtest
        """
        self.current_prices.update(prices)
        self.current_datetime = timestamp

        # Update position market values
        for symbol, position in self.positions.items():
            if symbol in prices:
                position.current_price = prices[symbol]
                position.market_value = position.quantity * prices[symbol]
                position.unrealized_pl = position.market_value - position.cost_basis
                position.unrealized_plpc = (
                    position.unrealized_pl / position.cost_basis if position.cost_basis > 0 else 0
                )

    def get_account(self) -> Account:
        """Get current account information."""
        positions_value = sum(pos.market_value for pos in self.positions.values())
        equity = self.cash + positions_value

        return Account(
            equity=equity,
            cash=self.cash,
            buying_power=self.cash,  # Simplified: no margin in backtest
            portfolio_value=equity,
            positions_value=positions_value,
        )

    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for a specific symbol."""
        return self.positions.get(symbol)

    def get_all_positions(self) -> List[Position]:
        """Get all open positions."""
        return list(self.positions.values())

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
        In backtest mode, market orders are filled immediately at current price.
        """
        order_id = str(uuid.uuid4())

        order = Order(
            id=order_id,
            symbol=symbol,
            quantity=quantity,
            side=side,
            order_type=order_type,
            time_in_force=time_in_force,
            limit_price=limit_price,
            stop_price=stop_price,
            status=OrderStatus.PENDING,
            created_at=self.current_datetime,
        )

        self.orders[order_id] = order

        # Execute market orders immediately in backtest
        if order_type == OrderType.MARKET:
            self._execute_order(order)

        return order

    def _execute_order(self, order: Order):
        """
        Execute an order (fill it).

        Args:
            order: Order to execute
        """
        symbol = order.symbol
        current_price = self.current_prices.get(symbol)

        if current_price is None:
            order.status = OrderStatus.REJECTED
            return

        total_cost = order.quantity * current_price

        if order.side == OrderSide.BUY:
            # Check if we have enough cash
            if total_cost > self.cash:
                order.status = OrderStatus.REJECTED
                return

            # Deduct cash
            self.cash -= total_cost

            # Update or create position
            if symbol in self.positions:
                pos = self.positions[symbol]
                new_quantity = pos.quantity + order.quantity
                new_cost_basis = pos.cost_basis + total_cost
                pos.quantity = new_quantity
                pos.cost_basis = new_cost_basis
                pos.avg_entry_price = new_cost_basis / new_quantity
                pos.current_price = current_price
                pos.market_value = new_quantity * current_price
                pos.unrealized_pl = pos.market_value - pos.cost_basis
                pos.unrealized_plpc = pos.unrealized_pl / pos.cost_basis if pos.cost_basis > 0 else 0
            else:
                self.positions[symbol] = Position(
                    symbol=symbol,
                    quantity=order.quantity,
                    avg_entry_price=current_price,
                    current_price=current_price,
                    market_value=total_cost,
                    cost_basis=total_cost,
                    unrealized_pl=0.0,
                    unrealized_plpc=0.0,
                )

        elif order.side == OrderSide.SELL:
            # Check if we have position to sell
            if symbol not in self.positions:
                order.status = OrderStatus.REJECTED
                return

            pos = self.positions[symbol]
            if pos.quantity < order.quantity:
                order.status = OrderStatus.REJECTED
                return

            # Add cash from sale
            self.cash += total_cost

            # Update position
            pos.quantity -= order.quantity
            pos.cost_basis -= (pos.avg_entry_price * order.quantity)

            if pos.quantity == 0:
                # Close position
                del self.positions[symbol]
            else:
                # Update position values
                pos.market_value = pos.quantity * current_price
                pos.unrealized_pl = pos.market_value - pos.cost_basis
                pos.unrealized_plpc = pos.unrealized_pl / pos.cost_basis if pos.cost_basis > 0 else 0

        # Mark order as filled
        order.status = OrderStatus.FILLED
        order.filled_qty = order.quantity
        order.filled_avg_price = current_price
        order.filled_at = self.current_datetime

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order."""
        order = self.orders.get(order_id)
        if order and order.status == OrderStatus.PENDING:
            order.status = OrderStatus.CANCELLED
            return True
        return False

    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID."""
        return self.orders.get(order_id)

    def get_bars(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        timeframe: str = "1Day",
    ) -> List[Bar]:
        """
        Get historical price bars.
        Note: In backtest mode, this should be provided by the backtest harness.
        This is a placeholder that returns empty list.
        """
        # TODO: Integrate with historical data provider
        return []

    def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol."""
        return self.current_prices.get(symbol, 0.0)

    def close_position(self, symbol: str) -> Optional[Order]:
        """Close an existing position."""
        position = self.get_position(symbol)
        if not position:
            return None

        return self.submit_order(
            symbol=symbol,
            quantity=position.quantity,
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
        )

    def close_all_positions(self) -> List[Order]:
        """Close all open positions."""
        orders = []
        symbols = list(self.positions.keys())  # Copy keys to avoid modification during iteration

        for symbol in symbols:
            order = self.close_position(symbol)
            if order:
                orders.append(order)

        return orders

    def get_portfolio_value(self) -> float:
        """Get total portfolio value (cash + positions)."""
        return self.get_account().portfolio_value

    def reset(self, initial_cash: Optional[float] = None):
        """
        Reset broker state for new backtest.

        Args:
            initial_cash: Optional new initial cash amount
        """
        if initial_cash is not None:
            self.initial_cash = initial_cash

        self.cash = self.initial_cash
        self.positions.clear()
        self.orders.clear()
        self.current_prices.clear()
        self.current_datetime = None
