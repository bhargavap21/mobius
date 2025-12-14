"""
Market Data Tools - Stock prices, indicators, market info

Uses Alpaca API for real-time and historical market data
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockLatestQuoteRequest
from alpaca.data.enums import Adjustment
from alpaca.data.timeframe import TimeFrame
from config import settings

logger = logging.getLogger(__name__)


# Initialize Alpaca data client
data_client = StockHistoricalDataClient(
    api_key=settings.alpaca_api_key,
    secret_key=settings.alpaca_secret_key,
)


def get_stock_price(
    symbol: str,
    timeframe: str = "1day",
    bars: int = 100,
) -> Dict[str, Any]:
    """
    Get historical stock prices

    Args:
        symbol: Stock ticker (e.g., "AAPL", "TSLA")
        timeframe: Data interval - "1min", "5min", "1hour", "1day"
        bars: Number of bars to retrieve

    Returns:
        Dict with price data
    """
    try:
        logger.info(f"📊 Fetching {bars} bars of {symbol} at {timeframe}")

        # Map timeframe to Alpaca TimeFrame
        timeframe_map = {
            "1min": TimeFrame.Minute,
            "5min": TimeFrame(5, "Min"),
            "15min": TimeFrame(15, "Min"),
            "1hour": TimeFrame.Hour,
            "1day": TimeFrame.Day,
        }

        tf = timeframe_map.get(timeframe, TimeFrame.Day)

        # Calculate start date (rough estimate)
        if timeframe == "1min":
            start = datetime.now() - timedelta(days=1)
        elif timeframe == "1hour":
            start = datetime.now() - timedelta(days=10)
        else:
            start = datetime.now() - timedelta(days=bars * 2)

        # Request data (with raw prices to avoid split/dividend adjustment issues)
        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=tf,
            start=start,
            limit=bars,
            adjustment=Adjustment.RAW,  # Use raw prices to avoid split/dividend adjustment issues
            feed="iex"  # Use free IEX data instead of paid SIP data
        )

        bars_data = data_client.get_stock_bars(request)

        if symbol not in bars_data:
            return {
                "success": False,
                "error": f"No data found for {symbol}",
                "symbol": symbol,
            }

        # Convert to list of dicts
        price_data = []
        for bar in bars_data[symbol]:
            price_data.append(
                {
                    "timestamp": bar.timestamp.isoformat(),
                    "open": float(bar.open),
                    "high": float(bar.high),
                    "low": float(bar.low),
                    "close": float(bar.close),
                    "volume": int(bar.volume),
                }
            )

        current_price = price_data[-1]["close"] if price_data else None

        logger.info(f"✅ Fetched {len(price_data)} bars for {symbol}")
        logger.info(f"   Current price: ${current_price:.2f}")

        return {
            "success": True,
            "symbol": symbol,
            "timeframe": timeframe,
            "current_price": current_price,
            "bars_count": len(price_data),
            "data": price_data[-10:],  # Return last 10 for brevity
            "summary": {
                "latest_close": price_data[-1]["close"] if price_data else None,
                "latest_high": price_data[-1]["high"] if price_data else None,
                "latest_low": price_data[-1]["low"] if price_data else None,
                "latest_volume": price_data[-1]["volume"] if price_data else None,
            },
        }

    except Exception as e:
        logger.error(f"❌ Error fetching stock price for {symbol}: {e}")
        return {
            "success": False,
            "error": str(e),
            "symbol": symbol,
        }


def get_current_price(symbol: str) -> Dict[str, Any]:
    """
    Get current stock price (latest quote)

    Args:
        symbol: Stock ticker

    Returns:
        Current price info
    """
    try:
        logger.info(f"💰 Fetching current price for {symbol}")

        request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
        quote = data_client.get_stock_latest_quote(request)

        if symbol not in quote:
            return {
                "success": False,
                "error": f"No quote found for {symbol}",
                "symbol": symbol,
            }

        q = quote[symbol]

        result = {
            "success": True,
            "symbol": symbol,
            "bid_price": float(q.bid_price),
            "ask_price": float(q.ask_price),
            "bid_size": int(q.bid_size),
            "ask_size": int(q.ask_size),
            "timestamp": q.timestamp.isoformat(),
        }

        logger.info(
            f"✅ {symbol}: Bid ${result['bid_price']:.2f} / Ask ${result['ask_price']:.2f}"
        )

        return result

    except Exception as e:
        logger.error(f"❌ Error fetching current price for {symbol}: {e}")
        return {
            "success": False,
            "error": str(e),
            "symbol": symbol,
        }


def calculate_technical_indicators(
    symbol: str, indicators: List[str] = None
) -> Dict[str, Any]:
    """
    Calculate technical indicators for a stock

    Args:
        symbol: Stock ticker
        indicators: List of indicators (e.g., ["RSI", "MACD", "SMA"])

    Returns:
        Technical indicator values
    """
    if indicators is None:
        indicators = ["SMA_20", "SMA_50"]

    try:
        logger.info(f"📈 Calculating indicators for {symbol}: {indicators}")

        # Get price data
        price_data = get_stock_price(symbol, timeframe="1day", bars=200)

        if not price_data["success"]:
            return price_data

        # For now, return simple moving averages
        # TODO: Implement full TA-Lib integration in next phase
        result = {
            "success": True,
            "symbol": symbol,
            "indicators": {},
            "note": "Full technical indicators coming in Phase 3",
        }

        logger.info(f"✅ Calculated {len(indicators)} indicators for {symbol}")

        return result

    except Exception as e:
        logger.error(f"❌ Error calculating indicators for {symbol}: {e}")
        return {
            "success": False,
            "error": str(e),
            "symbol": symbol,
        }


def get_market_status() -> Dict[str, Any]:
    """
    Check if the market is open

    Returns:
        Market status information
    """
    try:
        from alpaca.trading.client import TradingClient

        trading_client = TradingClient(
            api_key=settings.alpaca_api_key,
            secret_key=settings.alpaca_secret_key,
            paper=True,
        )

        clock = trading_client.get_clock()

        result = {
            "success": True,
            "is_open": clock.is_open,
            "timestamp": clock.timestamp.isoformat(),
            "next_open": clock.next_open.isoformat(),
            "next_close": clock.next_close.isoformat(),
        }

        status = "🟢 OPEN" if clock.is_open else "🔴 CLOSED"
        logger.info(f"Market status: {status}")

        return result

    except Exception as e:
        logger.error(f"❌ Error fetching market status: {e}")
        return {
            "success": False,
            "error": str(e),
        }


# Tool schemas for Claude
MARKET_DATA_TOOLS = [
    {
        "name": "get_stock_price",
        "description": "Get historical stock price data for any ticker. Returns open, high, low, close, volume for specified timeframe.",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., 'AAPL', 'TSLA', 'NVDA')",
                },
                "timeframe": {
                    "type": "string",
                    "enum": ["1min", "5min", "15min", "1hour", "1day"],
                    "description": "Data interval/timeframe",
                    "default": "1day",
                },
                "bars": {
                    "type": "integer",
                    "description": "Number of bars/candles to retrieve",
                    "default": 100,
                },
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "get_current_price",
        "description": "Get the current real-time price for a stock (latest bid/ask quote).",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol",
                }
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "get_market_status",
        "description": "Check if the stock market is currently open or closed, and when it opens/closes next.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
]
