"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Send, Lightbulb, TrendingUp, ArrowLeftRight, TrendingDown, Wifi, WifiOff, Plus, Clock, Sparkles, Zap, Target, Shield, DollarSign, Brain, Check } from "lucide-react";
import ReactMarkdown from "react-markdown";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { useWebSocketChat } from "@/hooks/useWebSocketChat";
import type { ParsedStrategy, ChatMessage, Guardrail } from "@/types";

// Load initial state from sessionStorage before component renders
const getInitialState = () => {
  if (typeof window === 'undefined') return { messages: [], parsedStrategy: null, strategyJson: null };
  
  try {
    // Check if we're coming from breadcrumb navigation
    const fromBreadcrumb = sessionStorage.getItem('fromBreadcrumb');
    
    // Clear the flag immediately
    if (fromBreadcrumb) {
      sessionStorage.removeItem('fromBreadcrumb');
    }
    
    // Only load saved state if coming from breadcrumb
    if (!fromBreadcrumb) {
      // Clear session storage on fresh load/menu navigation
      sessionStorage.removeItem('dashboardState');
      sessionStorage.removeItem('builderState');
      return { messages: [], parsedStrategy: null, strategyJson: null };
    }
    
    const savedState = sessionStorage.getItem('dashboardState');
    if (!savedState) {
      return { messages: [], parsedStrategy: null, strategyJson: null };
    }
    
    const state = JSON.parse(savedState);
    const messages = Array.isArray(state.messages) ? state.messages : [];
    
    let parsedStrategy = null;
    let strategyJson = null;
    
    if (state.strategyJson && typeof state.strategyJson === 'object') {
      strategyJson = state.strategyJson;
      
      try {
        parsedStrategy = {
        strategy_schema: {
          nodes: strategyJson.flowchart?.nodes || [],
          connections: strategyJson.flowchart?.edges?.map((edge: any, i: number) => ({
            id: `e${i}`,
            source: edge[0],
            target: edge[1]
          })) || []
        },
        guardrails: strategyJson.guardrails?.enabled?.map((g: any) => ({
          type: g.key,
          level: g.status === "ok" ? "info" : g.status === "warning" ? "warning" : "error",
          message: g.label
        })) || [],
        rationale: strategyJson.assistant_panel?.assistant_reply || "Strategy created",
        estimated_return: strategyJson.strategy_metrics?.impact_monthly_return_delta_pct || 0,
        required_capital: strategyJson.strategy_metrics?.estimated_capital_required_usd || 0,
        duration: strategyJson.strategy_metrics?.duration || "30 days"
        };
      } catch (parseError) {
        console.error('Failed to parse strategy JSON:', parseError);
      }
    }
    
    return { messages, parsedStrategy, strategyJson };
  } catch (error) {
    console.error('Failed to load dashboard state:', error);
    return { messages: [], parsedStrategy: null, strategyJson: null };
  }
};

export default function Dashboard() {
  const router = useRouter();
  const [input, setInput] = useState("");
  const initialStateRef = useRef(getInitialState());
  const [parsedStrategy, setParsedStrategy] = useState<ParsedStrategy | null>(() => initialStateRef.current.parsedStrategy);
  const [savedStrategyJson, setSavedStrategyJson] = useState<any>(initialStateRef.current.strategyJson);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [currentStep, setCurrentStep] = useState(0);
  
  // Use WebSocket hook with initial messages
  const { messages, isConnected, isLoading, error, strategyJson, streamingMessage, sendMessage } = useWebSocketChat(
    'ws://localhost:8000/ws/chat',
    initialStateRef.current.messages
  );
  
  // Use saved strategyJson if websocket hasn't provided one yet
  const activeStrategyJson = strategyJson || savedStrategyJson;
  
  // Progressive step animation with sub-steps
  const [subStepText, setSubStepText] = useState("");
  
  useEffect(() => {
    if (isLoading) {
      setCurrentStep(0);
      setSubStepText("");
      
      // Step 1 substeps
      const step1Texts = [
        "Scanning market indicators...",
        "Analyzing price movements...",
        "Identifying trend patterns...",
      ];
      
      // Step 2 substeps
      const step2Texts = [
        "Calculating risk tolerance...",
        "Setting stop-loss parameters...",
        "Configuring position sizing...",
      ];
      
      // Step 3 substeps
      const step3Texts = [
        "Optimizing entry points...",
        "Computing expected returns...",
        "Finalizing strategy parameters...",
      ];
      
      let stepTextIndex = 0;
      let currentStepLocal = 0;
      
      // Change substep text faster
      const textInterval = setInterval(() => {
        if (currentStepLocal === 0) {
          setSubStepText(step1Texts[stepTextIndex % step1Texts.length]);
        } else if (currentStepLocal === 1) {
          setSubStepText(step2Texts[stepTextIndex % step2Texts.length]);
        } else if (currentStepLocal === 2) {
          setSubStepText(step3Texts[stepTextIndex % step3Texts.length]);
        }
        stepTextIndex++;
      }, 1000); // Change text every 1 second
      
      // Change main step every 3.5 seconds (more balanced timing)
      const stepInterval = setInterval(() => {
        currentStepLocal++;
        setCurrentStep(prev => {
          if (prev < 2) return prev + 1;
          return prev;
        });
        stepTextIndex = 0; // Reset text index for new step
        
        if (currentStepLocal > 2) {
          clearInterval(textInterval);
          clearInterval(stepInterval);
        }
      }, 3500); // Increased from 2.5s to 3.5s
      
      return () => {
        clearInterval(textInterval);
        clearInterval(stepInterval);
      };
    } else {
      setSubStepText("");
    }
  }, [isLoading]);
  
  // Auto-scroll to bottom when messages change or streaming updates
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingMessage, isLoading]);
  
  // Update parsed strategy when strategyJson changes
  useEffect(() => {
    if (activeStrategyJson) {
      // Convert strategyJson to ParsedStrategy format
      const parsed: ParsedStrategy = {
        strategy_schema: {
          nodes: activeStrategyJson.flowchart?.nodes || [],
          connections: activeStrategyJson.flowchart?.edges?.map((edge: any, i: number) => ({
            id: `e${i}`,
            source: edge[0],
            target: edge[1]
          })) || []
        },
        guardrails: activeStrategyJson.guardrails?.enabled?.map((g: any) => ({
          type: g.key,
          level: g.status === "ok" ? "info" : g.status === "warning" ? "warning" : "error",
          message: g.label
        })) || [],
        rationale: activeStrategyJson.assistant_panel?.assistant_reply || "Strategy created",
        estimated_return: activeStrategyJson.strategy_metrics?.impact_monthly_return_delta_pct || 0,
        required_capital: activeStrategyJson.strategy_metrics?.estimated_capital_required_usd || 0,
        duration: activeStrategyJson.strategy_metrics?.duration || "30 days"
      };
      setParsedStrategy(parsed);
    }
  }, [activeStrategyJson]);
  
  // Update savedStrategyJson when new strategyJson arrives from WebSocket
  useEffect(() => {
    if (strategyJson) {
      setSavedStrategyJson(strategyJson);
    }
  }, [strategyJson]);
  
  // Auto-save state to sessionStorage for seamless navigation
  useEffect(() => {
    // Only save if we have actual data (not just empty initial state)
    if (messages.length > 0 && activeStrategyJson) {
      const state = {
        strategyJson: activeStrategyJson,
        messages: messages,
        parsedStrategy: parsedStrategy
      };
      sessionStorage.setItem('dashboardState', JSON.stringify(state));
      sessionStorage.setItem('builderState', JSON.stringify(state));
    }
  }, [messages, activeStrategyJson, parsedStrategy]);

  const examples = [
    { label: "Momentum", icon: TrendingUp },
    { label: "Mean Reversion", icon: ArrowLeftRight },
    { label: "Arbitrage", icon: TrendingDown },
    { label: "Long/Short", icon: Lightbulb },
  ];

  const handleSend = () => {
    if (!input.trim() || isLoading || !isConnected) return;
    sendMessage(input);
    setInput("");
  };

  const handleExampleClick = (example: string) => {
    setInput(`I have $1000, please choose for me the right strategy that gives at least 7% returns monthly. Strategy type: ${example}`);
  };
  
  const handleAddStrategy = () => {
    // Clear session when creating a new strategy
    sessionStorage.removeItem('dashboardState');
    sessionStorage.removeItem('builderState');
    sessionStorage.removeItem('fromBreadcrumb');
    router.push('/builder');
  };

  const getGuardrailIcon = (level: string) => {
    switch (level) {
      case "error":
        return "⛔";
      case "warning":
        return "⚠️";
      default:
        return "✅";
    }
  };
  
  const handleBuildStrategy = () => {
    // Pass the strategy data and messages to the builder page
    const state = {
      strategyJson: activeStrategyJson,
      messages: messages,
      parsedStrategy: parsedStrategy
    };
    
    // Store in both for bidirectional navigation
    sessionStorage.setItem('builderState', JSON.stringify(state));
    sessionStorage.setItem('dashboardState', JSON.stringify(state));
    router.push('/builder');
  };

  // Mock function to simulate AI response when WebSocket is not connected
  const handleMockDemo = () => {
    const parsed: ParsedStrategy = {
      strategy_schema: {
        nodes: [
          { 
            id: "n1", 
            type: "start", 
            data: { label: "Start Strategy" },
            position: { x: 0, y: 0 }
          },
          { 
            id: "n2", 
            type: "crypto_category", 
            data: { label: "Bitcoin (BTC)", value: "BTC" },
            position: { x: 0, y: 100 }
          },
          { 
            id: "n3", 
            type: "entry_condition", 
            data: { label: "AI-Optimized Entry", config: { mode: "ai_optimized" } },
            position: { x: 0, y: 200 }
          },
          { 
            id: "n4", 
            type: "exit_target", 
            data: { label: "Profit Target 7%", value: 7 },
            position: { x: 100, y: 300 }
          },
          { 
            id: "n5", 
            type: "stop_loss", 
            data: { label: "Stop Loss -3%", value: -3 },
            position: { x: -100, y: 300 }
          }
        ],
        connections: [
          { id: "e1", source: "n1", target: "n2" },
          { id: "e2", source: "n2", target: "n3" },
          { id: "e3", source: "n3", target: "n4" },
          { id: "e4", source: "n3", target: "n5" }
        ]
      },
      guardrails: [
        { type: "no_short_selling", level: "info", message: "No short selling enabled" },
        { type: "max_drawdown", level: "info", message: "Max 10% drawdown protection" },
        { type: "no_leverage", level: "warning", message: "Position sizing: Use with caution for $1000 capital" }
      ],
      rationale: "I've created a momentum-based Bitcoin strategy for you. With $1000 capital, this strategy focuses on capturing short-term price movements with AI-optimized entry points, a 7% profit target, and -3% stop loss for risk management.",
      estimated_return: 7.2,
      required_capital: 1000,
      duration: "30 days"
    };

    setParsedStrategy(parsed);
  };

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <div className="flex-shrink-0 px-6 py-3">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h1 className="text-xl font-bold mb-1">Create a New Strategy</h1>
              <p className="text-sm text-gray-400">
                Describe your trading strategy in natural language. Our AI will parse it and set it up for backtesting.
              </p>
            </div>
            <Button
              onClick={handleAddStrategy}
              className="flex items-center gap-2 flex-shrink-0"
            >
              <Plus className="w-4 h-4" />
              Add Strategy
            </Button>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-hidden">
        <div className="max-w-7xl mx-auto px-6 pb-6 h-full">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
          {/* Chat Section */}
          <div className="h-full flex flex-col min-h-0">
            <Card className="h-full flex flex-col overflow-hidden">
              {/* Connection Status */}
              <div className="flex-shrink-0 flex items-center justify-between mb-4 pb-3 border-b border-gray-800">
                <h3 className="font-semibold">AI Chat</h3>
                <div className="flex items-center gap-2">
                  {isConnected ? (
                    <>
                      <Wifi className="w-4 h-4 text-green-500" />
                      <span className="text-xs text-green-500">Connected</span>
                    </>
                  ) : (
                    <>
                      <WifiOff className="w-4 h-4 text-yellow-500" />
                      <span className="text-xs text-yellow-500">Connecting...</span>
                    </>
                  )}
                </div>
              </div>
              
              <div className="flex-1 overflow-y-auto space-y-4 min-h-0 pr-2"
                   style={{ scrollbarGutter: 'stable' }}
              >
                {/* WebSocket not connected - Show demo option */}
                {!isConnected && messages.length === 0 && (
                  <div className="flex flex-col items-center justify-center h-full space-y-4">
                    <div className="text-center max-w-md">
                      <WifiOff className="w-12 h-12 mx-auto mb-4 text-yellow-500 opacity-50" />
                      <h3 className="text-lg font-semibold mb-2">AI Server Offline</h3>
                      <p className="text-sm text-gray-400 mb-6">
                        The WebSocket server is not connected. You can try the demo mode to see how the AI strategy creation works.
                      </p>
                      <Button onClick={handleMockDemo} className="mx-auto">
                        <Lightbulb className="w-4 h-4 mr-2" />
                        Try Demo Mode
                      </Button>
                    </div>
                  </div>
                )}
                
                {/* Initial greeting */}
                {messages.length === 0 && isConnected && (
                  <div className="flex justify-start">
                    <div className="max-w-[80%] rounded-lg p-4 bg-card-hover text-foreground">
                      <p className="text-sm">Hello! I'm your AI Trading Assistant. Tell me, what kind of trading strategy are you looking for today?</p>
                    </div>
                  </div>
                )}
                
                {/* Error message */}
                {error && (
                  <div className="flex justify-start">
                    <div className="max-w-[80%] rounded-lg p-4 bg-red-500/10 border border-red-500/30">
                      <p className="text-sm text-red-500">{error}</p>
                    </div>
                  </div>
                )}
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg p-4 ${
                        message.role === "user"
                          ? "bg-primary text-white"
                          : "bg-card-hover text-foreground"
                      }`}
                    >
                      <div className="text-sm prose prose-invert prose-sm max-w-none">
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                      </div>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-card-hover rounded-lg p-4">
                      {streamingMessage ? (
                        <div className="flex items-start">
                          <div className="text-sm prose prose-invert prose-sm max-w-none">
                            <ReactMarkdown>{streamingMessage}</ReactMarkdown>
                          </div>
                          <span className="inline-block w-1 h-4 bg-gray-400 ml-1 animate-pulse flex-shrink-0"></span>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <div className="flex gap-1">
                            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                          </div>
                          <p className="text-sm text-gray-400">AI is thinking...</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}
                {/* Invisible div for auto-scroll */}
                <div ref={messagesEndRef} />
              </div>

              <div className="flex-shrink-0 border-t border-gray-800 pt-4 mt-4">
                <div className="flex gap-2 items-end">
                  <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        handleSend();
                      }
                    }}
                    placeholder="e.g., I have $1000, please choose a strategy that gives at least 7% returns monthly"
                    className="flex-1 bg-card-hover border border-gray-700 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50 resize-none min-h-[60px] max-h-[200px]"
                    disabled={isLoading || !isConnected}
                    rows={2}
                    style={{ height: 'auto' }}
                    onInput={(e) => {
                      const target = e.target as HTMLTextAreaElement;
                      target.style.height = 'auto';
                      target.style.height = Math.min(target.scrollHeight, 200) + 'px';
                    }}
                  />
                  <Button onClick={handleSend} disabled={isLoading || !isConnected}>
                    <Send className="w-4 h-4" />
                  </Button>
                </div>

                <div className="mt-4">
                  <p className="text-xs text-gray-500 mb-2">Examples:</p>
                  <div className="flex flex-wrap gap-2">
                    {examples.map((example) => (
                      <button
                        key={example.label}
                        onClick={() => handleExampleClick(example.label)}
                        className="flex items-center gap-1 px-3 py-1 bg-card-hover hover:bg-primary/20 border border-gray-700 rounded-full text-xs transition-colors"
                      >
                        <example.icon className="w-3 h-3" />
                        {example.label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {/* Parsed Strategy Section */}
          <div className="h-full flex flex-col min-h-0">
            {isLoading ? (
              <Card className="h-full flex flex-col overflow-hidden relative">
                {/* Gradient background effect */}
                <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-purple-500/5 opacity-50"></div>
                
                <div className="relative flex-1 overflow-y-auto pr-2 flex flex-col" style={{ scrollbarGutter: 'stable' }}>
                  {/* Header Section */}
                  <div className="flex-shrink-0 text-center pt-8 pb-6">
                    <div className="relative inline-flex items-center justify-center mb-4">
                      {/* Rotating rings */}
                      <div className="absolute w-24 h-24 rounded-full border-2 border-primary/30 animate-spin" style={{ animationDuration: '3s' }}></div>
                      <div className="absolute w-20 h-20 rounded-full border-2 border-purple-500/30 animate-spin" style={{ animationDuration: '2s', animationDirection: 'reverse' }}></div>
                      
                      {/* Pulsating outer glow */}
                      <div className="absolute w-20 h-20 rounded-full bg-primary/20 animate-ping" style={{ animationDuration: '2s' }}></div>
                      
                      {/* Center icon with scale animation */}
                      <div className="relative z-10 w-16 h-16 rounded-full bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center shadow-lg shadow-primary/50 animate-[pulse_2s_ease-in-out_infinite]">
                        <Sparkles className="w-8 h-8 text-white animate-[pulse_1.5s_ease-in-out_infinite]" />
                      </div>
                    </div>
                    
                    <h3 className="text-2xl font-bold bg-gradient-to-r from-primary via-purple-400 to-primary bg-clip-text text-transparent mb-2">
                      Generating Strategy
                    </h3>
                    <p className="text-sm text-gray-400">AI agent is working on your request</p>
                  </div>
                  
                  {/* Steps Container */}
                  <div className="flex-1 max-w-lg mx-auto w-full px-6 pb-6">
                    <div className="relative">
                      {/* Vertical connecting line */}
                      <div className="absolute left-[18px] top-0 bottom-0 w-0.5 bg-gradient-to-b from-transparent via-gray-700 to-transparent"></div>
                      
                      <div className="space-y-6">
                        {/* Step 1 */}
                        <div 
                          className={`relative transition-all duration-700 ease-out ${
                            currentStep >= 0 ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
                          }`}
                        >
                          <div className="flex items-start gap-4">
                            {/* Step indicator */}
                            <div className={`relative z-10 flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center transition-all duration-500 ${
                              currentStep > 0 
                                ? 'bg-gradient-to-br from-green-400 to-emerald-600 shadow-lg shadow-green-500/50' 
                                : currentStep === 0
                                ? 'bg-gradient-to-br from-primary to-blue-600 shadow-lg shadow-primary/50 animate-pulse'
                                : 'bg-gray-800 border-2 border-gray-700'
                            }`}>
                              {currentStep > 0 ? (
                                <Check className="w-5 h-5 text-white" strokeWidth={3} />
                              ) : currentStep === 0 ? (
                                <Target className="w-5 h-5 text-white" />
                              ) : (
                                <span className="text-xs text-gray-500 font-bold">1</span>
                              )}
                            </div>
                            
                            {/* Step content */}
                            <div className="flex-1 pt-1">
                              <div className={`transition-all duration-500 ${
                                currentStep === 0 ? 'text-white' : currentStep > 0 ? 'text-gray-300' : 'text-gray-500'
                              }`}>
                                <h4 className="font-semibold mb-1">Analyzing market patterns</h4>
                                <p className="text-xs text-gray-400 mb-2">Identifying optimal entry and exit points</p>
                              </div>
                              
                              {currentStep === 0 && (
                                <div className="mt-2 flex items-center gap-2">
                                  <div className="flex gap-1">
                                    <span className="w-1 h-1 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                                    <span className="w-1 h-1 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                                    <span className="w-1 h-1 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                                  </div>
                                  <p className="text-xs text-primary font-medium animate-pulse">{subStepText}</p>
                                </div>
                              )}
                              
                              {currentStep > 0 && (
                                <div className="flex items-center gap-1.5 mt-2">
                                  <div className="h-1 w-1 rounded-full bg-green-500"></div>
                                  <p className="text-xs text-green-400 font-medium">Completed in 1.2s</p>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                        
                        {/* Step 2 */}
                        <div 
                          className={`relative transition-all duration-700 ease-out ${
                            currentStep >= 1 ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
                          }`}
                        >
                          <div className="flex items-start gap-4">
                            <div className={`relative z-10 flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center transition-all duration-500 ${
                              currentStep > 1 
                                ? 'bg-gradient-to-br from-green-400 to-emerald-600 shadow-lg shadow-green-500/50' 
                                : currentStep === 1
                                ? 'bg-gradient-to-br from-emerald-500 to-teal-600 shadow-lg shadow-emerald-500/50 animate-pulse'
                                : 'bg-gray-800 border-2 border-gray-700'
                            }`}>
                              {currentStep > 1 ? (
                                <Check className="w-5 h-5 text-white" strokeWidth={3} />
                              ) : currentStep === 1 ? (
                                <Shield className="w-5 h-5 text-white" />
                              ) : (
                                <span className="text-xs text-gray-500 font-bold">2</span>
                              )}
                            </div>
                            
                            <div className="flex-1 pt-1">
                              <div className={`transition-all duration-500 ${
                                currentStep === 1 ? 'text-white' : currentStep > 1 ? 'text-gray-300' : 'text-gray-500'
                              }`}>
                                <h4 className="font-semibold mb-1">Configuring safety measures</h4>
                                <p className="text-xs text-gray-400 mb-2">Setting up risk management and guardrails</p>
                              </div>
                              
                              {currentStep === 1 && (
                                <div className="mt-2 flex items-center gap-2">
                                  <div className="flex gap-1">
                                    <span className="w-1 h-1 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                                    <span className="w-1 h-1 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                                    <span className="w-1 h-1 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                                  </div>
                                  <p className="text-xs text-emerald-400 font-medium animate-pulse">{subStepText}</p>
                                </div>
                              )}
                              
                              {currentStep > 1 && (
                                <div className="flex items-center gap-1.5 mt-2">
                                  <div className="h-1 w-1 rounded-full bg-green-500"></div>
                                  <p className="text-xs text-green-400 font-medium">Completed in 0.9s</p>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                        
                        {/* Step 3 */}
                        <div 
                          className={`relative transition-all duration-700 ease-out ${
                            currentStep >= 2 ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
                          }`}
                        >
                          <div className="flex items-start gap-4">
                            <div className={`relative z-10 flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center transition-all duration-500 ${
                              currentStep === 2
                                ? 'bg-gradient-to-br from-yellow-500 to-orange-600 shadow-lg shadow-yellow-500/50 animate-pulse'
                                : 'bg-gray-800 border-2 border-gray-700'
                            }`}>
                              {currentStep === 2 ? (
                                <DollarSign className="w-5 h-5 text-white" />
                              ) : (
                                <span className="text-xs text-gray-500 font-bold">3</span>
                              )}
                            </div>
                            
                            <div className="flex-1 pt-1">
                              <div className={`transition-all duration-500 ${
                                currentStep === 2 ? 'text-white' : 'text-gray-500'
                              }`}>
                                <h4 className="font-semibold mb-1">Optimizing risk/reward</h4>
                                <p className="text-xs text-gray-400 mb-2">Calculating capital allocation and returns</p>
                              </div>
                              
                              {currentStep === 2 && (
                                <div className="mt-2 flex items-center gap-2">
                                  <div className="flex gap-1">
                                    <span className="w-1 h-1 bg-yellow-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                                    <span className="w-1 h-1 bg-yellow-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                                    <span className="w-1 h-1 bg-yellow-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                                  </div>
                                  <p className="text-xs text-yellow-400 font-medium animate-pulse">{subStepText}</p>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            ) : parsedStrategy ? (
              <Card className="h-full flex flex-col overflow-hidden">
                <div className="flex-1 overflow-y-auto pr-2" style={{ scrollbarGutter: 'stable' }}>
                  <h2 className="text-xl font-semibold mb-4">Parsed Strategy</h2>
                  <p className="text-gray-300 mb-4">{parsedStrategy.rationale}</p>

                  <div className="space-y-4">
                    <div>
                      <h3 className="text-sm font-medium text-gray-400 mb-2">Guardrails</h3>
                      <div className="space-y-2">
                        {parsedStrategy.guardrails.map((guardrail, index) => (
                          <div
                            key={index}
                            className={`flex items-center gap-2 p-2 rounded-lg ${
                              guardrail.level === "error"
                                ? "bg-danger/10 border border-danger/30"
                                : guardrail.level === "warning"
                                ? "bg-warning/10 border border-warning/30"
                                : "bg-success/10 border border-success/30"
                            }`}
                          >
                            <span>{getGuardrailIcon(guardrail.level)}</span>
                            <span className="text-sm">{guardrail.message}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="space-y-4 pt-4 border-t border-gray-800">
                      <div className="flex items-start gap-3 p-3 bg-card-hover rounded-lg">
                        <Clock className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                        <div>
                          <p className="text-xs text-gray-400 mb-1">Strategy Duration</p>
                          <p className="text-lg font-semibold">
                            {parsedStrategy.duration || "30 days"}
                          </p>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-xs text-gray-400">Strategy Impact</p>
                          <p className="text-lg font-semibold text-success">
                            +{parsedStrategy.estimated_return}% expected monthly returns
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-400">Estimated Capital Required</p>
                          <p className="text-lg font-semibold">
                            ${parsedStrategy.required_capital.toLocaleString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex-shrink-0 flex gap-3 mt-6 pt-4 border-t border-gray-800">
                  <Button variant="outline" size="md" className="flex-1">
                    <Lightbulb className="w-4 h-4 mr-2" />
                    Explain
                  </Button>
                  <Button size="md" className="flex-1" onClick={handleBuildStrategy}>
                    Build Strategy
                  </Button>
                </div>
              </Card>
            ) : (
              <Card className="h-full flex items-center justify-center">
                <div className="text-center text-gray-500">
                  <Lightbulb className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>Your parsed strategy will appear here</p>
                </div>
              </Card>
            )}
          </div>
        </div>
        </div>
      </div>
    </div>
  );
}
