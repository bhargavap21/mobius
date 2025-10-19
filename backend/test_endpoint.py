#!/usr/bin/env python3
"""
Test script to test the community endpoint directly
"""
import asyncio
import logging
from db.repositories.community_repository import CommunityRepository
from db.supabase_client import get_supabase_admin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_endpoint_logic():
    """Test the endpoint logic directly"""
    try:
        community_repo = CommunityRepository()
        
        # Simulate the endpoint logic
        page = 1
        page_size = 20
        
        logger.info("🔍 Testing endpoint logic...")
        
        # Try to get data from database
        result = await community_repo.get_shared_agents(page=page, page_size=page_size)
        logger.info(f"✅ Got result from community_repo: {len(result.items)} items")
        
        # Transform the data to include author names and performance metrics
        agents_with_details = []
        logger.info(f"🔍 Processing {len(result.items)} shared agents...")
        
        for i, agent in enumerate(result.items):
            logger.info(f"📋 Processing agent {i+1}: {agent.name}")
            
            # Get original bot data for performance metrics
            original_bot_response = community_repo.client.table('trading_bots').select('*').eq('id', str(agent.original_bot_id)).execute()
            
            if original_bot_response.data:
                original_bot = original_bot_response.data[0]
                logger.info(f"  ✅ Found original bot: {original_bot.get('name')}")
                
                backtest_results = original_bot.get('backtest_results', {})
                logger.info(f"  📊 Backtest results keys: {list(backtest_results.keys()) if backtest_results else 'None'}")
                
                # Get author name
                author_response = community_repo.client.table('users').select('full_name').eq('id', str(agent.author_id)).execute()
                author_name = author_response.data[0].get('full_name', 'Anonymous') if author_response.data else 'Anonymous'
                logger.info(f"  👤 Author: {author_name}")
                
                # Get backtest summary
                backtest_summary = backtest_results.get('summary', {}) if backtest_results else {}
                
                agent_data = {
                    "id": str(agent.id),
                    "name": agent.name,
                    "description": agent.description,
                    "author": author_name,
                    "tags": agent.tags,
                    "total_return": backtest_summary.get('total_return', 0.0),
                    "win_rate": backtest_summary.get('win_rate', 0),
                    "total_trades": backtest_summary.get('total_trades', 0),
                    "symbol": original_bot.get('strategy_config', {}).get('asset', 'N/A'),
                    "views": agent.views,
                    "likes": agent.likes,
                    "downloads": agent.downloads,
                    "shared_at": agent.shared_at.isoformat(),
                    "liked": agent.liked
                }
                agents_with_details.append(agent_data)
                logger.info(f"  ✅ Added agent data: {agent_data['name']} by {agent_data['author']}")
            else:
                logger.error(f"  ❌ Original bot not found for agent: {agent.name}")
        
        logger.info(f"🎯 Final agents_with_details count: {len(agents_with_details)}")
        
        response_data = {
            "success": True, 
            "agents": agents_with_details,
            "pagination": {
                "page": result.page,
                "page_size": result.page_size,
                "total": result.total,
                "total_pages": result.total_pages
            }
        }
        
        logger.info(f"🎉 Final response: {response_data}")
        
    except Exception as e:
        logger.error(f"❌ Error in endpoint logic: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_endpoint_logic())
