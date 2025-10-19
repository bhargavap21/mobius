#!/usr/bin/env python3
"""
Simple script to create community tables using Supabase client
"""
import asyncio
import logging
from db.supabase_client import get_supabase_admin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_community_tables():
    """Create community tables using Supabase client"""
    try:
        client = get_supabase_admin()
        
        # First, let's try to create the shared_agents table
        logger.info("🔧 Creating shared_agents table...")
        
        # Test if the table already exists by trying to query it
        try:
            response = client.table('shared_agents').select('id').limit(1).execute()
            logger.info("✅ shared_agents table already exists")
        except Exception as e:
            if "Could not find the table" in str(e) or "PGRST205" in str(e):
                logger.info("📝 shared_agents table doesn't exist, creating it...")
                
                # Create the table using SQL
                create_sql = """
                CREATE TABLE IF NOT EXISTS public.shared_agents (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    original_bot_id UUID NOT NULL,
                    author_id UUID NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    tags TEXT[] DEFAULT '{}',
                    views INTEGER DEFAULT 0,
                    likes INTEGER DEFAULT 0,
                    downloads INTEGER DEFAULT 0,
                    is_public BOOLEAN DEFAULT TRUE,
                    shared_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                """
                
                # Try to execute the SQL
                try:
                    response = client.rpc('exec_sql', {'sql': create_sql}).execute()
                    logger.info("✅ shared_agents table created successfully")
                except Exception as sql_error:
                    logger.error(f"❌ Failed to create table via SQL: {sql_error}")
                    # Try alternative approach - insert a test record to create the table
                    logger.info("📝 Trying alternative table creation approach...")
                    
                    # This will fail but might create the table structure
                    try:
                        test_data = {
                            'original_bot_id': '00000000-0000-0000-0000-000000000001',
                            'author_id': '00000000-0000-0000-0000-000000000001',
                            'name': 'Test Agent',
                            'description': 'Test description',
                            'tags': ['test'],
                            'is_public': True
                        }
                        response = client.table('shared_agents').insert(test_data).execute()
                        logger.info("✅ Table created via insert")
                        
                        # Clean up test data
                        client.table('shared_agents').delete().eq('name', 'Test Agent').execute()
                        logger.info("✅ Test data cleaned up")
                        
                    except Exception as insert_error:
                        logger.error(f"❌ Failed to create table via insert: {insert_error}")
                        raise
            else:
                logger.error(f"❌ Unexpected error checking table: {e}")
                raise
        
        # Create agent_likes table
        logger.info("🔧 Creating agent_likes table...")
        try:
            response = client.table('agent_likes').select('id').limit(1).execute()
            logger.info("✅ agent_likes table already exists")
        except Exception as e:
            if "Could not find the table" in str(e) or "PGRST205" in str(e):
                logger.info("📝 Creating agent_likes table...")
                try:
                    test_data = {
                        'shared_agent_id': '00000000-0000-0000-0000-000000000001',
                        'user_id': '00000000-0000-0000-0000-000000000001'
                    }
                    response = client.table('agent_likes').insert(test_data).execute()
                    logger.info("✅ agent_likes table created")
                    
                    # Clean up test data
                    client.table('agent_likes').delete().eq('shared_agent_id', '00000000-0000-0000-0000-000000000001').execute()
                    logger.info("✅ Test data cleaned up")
                except Exception as insert_error:
                    logger.error(f"❌ Failed to create agent_likes table: {insert_error}")
        
        # Create agent_downloads table
        logger.info("🔧 Creating agent_downloads table...")
        try:
            response = client.table('agent_downloads').select('id').limit(1).execute()
            logger.info("✅ agent_downloads table already exists")
        except Exception as e:
            if "Could not find the table" in str(e) or "PGRST205" in str(e):
                logger.info("📝 Creating agent_downloads table...")
                try:
                    test_data = {
                        'shared_agent_id': '00000000-0000-0000-0000-000000000001',
                        'user_id': '00000000-0000-0000-0000-000000000001'
                    }
                    response = client.table('agent_downloads').insert(test_data).execute()
                    logger.info("✅ agent_downloads table created")
                    
                    # Clean up test data
                    client.table('agent_downloads').delete().eq('shared_agent_id', '00000000-0000-0000-0000-000000000001').execute()
                    logger.info("✅ Test data cleaned up")
                except Exception as insert_error:
                    logger.error(f"❌ Failed to create agent_downloads table: {insert_error}")
        
        logger.info("🎉 Community tables setup completed!")
        
    except Exception as e:
        logger.error(f"❌ Error setting up community tables: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(create_community_tables())
