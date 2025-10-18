"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  Background,
  Controls,
  Connection,
  useNodesState,
  useEdgesState,
} from "reactflow";
import "reactflow/dist/style.css";
import ReactMarkdown from "react-markdown";
import { MessageSquare, History, Bitcoin, TrendingUp, Target, AlertCircle, DollarSign, Shield, Send, Wifi, WifiOff, Clock, ArrowLeftRight, TrendingDown, Lightbulb } from "lucide-react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import type { StrategySchema, Guardrail } from "@/types";
import { useWebSocketChat } from "@/hooks/useWebSocketChat";

interface StrategyBuilderProps {
  schema?: StrategySchema;
  onSchemaChange?: (schema: StrategySchema) => void;
  initialData?: {
    strategyJson?: any;
    messages?: any[];
    parsedStrategy?: any;
  };
  onStateChange?: (state: { strategyJson: any; messages: any[] }) => void;
}

const nodeTypes = {
  start: { icon: TrendingUp, label: "Start Strategy", color: "#3b82f6" },
  crypto_category: { icon: Bitcoin, label: "Crypto Category", color: "#2563eb" },
  entry_condition: { icon: TrendingUp, label: "Set Entry Condition", color: "#16a34a" },
  profit_target: { icon: Target, label: "Profit Target", color: "#3b82f6" },
  stop_loss: { icon: AlertCircle, label: "Stop Loss", color: "#dc2626" },
  capital: { icon: DollarSign, label: "Manage Capital", color: "#ca8a04" },
  risk_class: { icon: Shield, label: "Degen Class", color: "#9333ea" },
  end: { icon: Target, label: "End Strategy", color: "#4b5563" },
};

// Backward compatibility mapping for old node type keys
const nodeTypeAliases: Record<string, keyof typeof nodeTypes> = {
  category: "crypto_category",
  entry: "entry_condition",
  exit_target: "profit_target",
  take_profit: "profit_target",
};

// Helper function to get node config with alias support
const getNodeConfig = (nodeType: string) => {
  const type = (nodeType in nodeTypes ? nodeType : nodeTypeAliases[nodeType]) as keyof typeof nodeTypes;
  return nodeTypes[type];
};

export default function StrategyBuilder({ schema, onSchemaChange, initialData, onStateChange }: StrategyBuilderProps) {
  const initialNodes: Node[] = schema?.nodes.map((node) => ({
    id: node.id,
    type: "default",
    position: node.position,
    data: { label: node.data.label },
  })) || [];

  const initialEdges: Edge[] = schema?.connections.map((conn) => ({
    id: conn.id,
    source: conn.source,
    target: conn.target,
  })) || [];

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [inputMessage, setInputMessage] = useState("");
  const [duration, setDuration] = useState("30 days");
  const [estimatedCapital, setEstimatedCapital] = useState(1000);
  const [monthlyReturn, setMonthlyReturn] = useState(7.0);
  const [currentGuardrails, setCurrentGuardrails] = useState<Guardrail[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // WebSocket chat integration with initial messages from previous page
  const initialMessages = initialData?.messages || [];
  const { messages, isConnected, isLoading, error, strategyJson, streamingMessage, sendMessage } = useWebSocketChat(
    'ws://localhost:8000/ws/chat',
    initialMessages
  );
  
  // Examples for quick strategy selection
  const examples = [
    { label: "Momentum", icon: TrendingUp },
    { label: "Mean Reversion", icon: ArrowLeftRight },
    { label: "Arbitrage", icon: TrendingDown },
    { label: "Long/Short", icon: Lightbulb },
  ];

  const handleExampleClick = (example: string) => {
    setInputMessage(`I have $1000, please choose for me the right strategy that gives at least 7% returns monthly. Strategy type: ${example}`);
  };
  
  // Auto-scroll to bottom when messages change or streaming updates
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingMessage, isLoading]);
  
  // Initialize with data from previous page
  useEffect(() => {
    if (initialData?.strategyJson) {
      const json = initialData.strategyJson;
      
      // Update flowchart
      if (json.flowchart?.nodes) {
        const newNodes: Node[] = json.flowchart.nodes.map((node: any, index: number) => {
          const nodeConfig = getNodeConfig(node.type);
          
          // Extract detailed info from meta
          let detailText = "";
          if (node.meta) {
            if (node.meta.category) {
              detailText = node.meta.category;
            } else if (node.meta.mode) {
              detailText = node.meta.mode === "ai_optimized" ? "AI-Optimized" : node.meta.mode;
            } else if (node.meta.target_pct) {
              detailText = `${node.meta.target_pct}%`;
            } else if (node.meta.stop_pct) {
              detailText = `${node.meta.stop_pct}%`;
            } else if (node.meta.rules && node.meta.rules.length > 0) {
              detailText = node.meta.rules[0];
            }
          }
          
          return {
            id: node.id,
            type: "default",
            position: { x: 250, y: 50 + index * 100 },
            data: { 
              label: (
                <div className="flex flex-col gap-1">
                  <div className="flex items-center gap-2">
                    {nodeConfig && <nodeConfig.icon className="w-4 h-4" />}
                    <span className="font-medium">{node.label}</span>
                  </div>
                  {detailText && (
                    <div className="text-xs opacity-80 ml-6">{detailText}</div>
                  )}
                </div>
              ),
            },
            style: {
              background: nodeConfig?.color || "#4b5563",
              color: "white",
              border: "1px solid #374151",
              borderRadius: "8px",
              padding: "10px",
              minWidth: "180px",
            },
          };
        });
        setNodes(newNodes);
      }
      
      // Update edges
      if (json.flowchart?.edges) {
        const newEdges: Edge[] = json.flowchart.edges.map((edge: any, index: number) => ({
          id: `e${index + 1}`,
          source: edge[0],
          target: edge[1],
        }));
        setEdges(newEdges);
      }
      
      // Update configuration
      if (json.strategy_metrics?.duration) {
        setDuration(json.strategy_metrics.duration);
      }
      
      if (json.strategy_metrics) {
        if (json.strategy_metrics.estimated_capital_required_usd) {
          setEstimatedCapital(json.strategy_metrics.estimated_capital_required_usd);
        }
        if (json.strategy_metrics.impact_monthly_return_delta_pct) {
          setMonthlyReturn(json.strategy_metrics.impact_monthly_return_delta_pct);
        }
      }
      
      if (json.guardrails?.enabled) {
        const newGuardrails: Guardrail[] = json.guardrails.enabled.map((g: any) => ({
          type: g.key,
          level: g.status === "ok" ? "info" : g.status === "warning" ? "warning" : "error",
          message: g.label,
        }));
        setCurrentGuardrails(newGuardrails);
      }
    }
  }, [initialData, setNodes, setEdges]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  // Notify parent component when state changes (with proper ref to avoid infinite loops)
  const onStateChangeRef = useRef(onStateChange);
  useEffect(() => {
    onStateChangeRef.current = onStateChange;
  }, [onStateChange]);
  
  useEffect(() => {
    if (onStateChangeRef.current && (messages.length > 0 || strategyJson)) {
      onStateChangeRef.current({
        strategyJson: strategyJson,
        messages: messages
      });
    }
  }, [messages, strategyJson]);
  
  // Update UI when strategy JSON is received from backend
  useEffect(() => {
    if (strategyJson) {
      console.log('🔄 Strategy JSON received, updating UI:', strategyJson);
      
      // Update flowchart nodes
      if (strategyJson.flowchart?.nodes) {
        console.log('📊 Updating flowchart with', strategyJson.flowchart.nodes.length, 'nodes');
        const newNodes: Node[] = strategyJson.flowchart.nodes.map((node: any, index: number) => {
          const nodeConfig = getNodeConfig(node.type);
          
          // Extract detailed info from meta
          let detailText = "";
          if (node.meta) {
            if (node.meta.category) {
              detailText = node.meta.category;
            } else if (node.meta.mode) {
              detailText = node.meta.mode === "ai_optimized" ? "AI-Optimized" : node.meta.mode;
            } else if (node.meta.target_pct) {
              detailText = `${node.meta.target_pct}%`;
            } else if (node.meta.stop_pct) {
              detailText = `${node.meta.stop_pct}%`;
            } else if (node.meta.rules && node.meta.rules.length > 0) {
              detailText = node.meta.rules[0];
            }
          }
          
          return {
            id: node.id,
            type: "default",
            position: { x: 250, y: 50 + index * 100 },
            data: { 
              label: (
                <div className="flex flex-col gap-1">
                  <div className="flex items-center gap-2">
                    {nodeConfig && <nodeConfig.icon className="w-4 h-4" />}
                    <span className="font-medium">{node.label}</span>
                  </div>
                  {detailText && (
                    <div className="text-xs opacity-80 ml-6">{detailText}</div>
                  )}
                </div>
              ),
            },
            style: {
              background: nodeConfig?.color || "#4b5563",
              color: "white",
              border: "1px solid #374151",
              borderRadius: "8px",
              padding: "10px",
              minWidth: "180px",
            },
          };
        });
        setNodes(newNodes);
      }
      
      // Update edges
      if (strategyJson.flowchart?.edges) {
        const newEdges: Edge[] = strategyJson.flowchart.edges.map((edge: any, index: number) => ({
          id: `e${index + 1}`,
          source: edge[0],
          target: edge[1],
        }));
        setEdges(newEdges);
      }
      
      // Update duration
      if (strategyJson.strategy_metrics?.duration) {
        console.log('⏱️ Updating duration to:', strategyJson.strategy_metrics.duration);
        setDuration(strategyJson.strategy_metrics.duration);
      }
      
      // Update metrics
      if (strategyJson.strategy_metrics) {
        console.log('📈 Updating metrics:', strategyJson.strategy_metrics);
        if (strategyJson.strategy_metrics.estimated_capital_required_usd) {
          setEstimatedCapital(strategyJson.strategy_metrics.estimated_capital_required_usd);
        }
        if (strategyJson.strategy_metrics.impact_monthly_return_delta_pct) {
          setMonthlyReturn(strategyJson.strategy_metrics.impact_monthly_return_delta_pct);
        }
      }
      
      // Update guardrails
      if (strategyJson.guardrails?.enabled) {
        console.log('🛡️ Updating guardrails:', strategyJson.guardrails.enabled.length, 'items');
        const newGuardrails: Guardrail[] = strategyJson.guardrails.enabled.map((g: any) => ({
          type: g.key,
          level: g.status === "ok" ? "info" : g.status === "warning" ? "warning" : "error",
          message: g.label,
        }));
        setCurrentGuardrails(newGuardrails);
      }
    }
  }, [strategyJson, setNodes, setEdges]);
  
  const handleSendMessage = () => {
    if (inputMessage.trim() && isConnected) {
      sendMessage(inputMessage);
      setInputMessage("");
    }
  };
  
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-90px)]">
      {/* Left Sidebar - Chat */}
      <div className="lg:col-span-1 h-full min-h-0">
        <Card className="h-full flex flex-col overflow-hidden">
          <div className="flex-shrink-0 flex items-center justify-between mb-4 pb-4 border-b border-gray-800">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-5 h-5" />
              <h3 className="font-semibold">AI Assistant</h3>
            </div>
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
            {/* Connection status */}
            {!isConnected && (
              <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3">
                <p className="text-sm text-yellow-500">Connecting to AI assistant...</p>
              </div>
            )}
            
            {/* Error message */}
            {error && (
              <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
                <p className="text-sm text-red-500">{error}</p>
              </div>
            )}
            
            {/* Strategy updated notification */}
            {strategyJson && (
              <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3">
                <p className="text-sm text-green-500">✅ Strategy builder updated with new configuration</p>
              </div>
            )}
            
            {/* Initial greeting */}
            {messages.length === 0 && isConnected && (
              <div className="bg-card-hover rounded-lg p-3">
                <p className="text-sm">
                  Hello! I'm your AI Trading Assistant. Tell me, what kind of trading strategy are you looking for today?
                </p>
              </div>
            )}
            
            {/* Chat messages */}
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`rounded-lg p-3 ${
                  msg.role === "user"
                    ? "bg-primary text-white ml-8"
                    : "bg-card-hover"
                }`}
              >
                <div className="text-sm prose prose-invert prose-sm max-w-none">
                  <ReactMarkdown
                    components={{
                      p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                      ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
                      ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
                      li: ({ children }) => <li className="ml-2">{children}</li>,
                      strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                      em: ({ children }) => <em className="italic">{children}</em>,
                      code: ({ children }) => <code className="bg-black/30 px-1 py-0.5 rounded text-xs">{children}</code>,
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>
                </div>
              </div>
            ))}
            
            {/* Loading indicator */}
            {isLoading && (
              <div className="bg-card-hover rounded-lg p-3">
                {streamingMessage ? (
                  <div className="text-sm prose prose-invert prose-sm max-w-none">
                    <ReactMarkdown
                      components={{
                        p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                        ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
                        ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
                        li: ({ children }) => <li className="ml-2">{children}</li>,
                        strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                        em: ({ children }) => <em className="italic">{children}</em>,
                        code: ({ children }) => <code className="bg-black/30 px-1 py-0.5 rounded text-xs">{children}</code>,
                      }}
                    >
                      {streamingMessage}
                    </ReactMarkdown>
                    <span className="inline-block w-1 h-4 bg-gray-400 ml-1 animate-pulse"></span>
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
            )}
            {/* Invisible div for auto-scroll */}
            <div ref={messagesEndRef} />
          </div>

          <div className="flex-shrink-0 border-t border-gray-800 pt-4 mt-4">
            <div className="flex gap-2 items-end">
              <textarea
                placeholder="Type your message..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                disabled={!isConnected || isLoading}
                className="flex-1 bg-card-hover border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50 resize-none min-h-[60px] max-h-[200px]"
                rows={2}
                style={{ height: 'auto' }}
                onInput={(e) => {
                  const target = e.target as HTMLTextAreaElement;
                  target.style.height = 'auto';
                  target.style.height = Math.min(target.scrollHeight, 200) + 'px';
                }}
              />
              <button
                onClick={handleSendMessage}
                disabled={!isConnected || isLoading || !inputMessage.trim()}
                className="bg-primary hover:bg-primary/80 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg px-3 py-2 transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>

            <div className="mt-2">
              <p className="text-[10px] text-gray-500 mb-1.5">Examples:</p>
              <div className="flex flex-wrap gap-1.5">
                {examples.map((example) => (
                  <button
                    key={example.label}
                    onClick={() => handleExampleClick(example.label)}
                    className="flex items-center gap-1 px-2 py-0.5 bg-card-hover hover:bg-primary/20 border border-gray-700 rounded-full text-[10px] transition-colors"
                  >
                    <example.icon className="w-2.5 h-2.5" />
                    {example.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Center - Visual Flowchart Editor */}
      <div className="lg:col-span-2 h-full min-h-0">
        <Card className="h-full flex flex-col overflow-hidden">
          <div className="flex-shrink-0 flex items-center justify-between mb-4 pb-4 border-b border-gray-800">
            <h3 className="font-semibold">Visual Flowchart Editor</h3>
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                <MessageSquare className="w-4 h-4 mr-2" />
                Comments
              </Button>
              <Button variant="outline" size="sm">
                <History className="w-4 h-4 mr-2" />
                Version History
              </Button>
            </div>
          </div>

          <div className="flex-1 bg-[#0A0E1A] rounded-lg border border-gray-800">
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              fitView
            >
              <Background color="#374151" gap={16} />
              <Controls />
            </ReactFlow>
          </div>
        </Card>
      </div>

      {/* Right Sidebar - Configuration */}
      <div className="lg:col-span-1 h-full min-h-0">
        <Card className="h-full flex flex-col overflow-hidden">
          <h3 className="flex-shrink-0 text-lg font-semibold mb-6">Configuration</h3>

          <div className="flex-1 overflow-y-auto space-y-3 pr-2 min-h-0" style={{ scrollbarGutter: 'stable' }}>
            {/* Duration */}
            <div className="p-3 bg-card-hover border border-gray-700 rounded-lg">
              <div className="flex items-center gap-2 mb-1.5">
                <Clock className="w-5 h-5 text-primary" />
                <span className="text-sm font-semibold">Strategy Duration</span>
              </div>
              <p className="text-xl font-bold">{duration}</p>
              <p className="text-xs text-gray-400 mt-0.5">backtest period</p>
            </div>

            {/* Strategy Impact */}
            <div className="p-3 bg-gradient-to-br from-primary/10 to-primary/5 border border-primary/30 rounded-lg">
              <div className="flex items-center gap-2 mb-1.5">
                <TrendingUp className="w-5 h-5 text-primary" />
                <span className="text-sm font-semibold">Strategy Impact</span>
              </div>
              <p className="text-xl font-bold text-primary">+{monthlyReturn}%</p>
              <p className="text-xs text-gray-400 mt-0.5">expected monthly returns</p>
            </div>

            {/* Estimated Capital */}
            <div className="p-3 bg-card-hover border border-gray-700 rounded-lg">
              <div className="flex items-center gap-2 mb-1.5">
                <DollarSign className="w-5 h-5 text-gray-400" />
                <span className="text-sm font-semibold">Estimated Capital</span>
              </div>
              <p className="text-xl font-bold">${estimatedCapital.toLocaleString()}</p>
              <p className="text-xs text-gray-400 mt-0.5">required to start</p>
            </div>

            <div className="h-px bg-gray-800 my-2"></div>

            {/* Guardrails */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Shield className="w-5 h-5 text-success" />
                <h4 className="text-sm font-semibold">Guardrails (Safety Nets)</h4>
              </div>
              <div className="space-y-2">
                {(currentGuardrails.length > 0 ? currentGuardrails : [
                  { type: "no_short_selling", level: "info" as const, message: "No short selling" },
                  { type: "max_drawdown", level: "info" as const, message: "Max 10% Drawdown" },
                ]).map((guardrail, index) => (
                  <div
                    key={index}
                    className={`flex items-center gap-3 p-3 rounded-lg text-sm ${
                      guardrail.level === "error"
                        ? "bg-danger/10 border border-danger/30 text-danger"
                        : guardrail.level === "warning"
                        ? "bg-warning/10 border border-warning/30 text-warning"
                        : "bg-success/10 border border-success/30 text-success"
                    }`}
                  >
                    <span className="text-base">{guardrail.level === "error" ? "⛔" : guardrail.level === "warning" ? "⚠️" : "✅"}</span>
                    <span className="flex-1">{guardrail.message}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex-shrink-0 flex gap-3 mt-6 pt-6 border-t border-gray-800">
            <Button variant="outline" size="md" className="flex-1">
              Explain
            </Button>
            <Button size="md" className="flex-1">
              Run Backtest
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}
