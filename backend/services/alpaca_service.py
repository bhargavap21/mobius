"""
Alpaca Trading API integration service for paper trading
"""
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from config import settings
from typing import Dict, Any, List, Optional
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class AlpacaService:
    """Service for interacting with Alpaca paper trading API"""

    def __init__(self):
        """Initialize Alpaca trading client"""
        self.trading_client = TradingClient(
            api_key=settings.alpaca_api_key,
            secret_key=settings.alpaca_secret_key,
            paper=True  # Force paper trading
        )
        self.data_client = StockHistoricalDataClient(
            api_key=settings.alpaca_api_key,
            secret_key=settings.alpaca_secret_key
        )
        logger.info("✅ Alpaca service initialized (Paper Trading)")

    async def get_account(self) -> Dict[str, Any]:
        """
        Get account information including buying power and equity

        Returns:
            Account details dictionary
        """
        try:
            account = self.trading_client.get_account()
            return {
                "account_id": str(account.id),
                "status": account.status,
                "cash": float(account.cash),
                "portfolio_value": float(account.portfolio_value),
                "buying_power": float(account.buying_power),
                "equity": float(account.equity),
                "last_equity": float(account.last_equity),
                "currency": account.currency,
                "pattern_day_trader": account.pattern_day_trader,
                "trading_blocked": account.trading_blocked,
                "transfers_blocked": account.transfers_blocked,
                "account_blocked": account.account_blocked
            }
        except Exception as e:
            logger.error(f"❌ Failed to get account info: {e}")
            raise

    async def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get all open positions

        Returns:
            List of position dictionaries
        """
        try:
            positions = self.trading_client.get_all_positions()
            return [{
                "symbol": pos.symbol,
                "qty": float(pos.qty),
                "side": pos.side,
                "avg_entry_price": float(pos.avg_entry_price),
                "current_price": float(pos.current_price),
                "market_value": float(pos.market_value),
                "cost_basis": float(pos.cost_basis),
                "unrealized_pl": float(pos.unrealized_pl),
                "unrealized_plpc": float(pos.unrealized_plpc),
                "unrealized_intraday_pl": float(pos.unrealized_intraday_pl),
                "unrealized_intraday_plpc": float(pos.unrealized_intraday_plpc),
            } for pos in positions]
        except Exception as e:
            logger.error(f"❌ Failed to get positions: {e}")
            raise

    async def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific position by symbol

        Args:
            symbol: Stock symbol

        Returns:
            Position dictionary or None if not found
        """
        try:
            pos = self.trading_client.get_open_position(symbol)
            return {
                "symbol": pos.symbol,
                "qty": float(pos.qty),
                "side": pos.side,
                "avg_entry_price": float(pos.avg_entry_price),
                "current_price": float(pos.current_price),
                "market_value": float(pos.market_value),
                "cost_basis": float(pos.cost_basis),
                "unrealized_pl": float(pos.unrealized_pl),
                "unrealized_plpc": float(pos.unrealized_plpc),
            }
        except Exception as e:
            logger.warning(f"⚠️  No position found for {symbol}: {e}")
            return None

    async def place_market_order(
        self,
        symbol: str,
        qty: float,
        side: str,
        time_in_force: str = "day"
    ) -> Dict[str, Any]:
        """
        Place a market order

        Args:
            symbol: Stock symbol
            qty: Quantity to trade
            side: 'buy' or 'sell'
            time_in_force: Order duration (day, gtc, ioc, fok)

        Returns:
            Order details dictionary
        """
        try:
            # Convert side to OrderSide enum
            order_side = OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL

            # Convert time_in_force to enum
            tif_map = {
                "day": TimeInForce.DAY,
                "gtc": TimeInForce.GTC,
                "ioc": TimeInForce.IOC,
                "fok": TimeInForce.FOK
            }
            tif = tif_map.get(time_in_force.lower(), TimeInForce.DAY)

            # Create order request
            order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=order_side,
                time_in_force=tif
            )

            # Submit order
            order = self.trading_client.submit_order(order_data)

            logger.info(f"📈 {side.upper()} order placed: {qty} shares of {symbol}, Order ID: {order.id}")

            return {
                "order_id": str(order.id),
                "symbol": order.symbol,
                "qty": float(order.qty),
                "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
                "side": order.side.value,
                "order_type": order.order_type.value,
                "time_in_force": order.time_in_force.value,
                "status": order.status.value,
                "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else None,
                "submitted_at": str(order.submitted_at),
                "filled_at": str(order.filled_at) if order.filled_at else None,
            }
        except Exception as e:
            logger.error(f"❌ Failed to place order for {symbol}: {e}")
            raise

    async def get_order(self, order_id: str) -> Dict[str, Any]:
        """
        Get order details by ID

        Args:
            order_id: Alpaca order ID

        Returns:
            Order details dictionary
        """
        try:
            order = self.trading_client.get_order_by_id(order_id)
            return {
                "order_id": str(order.id),
                "symbol": order.symbol,
                "qty": float(order.qty),
                "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
                "side": order.side.value,
                "order_type": order.order_type.value,
                "status": order.status.value,
                "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else None,
                "submitted_at": str(order.submitted_at),
                "filled_at": str(order.filled_at) if order.filled_at else None,
            }
        except Exception as e:
            logger.error(f"❌ Failed to get order {order_id}: {e}")
            raise

    async def get_latest_price(self, symbol: str) -> Optional[float]:
        """
        Get latest quote price for a symbol

        Args:
            symbol: Stock symbol

        Returns:
            Latest price or None
        """
        try:
            request_params = StockLatestQuoteRequest(symbol_or_symbols=symbol)
            latest_quote = self.data_client.get_stock_latest_quote(request_params)

            if symbol in latest_quote:
                quote = latest_quote[symbol]
                # Use mid price (average of bid and ask)
                return float((quote.ask_price + quote.bid_price) / 2)
            return None
        except Exception as e:
            logger.warning(f"⚠️  Failed to get latest price for {symbol}: {e}")
            return None

    async def cancel_all_orders(self) -> List[str]:
        """
        Cancel all open orders

        Returns:
            List of cancelled order IDs
        """
        try:
            cancelled_orders = self.trading_client.cancel_orders()
            order_ids = [str(order.id) for order in cancelled_orders]
            logger.info(f"🚫 Cancelled {len(order_ids)} orders")
            return order_ids
        except Exception as e:
            logger.error(f"❌ Failed to cancel orders: {e}")
            raise

    async def close_all_positions(self) -> bool:
        """
        Close all open positions

        Returns:
            True if successful
        """
        try:
            self.trading_client.close_all_positions(cancel_orders=True)
            logger.info("🚫 Closed all positions")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to close positions: {e}")
            raise


# Global instance
alpaca_service = AlpacaService()
