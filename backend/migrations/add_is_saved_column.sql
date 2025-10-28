-- Add is_saved column to trading_bots table
-- is_saved = true: manually saved to "My Bots"
-- is_saved = false: auto-saved chat history

ALTER TABLE trading_bots
ADD COLUMN IF NOT EXISTS is_saved BOOLEAN DEFAULT false;

-- Update existing records to be marked as saved (backward compatibility)
-- UPDATE trading_bots SET is_saved = true WHERE is_saved IS NULL;
