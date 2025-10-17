"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Send, Lightbulb, TrendingUp, ArrowLeftRight, TrendingDown, Wifi, WifiOff } from "lucide-react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { useWebSocketChat } from "@/hooks/useWebSocketChat";
import type { ParsedStrategy, ChatMessage, Guardrail } from "@/types";

export default function Dashboard() {
  const router = useRouter();
  const [input, setInput] = useState("");
  const [parsedStrategy, setParsedStrategy] = useState<ParsedStrategy | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Use WebSocket hook
  const { messages, isConnected, isLoading, error, strategyJson, streamingMessage, sendMessage } = useWebSocketChat();
  
  // Auto-scroll to bottom when messages change or streaming updates
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingMessage, isLoading]);
  
  // Update parsed strategy when strategyJson changes
  useEffect(() => {
    if (strategyJson) {
      // Convert strategyJson to ParsedStrategy format
      const parsed: ParsedStrategy = {
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
        required_capital: strategyJson.strategy_metrics?.estimated_capital_required_usd || 0
      };
      setParsedStrategy(parsed);
    }
  }, [strategyJson]);

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
      strategyJson: strategyJson,
      messages: messages,
      parsedStrategy: parsedStrategy
    };
    
    // Store in sessionStorage for the builder page to access
    sessionStorage.setItem('builderState', JSON.stringify(state));
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
      required_capital: 1000
    };

    setParsedStrategy(parsed);
  };

  return (
    <div className="container mx-auto px-6 py-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Create a New Strategy</h1>
          <p className="text-gray-400">
            Describe your trading strategy in natural language. Our AI will parse it and set it up for backtesting.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Chat Section */}
          <div className="space-y-6">
            <Card className="h-[700px] flex flex-col">
              {/* Connection Status */}
              <div className="flex items-center justify-between mb-4 pb-3 border-b border-gray-800">
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
              
              <div className="flex-1 overflow-y-auto space-y-4 mb-4">
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
                      <p className="text-sm">{message.content}</p>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-card-hover rounded-lg p-4">
                      {streamingMessage ? (
                        <p className="text-sm whitespace-pre-wrap">{streamingMessage}<span className="inline-block w-1 h-4 bg-gray-400 ml-1 animate-pulse"></span></p>
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

              <div className="border-t border-gray-800 pt-4">
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
          <div className="space-y-6">
            {parsedStrategy ? (
              <>
                <Card>
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

                    <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-800">
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

                  <div className="flex gap-3 mt-6">
                    <Button variant="outline" size="md" className="flex-1">
                      <Lightbulb className="w-4 h-4 mr-2" />
                      Explain
                    </Button>
                    <Button size="md" className="flex-1" onClick={handleBuildStrategy}>
                      Build Strategy
                    </Button>
                  </div>
                </Card>
              </>
            ) : (
              <Card className="h-[700px] flex items-center justify-center">
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
  );
}
