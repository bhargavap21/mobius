-- ============================================================================
-- COMMUNITY TABLES RLS MIGRATION
-- ============================================================================
-- This migration adds Row Level Security policies for community features
-- Run this in your Supabase SQL Editor to enable community table access
--
-- Prerequisites: The base schema.sql must already be run (tables already exist)
-- ============================================================================

-- Enable RLS on community tables (if not already enabled)
ALTER TABLE public.shared_agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_likes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_downloads ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- SHARED AGENTS POLICIES
-- ============================================================================

-- Drop existing policies if they exist (idempotent)
DROP POLICY IF EXISTS "Anyone can view public shared agents" ON public.shared_agents;
DROP POLICY IF EXISTS "Users can view own shared agents" ON public.shared_agents;
DROP POLICY IF EXISTS "Users can share own bots" ON public.shared_agents;
DROP POLICY IF EXISTS "Users can update own shared agents" ON public.shared_agents;
DROP POLICY IF EXISTS "Users can delete own shared agents" ON public.shared_agents;

-- Create new policies
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

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Anyone can view likes" ON public.agent_likes;
DROP POLICY IF EXISTS "Authenticated users can like agents" ON public.agent_likes;
DROP POLICY IF EXISTS "Users can unlike agents" ON public.agent_likes;

-- Create new policies
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

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Anyone can view download counts" ON public.agent_downloads;
DROP POLICY IF EXISTS "Anyone can download agents" ON public.agent_downloads;

-- Create new policies
CREATE POLICY "Anyone can view download counts"
    ON public.agent_downloads
    FOR SELECT
    USING (true);

CREATE POLICY "Anyone can download agents"
    ON public.agent_downloads
    FOR INSERT
    WITH CHECK (true); -- Allows anonymous downloads

-- ============================================================================
-- TRIGGERS FOR COMMUNITY TABLES
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
-- Uncomment these to verify the migration was successful:

-- SELECT COUNT(*) as shared_agents_count FROM public.shared_agents;
-- SELECT COUNT(*) as agent_likes_count FROM public.agent_likes;
-- SELECT COUNT(*) as agent_downloads_count FROM public.agent_downloads;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
-- Community features are now enabled with proper RLS policies!
-- Users can share bots, like them, and download them.
