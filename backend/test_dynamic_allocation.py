"""
Test Phase 2: Signal-weighted dynamic allocation
Tests trending stock selection and weighted capital allocation
"""

from tools.code_generator import parse_strategy
from tools.social_media import get_trending_stocks_reddit

print("\n" + "="*70)
print("🎯 Testing Phase 2: Signal-Weighted Dynamic Allocation")
print("="*70 + "\n")

# Test 1: Get trending stocks from Reddit
print("Test 1: Get trending stocks from r/wallstreetbets")
print("-" * 70)

trending = get_trending_stocks_reddit(
    subreddit="wallstreetbets",
    limit=100,
    top_n=5,
    min_mentions=2
)

if trending['success']:
    print(f"✅ Found {len(trending['trending_stocks'])} trending stocks")
    print(f"\n📊 Top Trending Stocks:")
    print(f"{'Rank':<6} {'Ticker':<8} {'Mentions':>10} {'Sentiment':>10} {'Score':>12}")
    print("-" * 70)

    for i, stock in enumerate(trending['trending_stocks'], 1):
        print(f"{i:<6} {stock['ticker']:<8} {stock['mentions']:>10} {stock['avg_sentiment']:>10.3f} {stock['weighted_score']:>12.2f}")

    print(f"\n💡 Capital Allocation (if $10,000):")
    total_score = sum(s['weighted_score'] for s in trending['trending_stocks'])
    for stock in trending['trending_stocks']:
        weight = stock['weighted_score'] / total_score
        allocation = 10000 * weight
        print(f"   {stock['ticker']:<6} → ${allocation:>8,.2f} ({weight*100:>5.1f}%)")
else:
    print(f"❌ Failed to get trending stocks: {trending.get('error')}")

print("\n" + "="*70 + "\n")

# Test 2: Parse dynamic portfolio strategy
print("Test 2: Parse 'trending stocks' strategy")
print("-" * 70)

strategy_desc = "Trade the top 5 trending stocks on wallstreetbets. Allocate more capital to stocks with higher sentiment. Buy when sentiment is positive, sell when negative."

parsed = parse_strategy(strategy_desc)

if parsed['success']:
    strategy = parsed['strategy']
    print(f"✅ Strategy parsed successfully")
    print(f"\n📋 Strategy Details:")
    print(f"   Name: {strategy.get('name')}")
    print(f"   Portfolio mode: {strategy.get('portfolio_mode')}")
    print(f"   Dynamic selection: {strategy.get('risk_management', {}).get('dynamic_selection')}")
    print(f"   Top N: {strategy.get('risk_management', {}).get('top_n')}")
    print(f"   Allocation: {strategy.get('risk_management', {}).get('allocation')}")
    print(f"   Assets (should be null): {strategy.get('assets')}")
    print(f"   Signal: {strategy['entry_conditions']['signal']}")
    print(f"   Source: {strategy['entry_conditions']['parameters'].get('source')}")
else:
    print(f"❌ Parse failed: {parsed.get('error')}")

print("\n" + "="*70 + "\n")

# Test 3: Parse static portfolio with signal weighting
print("Test 3: Parse 'signal-weighted' static portfolio")
print("-" * 70)

strategy_desc_2 = "Trade GME, AMC, and BBBY based on wallstreetbets sentiment. Allocate more capital to stocks with higher sentiment."

parsed = parse_strategy(strategy_desc_2)

if parsed['success']:
    strategy = parsed['strategy']
    print(f"✅ Strategy parsed successfully")
    print(f"\n📋 Strategy Details:")
    print(f"   Name: {strategy.get('name')}")
    print(f"   Portfolio mode: {strategy.get('portfolio_mode')}")
    print(f"   Assets: {strategy.get('assets')}")
    print(f"   Allocation: {strategy.get('risk_management', {}).get('allocation')}")
    print(f"   Dynamic selection: {strategy.get('risk_management', {}).get('dynamic_selection')}")
else:
    print(f"❌ Parse failed: {parsed.get('error')}")

print("\n" + "="*70)
print("✅ Dynamic allocation tests complete!")
print("="*70 + "\n")
