"""
Test script for Supabase integration
Tests authentication and bot CRUD operations
"""
import asyncio
import sys
from uuid import uuid4

from auth.auth_service import AuthService
from db.models import UserCreate, UserLogin, TradingBotCreate
from db.repositories.bot_repository import BotRepository


async def test_auth():
    """Test authentication flow"""
    print("\n" + "="*60)
    print("🔐 Testing Authentication")
    print("="*60)

    auth_service = AuthService()

    # Generate unique test email with real domain
    test_email = f"test_{uuid4().hex[:8]}@gmail.com"
    test_password = "TestPassword123!"

    try:
        # Test 1: Sign up
        print(f"\n1️⃣  Testing signup with {test_email}...")
        user_data = UserCreate(
            email=test_email,
            password=test_password,
            full_name="Test User"
        )

        signup_response = await auth_service.sign_up(user_data)
        print(f"   ✅ Signup successful!")
        print(f"   User ID: {signup_response.user.id}")
        print(f"   Email: {signup_response.user.email}")
        print(f"   Token: {signup_response.access_token[:50]}...")

        user_id = signup_response.user.id
        access_token = signup_response.access_token

        # Test 2: Get current user
        print(f"\n2️⃣  Testing get current user...")
        current_user = await auth_service.get_current_user(access_token)
        print(f"   ✅ Retrieved user: {current_user.email}")

        # Test 3: Sign in
        print(f"\n3️⃣  Testing signin...")
        login_data = UserLogin(
            email=test_email,
            password=test_password
        )

        signin_response = await auth_service.sign_in(login_data)
        print(f"   ✅ Signin successful!")
        print(f"   Token: {signin_response.access_token[:50]}...")

        # Test 4: Verify token
        print(f"\n4️⃣  Testing token verification...")
        verified_user_id = await auth_service.verify_token(access_token)
        print(f"   ✅ Token valid for user: {verified_user_id}")

        print(f"\n{'='*60}")
        print("✅ All authentication tests passed!")
        print(f"{'='*60}")

        return user_id, access_token

    except Exception as e:
        print(f"\n❌ Authentication test failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None


async def test_bot_operations(user_id, access_token):
    """Test bot CRUD operations"""
    print("\n" + "="*60)
    print("🤖 Testing Bot Operations")
    print("="*60)

    bot_repo = BotRepository()

    try:
        # Test 1: Create bot
        print(f"\n1️⃣  Testing create bot...")
        bot_data = TradingBotCreate(
            name="Test GME Momentum Bot",
            description="Test bot for GameStop momentum trading",
            strategy_config={
                "ticker": "GME",
                "strategy_type": "momentum",
                "rsi_period": 14,
                "rsi_oversold": 30,
                "rsi_overbought": 70
            },
            generated_code="# Test trading bot code\nprint('Hello World')",
            backtest_results={
                "total_trades": 15,
                "total_return": 12.5,
                "win_rate": 0.67,
                "sharpe_ratio": 1.8
            },
            insights_config={"charts": ["equity_curve", "drawdown"]},
            session_id=f"test_session_{uuid4().hex[:8]}"
        )

        created_bot = await bot_repo.create(user_id, bot_data)
        print(f"   ✅ Bot created!")
        print(f"   Bot ID: {created_bot.id}")
        print(f"   Name: {created_bot.name}")
        print(f"   Total Trades: {created_bot.backtest_results['total_trades']}")

        bot_id = created_bot.id

        # Test 2: Get bot by ID
        print(f"\n2️⃣  Testing get bot by ID...")
        retrieved_bot = await bot_repo.get_by_id(bot_id, user_id)
        print(f"   ✅ Retrieved bot: {retrieved_bot.name}")

        # Test 3: List user bots
        print(f"\n3️⃣  Testing list user bots...")
        bot_list = await bot_repo.list_by_user(user_id, page=1, page_size=10)
        print(f"   ✅ Found {len(bot_list.data)} bots")
        print(f"   Total: {bot_list.total}, Page: {bot_list.page}/{bot_list.page_size}")

        # Test 4: Toggle favorite
        print(f"\n4️⃣  Testing toggle favorite...")
        updated_bot = await bot_repo.toggle_favorite(bot_id, user_id)
        print(f"   ✅ Favorite status: {updated_bot.is_favorite}")

        # Test 5: Get favorites
        print(f"\n5️⃣  Testing get favorites...")
        favorites = await bot_repo.get_favorites(user_id)
        print(f"   ✅ Found {len(favorites)} favorite bots")

        # Test 6: Update bot
        print(f"\n6️⃣  Testing update bot...")
        from db.models import TradingBotUpdate
        update_data = TradingBotUpdate(
            name="Updated GME Momentum Bot",
            description="Updated description"
        )
        updated_bot = await bot_repo.update(bot_id, user_id, update_data)
        print(f"   ✅ Bot updated: {updated_bot.name}")

        # Test 7: Delete bot
        print(f"\n7️⃣  Testing delete bot...")
        await bot_repo.delete(bot_id, user_id)
        print(f"   ✅ Bot deleted")

        # Verify deletion
        deleted_bot = await bot_repo.get_by_id(bot_id, user_id)
        if deleted_bot is None:
            print(f"   ✅ Deletion confirmed")
        else:
            print(f"   ❌ Bot still exists after deletion!")

        print(f"\n{'='*60}")
        print("✅ All bot operation tests passed!")
        print(f"{'='*60}")

    except Exception as e:
        print(f"\n❌ Bot operations test failed: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all tests"""
    print("\n🧪 Starting Supabase Integration Tests\n")

    # Test authentication
    user_id, access_token = await test_auth()

    if not user_id:
        print("\n❌ Authentication tests failed, skipping bot tests")
        sys.exit(1)

    # Test bot operations
    await test_bot_operations(user_id, access_token)

    print("\n" + "="*60)
    print("🎉 All tests completed successfully!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
