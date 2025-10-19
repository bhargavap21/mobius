#!/usr/bin/env python3
"""
Script to set up community tables in Supabase
"""
import asyncio
import logging
from db.supabase_client import get_supabase_admin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_community_tables():
    """Set up community tables in Supabase"""
    try:
        # Get admin client
        client = get_supabase_admin()
        
        # Community tables SQL
        community_tables_sql = """
        -- Enable UUID extension if not already enabled
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

        -- COMMUNITY SHARED AGENTS TABLE
        CREATE TABLE IF NOT EXISTS public.shared_agents (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            original_bot_id UUID NOT NULL REFERENCES public.trading_bots(id) ON DELETE CASCADE,
            author_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            tags TEXT[] DEFAULT '{}',
            views INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            downloads INTEGER DEFAULT 0,
            is_public BOOLEAN DEFAULT TRUE,
            shared_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            CONSTRAINT shared_agents_name_check CHECK (char_length(name) > 0 AND char_length(name) <= 255),
            CONSTRAINT shared_agents_description_check CHECK (char_length(description) > 0 AND char_length(description) <= 2000)
        );

        -- COMMUNITY LIKES TABLE
        CREATE TABLE IF NOT EXISTS public.agent_likes (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            shared_agent_id UUID NOT NULL REFERENCES public.shared_agents(id) ON DELETE CASCADE,
            user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
            liked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(shared_agent_id, user_id)
        );

        -- COMMUNITY DOWNLOADS TABLE
        CREATE TABLE IF NOT EXISTS public.agent_downloads (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            shared_agent_id UUID NOT NULL REFERENCES public.shared_agents(id) ON DELETE CASCADE,
            user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
            downloaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            ip_address INET,
            user_agent TEXT
        );

        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_shared_agents_author_id ON public.shared_agents(author_id);
        CREATE INDEX IF NOT EXISTS idx_shared_agents_shared_at ON public.shared_agents(shared_at);
        CREATE INDEX IF NOT EXISTS idx_shared_agents_is_public ON public.shared_agents(is_public);
        CREATE INDEX IF NOT EXISTS idx_agent_likes_shared_agent_id ON public.agent_likes(shared_agent_id);
        CREATE INDEX IF NOT EXISTS idx_agent_likes_user_id ON public.agent_likes(user_id);
        CREATE INDEX IF NOT EXISTS idx_agent_downloads_shared_agent_id ON public.agent_downloads(shared_agent_id);

        -- Enable Row Level Security (RLS)
        ALTER TABLE public.shared_agents ENABLE ROW LEVEL SECURITY;
        ALTER TABLE public.agent_likes ENABLE ROW LEVEL SECURITY;
        ALTER TABLE public.agent_downloads ENABLE ROW LEVEL SECURITY;

        -- RLS Policies for shared_agents
        CREATE POLICY "Anyone can view public shared agents" ON public.shared_agents
            FOR SELECT USING (is_public = true);

        CREATE POLICY "Users can view their own shared agents" ON public.shared_agents
            FOR SELECT USING (auth.uid() = author_id);

        CREATE POLICY "Users can insert their own shared agents" ON public.shared_agents
            FOR INSERT WITH CHECK (auth.uid() = author_id);

        CREATE POLICY "Users can update their own shared agents" ON public.shared_agents
            FOR UPDATE USING (auth.uid() = author_id);

        CREATE POLICY "Users can delete their own shared agents" ON public.shared_agents
            FOR DELETE USING (auth.uid() = author_id);

        -- RLS Policies for agent_likes
        CREATE POLICY "Anyone can view likes" ON public.agent_likes
            FOR SELECT USING (true);

        CREATE POLICY "Users can insert their own likes" ON public.agent_likes
            FOR INSERT WITH CHECK (auth.uid() = user_id);

        CREATE POLICY "Users can delete their own likes" ON public.agent_likes
            FOR DELETE USING (auth.uid() = user_id);

        -- RLS Policies for agent_downloads
        CREATE POLICY "Anyone can view downloads" ON public.agent_downloads
            FOR SELECT USING (true);

        CREATE POLICY "Anyone can insert downloads" ON public.agent_downloads
            FOR INSERT WITH CHECK (true);
        """
        
        logger.info("🔧 Setting up community tables...")
        
        # Execute the SQL
        response = client.rpc('exec_sql', {'sql': community_tables_sql}).execute()
        
        logger.info("✅ Community tables setup completed!")
        logger.info(f"Response: {response}")
        
    except Exception as e:
        logger.error(f"❌ Error setting up community tables: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(setup_community_tables())
