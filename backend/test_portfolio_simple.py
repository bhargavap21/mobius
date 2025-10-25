"""
Simple test for multi-asset portfolio backtest (RSI only - fast)
"""

import sys
import os
from datetime import datetime, timedelta

from tools.code_generator import parse_strategy
from tools.backtester import backtest_strategy

print("\n" + "="*70)
print("🎯 Testing Multi-Asset Portfolio Backtesting")
print("="*70 + "\n")

# Test 1: Portfolio with RSI strategy (3 stocks)
print("Test 1: RSI-based portfolio (TSLA, AAPL, NVDA)")
print("-" * 70)

strategy_desc = "Trade TSLA, AAPL, and NVDA. Buy when RSI is below 30, sell when RSI is above 70"

parsed = parse_strategy(strategy_desc)

if parsed['success']:
    strategy = parsed['strategy']
    print(f"✅ Strategy parsed successfully")
    print(f"   Portfolio mode: {strategy.get('portfolio_mode')}")
    print(f"   Assets: {strategy.get('assets')}")
    print(f"   Max positions: {strategy.get('risk_management', {}).get('max_positions')}")
    print(f"   Signal: {strategy['entry_conditions']['signal']}")
    print()

    # Run backtest
    print("Running backtest (180 days)...")
    result = backtest_strategy(strategy, days=180, initial_capital=10000)

    if 'error' not in result:
        summary = result['summary']
        print(f"\n📊 Portfolio Results:")
        print(f"   Portfolio Mode: {summary.get('portfolio_mode', False)}")
        print(f"   Number of Assets: {summary.get('num_assets', 'N/A')}")
        print(f"   Total Return: {summary['total_return']:.2f}%")
        print(f"   Buy & Hold: {summary['buy_hold_return']:.2f}%")
        print(f"   Alpha: {summary['total_return'] - summary['buy_hold_return']:.2f}%")
        print(f"   Total Trades: {summary['total_trades']}")
        print(f"   Win Rate: {summary['win_rate']:.2f}%")
        print(f"   Sharpe Ratio: {summary['sharpe_ratio']:.2f}")
        print(f"   Max Drawdown: {summary['max_drawdown']:.2f}%")

        # Show breakdown per asset
        if 'asset_breakdown' in result:
            print(f"\n   📈 Performance by Asset:")
            for asset, breakdown in result['asset_breakdown'].items():
                print(f"      {asset:6} → {breakdown['total_return']:+7.2f}% ({breakdown['total_trades']:2} trades, {breakdown['win_rate']:.1f}% win rate)")

        # Show sample trades
        if 'trades' in result and len(result['trades']) > 0:
            print(f"\n   📝 Sample Trades (first 5):")
            for trade in result['trades'][:5]:
                asset = trade.get('asset', trade.get('symbol', 'N/A'))
                print(f"      {asset:6} | {trade['entry_date']} → {trade['exit_date']} | {trade['pnl_pct']:+6.2f}% | {trade['exit_reason']}")

        print(f"\n✅ Portfolio backtest successful!")
    else:
        print(f"❌ Backtest failed: {result.get('error')}")
else:
    print(f"❌ Parse failed: {parsed.get('error')}")

print("\n" + "="*70 + "\n")

# Test 2: Single stock (backward compatibility)
print("Test 2: Single stock strategy - backward compatibility (AAPL)")
print("-" * 70)

strategy_desc_2 = "Buy AAPL when RSI < 30, sell when RSI > 70"

parsed = parse_strategy(strategy_desc_2)

if parsed['success']:
    strategy = parsed['strategy']
    print(f"✅ Strategy parsed successfully")
    print(f"   Portfolio mode: {strategy.get('portfolio_mode')}")
    print(f"   Asset: {strategy.get('asset')}")
    print()

    # Run backtest
    print("Running backtest...")
    result = backtest_strategy(strategy, days=180, initial_capital=10000)

    if 'error' not in result:
        summary = result['summary']
        print(f"\n📊 Single Stock Results:")
        print(f"   Symbol: {summary.get('symbol', 'N/A')}")
        print(f"   Total Return: {summary['total_return']:.2f}%")
        print(f"   Buy & Hold: {summary['buy_hold_return']:.2f}%")
        print(f"   Total Trades: {summary['total_trades']}")

        print(f"\n✅ Single stock backtest successful (backward compatible)!")
    else:
        print(f"❌ Backtest failed: {result.get('error')}")
else:
    print(f"❌ Parse failed: {parsed.get('error')}")

print("\n" + "="*70)
print("✅ All tests complete!")
print("="*70 + "\n")
