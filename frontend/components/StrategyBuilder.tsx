"use client";

import { useState, useCallback } from "react";
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
import { MessageSquare, History, Bitcoin, TrendingUp, Target, AlertCircle, DollarSign, Shield } from "lucide-react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import type { StrategySchema, Guardrail } from "@/types";

interface StrategyBuilderProps {
  schema?: StrategySchema;
  onSchemaChange?: (schema: StrategySchema) => void;
}

const nodeTypes = {
  start: { icon: TrendingUp, label: "Start Strategy", color: "bg-primary" },
  crypto_category: { icon: Bitcoin, label: "Crypto Category", color: "bg-blue-600" },
  entry_condition: { icon: TrendingUp, label: "Set Entry Condition", color: "bg-green-600" },
  exit_target: { icon: Target, label: "Profit Target", color: "bg-blue-500" },
  stop_loss: { icon: AlertCircle, label: "Stop Loss", color: "bg-red-600" },
  capital: { icon: DollarSign, label: "Manage Capital", color: "bg-yellow-600" },
  risk_class: { icon: Shield, label: "Degen Class", color: "bg-purple-600" },
  end: { icon: Target, label: "End Strategy", color: "bg-gray-600" },
};

export default function StrategyBuilder({ schema, onSchemaChange }: StrategyBuilderProps) {
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

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const addNode = (type: keyof typeof nodeTypes) => {
    const nodeConfig = nodeTypes[type];
    const newNode: Node = {
      id: `${type}-${Date.now()}`,
      type: "default",
      position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
      data: { 
        label: (
          <div className="flex items-center gap-2">
            <nodeConfig.icon className="w-4 h-4" />
            <span>{nodeConfig.label}</span>
          </div>
        ),
      },
      style: {
        background: nodeConfig.color,
        color: "white",
        border: "1px solid #374151",
        borderRadius: "8px",
        padding: "10px",
      },
    };

    setNodes((nds) => [...nds, newNode]);
  };

  const guardrails: Guardrail[] = [
    { type: "no_short_selling", level: "info", message: "No short selling" },
    { type: "max_drawdown", level: "info", message: "Max 10% Drawdown" },
    { type: "high_risk_asset", level: "warning", message: "High risk asset class selected" },
    { type: "no_stop_loss", level: "error", message: "No stop loss (Critical Warning)" },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-200px)]">
      {/* Left Sidebar - Chat */}
      <div className="lg:col-span-1">
        <Card className="h-full flex flex-col">
          <div className="flex items-center gap-2 mb-4 pb-4 border-b border-gray-800">
            <MessageSquare className="w-5 h-5" />
            <h3 className="font-semibold">AI Assistant</h3>
          </div>

          <div className="flex-1 overflow-y-auto space-y-4 mb-4">
            <div className="bg-card-hover rounded-lg p-3">
              <p className="text-sm">
                Hello! I'm your AI Trading Assistant. Tell me, what kind of trading strategy are you looking for today?
              </p>
            </div>

            <div className="bg-primary rounded-lg p-3 ml-8">
              <p className="text-sm text-white">
                I have $1000, please choose for me the right strategy that gives at least 7% returns monthly.
              </p>
            </div>

            <div className="bg-card-hover rounded-lg p-3">
              <p className="text-sm">
                Great! I'm parsing your request for a high-return strategy with your given capital. I'll outline the key components and potential risks.
              </p>
            </div>
          </div>

          <div className="border-t border-gray-800 pt-4">
            <input
              type="text"
              placeholder="Type your message..."
              className="w-full bg-card-hover border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        </Card>

        {/* Toolbox */}
        <Card className="mt-4">
          <h3 className="font-semibold mb-4">Toolbox</h3>
          <div className="space-y-2">
            {Object.entries(nodeTypes).map(([key, config]) => (
              <button
                key={key}
                onClick={() => addNode(key as keyof typeof nodeTypes)}
                className="w-full flex items-center gap-2 p-2 bg-card-hover hover:bg-primary/20 rounded-lg transition-colors text-left text-sm"
              >
                <config.icon className="w-4 h-4" />
                <span>{config.label}</span>
              </button>
            ))}
          </div>

          <div className="mt-6">
            <h4 className="text-sm font-medium mb-2">Profit Target</h4>
            <div className="space-y-2">
              {["0.5%", "2%", "4%"].map((target) => (
                <button
                  key={target}
                  className="w-full p-2 bg-card-hover hover:bg-primary/20 rounded text-sm transition-colors"
                >
                  {target}
                </button>
              ))}
            </div>
          </div>
        </Card>
      </div>

      {/* Center - Visual Flowchart Editor */}
      <div className="lg:col-span-2">
        <Card className="h-full flex flex-col">
          <div className="flex items-center justify-between mb-4 pb-4 border-b border-gray-800">
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
      <div className="lg:col-span-1">
        <Card className="h-full flex flex-col">
          <h3 className="font-semibold mb-4">Configuration</h3>

          <div className="flex-1 overflow-y-auto space-y-6">
            {/* Degen Class */}
            <div>
              <h4 className="text-sm font-medium mb-3 flex items-center gap-2">
                <Shield className="w-4 h-4" />
                Degen Class:
              </h4>
              <div className="grid grid-cols-3 gap-2">
                {["High", "Medium", "Low"].map((level) => (
                  <button
                    key={level}
                    className={`p-2 rounded text-sm transition-colors ${
                      level === "High"
                        ? "bg-primary text-white"
                        : "bg-card-hover hover:bg-primary/20"
                    }`}
                  >
                    {level}
                  </button>
                ))}
              </div>
            </div>

            {/* Strategy Impact */}
            <div className="p-4 bg-primary/10 border border-primary/30 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-4 h-4 text-primary" />
                <span className="text-sm font-medium">Strategy Impact:</span>
              </div>
              <p className="text-sm">+0.5% expected monthly returns</p>
            </div>

            {/* Estimated Capital */}
            <div className="p-4 bg-card-hover rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <DollarSign className="w-4 h-4" />
                <span className="text-sm font-medium">Estimated Capital Required:</span>
              </div>
              <p className="text-sm">$1000</p>
            </div>

            {/* Guardrails */}
            <div>
              <h4 className="text-sm font-medium mb-3">Guardrails (Safety Nets)</h4>
              <div className="space-y-2">
                {guardrails.map((guardrail, index) => (
                  <div
                    key={index}
                    className={`flex items-center gap-2 p-2 rounded-lg text-sm ${
                      guardrail.level === "error"
                        ? "bg-danger/10 border border-danger/30 text-danger"
                        : guardrail.level === "warning"
                        ? "bg-warning/10 border border-warning/30 text-warning"
                        : "bg-success/10 border border-success/30 text-success"
                    }`}
                  >
                    {guardrail.level === "error" ? "⛔" : guardrail.level === "warning" ? "⚠️" : "✅"}
                    <span>{guardrail.message}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 mt-6 pt-4 border-t border-gray-800">
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
