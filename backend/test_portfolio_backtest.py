"""
Test multi-asset portfolio backtest functionality
Tests Phase 1: Equal-weight portfolio with various signal types
"""

import sys
import os
from datetime import datetime, timedelta

from tools.code_generator import parse_strategy
from tools.backtester import backtest_strategy

print("\n" + "="*70)
print("🎯 Testing Multi-Asset Portfolio Backtesting (Phase 1)")
print("="*70 + "\n")

# Test 1: Portfolio with RSI strategy
print("Test 1: RSI-based portfolio (TSLA, AAPL, NVDA)")
print("-" * 70)

strategy_desc_1 = "Trade TSLA, AAPL, and NVDA. Buy when RSI is below 30, sell when RSI is above 70"

parsed = parse_strategy(strategy_desc_1)

if parsed['success']:
    strategy = parsed['strategy']
    print(f"✅ Strategy parsed successfully")
    print(f"   Portfolio mode: {strategy.get('portfolio_mode')}")
    print(f"   Assets: {strategy.get('assets')}")
    print(f"   Signal: {strategy['entry_conditions']['signal']}")
    print()

    # Run backtest
    print("Running backtest...")
    result = backtest_strategy(strategy, days=180, initial_capital=10000)

    if 'error' not in result:
        summary = result['summary']
        print(f"\n📊 Portfolio Results:")
        print(f"   Total Return: {summary['total_return']:.2f}%")
        print(f"   Buy & Hold: {summary['buy_hold_return']:.2f}%")
        print(f"   Total Trades: {summary['total_trades']}")
        print(f"   Win Rate: {summary['win_rate']:.2f}%")
        print(f"   Sharpe Ratio: {summary['sharpe_ratio']:.2f}")
        print(f"   Max Drawdown: {summary['max_drawdown']:.2f}%")

        # Show breakdown per asset
        if 'asset_breakdown' in result:
            print(f"\n   Asset Breakdown:")
            for asset, breakdown in result['asset_breakdown'].items():
                print(f"      {asset}: {breakdown['total_return']:.2f}% ({breakdown['total_trades']} trades)")
    else:
        print(f"❌ Backtest failed: {result['error']}")
else:
    print(f"❌ Parse failed: {parsed['error']}")

print("\n" + "="*70 + "\n")

# Test 2: Portfolio with sentiment strategy
print("Test 2: Sentiment-based portfolio (GME, AMC)")
print("-" * 70)

strategy_desc_2 = "Create a portfolio of GME and AMC based on wallstreetbets sentiment. Buy when sentiment is above 0.1, sell when below -0.1"

parsed = parse_strategy(strategy_desc_2)

if parsed['success']:
    strategy = parsed['strategy']
    print(f"✅ Strategy parsed successfully")
    print(f"   Portfolio mode: {strategy.get('portfolio_mode')}")
    print(f"   Assets: {strategy.get('assets')}")
    print(f"   Signal: {strategy['entry_conditions']['signal']}")
    print(f"   Source: {strategy['entry_conditions']['parameters'].get('source')}")
    print()

    # Run backtest
    print("Running backtest...")
    result = backtest_strategy(strategy, days=180, initial_capital=10000)

    if 'error' not in result:
        summary = result['summary']
        print(f"\n📊 Portfolio Results:")
        print(f"   Total Return: {summary['total_return']:.2f}%")
        print(f"   Buy & Hold: {summary['buy_hold_return']:.2f}%")
        print(f"   Total Trades: {summary['total_trades']}")
        print(f"   Win Rate: {summary['win_rate']:.2f}%")

        # Show breakdown per asset
        if 'asset_breakdown' in result:
            print(f"\n   Asset Breakdown:")
            for asset, breakdown in result['asset_breakdown'].items():
                print(f"      {asset}: {breakdown['total_return']:.2f}% ({breakdown['total_trades']} trades)")
    else:
        print(f"❌ Backtest failed: {result['error']}")
else:
    print(f"❌ Parse failed: {parsed['error']}")

print("\n" + "="*70 + "\n")

# Test 3: Single stock strategy (backward compatibility)
print("Test 3: Single stock strategy - backward compatibility (BYND)")
print("-" * 70)

strategy_desc_3 = "Buy BYND when wallstreetbets sentiment is positive (above 0.05), sell when negative (below -0.05)"

parsed = parse_strategy(strategy_desc_3)

if parsed['success']:
    strategy = parsed['strategy']
    print(f"✅ Strategy parsed successfully")
    print(f"   Portfolio mode: {strategy.get('portfolio_mode')}")
    print(f"   Asset: {strategy.get('asset')}")
    print(f"   Assets list: {strategy.get('assets')}")
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
        print(f"   Win Rate: {summary['win_rate']:.2f}%")
    else:
        print(f"❌ Backtest failed: {result['error']}")
else:
    print(f"❌ Parse failed: {parsed['error']}")

print("\n" + "="*70)
print("✅ Portfolio backtest testing complete!")
print("="*70 + "\n")
