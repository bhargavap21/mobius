"""
Alpaca broker implementation for live and paper trading.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import (
    MarketOrderRequest, LimitOrderRequest, StopOrderRequest, StopLimitOrderRequest,
    GetOrdersRequest, ClosePositionRequest
)
from alpaca.trading.enums import OrderSide as AlpacaOrderSide, TimeInForce as AlpacaTimeInForce, QueryOrderStatus
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from .base_broker import (
    BaseBroker, Account, Position, Order, Bar,
    OrderSide, OrderType, OrderStatus, TimeInForce
)


class AlpacaBroker(BaseBroker):
    """
    Alpaca broker implementation for live/paper trading.
    Wraps Alpaca API with unified broker interface.
    """

    def __init__(self, api_key: str, secret_key: str, paper: bool = True):
        """
        Initialize Alpaca broker.

        Args:
            api_key: Alpaca API key
            secret_key: Alpaca secret key
            paper: Use paper trading if True, live trading if False
        """
        self.trading_client = TradingClient(api_key, secret_key, paper=paper)
        self.data_client = StockHistoricalDataClient(api_key, secret_key)
        self.paper = paper

    def get_account(self) -> Account:
        """Get current account information."""
        alpaca_account = self.trading_client.get_account()

        return Account(
            equity=float(alpaca_account.equity),
            cash=float(alpaca_account.cash),
            buying_power=float(alpaca_account.buying_power),
            portfolio_value=float(alpaca_account.portfolio_value),
            positions_value=float(alpaca_account.equity) - float(alpaca_account.cash),
        )

    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for a specific symbol."""
        try:
            alpaca_pos = self.trading_client.get_open_position(symbol)
            return self._convert_position(alpaca_pos)
        except Exception:
            # Position doesn't exist
            return None

    def get_all_positions(self) -> List[Position]:
        """Get all open positions."""
        alpaca_positions = self.trading_client.get_all_positions()
        return [self._convert_position(pos) for pos in alpaca_positions]

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
        """Submit a new order."""
        # Convert our enums to Alpaca enums
        alpaca_side = AlpacaOrderSide.BUY if side == OrderSide.BUY else AlpacaOrderSide.SELL
        alpaca_tif = self._convert_time_in_force(time_in_force)

        # Create appropriate order request
        if order_type == OrderType.MARKET:
            request = MarketOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=alpaca_side,
                time_in_force=alpaca_tif,
            )
        elif order_type == OrderType.LIMIT:
            if limit_price is None:
                raise ValueError("Limit price required for limit orders")
            request = LimitOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=alpaca_side,
                time_in_force=alpaca_tif,
                limit_price=limit_price,
            )
        elif order_type == OrderType.STOP:
            if stop_price is None:
                raise ValueError("Stop price required for stop orders")
            request = StopOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=alpaca_side,
                time_in_force=alpaca_tif,
                stop_price=stop_price,
            )
        elif order_type == OrderType.STOP_LIMIT:
            if limit_price is None or stop_price is None:
                raise ValueError("Both limit and stop price required for stop-limit orders")
            request = StopLimitOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=alpaca_side,
                time_in_force=alpaca_tif,
                limit_price=limit_price,
                stop_price=stop_price,
            )
        else:
            raise ValueError(f"Unsupported order type: {order_type}")

        # Submit order
        alpaca_order = self.trading_client.submit_order(request)
        return self._convert_order(alpaca_order)

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order."""
        try:
            self.trading_client.cancel_order_by_id(order_id)
            return True
        except Exception:
            return False

    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID."""
        try:
            alpaca_order = self.trading_client.get_order_by_id(order_id)
            return self._convert_order(alpaca_order)
        except Exception:
            return None

    def get_bars(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        timeframe: str = "1Day",
    ) -> List[Bar]:
        """Get historical price bars."""
        # Convert timeframe string to Alpaca TimeFrame
        alpaca_timeframe = self._convert_timeframe(timeframe)

        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=alpaca_timeframe,
            start=start,
            end=end,
        )

        bars_data = self.data_client.get_stock_bars(request)
        bars = []

        if symbol in bars_data:
            for bar in bars_data[symbol]:
                bars.append(Bar(
                    symbol=symbol,
                    timestamp=bar.timestamp,
                    open=float(bar.open),
                    high=float(bar.high),
                    low=float(bar.low),
                    close=float(bar.close),
                    volume=float(bar.volume),
                ))

        return bars

    def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol."""
        # Get latest bar (1 minute)
        end = datetime.now()
        start = end - timedelta(minutes=5)

        bars = self.get_bars(symbol, start, end, "1Min")
        if bars:
            return bars[-1].close
        return 0.0

    def close_position(self, symbol: str) -> Optional[Order]:
        """Close an existing position."""
        try:
            close_order = self.trading_client.close_position(symbol)
            return self._convert_order(close_order)
        except Exception:
            return None

    def close_all_positions(self) -> List[Order]:
        """Close all open positions."""
        cancel_orders = self.trading_client.close_all_positions(cancel_orders=True)
        return [self._convert_order(order) for order in cancel_orders]

    # Helper methods for converting between Alpaca and our types

    def _convert_position(self, alpaca_pos) -> Position:
        """Convert Alpaca position to our Position type."""
        return Position(
            symbol=alpaca_pos.symbol,
            quantity=float(alpaca_pos.qty),
            avg_entry_price=float(alpaca_pos.avg_entry_price),
            current_price=float(alpaca_pos.current_price),
            market_value=float(alpaca_pos.market_value),
            cost_basis=float(alpaca_pos.cost_basis),
            unrealized_pl=float(alpaca_pos.unrealized_pl),
            unrealized_plpc=float(alpaca_pos.unrealized_plpc),
        )

    def _convert_order(self, alpaca_order) -> Order:
        """Convert Alpaca order to our Order type."""
        # Convert side
        side = OrderSide.BUY if alpaca_order.side == AlpacaOrderSide.BUY else OrderSide.SELL

        # Convert order type
        order_type_map = {
            "market": OrderType.MARKET,
            "limit": OrderType.LIMIT,
            "stop": OrderType.STOP,
            "stop_limit": OrderType.STOP_LIMIT,
        }
        order_type = order_type_map.get(alpaca_order.order_type, OrderType.MARKET)

        # Convert time in force
        tif_map = {
            "day": TimeInForce.DAY,
            "gtc": TimeInForce.GTC,
            "ioc": TimeInForce.IOC,
            "fok": TimeInForce.FOK,
        }
        time_in_force = tif_map.get(alpaca_order.time_in_force, TimeInForce.DAY)

        # Convert status
        status_map = {
            "new": OrderStatus.PENDING,
            "pending_new": OrderStatus.PENDING,
            "accepted": OrderStatus.PENDING,
            "filled": OrderStatus.FILLED,
            "partially_filled": OrderStatus.PARTIALLY_FILLED,
            "cancelled": OrderStatus.CANCELLED,
            "canceled": OrderStatus.CANCELLED,
            "rejected": OrderStatus.REJECTED,
        }
        status = status_map.get(alpaca_order.status, OrderStatus.PENDING)

        return Order(
            id=alpaca_order.id,
            symbol=alpaca_order.symbol,
            quantity=float(alpaca_order.qty),
            side=side,
            order_type=order_type,
            time_in_force=time_in_force,
            limit_price=float(alpaca_order.limit_price) if alpaca_order.limit_price else None,
            stop_price=float(alpaca_order.stop_price) if alpaca_order.stop_price else None,
            status=status,
            filled_qty=float(alpaca_order.filled_qty) if alpaca_order.filled_qty else 0.0,
            filled_avg_price=float(alpaca_order.filled_avg_price) if alpaca_order.filled_avg_price else None,
            created_at=alpaca_order.created_at,
            filled_at=alpaca_order.filled_at,
        )

    def _convert_time_in_force(self, tif: TimeInForce) -> AlpacaTimeInForce:
        """Convert our TimeInForce to Alpaca TimeInForce."""
        tif_map = {
            TimeInForce.DAY: AlpacaTimeInForce.DAY,
            TimeInForce.GTC: AlpacaTimeInForce.GTC,
            TimeInForce.IOC: AlpacaTimeInForce.IOC,
            TimeInForce.FOK: AlpacaTimeInForce.FOK,
        }
        return tif_map.get(tif, AlpacaTimeInForce.DAY)

    def _convert_timeframe(self, timeframe: str) -> TimeFrame:
        """Convert timeframe string to Alpaca TimeFrame."""
        timeframe_map = {
            "1Min": TimeFrame.Minute,
            "5Min": TimeFrame(5, "Min"),
            "15Min": TimeFrame(15, "Min"),
            "1Hour": TimeFrame.Hour,
            "1Day": TimeFrame.Day,
            "1Week": TimeFrame.Week,
            "1Month": TimeFrame.Month,
        }
        return timeframe_map.get(timeframe, TimeFrame.Day)
