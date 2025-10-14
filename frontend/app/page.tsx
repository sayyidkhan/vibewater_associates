"use client";

import { useState } from "react";
import { Send, Lightbulb, TrendingUp, ArrowLeftRight, TrendingDown } from "lucide-react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { parseStrategyFromChat } from "@/lib/api";
import type { ParsedStrategy, ChatMessage, Guardrail } from "@/types";

export default function Dashboard() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content: "Hello! I'm your AI Trading Assistant. Tell me, what kind of trading strategy are you looking for today?",
      timestamp: new Date().toISOString(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [parsedStrategy, setParsedStrategy] = useState<ParsedStrategy | null>(null);

  const examples = [
    { label: "Momentum", icon: TrendingUp },
    { label: "Mean Reversion", icon: ArrowLeftRight },
    { label: "Arbitrage", icon: TrendingDown },
    { label: "Long/Short", icon: Lightbulb },
  ];

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = {
      role: "user",
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const result = await parseStrategyFromChat(input);
      setParsedStrategy(result);

      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: result.rationale,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        role: "assistant",
        content: "I'm having trouble parsing that strategy. Could you provide more details about your trading goals, capital, and risk tolerance?",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
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
            <Card className="h-[500px] flex flex-col">
              <div className="flex-1 overflow-y-auto space-y-4 mb-4">
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
                {loading && (
                  <div className="flex justify-start">
                    <div className="bg-card-hover rounded-lg p-4">
                      <p className="text-sm text-gray-400">Analyzing your strategy...</p>
                    </div>
                  </div>
                )}
              </div>

              <div className="border-t border-gray-800 pt-4">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && handleSend()}
                    placeholder="e.g., Buy 10 shares of AAPL when its RSI crosses below 30 and sell when it crosses above 70."
                    className="flex-1 bg-card-hover border border-gray-700 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                    disabled={loading}
                  />
                  <Button onClick={handleSend} disabled={loading}>
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
                    <Button size="md" className="flex-1">
                      Run Backtest
                    </Button>
                  </div>
                </Card>
              </>
            ) : (
              <Card className="h-[500px] flex items-center justify-center">
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
