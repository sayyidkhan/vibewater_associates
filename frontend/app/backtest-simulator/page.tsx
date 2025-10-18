"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Brain, LineChart, Shield, CheckCircle, TrendingUp, Home, ChevronRight, Clock, DollarSign, TrendingUp as TrendingUpIcon, Loader2, ArrowDown, Check, Circle } from "lucide-react";
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
      icon: LineChart,
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
      name: "Risk Validator",
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
    const strategyId = strategyData.strategyId || strategyData.id || 'test-strategy-id';
    
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
  };

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
              <nav className="flex items-center gap-1.5 text-sm">
                <button
                  onClick={() => router.push('/')}
                  className="flex items-center gap-1 text-gray-500 hover:text-primary transition-colors"
                >
                  <Home className="w-3.5 h-3.5" />
                  <span>Dashboard</span>
                </button>
                <ChevronRight className="w-4 h-4 text-gray-600" />
                <button
                  onClick={() => router.push('/builder')}
                  className="text-gray-500 hover:text-primary transition-colors"
                >
                  Strategy Builder
                </button>
                <ChevronRight className="w-4 h-4 text-gray-600" />
                <h1 className="text-lg font-bold text-gray-100">Backtest Simulator</h1>
              </nav>
            </div>
            
            {/* Subtitle */}
            <p className="text-sm text-gray-400 mt-0.5">
              Watch your strategy being analyzed, validated, and backtested in real-time
            </p>
          </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 h-[calc(100vh-110px)]">
          {/* Workflow Visualization Section */}
          <div className="overflow-hidden">
            <Card className="h-full flex flex-col">
              <div className="flex-shrink-0 flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <h2 className="text-lg font-semibold">Agent Workflow</h2>
                  {!isConnected && (
                    <span className="text-xs text-yellow-500">⚠️ Connecting...</span>
                  )}
                  {isConnected && !isRunning && (
                    <span className="text-xs text-green-500">✓ Connected</span>
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
                  <p className="text-sm text-red-400">❌ {executionError}</p>
                </div>
              )}

              <div className="flex-1 flex flex-col justify-between min-h-0">
                {/* Strategy Parameters */}
                {strategyData && (
                  <div className="grid grid-cols-3 gap-2 mb-3 pb-2 border-b border-gray-800">
                    {/* Duration */}
                    <div className="p-1.5 bg-card-hover border border-gray-700 rounded-lg">
                      <div className="flex items-center gap-1 mb-0.5">
                        <Clock className="w-3 h-3 text-primary" />
                        <span className="text-[10px] font-semibold">Duration</span>
                      </div>
                      <p className="text-xs font-bold">{strategyData.duration}</p>
                    </div>

                    {/* Estimated Capital */}
                    <div className="p-1.5 bg-card-hover border border-gray-700 rounded-lg">
                      <div className="flex items-center gap-1 mb-0.5">
                        <DollarSign className="w-3 h-3 text-gray-400" />
                        <span className="text-[10px] font-semibold">Capital</span>
                      </div>
                      <p className="text-xs font-bold">${strategyData.estimatedCapital?.toLocaleString()}</p>
                    </div>

                    {/* Expected Return */}
                    <div className="p-1.5 bg-gradient-to-br from-primary/10 to-primary/5 border border-primary/30 rounded-lg">
                      <div className="flex items-center gap-1 mb-0.5">
                        <TrendingUpIcon className="w-3 h-3 text-primary" />
                        <span className="text-[10px] font-semibold">Returns</span>
                      </div>
                      <p className="text-xs font-bold text-primary">+{strategyData.monthlyReturn}%</p>
                    </div>
                  </div>
                )}

                <div className="flex-1 flex flex-col justify-between">
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
                        className={`relative p-2 rounded-lg border-2 transition-all duration-500 cursor-pointer hover:scale-[1.02] ${
                          isActive
                            ? "border-primary bg-primary/10 shadow-lg shadow-primary/20"
                            : isCompleted
                            ? "border-green-500 bg-green-500/10"
                            : "border-gray-700 bg-card-hover opacity-50"
                        }`}
                      >
                        <div className="flex items-start gap-2">
                          <div
                            className={`p-1.5 rounded-lg transition-all duration-500 ${
                              isActive
                                ? "bg-primary animate-pulse"
                                : isCompleted
                                ? "bg-green-500"
                                : "bg-gray-700"
                            }`}
                            style={{ backgroundColor: isCompleted || isActive ? agent.color : undefined }}
                          >
                            <Icon className="w-4 h-4 text-white" />
                          </div>
                          
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-0.5">
                              <h3 className="text-sm font-semibold">{agent.name}</h3>
                              {isActive && (
                                <div className="relative">
                                  <span className="relative inline-flex items-center gap-1 px-2 py-0.5 bg-gradient-to-r from-primary to-blue-600 text-white text-[10px] font-medium rounded-full shadow-lg shadow-primary/30">
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
                                  <span className="text-[10px] text-green-500 font-medium">Complete</span>
                                </div>
                              )}
                            </div>
                            <p className="text-[10px] text-gray-400">{agent.description}</p>
                          </div>
                        </div>

                        {/* Processing Steps */}
                        {isActive && (
                          <div className="mt-2 pl-2 space-y-1">
                            {agent.steps.filter(step => step && step.trim()).map((step, stepIndex) => {
                              const isCompleteStep = step.includes('✓');
                              const isLastStep = stepIndex === agent.steps.filter(s => s && s.trim()).length - 1;
                              
                              return (
                                <div 
                                  key={stepIndex} 
                                  className={`flex items-center gap-1.5 text-[10px] transition-all duration-300 animate-fade-in ${
                                    isLastStep && !isCompleteStep ? 'text-primary' : 'text-gray-400'
                                  }`}
                                >
                                  {isLastStep && !isCompleteStep ? (
                                    <Loader2 className="w-2.5 h-2.5 text-primary animate-spin" />
                                  ) : (
                                    <CheckCircle className="w-2.5 h-2.5 text-green-500" />
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
                            isActive ? "h-4" : "h-16"
                          } ${
                            isConnectorActive ? "bg-primary" : "bg-gray-700"
                          }`}></div>
                          
                          {/* Status Icon */}
                          <div className={`flex items-center justify-center w-5 h-5 rounded-full transition-all duration-500 z-10 ${
                            isCompleted 
                              ? "bg-green-500 shadow-lg shadow-green-500/30" 
                              : isConnectorActive 
                              ? "bg-primary shadow-lg shadow-primary/30 animate-pulse" 
                              : "bg-gray-700"
                          }`}>
                            {isCompleted ? (
                              <Check className="w-3 h-3 text-white" />
                            ) : isConnectorActive ? (
                              <ArrowDown className="w-3 h-3 text-white animate-bounce" />
                            ) : (
                              <Circle className="w-1.5 h-1.5 text-gray-500 fill-gray-500" />
                            )}
                          </div>
                          
                          {/* Bottom Connector Line - Shorter if next agent is active */}
                          <div className={`w-0.5 transition-all duration-500 ${
                            agents[index + 1]?.status === "active" ? "h-4" : "h-16"
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
              <h2 className="flex-shrink-0 text-lg font-semibold mb-4">Agent Outputs</h2>
              
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
                          <Icon className="w-4 h-4 text-white" />
                        </div>
                        <h3 className="font-semibold text-sm">{agent.name}</h3>
                      </div>
                      
                      {canShowOutput && (
                        <div className="bg-card-hover border border-gray-700 rounded-lg p-3 mb-3">
                          <pre className="text-xs text-gray-300 whitespace-pre-wrap font-mono leading-relaxed">
                            {agent.output}
                          </pre>
                        </div>
                      )}
                      
                      {!canShowOutput && (
                        <div className="bg-card-hover border border-gray-700 rounded-lg p-3 mb-3">
                          <p className="text-xs text-gray-500 italic">Waiting for agent to start...</p>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
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

