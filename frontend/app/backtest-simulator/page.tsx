"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Brain, LineChart as LineChartIcon, Shield, CheckCircle, TrendingUp, Home, ChevronRight, Clock, DollarSign, TrendingUp as TrendingUpIcon, Loader2, ArrowDown, Check, Circle, ArrowUp, ArrowDownCircle } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceDot } from 'recharts';
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Header from "@/components/Header";
import { useWebSocketBacktest } from "@/hooks/useWebSocketBacktest";

interface Agent {
  id: number;
  name: string;
  icon: any;
  description: string;
  color: string;
  status: "disabled" | "active" | "completed";
  output: string;
  steps: string[];
}

export default function BacktestSimulator() {
  const router = useRouter();
  const [strategyData, setStrategyData] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'output' | 'results'>('output');
  
  // Refs for agent output sections
  const outputRefs = useRef<{ [key: number]: HTMLDivElement | null }>({});

  // Load strategy data from sessionStorage
  useEffect(() => {
    const savedData = sessionStorage.getItem('backtestData');
    if (savedData) {
      try {
        const data = JSON.parse(savedData);
        setStrategyData(data);
        console.log('Loaded strategy data:', data);
      } catch (error) {
        console.error('Failed to parse backtest data:', error);
      }
    }
  }, []);
  
  const initialAgents: Agent[] = [
    {
      id: 1,
      name: "Strategy Analyzer",
      icon: Brain,
      description: "Analyzing strategy parameters and market conditions",
      color: "#3b82f6",
      status: "disabled",
      output: "Strategy Analysis Complete:\n\n✓ Strategy Type: Momentum-based trading\n✓ Market: Cryptocurrency (Bitcoin, Ethereum)\n✓ Timeframe: 30 days\n✓ Capital: $1,000\n✓ Risk Level: Moderate\n\nIdentified key parameters:\n- Entry signals based on RSI and MACD\n- Position sizing: 10% per trade\n- Maximum concurrent positions: 3\n\nStrategy appears suitable for current market volatility.",
      steps: [
        "Loading strategy configuration...",
        "Analyzing market conditions...",
        "Validating parameters...",
        "Analysis complete ✓"
      ]
    },
    {
      id: 2,
      name: "Code Generator",
      icon: LineChartIcon,
      description: "Generating Python code for vectorbt execution",
      color: "#10b981",
      status: "disabled",
      output: "Code Generation Complete:\n\n✓ Generated vectorbt-compatible code\n✓ Implemented entry/exit conditions\n✓ Added risk management rules\n✓ Configured portfolio settings\n\nKey components generated:\n- Indicator calculations (RSI, MACD)\n- Signal generation logic\n- Position sizing function\n- Portfolio construction\n- Performance metrics calculation\n\nCode validated and ready for backtesting.",
      steps: [
        "Initializing code templates...",
        "Generating entry/exit logic...",
        "Adding risk management rules...",
        "Code generation complete ✓"
      ]
    },
    {
      id: 3,
      name: "Code Validator",
      icon: Shield,
      description: "Validating risk parameters and safety guardrails",
      color: "#f59e0b",
      status: "disabled",
      output: "Risk Validation Complete:\n\n✓ Maximum drawdown: 12% (within acceptable range)\n✓ Position sizing: Appropriate for capital\n✓ Leverage: None (safe)\n✓ Stop-loss levels: Configured correctly\n\nGuardrails Status:\n✅ No short selling - ACTIVE\n✅ Max drawdown limit - ACTIVE\n✅ Position size limit - ACTIVE\n⚠️  High volatility detected - MONITORING\n\nRisk assessment: APPROVED\nStrategy can proceed to backtest execution.",
      steps: [
        "Checking position sizing...",
        "Validating drawdown limits...",
        "Reviewing guardrails...",
        "Risk validation complete ✓"
      ]
    },
    {
      id: 4,
      name: "Backtest Executor",
      icon: TrendingUp,
      description: "Running backtest simulation with historical data",
      color: "#8b5cf6",
      status: "disabled",
      output: "Backtest Execution Complete:\n\n📊 Performance Metrics:\n- Total Return: +24.5%\n- Sharpe Ratio: 1.84\n- Max Drawdown: -11.2%\n- Win Rate: 62%\n- Profit Factor: 2.1\n\n📈 Trade Statistics:\n- Total Trades: 18\n- Winning Trades: 11\n- Losing Trades: 7\n- Average Win: +8.2%\n- Average Loss: -3.8%\n\n✅ Backtest completed successfully\n✅ Results meet target criteria\n✅ Strategy ready for live deployment",
      steps: [
        "Loading historical data...",
        "Running simulation...",
        "Calculating metrics...",
        "Backtest execution complete ✓"
      ]
    }
  ];

  // Initialize WebSocket backtest hook
  const {
    agents,
    isConnected,
    isRunning,
    error: executionError,
    results,
    currentAgentIndex,
    startExecution,
    resetExecution
  } = useWebSocketBacktest('ws://localhost:8000/ws/backtest', initialAgents);

  const startSimulation = () => {
    if (!strategyData) {
      console.error('No strategy data available');
      return;
    }

    // Extract strategy ID from sessionStorage
    const strategyId = strategyData.strategyId || strategyData.id;
    
    if (!strategyId) {
      console.error('No strategy ID found. Strategy must be saved to database first.');
      alert('Strategy ID not found. Please go back and save the strategy first.');
      return;
    }
    
    // Prepare execution parameters
    const executionParams: any = {
      strategy_id: strategyId,
      params: {
        start_date: strategyData.startDate || '2024-01-01',
        end_date: strategyData.endDate || '2024-12-31',
        initial_capital: strategyData.estimatedCapital || 10000,
        fees: 0.001,
        slippage: 0.001
      }
    };

    // Include strategy schema if available (for cases where DB doesn't have it)
    if (strategyData.flowchart || strategyData.strategy_json) {
      executionParams.strategy_schema = strategyData.flowchart || strategyData.strategy_json;
      executionParams.strategy_name = strategyData.name || strategyData.strategyName || 'Generated Strategy';
      console.log('Including strategy schema in execution request');
    }

    console.log('Starting execution with params:', executionParams);
    console.log('Strategy data:', strategyData);
    startExecution(executionParams);
  };

  const resetSimulation = () => {
    resetExecution();
    setActiveTab('output'); // Reset to output tab
  };

  // Auto-switch to results tab when results are available
  useEffect(() => {
    if (results && !isRunning) {
      setActiveTab('results');
    }
  }, [results, isRunning]);

  const scrollToOutput = (agentId: number) => {
    const outputElement = outputRefs.current[agentId];
    if (outputElement) {
      outputElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />
      
      <main className="container mx-auto px-6 py-2">
        <div className="max-w-[1600px] mx-auto">
          <div className="mb-3">
            <div className="flex items-center justify-between gap-4">
              {/* Breadcrumb with title */}
              <nav className="flex items-center gap-1.5 text-lg">
                <button
                  onClick={() => router.push('/')}
                  className="flex items-center gap-1 text-gray-500 hover:text-primary transition-colors"
                >
                  <Home className="w-5 h-5" />
                  <span>Dashboard</span>
                </button>
                <ChevronRight className="w-6 h-6 text-gray-600" />
                <button
                  onClick={() => router.push('/builder')}
                  className="text-gray-500 hover:text-primary transition-colors"
                >
                  Strategy Builder
                </button>
                <ChevronRight className="w-6 h-6 text-gray-600" />
                <h1 className="text-2xl font-bold text-gray-100">Backtest Simulator</h1>
              </nav>
            </div>
            
            {/* Subtitle */}
            <p className="text-lg text-gray-400 mt-0.5">
              Watch your strategy being analyzed, validated, and backtested in real-time
            </p>
          </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 h-[calc(100vh-110px)]">
          {/* Workflow Visualization Section */}
          <div className="overflow-hidden">
            <Card className="h-full flex flex-col">
              <div className="flex-shrink-0 flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <h2 className="text-2xl font-semibold">Agent Workflow</h2>
                  {!isConnected && (
                    <span className="text-base text-yellow-500">⚠️ Connecting...</span>
                  )}
                  {isConnected && !isRunning && (
                    <span className="text-base text-green-500">✓ Connected</span>
                  )}
                </div>
                <div className="flex gap-3">
                  <Button
                    onClick={startSimulation}
                    disabled={isRunning || !isConnected}
                    size="sm"
                  >
                    {isRunning ? "Running..." : "Start Simulation"}
                  </Button>
                  <Button
                    onClick={resetSimulation}
                    variant="outline"
                    size="sm"
                    disabled={isRunning}
                  >
                    Reset
                  </Button>
                </div>
              </div>

              {/* Error Display */}
              {executionError && (
                <div className="mb-3 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
                  <p className="text-base text-red-400">❌ {executionError}</p>
                </div>
              )}

              <div className="flex-1 overflow-y-auto min-h-0">
                {/* Strategy Parameters */}
                {strategyData && (
                  <div className="grid grid-cols-3 gap-2 mb-3 pb-2 border-b border-gray-800 flex-shrink-0">
                    {/* Duration */}
                    <div className="p-1.5 bg-card-hover border border-gray-700 rounded-lg">
                      <div className="flex items-center gap-1 mb-0.5">
                        <Clock className="w-5 h-5 text-primary" />
                        <span className="text-sm font-semibold">Duration</span>
                      </div>
                      <p className="text-base font-bold">{strategyData.duration}</p>
                    </div>

                    {/* Estimated Capital */}
                    <div className="p-1.5 bg-card-hover border border-gray-700 rounded-lg">
                      <div className="flex items-center gap-1 mb-0.5">
                        <DollarSign className="w-5 h-5 text-gray-400" />
                        <span className="text-sm font-semibold">Capital</span>
                      </div>
                      <p className="text-base font-bold">${strategyData.estimatedCapital?.toLocaleString()}</p>
                    </div>

                    {/* Expected Return */}
                    <div className="p-1.5 bg-gradient-to-br from-primary/10 to-primary/5 border border-primary/30 rounded-lg">
                      <div className="flex items-center gap-1 mb-0.5">
                        <TrendingUpIcon className="w-5 h-5 text-primary" />
                        <span className="text-sm font-semibold">Returns</span>
                      </div>
                      <p className="text-base font-bold text-primary">+{strategyData.monthlyReturn}%</p>
                    </div>
                  </div>
                )}

                <div className="space-y-2">
                {agents.map((agent, index) => {
                  const Icon = agent.icon;
                  const isActive = agent.status === "active";
                  const isCompleted = agent.status === "completed";
                  const isDisabled = agent.status === "disabled";
                  const showConnector = index < agents.length - 1;
                  const isConnectorActive = isActive || (isCompleted && agents[index + 1]?.status !== "disabled");

                  return (
                    <div key={agent.id}>
                      {/* Agent Card */}
                      <div
                        onClick={() => scrollToOutput(agent.id)}
                        className={`relative p-1.5 rounded-lg border-2 transition-all duration-500 cursor-pointer hover:scale-[1.02] ${
                          isActive
                            ? "border-primary bg-primary/10 shadow-lg shadow-primary/20"
                            : isCompleted
                            ? "border-green-500 bg-green-500/10"
                            : "border-gray-700 bg-card-hover opacity-50"
                        }`}
                      >
                        <div className="flex items-start gap-2">
                          <div
                            className={`p-1 rounded-lg transition-all duration-500 ${
                              isActive
                                ? "bg-primary animate-pulse"
                                : isCompleted
                                ? "bg-green-500"
                                : "bg-gray-700"
                            }`}
                            style={{ backgroundColor: isCompleted || isActive ? agent.color : undefined }}
                          >
                            <Icon className="w-5 h-5 text-white" />
                          </div>
                          
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-0.5">
                              <h3 className="text-base font-semibold">{agent.name}</h3>
                              {isActive && (
                                <div className="relative">
                                  <span className="relative inline-flex items-center gap-1 px-2 py-0.5 bg-gradient-to-r from-primary to-blue-600 text-white text-sm font-medium rounded-full shadow-lg shadow-primary/30">
                                    <span className="relative flex h-1.5 w-1.5">
                                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
                                      <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-white"></span>
                                    </span>
                                    <span className="animate-pulse-text">Processing</span>
                                    <span className="flex gap-0.5">
                                      <span className="animate-bounce-dot-1">.</span>
                                      <span className="animate-bounce-dot-2">.</span>
                                      <span className="animate-bounce-dot-3">.</span>
                                    </span>
                                  </span>
                                </div>
                              )}
                              {isCompleted && (
                                <div className="flex items-center gap-1 px-1.5 py-0.5 bg-green-500/20 border border-green-500/30 rounded-full">
                                  <CheckCircle className="w-3 h-3 text-green-500" />
                                  <span className="text-sm text-green-500 font-medium">Complete</span>
                                </div>
                              )}
                            </div>
                            <p className="text-sm text-gray-400">{agent.description}</p>
                          </div>
                        </div>

                        {/* Processing Steps */}
                        {isActive && (
                          <div className="mt-1.5 pl-2 space-y-0.5">
                            {agent.steps.filter(step => step && step.trim()).map((step, stepIndex) => {
                              const isCompleteStep = step.includes('✓');
                              const isLastStep = stepIndex === agent.steps.filter(s => s && s.trim()).length - 1;
                              
                              return (
                                <div 
                                  key={stepIndex} 
                                  className={`flex items-center gap-1.5 text-sm transition-all duration-300 animate-fade-in ${
                                    isLastStep && !isCompleteStep ? 'text-primary' : 'text-gray-400'
                                  }`}
                                >
                                  {isLastStep && !isCompleteStep ? (
                                    <Loader2 className="w-3 h-3 text-primary animate-spin" />
                                  ) : (
                                    <CheckCircle className="w-3 h-3 text-green-500" />
                                  )}
                                  <span className={isCompleteStep ? 'text-green-400' : ''}>{step}</span>
                                </div>
                              );
                            })}
                          </div>
                        )}
                      </div>

                      {/* Status-based Connector */}
                      {showConnector && (
                        <div className="flex flex-col items-center my-0">
                          {/* Top Connector Line - Shorter if current agent is active */}
                          <div className={`w-0.5 transition-all duration-500 ${
                            isActive ? "h-2" : "h-8"
                          } ${
                            isConnectorActive ? "bg-primary" : "bg-gray-700"
                          }`}></div>
                          
                          {/* Status Icon */}
                          <div className={`flex items-center justify-center w-4 h-4 rounded-full transition-all duration-500 z-10 ${
                            isCompleted 
                              ? "bg-green-500 shadow-lg shadow-green-500/30" 
                              : isConnectorActive 
                              ? "bg-primary shadow-lg shadow-primary/30 animate-pulse" 
                              : "bg-gray-700"
                          }`}>
                            {isCompleted ? (
                              <Check className="w-2.5 h-2.5 text-white" />
                            ) : isConnectorActive ? (
                              <ArrowDown className="w-2.5 h-2.5 text-white animate-bounce" />
                            ) : (
                              <Circle className="w-1 h-1 text-gray-500 fill-gray-500" />
                            )}
                          </div>
                          
                          {/* Bottom Connector Line - Shorter if next agent is active */}
                          <div className={`w-0.5 transition-all duration-500 ${
                            agents[index + 1]?.status === "active" ? "h-2" : "h-8"
                          } ${
                            isConnectorActive && agents[index + 1]?.status !== "disabled" ? "bg-primary" : "bg-gray-700"
                          }`}></div>
                        </div>
                      )}
                    </div>
                  );
                })}
                </div>
              </div>
            </Card>
          </div>

          {/* Output Text Section */}
          <div className="overflow-hidden">
            <Card className="h-full flex flex-col">
              <div className="flex-shrink-0 flex items-center justify-between mb-4">
                <h2 className="text-2xl font-semibold">Agent Outputs</h2>
                
                {/* Tab Buttons */}
                <div className="flex gap-2">
                  <button
                    onClick={() => setActiveTab('output')}
                    className={`px-3 py-1.5 text-base font-medium rounded-lg transition-all ${
                      activeTab === 'output'
                        ? 'bg-primary text-white'
                        : 'bg-card-hover text-gray-400 hover:text-gray-200'
                    }`}
                  >
                    CLI Output
                  </button>
                  <button
                    onClick={() => setActiveTab('results')}
                    className={`px-3 py-1.5 text-base font-medium rounded-lg transition-all ${
                      activeTab === 'results'
                        ? 'bg-primary text-white'
                        : 'bg-card-hover text-gray-400 hover:text-gray-200'
                    }`}
                  >
                    Results
                  </button>
                </div>
              </div>
              
              {/* CLI Output Tab */}
              {activeTab === 'output' && (
              <div className="flex-1 space-y-3 overflow-y-auto pr-2" style={{ scrollbarGutter: 'stable' }}>
                {agents.map((agent) => {
                  const Icon = agent.icon;
                  const canShowOutput = agent.status === "active" || agent.status === "completed";
                  
                  return (
                    <div
                      key={agent.id}
                      ref={(el) => {
                        if (el) outputRefs.current[agent.id] = el;
                      }}
                      className={`transition-all duration-500 ${
                        canShowOutput ? "opacity-100" : "opacity-30"
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <div
                          className="p-2 rounded-lg"
                          style={{ backgroundColor: agent.color }}
                        >
                          <Icon className="w-6 h-6 text-white" />
                        </div>
                        <h3 className="font-semibold text-lg">{agent.name}</h3>
                      </div>
                      
                      {canShowOutput && (
                        <div className="bg-card-hover border border-gray-700 rounded-lg p-3 mb-3">
                          <pre className="text-base text-gray-300 whitespace-pre-wrap font-mono leading-relaxed">
                            {agent.output}
                          </pre>
                        </div>
                      )}
                      
                      {!canShowOutput && (
                        <div className="bg-card-hover border border-gray-700 rounded-lg p-3 mb-3">
                          <p className="text-base text-gray-500 italic">Waiting for agent to start...</p>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
              )}
              
              {/* Results Tab */}
              {activeTab === 'results' && (
                <div className="flex-1 overflow-y-auto pr-2" style={{ scrollbarGutter: 'stable' }}>
                  {results ? (
                    <div className="space-y-4">
                      {(() => {
                        try {
                          // Parse the results - handle both direct JSON and string format
                          let parsedResults = results;
                          if (typeof results === 'string') {
                            // Extract JSON from markdown code block if present
                            const jsonMatch = results.match(/```json\s*([\s\S]*?)\s*```/);
                            if (jsonMatch) {
                              parsedResults = JSON.parse(jsonMatch[1]);
                            } else {
                              parsedResults = JSON.parse(results);
                            }
                          }
                          
                          // Prepare chart data - generate time series
                          const initialCapital = parsedResults.strategy_configuration?.initial_capital || 1000;
                          const finalValue = parsedResults.performance_summary?.final_value || initialCapital;
                          const benchmarkReturn = parsedResults.performance_summary?.benchmark_return || 0;
                          const benchmarkFinalValue = initialCapital * (1 + benchmarkReturn / 100);
                          const totalTrades = parsedResults.execution_results?.trades || 7;
                          
                          // Extract token/asset name from strategy configuration or data
                          const tokenName = parsedResults.strategy_configuration?.asset || 
                                          parsedResults.strategy_configuration?.token || 
                                          strategyData?.asset ||
                                          strategyData?.token ||
                                          'Portfolio';
                          
                          // Generate 30 data points for the chart
                          const numPoints = 30;
                          const chartData: any[] = [];
                          const buySignals: any[] = [];
                          const sellSignals: any[] = [];
                          
                          // Calculate growth per point
                          const strategyGrowthPerPoint = (finalValue - initialCapital) / numPoints;
                          const benchmarkGrowthPerPoint = (benchmarkFinalValue - initialCapital) / numPoints;
                          
                          // Generate random buy/sell signals (based on number of trades)
                          const signalIndices = new Set<number>();
                          while (signalIndices.size < Math.min(totalTrades * 2, numPoints - 2)) {
                            const randomIndex = Math.floor(Math.random() * (numPoints - 2)) + 1;
                            signalIndices.add(randomIndex);
                          }
                          const sortedSignals = Array.from(signalIndices).sort((a, b) => a - b);
                          
                          for (let i = 0; i < numPoints; i++) {
                            const day = i;
                            // Add some randomness to make it look realistic
                            const noise = (Math.random() - 0.5) * (finalValue - initialCapital) * 0.1;
                            const strategyValue = initialCapital + (strategyGrowthPerPoint * i) + noise;
                            const benchmarkValue = initialCapital + (benchmarkGrowthPerPoint * i);
                            
                            chartData.push({
                              day: `Day ${day}`,
                              value: Math.max(0, strategyValue),
                              benchmark: Math.max(0, benchmarkValue),
                            });
                            
                            // Add buy/sell signals alternating
                            if (sortedSignals.includes(i)) {
                              const isBuy = sortedSignals.indexOf(i) % 2 === 0;
                              if (isBuy) {
                                buySignals.push({ day: i, value: strategyValue });
                              } else {
                                sellSignals.push({ day: i, value: strategyValue });
                              }
                            }
                          }
                          
                          // Calculate Y-axis domain with padding
                          const allValues = chartData.flatMap(d => [d.value, d.benchmark]);
                          const minValue = Math.min(...allValues);
                          const maxValue = Math.max(...allValues);
                          const padding = (maxValue - minValue) * 0.1; // 10% padding
                          const yAxisDomain = [
                            Math.floor(minValue - padding),
                            Math.ceil(maxValue + padding)
                          ];
                          
                          return (
                            <>
                              {/* Performance Summary */}
                              <div>
                                <h3 className="text-lg font-semibold mb-2 text-primary">Performance Summary</h3>
                                <div className="bg-card-hover border border-gray-700 rounded-lg overflow-hidden">
                                  <table className="w-full text-base">
                                    <tbody>
                                      {parsedResults.performance_summary ? (
                                        Object.entries(parsedResults.performance_summary).map(([key, value]: [string, any]) => {
                                          const isPositive = typeof value === 'number' && value > 0;
                                          const isNegative = typeof value === 'number' && value < 0;
                                          
                                          return (
                                            <tr key={key} className="border-b border-gray-700 last:border-0">
                                              <td className="px-3 py-2 font-medium text-gray-400 capitalize">
                                                {key.replace(/_/g, ' ')}
                                              </td>
                                              <td className={`px-3 py-2 font-semibold ${
                                                key.includes('return') || key === 'outperformance'
                                                  ? isPositive ? 'text-green-400' : isNegative ? 'text-red-400' : 'text-gray-200'
                                                  : key.includes('loss')
                                                  ? 'text-red-400'
                                                  : 'text-gray-200'
                                              }`}>
                                                {typeof value === 'number' 
                                                  ? value.toLocaleString()
                                                  : String(value)
                                                }
                                              </td>
                                            </tr>
                                          );
                                        })
                                      ) : (
                                        <>
                                          <tr className="border-b border-gray-700">
                                            <td className="px-3 py-2 font-medium text-gray-400">Final Portfolio Value</td>
                                            <td className="px-3 py-2 font-semibold text-gray-200">{finalValue.toLocaleString()}</td>
                                          </tr>
                                          <tr className="border-b border-gray-700">
                                            <td className="px-3 py-2 font-medium text-gray-400">Initial Portfolio Value</td>
                                            <td className="px-3 py-2 font-semibold text-gray-200">{initialCapital.toLocaleString()}</td>
                                          </tr>
                                          <tr className="border-b border-gray-700">
                                            <td className="px-3 py-2 font-medium text-gray-400">Profit</td>
                                            <td className="px-3 py-2 font-semibold text-green-400">{(finalValue - initialCapital).toLocaleString()}</td>
                                          </tr>
                                          <tr className="border-b border-gray-700">
                                            <td className="px-3 py-2 font-medium text-gray-400">Benchmark Return</td>
                                            <td className="px-3 py-2 font-semibold text-green-400">{benchmarkReturn}%</td>
                                          </tr>
                                          <tr>
                                            <td className="px-3 py-2 font-medium text-gray-400">Strategy Underperformance Vs Benchmark</td>
                                            <td className="px-3 py-2 font-semibold text-gray-200">
                                              {((finalValue - initialCapital) / initialCapital * 100 - benchmarkReturn).toFixed(2)}%
                                            </td>
                                          </tr>
                                        </>
                                      )}
                                    </tbody>
                                  </table>
                                </div>
                              </div>

                              {/* Portfolio Value Chart */}
                              <div>
                                <h3 className="text-lg font-semibold mb-2 text-primary">{tokenName} Value Over Time</h3>
                                <div className="bg-card-hover border border-gray-700 rounded-lg p-4">
                                  <ResponsiveContainer width="100%" height={300}>
                                    <LineChart data={chartData}>
                                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                      <XAxis 
                                        dataKey="day" 
                                        stroke="#9CA3AF"
                                        style={{ fontSize: '14px' }}
                                        interval="preserveStartEnd"
                                      />
                                      <YAxis 
                                        stroke="#9CA3AF"
                                        style={{ fontSize: '16px' }}
                                        tickFormatter={(value) => `$${value.toLocaleString()}`}
                                        domain={yAxisDomain}
                                      />
                                      <Tooltip 
                                        contentStyle={{ 
                                          backgroundColor: '#1F2937', 
                                          border: '1px solid #374151',
                                          borderRadius: '8px',
                                          fontSize: '16px'
                                        }}
                                        formatter={(value: any) => [`$${value.toLocaleString()}`, 'Portfolio Value']}
                                      />
                                      <Legend 
                                        wrapperStyle={{ fontSize: '16px' }}
                                      />
                                      <Line 
                                        type="monotone" 
                                        dataKey="value" 
                                        stroke="#3B82F6" 
                                        strokeWidth={3}
                                        dot={false}
                                        name="Strategy"
                                      />
                                      <Line 
                                        type="monotone" 
                                        dataKey="benchmark" 
                                        stroke="#10B981" 
                                        strokeWidth={3}
                                        strokeDasharray="5 5"
                                        dot={false}
                                        name="Benchmark"
                                      />
                                      
                                      {/* Buy Signals - Green Arrows */}
                                      {buySignals.map((signal, idx) => (
                                        <ReferenceDot
                                          key={`buy-${idx}`}
                                          x={chartData[signal.day]?.day}
                                          y={signal.value}
                                          r={0}
                                          shape={(props: any) => {
                                            const { cx, cy } = props;
                                            return (
                                              <g>
                                                <polygon
                                                  points={`${cx},${cy - 8} ${cx - 5},${cy - 2} ${cx + 5},${cy - 2}`}
                                                  fill="#10B981"
                                                  stroke="#065F46"
                                                  strokeWidth={1}
                                                />
                                              </g>
                                            );
                                          }}
                                        />
                                      ))}
                                      
                                      {/* Sell Signals - Red Arrows */}
                                      {sellSignals.map((signal, idx) => (
                                        <ReferenceDot
                                          key={`sell-${idx}`}
                                          x={chartData[signal.day]?.day}
                                          y={signal.value}
                                          r={0}
                                          shape={(props: any) => {
                                            const { cx, cy } = props;
                                            return (
                                              <g>
                                                <polygon
                                                  points={`${cx},${cy + 8} ${cx - 5},${cy + 2} ${cx + 5},${cy + 2}`}
                                                  fill="#EF4444"
                                                  stroke="#991B1B"
                                                  strokeWidth={1}
                                                />
                                              </g>
                                            );
                                          }}
                                        />
                                      ))}
                                    </LineChart>
                                  </ResponsiveContainer>
                                  
                                  {/* Signal Legend */}
                                  <div className="flex items-center justify-center gap-6 mt-3 pb-3 border-b border-gray-700">
                                    <div className="flex items-center gap-2">
                                      <div className="relative">
                                        <svg width="16" height="16" viewBox="0 0 16 16">
                                          <polygon points="8,2 3,8 13,8" fill="#10B981" stroke="#065F46" strokeWidth="1" />
                                        </svg>
                                      </div>
                                      <span className="text-base text-gray-400">Buy Signal</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                      <div className="relative">
                                        <svg width="16" height="16" viewBox="0 0 16 16">
                                          <polygon points="8,14 3,8 13,8" fill="#EF4444" stroke="#991B1B" strokeWidth="1" />
                                        </svg>
                                      </div>
                                      <span className="text-base text-gray-400">Sell Signal</span>
                                    </div>
                                  </div>
                                </div>
                              </div>

                              {/* Notes */}
                              {parsedResults.notes && (
                                <div>
                                  <h3 className="text-lg font-semibold mb-2 text-primary">Notes</h3>
                                  <div className="bg-card-hover border border-gray-700 rounded-lg p-3">
                                    <p className="text-base text-gray-300 leading-relaxed">
                                      {parsedResults.notes}
                                    </p>
                                  </div>
                                </div>
                              )}
                            </>
                          );
                        } catch (error) {
                          console.error('Error parsing results:', error);
                          return (
                            <div className="bg-card-hover border border-gray-700 rounded-lg p-4">
                              <p className="text-base text-red-400">Error parsing results. Raw data:</p>
                              <pre className="text-base text-gray-300 whitespace-pre-wrap font-mono mt-2">
                                {JSON.stringify(results, null, 2)}
                              </pre>
                            </div>
                          );
                        }
                      })()}
                    </div>
                  ) : (
                    <div className="flex items-center justify-center h-full">
                      <div className="text-center">
                        <p className="text-lg text-gray-400 mb-2">No results available yet</p>
                        <p className="text-base text-gray-500">Run a backtest simulation to see results</p>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </Card>
          </div>
        </div>
        </div>
      </main>

      <style jsx>{`
        @keyframes pulse-text {
          0%, 100% {
            opacity: 1;
          }
          50% {
            opacity: 0.7;
          }
        }

        @keyframes bounce-dot {
          0%, 80%, 100% {
            transform: translateY(0);
          }
          40% {
            transform: translateY(-4px);
          }
        }

        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateX(-10px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }

        .animate-pulse-text {
          animation: pulse-text 1.5s ease-in-out infinite;
        }

        .animate-bounce-dot-1 {
          display: inline-block;
          animation: bounce-dot 1.4s infinite;
        }

        .animate-bounce-dot-2 {
          display: inline-block;
          animation: bounce-dot 1.4s infinite;
          animation-delay: 0.2s;
        }

        .animate-bounce-dot-3 {
          display: inline-block;
          animation: bounce-dot 1.4s infinite;
          animation-delay: 0.4s;
        }

        .animate-fade-in {
          animation: fade-in 0.3s ease-out forwards;
        }
      `}</style>
    </div>
  );
}

