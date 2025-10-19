#!/usr/bin/env python3
"""
Debug script to check shared agents and their original bots
"""
import asyncio
import logging
from db.repositories.community_repository import CommunityRepository
from db.supabase_client import get_supabase_admin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_shared_agents():
    """Debug shared agents and their original bots"""
    try:
        repo = CommunityRepository()
        client = get_supabase_admin()
        
        # Get shared agents
        result = await repo.get_shared_agents(page=1, page_size=20)
        
        logger.info(f"🔍 Found {len(result.items)} shared agents")
        
        for i, agent in enumerate(result.items):
            logger.info(f"\n📋 Agent {i+1}: {agent.name}")
            logger.info(f"  - ID: {agent.id}")
            logger.info(f"  - Author ID: {agent.author_id}")
            logger.info(f"  - Original Bot ID: {agent.original_bot_id}")
            
            # Check if original bot exists
            bot_response = client.table('trading_bots').select('*').eq('id', str(agent.original_bot_id)).execute()
            
            if bot_response.data:
                original_bot = bot_response.data[0]
                logger.info(f"  ✅ Original bot found: {original_bot.get('name')}")
                logger.info(f"     - Bot owner: {original_bot.get('user_id')}")
                logger.info(f"     - Bot has backtest_results: {'backtest_results' in original_bot}")
            else:
                logger.error(f"  ❌ Original bot NOT found for ID: {agent.original_bot_id}")
                
                # Check if any bots exist with similar IDs
                all_bots = client.table('trading_bots').select('id, name, user_id').execute()
                logger.info(f"  📋 Available bots:")
                for bot in all_bots.data[:5]:
                    logger.info(f"     - {bot.get('name')} (ID: {bot.get('id')})")
            
            # Check if author exists
            author_response = client.table('users').select('*').eq('id', str(agent.author_id)).execute()
            
            if author_response.data:
                author = author_response.data[0]
                logger.info(f"  ✅ Author found: {author.get('full_name', author.get('email', 'Unknown'))}")
            else:
                logger.error(f"  ❌ Author NOT found for ID: {agent.author_id}")
        
    except Exception as e:
        logger.error(f"❌ Error debugging shared agents: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(debug_shared_agents())
