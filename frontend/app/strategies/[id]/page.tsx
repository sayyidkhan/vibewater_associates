"use client";

import { useState, useEffect } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Scatter, ScatterChart, ComposedChart } from "recharts";
import { Download, Image as ImageIcon, Link as LinkIcon, Calendar } from "lucide-react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { getStrategy, getStrategyBacktests, getStrategyTrades } from "@/lib/api";
import { formatCurrency, formatPercentage, formatDate } from "@/lib/utils";
import type { Strategy, BacktestRun, Trade } from "@/types";

export default function StrategyDetailPage({ params }: { params: { id: string } }) {
  const [strategy, setStrategy] = useState<Strategy | null>(null);
  const [backtest, setBacktest] = useState<BacktestRun | null>(null);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [timeframe, setTimeframe] = useState("1M");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStrategyData();
  }, [params.id]);

  const loadStrategyData = async () => {
    try {
      setLoading(true);
      const strategyData = await getStrategy(params.id);
      setStrategy(strategyData);

      const backtests = await getStrategyBacktests(params.id);
      if (backtests.length > 0) {
        // Get the most recent backtest (first one, sorted by newest)
        const latestBacktest = backtests[0];
        console.log("Loaded backtest with", latestBacktest.equity_series.length, "equity points");
        console.log("First equity point:", latestBacktest.equity_series[0]);
        console.log("Last equity point:", latestBacktest.equity_series[latestBacktest.equity_series.length - 1]);
        setBacktest(latestBacktest);
        setTrades(latestBacktest.trades || []);
      }

      // const tradesData = await getStrategyTrades(params.id);
      // setTrades(tradesData);
    } catch (error) {
      console.error("Failed to load strategy:", error);
      // Use mock data for demo
      setStrategy(mockStrategy);
      setBacktest(mockBacktest);
      setTrades(mockTrades);
    } finally {
      setLoading(false);
    }
  };

  // Prepare chart data with trade markers on BTC price
  const prepareChartData = () => {
    if (!backtest) return { priceData: [], buyTrades: [], sellTrades: [] };
    
    // Extract Bitcoin prices from equity series
    const rawData = backtest.equity_series.map(point => ({
      date: point.date,
      btcPrice: point.btc_price || 0,
    }));

    // Check if data is in reverse order
    const firstDate = new Date(rawData[0]?.date || 0);
    const lastDate = new Date(rawData[rawData.length - 1]?.date || 0);
    const isReversed = firstDate > lastDate;

    console.log("Raw data - First date:", rawData[0]?.date, "Last date:", rawData[rawData.length - 1]?.date);
    console.log("Is reversed?", isReversed);

    // Sort by date ascending (earliest to latest) and add index for ordering
    const priceData = [...rawData]
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
      .map((point, index) => ({
        ...point,
        index: index, // Add explicit index for X-axis ordering
        displayDate: point.date, // Keep original date for display
      }));

    console.log("Sorted data - First date:", priceData[0]?.date, "Last date:", priceData[priceData.length - 1]?.date);
    console.log("Equity data points:", priceData.length);
    console.log("Total trades:", trades.length);
    console.log("Sample BTC prices (first 3):", priceData.slice(0, 3));

    // Map trades to their prices and find their index in priceData
    const buyTrades = trades.filter(t => t.type === "BUY").map(t => {
      const tradeDate = t.date.split('T')[0];
      const index = priceData.findIndex(p => p.displayDate === tradeDate);
      return {
        index: index,
        btcPrice: t.price,
        type: "BUY",
      };
    }).filter(t => t.index >= 0);

    const sellTrades = trades.filter(t => t.type === "SELL").map(t => {
      const tradeDate = t.date.split('T')[0];
      const index = priceData.findIndex(p => p.displayDate === tradeDate);
      return {
        index: index,
        btcPrice: t.price,
        type: "SELL",
      };
    }).filter(t => t.index >= 0);

    console.log("Buy trades:", buyTrades.length, buyTrades);
    console.log("Sell trades:", sellTrades.length, sellTrades);

    return { priceData, buyTrades, sellTrades };
  };

  const chartData = prepareChartData();

  if (loading) {
    return (
      <div className="container mx-auto px-6 py-8">
        <div className="text-center py-12 text-gray-400">Loading strategy...</div>
      </div>
    );
  }

  if (!strategy || !backtest) {
    return (
      <div className="container mx-auto px-6 py-8">
        <div className="text-center py-12 text-gray-400">Strategy not found</div>
      </div>
    );
  }

  const metrics = backtest.metrics;

  return (
    <div className="container mx-auto px-6 py-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Bitcoin (BTC) Performance</h1>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <Card>
            <p className="text-sm text-gray-400 mb-1">Total Amount Invested</p>
            <p className="text-2xl font-bold">{formatCurrency(metrics.total_amount_invested)}</p>
          </Card>
          <Card>
            <p className="text-sm text-gray-400 mb-1">Total Gain ()</p>
            <p className="text-2xl font-bold text-success">{formatCurrency(metrics.total_gain)}</p>
          </Card>
          <Card>
            <p className="text-sm text-gray-400 mb-1">Total Lost ()</p>
            <p className="text-2xl font-bold text-danger">{formatCurrency(metrics.total_loss)}</p>
          </Card>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4 mb-6">
          <Card>
            <p className="text-xs text-gray-400 mb-1">Total Return</p>
            <p className="text-xl font-bold text-success">{formatPercentage(metrics.total_return)}</p>
          </Card>
          <Card>
            <p className="text-xs text-gray-400 mb-1">CAGR</p>
            <p className="text-xl font-bold">{formatPercentage(metrics.cagr)}</p>
          </Card>
          <Card>
            <p className="text-xs text-gray-400 mb-1">Sharpe Ratio</p>
            <p className="text-xl font-bold">{metrics.sharpe_ratio.toFixed(1)}</p>
          </Card>
          <Card>
            <p className="text-xs text-gray-400 mb-1">Max Drawdown</p>
            <p className="text-xl font-bold text-danger">{formatPercentage(metrics.max_drawdown)}</p>
          </Card>
          <Card>
            <p className="text-xs text-gray-400 mb-1">Win Rate</p>
            <p className="text-xl font-bold">{metrics.win_rate}%</p>
          </Card>
          <Card>
            <p className="text-xs text-gray-400 mb-1">Trades</p>
            <p className="text-xl font-bold">{metrics.trades}</p>
          </Card>
          <Card>
            <p className="text-xs text-gray-400 mb-1">vs USD</p>
            <p className="text-xl font-bold text-success">{formatPercentage(metrics.vs_benchmark)}</p>
          </Card>
        </div>

        {/* Timeframe and Options */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex gap-2">
            {["1M", "3M", "YTD", "1Y", "Max"].map((tf) => (
              <Button
                key={tf}
                variant={timeframe === tf ? "primary" : "outline"}
                size="sm"
                onClick={() => setTimeframe(tf)}
              >
                {tf}
              </Button>
            ))}
            <Button variant="outline" size="sm">
              <Calendar className="w-4 h-4 mr-2" />
              Custom
            </Button>
          </div>

          <div className="flex items-center gap-4 text-sm">
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" className="rounded" defaultChecked />
              <span>Benchmark (USD)</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" className="rounded" defaultChecked />
              <span>Gas Fees/Slippage</span>
            </label>
            <select className="bg-card border border-gray-700 rounded px-3 py-1">
              <option>Position Sizing</option>
            </select>
            <select className="bg-card border border-gray-700 rounded px-3 py-1">
              <option>Exposure</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Charts */}
          <div className="lg:col-span-2 space-y-6">
            {/* Equity Curve */}
            <Card>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-lg font-semibold">Cumulative Equity</h2>
                  <p className="text-sm text-gray-400">As of today</p>
                </div>
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-primary"></div>
                    <span className="text-sm">Portfolio Value</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-success"></div>
                    <span className="text-sm">Buy</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-danger"></div>
                    <span className="text-sm">Sell</span>
                  </div>
                </div>
              </div>

              <ResponsiveContainer width="100%" height={350}>
                <ComposedChart data={chartData.priceData} margin={{ bottom: 40 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis 
                    dataKey="index"
                    type="number"
                    domain={[0, chartData.priceData.length - 1]}
                    ticks={[0, 10, 20, 30, 40, 50, 60, 70, 80, 89]}
                    stroke="#9CA3AF" 
                    tick={{ fontSize: 11, fill: '#9CA3AF' }}
                    tickFormatter={(index) => {
                      const point = chartData.priceData[index];
                      if (!point) return '';
                      const parts = point.displayDate.split('-');
                      if (parts.length === 3) {
                        return `${parts[1]}/${parts[2]}`;
                      }
                      return '';
                    }}
                  />
                  <YAxis 
                    stroke="#9CA3AF" 
                    tick={{ fontSize: 12, fill: '#9CA3AF' }}
                    domain={['dataMin - 5000', 'dataMax + 5000']}
                    tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#1A1F2E",
                      border: "1px solid #374151",
                      borderRadius: "8px",
                    }}
                    formatter={(value: any) => [`$${value.toLocaleString()}`, 'BTC Price']}
                  />
                  <Line
                    type="monotone"
                    dataKey="btcPrice"
                    stroke="#3B82F6"
                    strokeWidth={2}
                    dot={(props: any) => {
                      const { cx, cy, payload } = props;
                      // Check if this point is a buy or sell
                      const isBuy = chartData.buyTrades.some(t => t.index === payload.index);
                      const isSell = chartData.sellTrades.some(t => t.index === payload.index);
                      
                      if (isBuy) {
                        return <circle cx={cx} cy={cy} r={7} fill="#10B981" stroke="#fff" strokeWidth={2} />;
                      }
                      if (isSell) {
                        return <circle cx={cx} cy={cy} r={7} fill="#EF4444" stroke="#fff" strokeWidth={2} />;
                      }
                      return <g />;
                    }}
                    name="BTC Price (USD)"
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </Card>

            {/* Drawdown */}
            <Card>
              <h2 className="text-lg font-semibold mb-4">Drawdown</h2>
              <div className="h-24 bg-gradient-to-r from-danger/50 to-danger/20 rounded-lg mb-4"></div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Max Drawdown: {formatPercentage(metrics.max_drawdown)}</span>
                <span className="text-gray-400">
                  Longest Duration: {metrics.max_drawdown_duration} days
                </span>
              </div>
            </Card>
          </div>

          {/* Right Column - Trades and Monthly Returns */}
          <div className="space-y-6">
            {/* Recent Trades */}
            <Card>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Bitcoin (BTC) Trades</h2>
                <button className="text-sm text-primary hover:underline">View All</button>
              </div>

              <div className="space-y-3">
                {trades.slice(0, 3).map((trade) => (
                  <div key={trade.id} className="border-b border-gray-800 pb-3 last:border-0">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium">{trade.type} BTC</span>
                      <span
                        className={trade.return && trade.return > 0 ? "text-success" : "text-danger"}
                      >
                        {trade.return ? formatPercentage(trade.return) : ""}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-sm text-gray-400">
                      <span>{formatDate(trade.date)}</span>
                      <span>{formatCurrency(trade.amount)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Monthly Returns Heatmap */}
            <Card>
              <h2 className="text-lg font-semibold mb-4">BTC Monthly Returns (%)</h2>
              <div className="space-y-2">
                {mockMonthlyReturns.map((row, i) => (
                  <div key={i} className="flex gap-2">
                    <span className="text-xs text-gray-400 w-8">{row.month}</span>
                    <div className="flex-1 grid grid-cols-5 gap-1">
                      {row.values.map((value, j) => (
                        <div
                          key={j}
                          className={`h-8 rounded flex items-center justify-center text-xs font-medium ${
                            value > 0
                              ? "bg-success/30 text-success"
                              : value < 0
                              ? "bg-danger/30 text-danger"
                              : "bg-gray-700 text-gray-400"
                          }`}
                        >
                          {value.toFixed(1)}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
                <div className="flex gap-2 pt-2">
                  <span className="w-8"></span>
                  <div className="flex-1 grid grid-cols-5 gap-1 text-xs text-gray-400 text-center">
                    {["2020", "2021", "2022", "2023", "2024"].map((year) => (
                      <span key={year}>{year}</span>
                    ))}
                  </div>
                </div>
              </div>
              <p className="text-xs text-gray-500 text-center mt-4">Click cell to zoom</p>
            </Card>
          </div>
        </div>

        {/* Export Options */}
        <div className="flex items-center justify-center gap-4 mt-8">
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export CSV
          </Button>
          <Button variant="outline">
            <ImageIcon className="w-4 h-4 mr-2" />
            Export PNG
          </Button>
          <Button variant="outline">
            <LinkIcon className="w-4 h-4 mr-2" />
            Permalink
          </Button>
        </div>
      </div>
    </div>
  );
}

// Mock data
const mockStrategy: Strategy = {
  id: "1",
  user_id: "user1",
  name: "Bitcoin (BTC) Performance",
  description: "Bitcoin trading strategy",
  status: "Live",
  schema_json: { nodes: [], connections: [] },
  guardrails: [],
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

const mockBacktest: BacktestRun = {
  id: "1",
  strategy_id: "1",
  params: {
    symbols: ["BTC"],
    timeframe: "1D",
    start_date: "2020-01-01",
    end_date: "2024-12-31",
    initial_capital: 100000,
    benchmark: "USD",
    fees: 0.001,
    slippage: 0.0005,
    position_sizing: "fixed",
    exposure: 1.0,
  },
  metrics: {
    total_amount_invested: 100000,
    total_gain: 15200,
    total_loss: 5100,
    total_return: 15.2,
    cagr: 8.5,
    sharpe_ratio: 1.2,
    max_drawdown: -7.3,
    max_drawdown_duration: 45,
    win_rate: 62,
    trades: 125,
    vs_benchmark: 3.1,
  },
  equity_series: Array.from({ length: 50 }, (_, i) => ({
    date: `2024-${String(Math.floor(i / 4) + 1).padStart(2, "0")}-${String((i % 4) * 7 + 1).padStart(2, "0")}`,
    value: 100000 + Math.random() * 20000 - 5000 + i * 300,
    benchmark: 100000 + i * 200,
  })),
  drawdown_series: [],
  monthly_returns: [],
  trades: [],
  created_at: new Date().toISOString(),
};

const mockTrades: Trade[] = [
  {
    id: "1",
    date: "2024-01-15",
    type: "BUY",
    symbol: "BTC",
    price: 62650,
    quantity: 0.15,
    amount: 62650,
    return: 12.5,
  },
  {
    id: "2",
    date: "2024-01-12",
    type: "SELL",
    symbol: "BTC",
    price: 59500,
    quantity: 0.15,
    amount: 59500,
    return: -5.2,
  },
  {
    id: "3",
    date: "2024-01-10",
    type: "BUY",
    symbol: "BTC",
    price: 60650.75,
    quantity: 0.15,
    amount: 60650.75,
    return: 8.1,
  },
];

const mockMonthlyReturns = [
  { month: "Jan", values: [5.2, 1.2, -1.2, 3.4, 2.1] },
  { month: "Feb", values: [3.1, -2.5, 2.5, -0.5, 1.8] },
  { month: "Mar", values: [-4.5, 5.8, 0.8, 1.0, -0.3] },
  { month: "Apr", values: [10.3, 7.1, -1.8, -2.3, 3.2] },
  { month: "May", values: [1.5, -15.2, 3.2, 0.2, -1.1] },
  { month: "Jun", values: [0.5, -6.7, -12.1, 4.1, 2.5] },
  { month: "Jul", values: [2.8, 2.9, 1.1, -0.8, 1.9] },
  { month: "Aug", values: [-3.1, -0.9, -5.4, 2.7, 0.8] },
  { month: "Sep", values: [6.2, 4.3, -3.3, 1.5, -0.2] },
  { month: "Oct", values: [1.9, 20.1, 6.5, -0.1, 3.1] },
  { month: "Nov", values: [8.2, -7.5, -2.2, 3.9, 2.8] },
  { month: "Dec", values: [4.7, 3.1, 0.9, -1.1, 1.5] },
];
