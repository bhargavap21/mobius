#!/usr/bin/env python3
"""
Test script to check community API functionality
"""
import asyncio
import logging
from db.repositories.community_repository import CommunityRepository
from uuid import UUID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_community_api():
    """Test community API functionality"""
    try:
        repo = CommunityRepository()
        
        # Test getting shared agents
        logger.info("🔍 Testing get_shared_agents...")
        result = await repo.get_shared_agents(page=1, page_size=20)
        
        logger.info(f"✅ Got result: {type(result)}")
        logger.info(f"✅ Items count: {len(result.items)}")
        logger.info(f"✅ Total: {result.total}")
        
        for i, agent in enumerate(result.items):
            logger.info(f"  Agent {i+1}: {agent.name} (ID: {agent.id})")
            logger.info(f"    - Author ID: {agent.author_id}")
            logger.info(f"    - Original Bot ID: {agent.original_bot_id}")
            logger.info(f"    - Public: {agent.is_public}")
        
    except Exception as e:
        logger.error(f"❌ Error testing community API: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_community_api())
