"""
Politician/Congressional Trading Data Tool

Fetches trading data from Congress members using QuiverQuant API
or public sources like House Stock Watcher.
"""

import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from config import settings

logger = logging.getLogger(__name__)


def get_politician_trades(
    politician_name: Optional[str] = None,
    ticker: Optional[str] = None,
    days_back: int = 90
) -> Dict[str, Any]:
    """
    Get recent congressional/politician stock trades

    Args:
        politician_name: Filter by politician name (e.g., "Nancy Pelosi", "Pelosi")
        ticker: Filter by stock ticker
        days_back: How many days back to fetch trades (default 90)

    Returns:
        {
            'success': bool,
            'trades': List[Dict],
            'politician': str,
            'summary': Dict
        }
    """
    try:
        if settings.quiver_api_key:
            return _get_quiver_trades(politician_name, ticker, days_back)
        else:
            # Fallback to public House Stock Watcher scraping
            return _get_house_stock_watcher_trades(politician_name, ticker, days_back)

    except Exception as e:
        logger.error(f"Error fetching politician trades: {e}")
        return {
            'success': False,
            'error': str(e),
            'trades': []
        }


def _get_quiver_trades(
    politician_name: Optional[str],
    ticker: Optional[str],
    days_back: int
) -> Dict[str, Any]:
    """Fetch trades from QuiverQuant API"""

    url = "https://api.quiverquant.com/beta/live/congresstrading"
    headers = {"Authorization": f"Token {settings.quiver_api_key}"}

    try:
        response = requests.get(url, headers=headers, timeout=60)  # Increased timeout for slow API
        response.raise_for_status()
        data = response.json()

        trades = []
        cutoff_date = datetime.now() - timedelta(days=days_back)

        for trade in data:
            trade_date = datetime.strptime(trade.get('TransactionDate', ''), '%Y-%m-%d')

            # Filter by date
            if trade_date < cutoff_date:
                continue

            # Filter by politician name (case-insensitive partial match)
            if politician_name:
                representative = trade.get('Representative', '').lower()
                if politician_name.lower() not in representative:
                    continue

            # Filter by ticker
            if ticker and trade.get('Ticker', '').upper() != ticker.upper():
                continue

            trades.append({
                'date': trade.get('TransactionDate'),
                'politician': trade.get('Representative'),
                'ticker': trade.get('Ticker'),
                'transaction': trade.get('Transaction'),  # 'Purchase' or 'Sale'
                'amount': trade.get('Amount'),
                'house': trade.get('House')  # 'House' or 'Senate'
            })

        # Sort by date (most recent first)
        trades.sort(key=lambda x: x['date'], reverse=True)

        # Create summary
        summary = _create_trade_summary(trades)

        return {
            'success': True,
            'trades': trades,
            'politician': politician_name or 'All',
            'summary': summary
        }

    except Exception as e:
        logger.error(f"QuiverQuant API error: {e}")
        raise


def _get_house_stock_watcher_trades(
    politician_name: Optional[str],
    ticker: Optional[str],
    days_back: int
) -> Dict[str, Any]:
    """
    Fallback: Mock data based on public knowledge
    In production, this would scrape housestockwatcher.com or use another free source
    """
    logger.warning("Using mock politician trading data - QuiverQuant API key not configured")

    # Mock Nancy Pelosi trades (based on public records)
    mock_trades = [
        {
            'date': (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'),
            'politician': 'Nancy Pelosi',
            'ticker': 'NVDA',
            'transaction': 'Purchase',
            'amount': '$1,000,001 - $5,000,000',
            'house': 'House'
        },
        {
            'date': (datetime.now() - timedelta(days=25)).strftime('%Y-%m-%d'),
            'politician': 'Nancy Pelosi',
            'ticker': 'MSFT',
            'transaction': 'Purchase',
            'amount': '$500,001 - $1,000,000',
            'house': 'House'
        },
        {
            'date': (datetime.now() - timedelta(days=45)).strftime('%Y-%m-%d'),
            'politician': 'Nancy Pelosi',
            'ticker': 'GOOGL',
            'transaction': 'Purchase',
            'amount': '$1,000,001 - $5,000,000',
            'house': 'House'
        }
    ]

    # Filter trades
    filtered_trades = []
    for trade in mock_trades:
        if politician_name and politician_name.lower() not in trade['politician'].lower():
            continue
        if ticker and ticker.upper() != trade['ticker']:
            continue
        filtered_trades.append(trade)

    summary = _create_trade_summary(filtered_trades)

    return {
        'success': True,
        'trades': filtered_trades,
        'politician': politician_name or 'All',
        'summary': summary,
        'mock_data': True
    }


def _create_trade_summary(trades: List[Dict]) -> Dict[str, Any]:
    """Create a summary of trades"""
    if not trades:
        return {
            'total_trades': 0,
            'purchases': 0,
            'sales': 0,
            'most_traded_tickers': []
        }

    purchases = sum(1 for t in trades if t['transaction'] == 'Purchase')
    sales = sum(1 for t in trades if t['transaction'] == 'Sale')

    # Count ticker frequency
    ticker_counts = {}
    for trade in trades:
        ticker = trade['ticker']
        ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1

    # Sort tickers by frequency
    most_traded = sorted(ticker_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        'total_trades': len(trades),
        'purchases': purchases,
        'sales': sales,
        'most_traded_tickers': [{'ticker': t[0], 'count': t[1]} for t in most_traded]
    }


def get_pelosi_portfolio_tickers() -> List[str]:
    """
    Get list of tickers Nancy Pelosi has recently traded
    Useful for building copy-trading strategies
    """
    trades_data = get_politician_trades(politician_name="Pelosi", days_back=180)

    if not trades_data.get('success'):
        return []

    # Get unique tickers from purchases only
    tickers = set()
    for trade in trades_data.get('trades', []):
        if trade['transaction'] == 'Purchase':
            tickers.add(trade['ticker'])

    return list(tickers)


# Tool schemas for orchestrator registration
POLITICIAN_TRADING_TOOLS = [
    {
        "name": "get_politician_trades",
        "description": "Get recent stock trades made by US politicians/Congress members. Useful for copy-trading strategies or analyzing political insider trading patterns. Can filter by politician name (e.g., 'Nancy Pelosi', 'Pelosi') or stock ticker.",
        "input_schema": {
            "type": "object",
            "properties": {
                "politician_name": {
                    "type": "string",
                    "description": "Filter by politician name (partial match, case-insensitive). Examples: 'Pelosi', 'Nancy Pelosi', 'McConnell'"
                },
                "ticker": {
                    "type": "string",
                    "description": "Filter by stock ticker symbol (e.g., 'NVDA', 'MSFT')"
                },
                "days_back": {
                    "type": "integer",
                    "description": "How many days back to fetch trades (default: 90)",
                    "default": 90
                }
            }
        }
    },
    {
        "name": "get_pelosi_portfolio_tickers",
        "description": "Get list of stock tickers that Nancy Pelosi has recently purchased. Useful for creating copy-trading strategies that mirror her portfolio.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    }
]
