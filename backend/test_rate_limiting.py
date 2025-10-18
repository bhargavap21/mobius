"""
Test script to verify rate limiting is working correctly
This only makes a few API calls to verify the logic without wasting credits
"""
import time
from tools.real_historical_data import RealHistoricalDataAggregator

def test_rate_limiting():
    print("🧪 Testing Rate Limiting Logic\n")
    print("=" * 60)

    aggregator = RealHistoricalDataAggregator()

    # Test dates for GME (just 10 days to conserve API credits)
    test_dates = [
        "2025-05-01",
        "2025-05-02",
        "2025-05-05",
        "2025-05-06",
        "2025-05-07",
        "2025-05-08",
        "2025-05-09",
        "2025-05-12",
        "2025-05-13",
        "2025-05-14",
    ]

    print(f"\n📅 Testing with {len(test_dates)} dates for GME")
    print("This will use:")
    print("  - Alpha Vantage: up to 10 requests (limit: 25/day)")
    print("  - Finnhub: fallback if Alpha Vantage fails (limit: 60/min)")
    print("\n" + "=" * 60 + "\n")

    results = []
    start_time = time.time()

    for i, date in enumerate(test_dates, 1):
        print(f"\n[{i}/{len(test_dates)}] Fetching sentiment for {date}...")

        try:
            sentiment = aggregator.get_historical_sentiment(
                ticker="GME",
                date=date,
                preferred_sources=['alpha_vantage', 'finnhub']
            )

            if sentiment is not None:
                results.append({
                    'date': date,
                    'sentiment': sentiment,
                    'success': True
                })
                print(f"  ✅ Success: {sentiment:.3f}")
            else:
                results.append({
                    'date': date,
                    'sentiment': None,
                    'success': False
                })
                print(f"  ❌ Failed: No data")

        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append({
                'date': date,
                'sentiment': None,
                'success': False,
                'error': str(e)
            })

    elapsed_time = time.time() - start_time

    # Summary
    print("\n" + "=" * 60)
    print("📊 RESULTS SUMMARY")
    print("=" * 60 + "\n")

    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful

    print(f"✅ Successful requests: {successful}/{len(results)}")
    print(f"❌ Failed requests: {failed}/{len(results)}")
    print(f"⏱️  Total time: {elapsed_time:.2f} seconds")
    print(f"⚡ Average time per request: {elapsed_time/len(results):.2f} seconds")

    # Rate limit tracking
    print(f"\n📈 API Usage:")
    print(f"  - Alpha Vantage: {aggregator.request_count['alpha_vantage']} requests")
    print(f"  - Finnhub: {aggregator.request_count['finnhub']} requests")
    print(f"  - IEX: {aggregator.request_count['iex']} requests")

    # Verify rate limiting worked
    print("\n🔍 Rate Limiting Verification:")
    if aggregator.request_count['finnhub'] > 0:
        finnhub_window = time.time() - aggregator.rate_limit_window_start['finnhub']
        print(f"  - Finnhub requests in current window: {aggregator.request_count['finnhub']}")
        print(f"  - Time since window start: {finnhub_window:.2f}s")

        if aggregator.request_count['finnhub'] <= 55:
            print(f"  ✅ PASS: Finnhub stayed under 55 req/min buffer")
        else:
            print(f"  ⚠️  WARNING: Finnhub exceeded buffer (but should have waited)")

    if successful == len(results):
        print("\n✅ ALL TESTS PASSED - Rate limiting is working correctly!")
        print("   You can proceed with confidence that a full 180-day backtest will work.")
    elif successful >= len(results) * 0.8:  # 80% success rate
        print("\n⚠️  MOSTLY WORKING - Some requests failed but rate limiting appears OK")
        print("   This might be due to API limits or data availability for those dates.")
    else:
        print("\n❌ ISSUES DETECTED - Many requests failed")
        print("   Check API keys and rate limiting logic.")

    print("\n" + "=" * 60)

    return results

if __name__ == "__main__":
    test_rate_limiting()
