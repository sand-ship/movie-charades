-- Supabase schema migration for games table
-- Run this in Supabase SQL editor

-- Add session_id column (for deduplication)
ALTER TABLE games ADD COLUMN session_id TEXT;

-- Rename correct_movie_id to player_film_id (semantic clarity)
ALTER TABLE games RENAME COLUMN correct_movie_id TO player_film_id;

-- Create index on session_id for faster lookups
CREATE INDEX idx_games_session_id ON games(session_id);

-- Create index on outcome for filtering
CREATE INDEX idx_games_outcome ON games(outcome);

-- Drop the stumpers table (no longer needed)
-- DROP TABLE IF EXISTS stumpers;

-- Verify migration
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'games'
ORDER BY ordinal_position;
