#!/usr/bin/env python3
"""
Test script to check database contents
"""
import asyncio
import logging
from db.supabase_client import get_supabase_admin
from uuid import UUID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_database():
    """Test database contents"""
    try:
        client = get_supabase_admin()
        
        # Check trading_bots table
        logger.info("🔍 Checking trading_bots table...")
        try:
            response = client.table('trading_bots').select('*').execute()
            logger.info(f"✅ Found {len(response.data)} trading bots")
            for bot in response.data[:3]:  # Show first 3 bots
                logger.info(f"  - Bot: {bot.get('name', 'No name')} (ID: {bot.get('id')}, User: {bot.get('user_id')})")
        except Exception as e:
            logger.error(f"❌ Error querying trading_bots: {e}")
        
        # Check shared_agents table
        logger.info("🔍 Checking shared_agents table...")
        try:
            response = client.table('shared_agents').select('*').execute()
            logger.info(f"✅ Found {len(response.data)} shared agents")
            for agent in response.data[:3]:  # Show first 3 agents
                logger.info(f"  - Agent: {agent.get('name', 'No name')} (ID: {agent.get('id')}, Author: {agent.get('author_id')})")
        except Exception as e:
            logger.error(f"❌ Error querying shared_agents: {e}")
        
        # Check users table
        logger.info("🔍 Checking users table...")
        try:
            response = client.table('users').select('*').execute()
            logger.info(f"✅ Found {len(response.data)} users")
            for user in response.data[:3]:  # Show first 3 users
                logger.info(f"  - User: {user.get('email', 'No email')} (ID: {user.get('id')})")
        except Exception as e:
            logger.error(f"❌ Error querying users: {e}")
        
        # Test creating a shared agent
        logger.info("🔍 Testing shared agent creation...")
        try:
            # First, get a bot to use
            bot_response = client.table('trading_bots').select('*').limit(1).execute()
            if bot_response.data:
                bot = bot_response.data[0]
                bot_id = bot['id']
                user_id = bot['user_id']
                
                logger.info(f"📝 Testing with bot: {bot.get('name')} (ID: {bot_id}, User: {user_id})")
                
                # Try to create a shared agent
                shared_agent_data = {
                    'original_bot_id': bot_id,
                    'author_id': user_id,
                    'name': 'Test Shared Agent',
                    'description': 'Test description for shared agent',
                    'tags': ['test'],
                    'is_public': True
                }
                
                response = client.table('shared_agents').insert(shared_agent_data).execute()
                if response.data:
                    shared_agent_id = response.data[0]['id']
                    logger.info(f"✅ Successfully created shared agent: {shared_agent_id}")
                    
                    # Clean up test data
                    client.table('shared_agents').delete().eq('id', shared_agent_id).execute()
                    logger.info("✅ Test data cleaned up")
                else:
                    logger.error("❌ Failed to create shared agent - no data returned")
            else:
                logger.error("❌ No bots found to test with")
                
        except Exception as e:
            logger.error(f"❌ Error testing shared agent creation: {e}")
        
    except Exception as e:
        logger.error(f"❌ Error testing database: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_database())
