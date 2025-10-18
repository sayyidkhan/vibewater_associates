import { useState, useEffect, useRef, useCallback } from 'react';

interface AgentUpdate {
  type: 'agent_start' | 'agent_step' | 'agent_output' | 'agent_complete' | 'execution_complete' | 'error' | 'execution_started';
  agent_id?: number;
  agent_name?: string;
  description?: string;
  step?: string;
  output?: string;
  results?: any;
  error?: string;
  strategy_id?: string;
}

interface Agent {
  id: number;
  name: string;
  icon: any;
  description: string;
  color: string;
  status: "disabled" | "active" | "completed" | "error";
  output: string;
  steps: string[];
}

interface ExecutionParams {
  strategy_id: string;
  strategy_schema?: any;
  strategy_name?: string;
  params: {
    start_date?: string;
    end_date?: string;
    initial_capital?: number;
    fees?: number;
    slippage?: number;
  };
}

interface UseWebSocketBacktestReturn {
  agents: Agent[];
  isConnected: boolean;
  isRunning: boolean;
  error: string | null;
  results: any | null;
  currentAgentIndex: number;
  startExecution: (params: ExecutionParams) => void;
  resetExecution: () => void;
}

export function useWebSocketBacktest(
  url: string = 'ws://localhost:8000/ws/backtest',
  initialAgents: Agent[]
): UseWebSocketBacktestReturn {
  const [agents, setAgents] = useState<Agent[]>(initialAgents);
  const [isConnected, setIsConnected] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<any | null>(null);
  const [currentAgentIndex, setCurrentAgentIndex] = useState(-1);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(url);
      
      ws.onopen = () => {
        console.log('WebSocket backtest connection established');
        setIsConnected(true);
        setError(null);
      };
      
      ws.onmessage = (event) => {
        try {
          const data: AgentUpdate = JSON.parse(event.data);
          console.log('Received update:', data);
          
          switch (data.type) {
            case 'execution_started':
              setIsRunning(true);
              setError(null);
              setResults(null);
              console.log('Execution started for strategy:', data.strategy_id);
              break;
            
            case 'agent_start':
              if (data.agent_id !== undefined) {
                console.log(`Agent ${data.agent_id} started: ${data.agent_name}`);
                setCurrentAgentIndex(data.agent_id - 1);
                setAgents(prev => prev.map((agent, idx) => {
                  if (agent.id === data.agent_id) {
                    return { ...agent, status: "active" };
                  } else if (idx < (data.agent_id! - 1)) {
                    return { ...agent, status: "completed" };
                  }
                  return agent;
                }));
              }
              break;
            
            case 'agent_step':
              if (data.agent_id !== undefined && data.step) {
                console.log(`Agent ${data.agent_id} step: ${data.step}`);
                setAgents(prev => prev.map(agent => {
                  if (agent.id === data.agent_id) {
                    // Add step to steps array if not already there
                    const updatedSteps = agent.steps.includes(data.step!) 
                      ? agent.steps 
                      : [...agent.steps.slice(0, -1), data.step!, agent.steps[agent.steps.length - 1]];
                    return { ...agent, steps: updatedSteps };
                  }
                  return agent;
                }));
              }
              break;
            
            case 'agent_output':
              if (data.agent_id !== undefined && data.output) {
                console.log(`Agent ${data.agent_id} output:`, data.output);
                setAgents(prev => prev.map(agent => {
                  if (agent.id === data.agent_id) {
                    // Append output instead of replacing to show streaming logs
                    const newOutput = agent.output 
                      ? `${agent.output}\n${data.output}`
                      : data.output!;
                    return { ...agent, output: newOutput };
                  }
                  return agent;
                }));
              }
              break;
            
            case 'agent_complete':
              if (data.agent_id !== undefined) {
                console.log(`Agent ${data.agent_id} completed`);
                setAgents(prev => prev.map(agent => {
                  if (agent.id === data.agent_id) {
                    return { ...agent, status: "completed" };
                  }
                  return agent;
                }));
              }
              break;
            
            case 'execution_complete':
              console.log('Execution complete with results:', data.results);
              setIsRunning(false);
              setResults(data.results);
              setAgents(prev => prev.map(agent => ({
                ...agent,
                status: "completed"
              })));
              break;
            
            case 'error':
              console.error('Execution error:', data.error);
              setError(data.error || 'Unknown error occurred');
              setIsRunning(false);
              
              // Mark current agent as error
              if (currentAgentIndex >= 0) {
                setAgents(prev => prev.map((agent, idx) => {
                  if (idx === currentAgentIndex) {
                    return { 
                      ...agent, 
                      status: "error",
                      output: `❌ Error: ${data.error}`
                    };
                  }
                  return agent;
                }));
              }
              break;
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
          setError('Failed to parse server response');
        }
      };
      
      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        setError('WebSocket connection error');
        setIsRunning(false);
      };
      
      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        
        // Don't auto-reconnect - let user manually retry
        setIsRunning(false);
      };
      
      wsRef.current = ws;
    } catch (err) {
      console.error('Error creating WebSocket:', err);
      setError('Failed to create WebSocket connection');
    }
  }, [url]);

  useEffect(() => {
    connect();
    
    // Cleanup on unmount
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [url]);

  const startExecution = useCallback((params: ExecutionParams) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      setError('WebSocket is not connected');
      return;
    }
    
    console.log('Starting execution with params:', params);
    
    // Reset state
    setIsRunning(true);
    setError(null);
    setResults(null);
    setCurrentAgentIndex(-1);
    
    // Reset all agents to disabled
    setAgents(prev => prev.map(agent => ({
      ...agent,
      status: "disabled" as const,
      output: ""
    })));
    
    // Send execution request
    const message: any = {
      type: 'execute',
      strategy_id: params.strategy_id,
      params: params.params
    };

    // Include optional fields if provided
    if (params.strategy_schema) {
      message.strategy_schema = params.strategy_schema;
    }
    if (params.strategy_name) {
      message.strategy_name = params.strategy_name;
    }
    
    console.log('Sending WebSocket message:', message);
    wsRef.current.send(JSON.stringify(message));
  }, []);

  const resetExecution = useCallback(() => {
    setIsRunning(false);
    setError(null);
    setResults(null);
    setCurrentAgentIndex(-1);
    setAgents(initialAgents.map(agent => ({
      ...agent,
      status: "disabled" as const,
      output: ""
    })));
  }, [initialAgents]);

  return {
    agents,
    isConnected,
    isRunning,
    error,
    results,
    currentAgentIndex,
    startExecution,
    resetExecution
  };
}

