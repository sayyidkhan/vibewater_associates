"use client";

import React, { useState } from 'react';
import { Card } from './ui/Card';
import { Button } from './ui/Button';

interface ResearchRequest {
  market_focus?: string;
  strategy_types?: string[];
  risk_tolerance?: 'low' | 'medium' | 'high';
  max_strategies: number;
  research_depth: 'quick' | 'thorough';
}

interface ResearchedStrategy {
  id: string;
  name: string;
  description: string;
  category: string;
  market_type: string;
  complexity: string;
  expected_return: number;
  risk_level: string;
  confidence_score: number;
  research_source: string;
}

interface StrategyRanking {
  strategy_id: string;
  strategy_name: string;
  performance_score: number;
  rank: number;
  metrics: {
    total_return: number;
    sharpe_ratio: number;
    max_drawdown: number;
    win_rate: number;
    trades: number;
  };
}

export default function ResearchAgent() {
  const [isResearching, setIsResearching] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [strategies, setStrategies] = useState<ResearchedStrategy[]>([]);
  const [rankings, setRankings] = useState<StrategyRanking[]>([]);
  const [error, setError] = useState<string | null>(null);

  const [researchParams, setResearchParams] = useState<ResearchRequest>({
    market_focus: 'crypto',
    strategy_types: ['momentum', 'mean_reversion'],
    risk_tolerance: 'medium',
    max_strategies: 5,
    research_depth: 'quick'
  });

  const handleResearchStrategies = async () => {
    setIsResearching(true);
    setError(null);
    
    try {
      const response = await fetch('/api/research/strategies', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(researchParams),
      });

      if (!response.ok) {
        throw new Error(`Research failed: ${response.statusText}`);
      }

      const data = await response.json();
      setStrategies(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Research failed');
    } finally {
      setIsResearching(false);
    }
  };

  const handleAutonomousBacktest = async () => {
    setIsTesting(true);
    setError(null);

    try {
      const response = await fetch('/api/research/backtest/autonomous', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          strategy_ids: strategies.map(s => s.id),
          max_concurrent_tests: Math.min(strategies.length, 3)
        }),
      });

      if (!response.ok) {
        throw new Error(`Backtesting failed: ${response.statusText}`);
      }

      const data = await response.json();
      setRankings(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Backtesting failed');
    } finally {
      setIsTesting(false);
    }
  };

  const handleFullPipeline = async () => {
    setIsResearching(true);
    setIsTesting(true);
    setError(null);

    try {
      const response = await fetch('/api/research/pipeline/full', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          research_request: researchParams,
          backtest_request: {
            max_concurrent_tests: 3
          }
        }),
      });

      if (!response.ok) {
        throw new Error(`Pipeline failed: ${response.statusText}`);
      }

      const data = await response.json();
      setStrategies(data.all_rankings?.map((r: StrategyRanking) => ({
        id: r.strategy_id,
        name: r.strategy_name,
        description: `Performance Score: ${r.performance_score.toFixed(1)}`,
        category: 'researched',
        market_type: 'crypto',
        complexity: 'intermediate',
        expected_return: r.metrics.total_return,
        risk_level: 'medium',
        confidence_score: r.performance_score / 100,
        research_source: 'Full Pipeline'
      })) || []);
      setRankings(data.all_rankings || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Pipeline failed');
    } finally {
      setIsResearching(false);
      setIsTesting(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <h2 className="text-2xl font-bold mb-4">🔍 Research Agent</h2>
        <p className="text-gray-600 mb-6">
          Discover and analyze trading strategies autonomously using AI agents.
        </p>

        {/* Research Parameters */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium mb-2">Market Focus</label>
            <select
              value={researchParams.market_focus}
              onChange={(e) => setResearchParams(prev => ({ ...prev, market_focus: e.target.value }))}
              className="w-full p-2 border rounded-md"
            >
              <option value="crypto">Cryptocurrency</option>
              <option value="forex">Forex</option>
              <option value="stocks">Stocks</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Risk Tolerance</label>
            <select
              value={researchParams.risk_tolerance}
              onChange={(e) => setResearchParams(prev => ({ ...prev, risk_tolerance: e.target.value as 'low' | 'medium' | 'high' }))}
              className="w-full p-2 border rounded-md"
            >
              <option value="low">Low Risk</option>
              <option value="medium">Medium Risk</option>
              <option value="high">High Risk</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Max Strategies</label>
            <input
              type="number"
              min="1"
              max="10"
              value={researchParams.max_strategies}
              onChange={(e) => setResearchParams(prev => ({ ...prev, max_strategies: parseInt(e.target.value) }))}
              className="w-full p-2 border rounded-md"
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4 mb-6">
          <Button
            onClick={handleResearchStrategies}
            disabled={isResearching}
            className="bg-blue-600 hover:bg-blue-700"
          >
            {isResearching ? '🔍 Researching...' : '🔍 Research Strategies'}
          </Button>

          <Button
            onClick={handleAutonomousBacktest}
            disabled={isTesting || strategies.length === 0}
            className="bg-green-600 hover:bg-green-700"
          >
            {isTesting ? '🚀 Testing...' : '🚀 Run Backtests'}
          </Button>

          <Button
            onClick={handleFullPipeline}
            disabled={isResearching || isTesting}
            className="bg-purple-600 hover:bg-purple-700"
          >
            {(isResearching || isTesting) ? '🔄 Running Pipeline...' : '🔄 Full Pipeline'}
          </Button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <p className="text-red-800">❌ {error}</p>
          </div>
        )}
      </Card>

      {/* Researched Strategies */}
      {strategies.length > 0 && (
        <Card className="p-6">
          <h3 className="text-xl font-bold mb-4">📊 Researched Strategies ({strategies.length})</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {strategies.map((strategy, index) => (
              <div key={strategy.id || index} className="border rounded-lg p-4 bg-gray-50">
                <h4 className="font-semibold text-lg mb-2">{strategy.name}</h4>
                <p className="text-sm text-gray-600 mb-3">{strategy.description}</p>
                
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Category:</span>
                    <span className="font-medium">{strategy.category}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Expected Return:</span>
                    <span className="font-medium text-green-600">{strategy.expected_return.toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Risk Level:</span>
                    <span className={`font-medium ${
                      strategy.risk_level === 'low' ? 'text-green-600' :
                      strategy.risk_level === 'medium' ? 'text-yellow-600' : 'text-red-600'
                    }`}>
                      {strategy.risk_level}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Confidence:</span>
                    <span className="font-medium">{(strategy.confidence_score * 100).toFixed(0)}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Performance Rankings */}
      {rankings.length > 0 && (
        <Card className="p-6">
          <h3 className="text-xl font-bold mb-4">🏆 Performance Rankings</h3>
          <div className="space-y-4">
            {rankings.map((ranking, index) => (
              <div 
                key={ranking.strategy_id} 
                className={`border rounded-lg p-4 ${
                  index === 0 ? 'bg-yellow-50 border-yellow-200' : 'bg-gray-50'
                }`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <span className={`text-2xl font-bold ${
                      index === 0 ? 'text-yellow-600' : 'text-gray-600'
                    }`}>
                      #{ranking.rank}
                    </span>
                    <div>
                      <h4 className="font-semibold text-lg">{ranking.strategy_name}</h4>
                      <p className="text-sm text-gray-600">
                        Performance Score: {ranking.performance_score.toFixed(1)}/100
                      </p>
                    </div>
                  </div>
                  {index === 0 && <span className="text-2xl">🏆</span>}
                </div>

                <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
                  <div className="text-center">
                    <div className="font-medium text-green-600">
                      {ranking.metrics.total_return.toFixed(1)}%
                    </div>
                    <div className="text-gray-500">Total Return</div>
                  </div>
                  <div className="text-center">
                    <div className="font-medium">
                      {ranking.metrics.sharpe_ratio.toFixed(2)}
                    </div>
                    <div className="text-gray-500">Sharpe Ratio</div>
                  </div>
                  <div className="text-center">
                    <div className="font-medium text-red-600">
                      {ranking.metrics.max_drawdown.toFixed(1)}%
                    </div>
                    <div className="text-gray-500">Max Drawdown</div>
                  </div>
                  <div className="text-center">
                    <div className="font-medium">
                      {ranking.metrics.win_rate.toFixed(1)}%
                    </div>
                    <div className="text-gray-500">Win Rate</div>
                  </div>
                  <div className="text-center">
                    <div className="font-medium">
                      {ranking.metrics.trades}
                    </div>
                    <div className="text-gray-500">Trades</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}