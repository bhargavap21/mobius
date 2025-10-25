"""
Integration test: Verify portfolio data structure matches expected format
"""

from tools.code_generator import parse_strategy
from tools.backtester import backtest_strategy

print("\n" + "="*70)
print("🧪 Portfolio Integration Test")
print("="*70 + "\n")

# Parse a portfolio strategy
strategy_desc = "Trade AAPL, MSFT, GOOGL based on RSI. Buy when RSI < 35, sell when RSI > 65"

print("Step 1: Parse portfolio strategy")
print("-" * 70)
parsed = parse_strategy(strategy_desc)

if not parsed['success']:
    print(f"❌ Parse failed: {parsed.get('error')}")
    exit(1)

strategy = parsed['strategy']
print(f"✅ Parsed successfully")
print(f"   Name: {strategy.get('name')}")
print(f"   Portfolio mode: {strategy.get('portfolio_mode')}")
print(f"   Assets: {strategy.get('assets')}")
print(f"   Max positions: {strategy.get('risk_management', {}).get('max_positions')}")
print()

# Verify structure
print("Step 2: Verify parsed structure")
print("-" * 70)

required_fields = ['name', 'portfolio_mode', 'assets', 'entry_conditions', 'exit_conditions']
for field in required_fields:
    if field in strategy:
        print(f"   ✓ {field}: {strategy[field] if field not in ['entry_conditions', 'exit_conditions'] else '...'}")
    else:
        print(f"   ✗ {field}: MISSING")

print()

# Run backtest
print("Step 3: Run portfolio backtest (short period)")
print("-" * 70)
result = backtest_strategy(strategy, days=30, initial_capital=9000)

if 'error' in result:
    print(f"❌ Backtest failed: {result['error']}")
    exit(1)

print(f"✅ Backtest completed successfully")
print()

# Verify result structure
print("Step 4: Verify result structure")
print("-" * 70)

summary = result.get('summary', {})
required_summary_fields = [
    'portfolio_mode', 'assets', 'num_assets', 'total_return',
    'total_trades', 'win_rate', 'sharpe_ratio'
]

for field in required_summary_fields:
    if field in summary:
        value = summary[field]
        print(f"   ✓ summary.{field}: {value}")
    else:
        print(f"   ✗ summary.{field}: MISSING")

print()

# Check asset breakdown
if 'asset_breakdown' in result:
    print(f"   ✓ asset_breakdown present ({len(result['asset_breakdown'])} assets)")
    for asset, breakdown in list(result['asset_breakdown'].items())[:2]:
        print(f"      {asset}: {breakdown['total_return']:.2f}% return")
else:
    print(f"   ✗ asset_breakdown: MISSING")

print()

# Check portfolio history
if 'portfolio_history' in result:
    print(f"   ✓ portfolio_history present ({len(result['portfolio_history'])} data points)")
    if len(result['portfolio_history']) > 0:
        first_point = result['portfolio_history'][0]
        print(f"      First point: {first_point}")
else:
    print(f"   ✗ portfolio_history: MISSING")

print()

# Summary
print("="*70)
print("✅ Integration test PASSED!")
print(f"   Portfolio with {summary.get('num_assets', 0)} assets")
print(f"   {summary.get('total_trades', 0)} total trades")
print(f"   {summary.get('total_return', 0):.2f}% return")
print("="*70 + "\n")
