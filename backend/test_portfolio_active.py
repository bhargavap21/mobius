"""
Test portfolio with more active trading thresholds
"""

from tools.code_generator import parse_strategy
from tools.backtester import backtest_strategy

print("\n" + "="*70)
print("🎯 Testing Active Multi-Asset Portfolio")
print("="*70 + "\n")

# More aggressive RSI thresholds to trigger trades
print("Portfolio: TSLA, AAPL, MSFT with RSI 40/60")
print("-" * 70)

strategy_desc = "Trade TSLA, AAPL, and MSFT. Buy when RSI is below 40, sell when RSI is above 60"

parsed = parse_strategy(strategy_desc)

if parsed['success']:
    strategy = parsed['strategy']

    # Manually adjust thresholds for more active trading
    strategy['entry_conditions']['parameters']['rsi_threshold'] = 40
    strategy['entry_conditions']['parameters']['rsi_exit_threshold'] = 60

    print(f"✅ Strategy: {strategy['name']}")
    print(f"   Portfolio: {strategy.get('assets')}")
    print(f"   Entry: RSI < {strategy['entry_conditions']['parameters']['rsi_threshold']}")
    print(f"   Exit: RSI > {strategy['entry_conditions']['parameters']['rsi_exit_threshold']}")
    print()

    # Run backtest
    print("Running backtest (180 days)...")
    result = backtest_strategy(strategy, days=180, initial_capital=10000)

    if 'error' not in result:
        summary = result['summary']
        print(f"\n📊 Portfolio Results:")
        print(f"   Assets: {summary.get('num_assets', 'N/A')} stocks")
        print(f"   Total Return: {summary['total_return']:.2f}%")
        print(f"   Buy & Hold: {summary['buy_hold_return']:.2f}%")
        print(f"   Alpha: {summary['total_return'] - summary['buy_hold_return']:.2f}%")
        print(f"   Total Trades: {summary['total_trades']}")
        print(f"   Win Rate: {summary['win_rate']:.2f}%")
        print(f"   Sharpe Ratio: {summary['sharpe_ratio']:.2f}")

        # Show breakdown per asset
        if 'asset_breakdown' in result:
            print(f"\n   📈 Performance by Asset:")
            print(f"   {'Asset':<8} {'Return':>8} {'Trades':>7} {'Win Rate':>10} {'Final $':>10}")
            print(f"   {'-'*8} {'-'*8} {'-'*7} {'-'*10} {'-'*10}")
            for asset, breakdown in result['asset_breakdown'].items():
                print(f"   {asset:<8} {breakdown['total_return']:>+7.2f}% {breakdown['total_trades']:>7} {breakdown['win_rate']:>9.1f}% ${breakdown['final_capital']:>9.2f}")

        # Show sample trades
        if 'trades' in result and len(result['trades']) > 0:
            print(f"\n   📝 Recent Trades (last 10):")
            print(f"   {'Asset':<8} {'Entry Date':<12} {'Exit Date':<12} {'P&L':>8} {'Reason':<30}")
            print(f"   {'-'*8} {'-'*12} {'-'*12} {'-'*8} {'-'*30}")
            for trade in result['trades'][-10:]:
                asset = trade.get('asset', trade.get('symbol', 'N/A'))
                entry = trade['entry_date']
                exit = trade['exit_date']
                pnl = trade['pnl_pct']
                reason = trade['exit_reason'][:28]
                print(f"   {asset:<8} {entry:<12} {exit:<12} {pnl:>+7.2f}% {reason:<30}")

        print(f"\n✅ Portfolio backtest complete!")
    else:
        print(f"❌ Backtest failed: {result.get('error')}")
else:
    print(f"❌ Parse failed: {parsed.get('error')}")

print("\n" + "="*70 + "\n")
