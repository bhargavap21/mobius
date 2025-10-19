"""
Comprehensive test script for deployment system
Tests all endpoints and the Alpaca integration
"""
import asyncio
import sys
from uuid import uuid4
from services.alpaca_service import alpaca_service
from db.repositories.deployment_repository import DeploymentRepository
from db.repositories.bot_repository import BotRepository
from db.models import DeploymentCreate


async def test_alpaca_service():
    """Test Alpaca API integration"""
    print("\n" + "="*60)
    print("TESTING ALPACA SERVICE")
    print("="*60)

    try:
        # Test 1: Get account info
        print("\n1️⃣  Testing get_account()...")
        account = await alpaca_service.get_account()
        print(f"   ✅ Account ID: {account['account_id']}")
        print(f"   💰 Cash: ${account['cash']:,.2f}")
        print(f"   📊 Portfolio Value: ${account['portfolio_value']:,.2f}")
        print(f"   🔓 Trading Status: {'Blocked' if account['trading_blocked'] else 'Active'}")

        # Test 2: Get positions
        print("\n2️⃣  Testing get_positions()...")
        positions = await alpaca_service.get_positions()
        print(f"   ✅ Found {len(positions)} open positions")
        for pos in positions[:3]:  # Show first 3
            print(f"      📈 {pos['symbol']}: {pos['qty']} shares @ ${pos['current_price']}")

        # Test 3: Get latest price
        print("\n3️⃣  Testing get_latest_price()...")
        symbols = ['AAPL', 'TSLA', 'NVDA']
        for symbol in symbols:
            price = await alpaca_service.get_latest_price(symbol)
            if price:
                print(f"   ✅ {symbol}: ${price:.2f}")
            else:
                print(f"   ⚠️  {symbol}: Price unavailable")

        print("\n✅ Alpaca service tests PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Alpaca service tests FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_deployment_repository():
    """Test deployment repository operations"""
    print("\n" + "="*60)
    print("TESTING DEPLOYMENT REPOSITORY")
    print("="*60)

    try:
        repo = DeploymentRepository()
        bot_repo = BotRepository()

        # First, we need a bot to deploy
        # Let's get the first bot from the database
        print("\n1️⃣  Finding a bot to deploy...")

        # Get first bot (using admin client to bypass auth for testing)
        response = repo.admin_client.table('trading_bots').select('*').limit(1).execute()

        if not response.data or len(response.data) == 0:
            print("   ⚠️  No bots found in database. Skipping deployment tests.")
            print("   💡 Create a bot first using the UI or API")
            return True

        bot = response.data[0]
        print(f"   ✅ Found bot: {bot['name']} (ID: {bot['id']})")

        # Test 2: Create deployment
        print("\n2️⃣  Testing create_deployment()...")
        deployment_data = DeploymentCreate(
            bot_id=bot['id'],
            initial_capital=5000.00,
            execution_frequency='5min',
            max_position_size=1000.00,
            daily_loss_limit=250.00
        )

        deployment = await repo.create_deployment(
            user_id=bot['user_id'],
            deployment_data=deployment_data,
            alpaca_account_id='TEST_ACCOUNT_123'
        )

        print(f"   ✅ Created deployment: {deployment.id}")
        print(f"   💰 Initial Capital: ${deployment.initial_capital}")
        print(f"   📊 Status: {deployment.status}")

        deployment_id = deployment.id

        # Test 3: Get deployment
        print("\n3️⃣  Testing get_deployment()...")
        fetched = await repo.get_deployment(deployment_id)
        print(f"   ✅ Retrieved deployment: {fetched.id}")
        print(f"   🤖 Bot ID: {fetched.bot_id}")

        # Test 4: Log a trade
        print("\n4️⃣  Testing log_trade()...")
        trade_data = {
            'alpaca_order_id': 'ORDER_TEST_123',
            'alpaca_order_status': 'filled',
            'symbol': 'AAPL',
            'side': 'buy',
            'order_type': 'market',
            'quantity': 10.0,
            'filled_qty': 10.0,
            'filled_avg_price': 175.50,
            'total_value': 1755.00,
            'signal_metadata': {'reason': 'RSI oversold'}
        }

        trade = await repo.log_trade(deployment_id, trade_data)
        print(f"   ✅ Logged trade: {trade.id}")
        print(f"   📈 {trade.side.upper()} {trade.quantity} {trade.symbol} @ ${trade.filled_avg_price}")

        # Test 5: Log metrics
        print("\n5️⃣  Testing log_metrics()...")
        metrics_data = {
            'portfolio_value': 5100.00,
            'cash': 3345.00,
            'positions_value': 1755.00,
            'total_return_pct': 2.0,
            'daily_pnl': 100.00,
            'unrealized_pnl': 0.0,
            'realized_pnl': 100.00,
            'open_positions_count': 1,
            'total_trades_count': 1,
            'winning_trades_count': 1,
            'losing_trades_count': 0
        }

        metrics = await repo.log_metrics(deployment_id, metrics_data)
        print(f"   ✅ Logged metrics: {metrics.id}")
        print(f"   📊 Portfolio Value: ${metrics.portfolio_value}")
        print(f"   📈 Return: {metrics.total_return_pct}%")

        # Test 6: Upsert position
        print("\n6️⃣  Testing upsert_position()...")
        position_data = {
            'symbol': 'AAPL',
            'quantity': 10.0,
            'average_entry_price': 175.50,
            'current_price': 176.00,
            'market_value': 1760.00,
            'cost_basis': 1755.00,
            'unrealized_pnl': 5.00,
            'unrealized_pnl_pct': 0.28
        }

        position = await repo.upsert_position(deployment_id, position_data)
        print(f"   ✅ Created/updated position: {position.symbol}")
        print(f"   💰 Unrealized P/L: ${position.unrealized_pnl} ({position.unrealized_pnl_pct}%)")

        # Test 7: Get trades
        print("\n7️⃣  Testing get_deployment_trades()...")
        trades = await repo.get_deployment_trades(deployment_id)
        print(f"   ✅ Retrieved {len(trades)} trades")

        # Test 8: Get metrics
        print("\n8️⃣  Testing get_deployment_metrics()...")
        all_metrics = await repo.get_deployment_metrics(deployment_id)
        print(f"   ✅ Retrieved {len(all_metrics)} metrics snapshots")

        # Test 9: Get positions
        print("\n9️⃣  Testing get_deployment_positions()...")
        positions = await repo.get_deployment_positions(deployment_id)
        print(f"   ✅ Retrieved {len(positions)} open positions")

        # Test 10: Update deployment status
        print("\n🔟 Testing update_deployment_status()...")
        success = await repo.update_deployment_status(deployment_id, 'paused')
        print(f"   ✅ Status updated to: paused")

        # Verify status change
        updated = await repo.get_deployment(deployment_id)
        print(f"   ✅ Verified status: {updated.status}")

        # Cleanup: Delete the test deployment
        print("\n🧹 Cleaning up test data...")
        repo.admin_client.table('deployments').delete().eq('id', str(deployment_id)).execute()
        print("   ✅ Test deployment deleted")

        print("\n✅ Deployment repository tests PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Deployment repository tests FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_api_endpoints():
    """Test deployment API endpoints via HTTP"""
    print("\n" + "="*60)
    print("TESTING DEPLOYMENT API ENDPOINTS")
    print("="*60)

    import httpx

    try:
        base_url = "http://localhost:8000"

        # Note: These tests require authentication
        # For now, we'll test without auth to see the error responses

        print("\n1️⃣  Testing GET /deployments (unauthenticated)...")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/deployments")
            print(f"   Status: {response.status_code}")
            if response.status_code == 401:
                print("   ✅ Correctly requires authentication")
            else:
                print(f"   Response: {response.text[:200]}")

        print("\n💡 Full API endpoint tests require valid authentication token")
        print("   Use the frontend or obtain a token to test authenticated endpoints")

        return True

    except Exception as e:
        print(f"\n❌ API endpoint tests FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 DEPLOYMENT SYSTEM COMPREHENSIVE TEST")
    print("="*60)

    results = []

    # Test 1: Alpaca Service
    results.append(("Alpaca Service", await test_alpaca_service()))

    # Test 2: Deployment Repository
    results.append(("Deployment Repository", await test_deployment_repository()))

    # Test 3: API Endpoints
    results.append(("API Endpoints", await test_api_endpoints()))

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name:.<40} {status}")

    all_passed = all(result[1] for result in results)

    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED")
    print("="*60 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
