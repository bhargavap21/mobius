-- AI Trading Bot Database Schema
-- Run this in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- USERS TABLE
-- ============================================================================
-- Note: Supabase Auth handles user authentication
-- This table extends the auth.users table with additional profile info
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- TRADING BOTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.trading_bots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,

    -- Bot metadata
    name TEXT NOT NULL,
    description TEXT,

    -- Bot configuration (stores the complete strategy)
    strategy_config JSONB NOT NULL,
    generated_code TEXT NOT NULL,

    -- Backtest results
    backtest_results JSONB,
    insights_config JSONB,

    -- Session tracking
    session_id TEXT,

    -- Metadata
    is_favorite BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Indexes for better query performance
    CONSTRAINT trading_bots_name_check CHECK (char_length(name) > 0 AND char_length(name) <= 255)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_trading_bots_user_id ON public.trading_bots(user_id);
CREATE INDEX IF NOT EXISTS idx_trading_bots_created_at ON public.trading_bots(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_trading_bots_is_favorite ON public.trading_bots(user_id, is_favorite);

-- ============================================================================
-- BOT EXECUTIONS TABLE (optional - for tracking live runs)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.bot_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bot_id UUID NOT NULL REFERENCES public.trading_bots(id) ON DELETE CASCADE,

    -- Execution details
    status TEXT NOT NULL CHECK (status IN ('running', 'success', 'failed', 'cancelled')),
    result JSONB,
    error_message TEXT,

    -- Timing
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_bot_executions_bot_id ON public.bot_executions(bot_id);
CREATE INDEX IF NOT EXISTS idx_bot_executions_status ON public.bot_executions(status);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trading_bots ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bot_executions ENABLE ROW LEVEL SECURITY;

-- Users table policies
CREATE POLICY "Users can view own profile"
    ON public.users
    FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile"
    ON public.users
    FOR INSERT
    WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON public.users
    FOR UPDATE
    USING (auth.uid() = id);

-- Trading bots policies
CREATE POLICY "Users can view own bots"
    ON public.trading_bots
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create own bots"
    ON public.trading_bots
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own bots"
    ON public.trading_bots
    FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own bots"
    ON public.trading_bots
    FOR DELETE
    USING (auth.uid() = user_id);

-- Bot executions policies
CREATE POLICY "Users can view own bot executions"
    ON public.bot_executions
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.trading_bots
            WHERE trading_bots.id = bot_executions.bot_id
            AND trading_bots.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create executions for own bots"
    ON public.bot_executions
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.trading_bots
            WHERE trading_bots.id = bot_executions.bot_id
            AND trading_bots.user_id = auth.uid()
        )
    );

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to automatically create user profile when auth user is created
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-create user profile on auth signup
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- Triggers to auto-update updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_trading_bots_updated_at
    BEFORE UPDATE ON public.trading_bots
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL SETUP COMPLETE
-- ============================================================================
-- Next steps:
-- 1. Run this script in your Supabase SQL Editor
-- 2. Set up authentication in Supabase Dashboard
-- 3. Configure environment variables in backend/.env
