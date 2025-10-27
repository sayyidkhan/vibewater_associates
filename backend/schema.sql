-- Supabase Database Schema for Vibe Water Associates
-- Run this in your Supabase SQL editor to create the tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Strategies table
CREATE TABLE IF NOT EXISTS strategies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'Backtest' CHECK (status IN ('Live', 'Paper', 'Backtest')),
    schema_json JSONB NOT NULL,
    guardrails JSONB NOT NULL DEFAULT '[]'::jsonb,
    metrics JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Backtests table
CREATE TABLE IF NOT EXISTS backtests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    strategy_id TEXT NOT NULL,
    params JSONB NOT NULL,
    metrics JSONB NOT NULL,
    equity_series JSONB NOT NULL DEFAULT '[]'::jsonb,
    drawdown_series JSONB NOT NULL DEFAULT '[]'::jsonb,
    monthly_returns JSONB NOT NULL DEFAULT '[]'::jsonb,
    trades JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Strategy executions table
CREATE TABLE IF NOT EXISTS strategy_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    strategy_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'analyzing', 'generating_code', 'executing', 'completed', 'failed')),
    generated_code TEXT,
    execution_logs JSONB NOT NULL DEFAULT '[]'::jsonb,
    backtest_run_id TEXT,
    error_message TEXT,
    agent_insights JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

-- Backtest runs table (for strategy execution service)
CREATE TABLE IF NOT EXISTS backtest_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    strategy_id TEXT NOT NULL,
    params JSONB NOT NULL,
    metrics JSONB NOT NULL,
    equity_series JSONB NOT NULL DEFAULT '[]'::jsonb,
    drawdown_series JSONB NOT NULL DEFAULT '[]'::jsonb,
    monthly_returns JSONB NOT NULL DEFAULT '[]'::jsonb,
    trades JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_strategies_user_id ON strategies(user_id);
CREATE INDEX IF NOT EXISTS idx_strategies_status ON strategies(status);
CREATE INDEX IF NOT EXISTS idx_backtests_strategy_id ON backtests(strategy_id);
CREATE INDEX IF NOT EXISTS idx_backtests_created_at ON backtests(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_strategy_executions_strategy_id ON strategy_executions(strategy_id);
CREATE INDEX IF NOT EXISTS idx_strategy_executions_user_id ON strategy_executions(user_id);
CREATE INDEX IF NOT EXISTS idx_backtest_runs_strategy_id ON backtest_runs(strategy_id);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to auto-update updated_at for strategies
CREATE TRIGGER update_strategies_updated_at BEFORE UPDATE ON strategies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

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

-- Create index for research runs
CREATE INDEX IF NOT EXISTS idx_research_runs_user_id ON research_runs(user_id);
CREATE INDEX IF NOT EXISTS idx_research_runs_started_at ON research_runs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_research_runs_status ON research_runs(status);
