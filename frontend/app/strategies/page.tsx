"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { ChevronDown, Share2, Copy, ExternalLink } from "lucide-react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { getStrategies } from "@/lib/api";
import { formatPercentage } from "@/lib/utils";
import type { Strategy } from "@/types";

export default function StrategiesPage() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    performance: "all",
    risk: "all",
    turnover: "all",
    exchange: "all",
    tradingType: "all",
  });

  useEffect(() => {
    loadStrategies();
  }, [filters]);

  const loadStrategies = async () => {
    try {
      setLoading(true);
      const data = await getStrategies(filters);
      setStrategies(data);
    } catch (error) {
      console.error("Failed to load strategies:", error);
      // Use mock data for demo
      setStrategies(mockStrategies);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      Live: "bg-success/20 text-success border-success/30",
      Paper: "bg-warning/20 text-warning border-warning/30",
      Backtest: "bg-gray-700/50 text-gray-300 border-gray-600",
    };
    return styles[status as keyof typeof styles] || styles.Backtest;
  };

  return (
    <div className="container mx-auto px-6 py-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">My Strategies</h1>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-3 mb-6">
          {Object.entries({
            Performance: ["all", "high", "medium", "low"],
            Risk: ["all", "low", "medium", "high"],
            Turnover: ["all", "high", "medium", "low"],
            Exchange: ["all", "NYSE", "NASDAQ", "Crypto"],
            "Trading Type": ["all", "day", "swing", "position"],
          }).map(([label, options]) => (
            <div key={label} className="relative">
              <select
                className="appearance-none bg-card border border-gray-700 rounded-lg px-4 py-2 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-primary cursor-pointer"
                onChange={(e) =>
                  setFilters((prev) => ({
                    ...prev,
                    [label.toLowerCase().replace(" ", "")]: e.target.value,
                  }))
                }
              >
                {options.map((option) => (
                  <option key={option} value={option}>
                    {label}: {option.charAt(0).toUpperCase() + option.slice(1)}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none" />
            </div>
          ))}
        </div>

        {/* Strategies List */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">All Strategies</h2>

          {loading ? (
            <div className="text-center py-12 text-gray-400">Loading strategies...</div>
          ) : strategies.length === 0 ? (
            <Card className="text-center py-12">
              <p className="text-gray-400 mb-4">No strategies found</p>
              <Link href="/">
                <Button>Create Your First Strategy</Button>
              </Link>
            </Card>
          ) : (
            strategies.map((strategy) => (
              <Card key={strategy.id} className="hover:bg-card-hover transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-sm text-gray-500">Strategy {strategy.id}</span>
                      <span
                        className={`px-2 py-1 rounded-full text-xs border ${getStatusBadge(
                          strategy.status
                        )}`}
                      >
                        {strategy.status}
                      </span>
                    </div>

                    <h3 className="text-xl font-semibold mb-2">{strategy.name}</h3>
                    <p className="text-gray-400 text-sm mb-4">{strategy.description}</p>

                    {strategy.metrics && (
                      <div className="flex gap-6 text-sm">
                        <div>
                          <span className="text-gray-400">P/L: </span>
                          <span
                            className={
                              strategy.metrics.total_return >= 0 ? "text-success" : "text-danger"
                            }
                          >
                            {formatPercentage(strategy.metrics.total_return)}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-400">Sharpe: </span>
                          <span>{strategy.metrics.sharpe_ratio.toFixed(1)}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Drawdown: </span>
                          <span className="text-danger">
                            {formatPercentage(strategy.metrics.max_drawdown)}
                          </span>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="flex items-start gap-2 ml-4">
                    <button
                      className="p-2 hover:bg-card-hover rounded-lg transition-colors"
                      title="Share"
                    >
                      <Share2 className="w-4 h-4" />
                    </button>
                    <button
                      className="p-2 hover:bg-card-hover rounded-lg transition-colors"
                      title="Duplicate"
                    >
                      <Copy className="w-4 h-4" />
                    </button>
                    <Link href={`/strategies/${strategy.id}`}>
                      <button
                        className="p-2 hover:bg-card-hover rounded-lg transition-colors"
                        title="Open"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </button>
                    </Link>
                  </div>

                  <div className="ml-4 w-64 h-32 bg-gradient-to-br from-amber-900/20 to-amber-700/10 rounded-lg" />
                </div>
              </Card>
            ))
          )}
        </div>

        {/* Pagination */}
        {strategies.length > 0 && (
          <div className="flex items-center justify-center gap-2 mt-8">
            <Button variant="outline" size="sm">
              &larr;
            </Button>
            {[1, 2, 3, "...", 10].map((page, index) => (
              <Button
                key={index}
                variant={page === 1 ? "primary" : "outline"}
                size="sm"
                className="min-w-[40px]"
              >
                {page}
              </Button>
            ))}
            <Button variant="outline" size="sm">
              &rarr;
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}

// Mock data for demo
const mockStrategies: Strategy[] = [
  {
    id: "1",
    user_id: "user1",
    name: "Buy low, sell high",
    description: "A simple strategy that buys when the price is low and sells when the price is high.",
    status: "Live",
    schema_json: { nodes: [], connections: [] },
    guardrails: [],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    metrics: {
      total_return: 12.5,
      cagr: 8.5,
      sharpe_ratio: 1.8,
      max_drawdown: -5.2,
      win_rate: 62,
      trades: 125,
      vs_benchmark: 3.1,
    },
  },
  {
    id: "2",
    user_id: "user1",
    name: "Trend following",
    description: "A strategy that follows the trend of the market, buying when the trend is up and selling when the trend is down.",
    status: "Paper",
    schema_json: { nodes: [], connections: [] },
    guardrails: [],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    metrics: {
      total_return: 25.1,
      cagr: 18.3,
      sharpe_ratio: 2.3,
      max_drawdown: -8.9,
      win_rate: 58,
      trades: 87,
      vs_benchmark: 5.2,
    },
  },
  {
    id: "3",
    user_id: "user1",
    name: "Mean reversion",
    description: "A strategy that bets on the price reverting to its mean, buying when the price is below the mean and selling when the price is above the mean.",
    status: "Backtest",
    schema_json: { nodes: [], connections: [] },
    guardrails: [],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    metrics: {
      total_return: -2.3,
      cagr: -1.5,
      sharpe_ratio: -0.4,
      max_drawdown: -15.7,
      win_rate: 45,
      trades: 203,
      vs_benchmark: -8.1,
    },
  },
];
