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

-- Research sessions table to track research agent activities
CREATE TABLE IF NOT EXISTS research_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    session_type TEXT NOT NULL CHECK (session_type IN ('strategy_research', 'autonomous_backtest', 'full_pipeline')),
    parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
    status TEXT NOT NULL DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed')),
    strategies_found INTEGER DEFAULT 0,
    strategies_tested INTEGER DEFAULT 0,
    top_strategy_id TEXT,
    results JSONB,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Strategy performance rankings table
CREATE TABLE IF NOT EXISTS strategy_performance_rankings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    research_session_id UUID REFERENCES research_sessions(id) ON DELETE CASCADE,
    strategy_id TEXT NOT NULL,
    strategy_name TEXT NOT NULL,
    performance_score DECIMAL(5,2) NOT NULL,
    risk_adjusted_return DECIMAL(10,4),
    consistency_score DECIMAL(5,4),
    market_adaptability DECIMAL(5,4),
    rank_position INTEGER NOT NULL,
    backtest_metrics JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Research agent insights table for storing discovered patterns and learnings
CREATE TABLE IF NOT EXISTS research_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    insight_type TEXT NOT NULL CHECK (insight_type IN ('market_pattern', 'strategy_performance', 'risk_factor', 'optimization')),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    market_conditions JSONB,
    related_strategies TEXT[],
    supporting_data JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create additional indexes for research tables
CREATE INDEX IF NOT EXISTS idx_research_sessions_user_id ON research_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_research_sessions_status ON research_sessions(status);
CREATE INDEX IF NOT EXISTS idx_research_sessions_created_at ON research_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_strategy_performance_rankings_session_id ON strategy_performance_rankings(research_session_id);
CREATE INDEX IF NOT EXISTS idx_strategy_performance_rankings_strategy_id ON strategy_performance_rankings(strategy_id);
CREATE INDEX IF NOT EXISTS idx_strategy_performance_rankings_performance_score ON strategy_performance_rankings(performance_score DESC);
CREATE INDEX IF NOT EXISTS idx_research_insights_type ON research_insights(insight_type);
CREATE INDEX IF NOT EXISTS idx_research_insights_confidence ON research_insights(confidence_score DESC);

-- Trigger to auto-update updated_at for research_insights
CREATE TRIGGER update_research_insights_updated_at BEFORE UPDATE ON research_insights
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
