-- ============================================================================
-- COMMUNITY TABLES MIGRATION
-- ============================================================================
-- This migration creates community feature tables with RLS policies
-- Run this in your Supabase SQL Editor
-- ============================================================================

-- ============================================================================
-- CREATE COMMUNITY TABLES
-- ============================================================================

-- SHARED AGENTS TABLE
CREATE TABLE IF NOT EXISTS public.shared_agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    original_bot_id UUID NOT NULL REFERENCES public.trading_bots(id) ON DELETE CASCADE,
    author_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,

    -- Shared agent metadata
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    tags TEXT[] DEFAULT '{}',

    -- Community metrics
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    downloads INTEGER DEFAULT 0,

    -- Privacy settings
    is_public BOOLEAN DEFAULT TRUE,

    -- Timestamps
    shared_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT shared_agents_name_check CHECK (char_length(name) > 0 AND char_length(name) <= 255),
    CONSTRAINT shared_agents_description_check CHECK (char_length(description) > 0 AND char_length(description) <= 2000)
);

-- AGENT LIKES TABLE
CREATE TABLE IF NOT EXISTS public.agent_likes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shared_agent_id UUID NOT NULL REFERENCES public.shared_agents(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    liked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Ensure one like per user per agent
    UNIQUE(shared_agent_id, user_id)
);

-- AGENT DOWNLOADS TABLE
CREATE TABLE IF NOT EXISTS public.agent_downloads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shared_agent_id UUID NOT NULL REFERENCES public.shared_agents(id) ON DELETE CASCADE,
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL, -- Allow anonymous downloads
    downloaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address INET, -- Track anonymous downloads by IP
    user_agent TEXT -- Track browser/client info
);

-- ============================================================================
-- CREATE INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_shared_agents_author_id ON public.shared_agents(author_id);
CREATE INDEX IF NOT EXISTS idx_shared_agents_shared_at ON public.shared_agents(shared_at DESC);
CREATE INDEX IF NOT EXISTS idx_shared_agents_is_public ON public.shared_agents(is_public);
CREATE INDEX IF NOT EXISTS idx_shared_agents_views ON public.shared_agents(views DESC);
CREATE INDEX IF NOT EXISTS idx_shared_agents_likes ON public.shared_agents(likes DESC);
CREATE INDEX IF NOT EXISTS idx_shared_agents_downloads ON public.shared_agents(downloads DESC);
CREATE INDEX IF NOT EXISTS idx_shared_agents_tags ON public.shared_agents USING GIN(tags);

CREATE INDEX IF NOT EXISTS idx_agent_likes_shared_agent_id ON public.agent_likes(shared_agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_likes_user_id ON public.agent_likes(user_id);

CREATE INDEX IF NOT EXISTS idx_agent_downloads_shared_agent_id ON public.agent_downloads(shared_agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_downloads_user_id ON public.agent_downloads(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_downloads_downloaded_at ON public.agent_downloads(downloaded_at DESC);

-- ============================================================================
-- ENABLE ROW LEVEL SECURITY
-- ============================================================================

ALTER TABLE public.shared_agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_likes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_downloads ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- SHARED AGENTS POLICIES
-- ============================================================================

-- Drop existing policies if they exist (for idempotency)
DROP POLICY IF EXISTS "Anyone can view public shared agents" ON public.shared_agents;
DROP POLICY IF EXISTS "Users can view own shared agents" ON public.shared_agents;
DROP POLICY IF EXISTS "Users can share own bots" ON public.shared_agents;
DROP POLICY IF EXISTS "Users can update own shared agents" ON public.shared_agents;
DROP POLICY IF EXISTS "Users can delete own shared agents" ON public.shared_agents;

-- Create policies
CREATE POLICY "Anyone can view public shared agents"
    ON public.shared_agents
    FOR SELECT
    USING (is_public = TRUE);

CREATE POLICY "Users can view own shared agents"
    ON public.shared_agents
    FOR SELECT
    USING (auth.uid() = author_id);

CREATE POLICY "Users can share own bots"
    ON public.shared_agents
    FOR INSERT
    WITH CHECK (
        auth.uid() = author_id AND
        EXISTS (
            SELECT 1 FROM public.trading_bots
            WHERE trading_bots.id = shared_agents.original_bot_id
            AND trading_bots.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update own shared agents"
    ON public.shared_agents
    FOR UPDATE
    USING (auth.uid() = author_id);

CREATE POLICY "Users can delete own shared agents"
    ON public.shared_agents
    FOR DELETE
    USING (auth.uid() = author_id);

-- ============================================================================
-- AGENT LIKES POLICIES
-- ============================================================================

DROP POLICY IF EXISTS "Anyone can view likes" ON public.agent_likes;
DROP POLICY IF EXISTS "Authenticated users can like agents" ON public.agent_likes;
DROP POLICY IF EXISTS "Users can unlike agents" ON public.agent_likes;

CREATE POLICY "Anyone can view likes"
    ON public.agent_likes
    FOR SELECT
    USING (true);

CREATE POLICY "Authenticated users can like agents"
    ON public.agent_likes
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can unlike agents"
    ON public.agent_likes
    FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================================================
-- AGENT DOWNLOADS POLICIES
-- ============================================================================

DROP POLICY IF EXISTS "Anyone can view download counts" ON public.agent_downloads;
DROP POLICY IF EXISTS "Anyone can download agents" ON public.agent_downloads;

CREATE POLICY "Anyone can view download counts"
    ON public.agent_downloads
    FOR SELECT
    USING (true);

CREATE POLICY "Anyone can download agents"
    ON public.agent_downloads
    FOR INSERT
    WITH CHECK (true); -- Allows anonymous downloads

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Add updated_at trigger for shared_agents
DROP TRIGGER IF EXISTS update_shared_agents_updated_at ON public.shared_agents;

CREATE TRIGGER update_shared_agents_updated_at
    BEFORE UPDATE ON public.shared_agents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
-- Run these to verify the migration was successful:

SELECT
    'shared_agents' as table_name,
    COUNT(*) as row_count
FROM public.shared_agents

UNION ALL

SELECT
    'agent_likes' as table_name,
    COUNT(*) as row_count
FROM public.agent_likes

UNION ALL

SELECT
    'agent_downloads' as table_name,
    COUNT(*) as row_count
FROM public.agent_downloads;

-- Check RLS is enabled
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('shared_agents', 'agent_likes', 'agent_downloads');

-- ============================================================================
-- MIGRATION COMPLETE ✅
-- ============================================================================
-- Community tables created successfully!
-- - shared_agents: Share bots with the community
-- - agent_likes: Like/favorite community bots
-- - agent_downloads: Track bot downloads
--
-- All tables have RLS enabled with proper security policies.
