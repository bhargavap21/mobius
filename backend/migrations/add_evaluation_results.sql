-- Migration: Add evaluation_results column to trading_bots table
-- This column stores the results from the evaluation pipeline

ALTER TABLE public.trading_bots
ADD COLUMN IF NOT EXISTS evaluation_results JSONB;

-- Add comment for documentation
COMMENT ON COLUMN public.trading_bots.evaluation_results IS 'Evaluation pipeline results including scores, passed/failed checks, and detailed feedback';
