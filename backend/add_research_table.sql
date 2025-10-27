-- Add research_runs table for autonomous research agent
-- Run this in your Supabase SQL editor if you already have the database set up

-- Research runs table (for autonomous research agent)
CREATE TABLE IF NOT EXISTS research_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    num_strategies INTEGER NOT NULL,
    market_focus TEXT,
    risk_level TEXT NOT NULL DEFAULT 'Medium' CHECK (risk_level IN ('Low', 'Medium', 'High')),
    status TEXT NOT NULL DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed')),
    rankings JSONB DEFAULT '[]'::jsonb,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error_message TEXT
);

-- Create indexes for research runs
CREATE INDEX IF NOT EXISTS idx_research_runs_user_id ON research_runs(user_id);
CREATE INDEX IF NOT EXISTS idx_research_runs_started_at ON research_runs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_research_runs_status ON research_runs(status);
