import { useState, useEffect, useRef, useCallback } from 'react';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

interface StrategyJSON {
  account?: any;
  assistant_panel?: any;
  flowchart?: any;
  toolbox?: any;
  degen_class?: any;
  strategy_metrics?: any;
  guardrails?: any;
  actions?: any;
  versioning?: any;
}

interface WebSocketMessage {
  type: 'message_start' | 'content_chunk' | 'message_complete' | 'error' | 'pong';
  message_id?: string;
  chunk?: string;
  user_message?: string;
  strategy_json?: StrategyJSON;
  error?: string;
}

interface UseWebSocketChatReturn {
  messages: ChatMessage[];
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;
  strategyJson: StrategyJSON | null;
  streamingMessage: string;
  sendMessage: (content: string) => void;
  clearMessages: () => void;
}

export function useWebSocketChat(
  url: string = 'ws://localhost:8000/ws/chat',
  initialMessages: ChatMessage[] = []
): UseWebSocketChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [strategyJson, setStrategyJson] = useState<StrategyJSON | null>(null);
  const [streamingMessage, setStreamingMessage] = useState<string>('');
  
  const wsRef = useRef<WebSocket | null>(null);
  const currentMessageRef = useRef<string>('');
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const initializedRef = useRef(false);
  
  // Update messages if initialMessages changes (for when data is loaded from sessionStorage)
  useEffect(() => {
    if (initialMessages.length > 0 && !initializedRef.current) {
      setMessages(initialMessages);
      initializedRef.current = true;
    }
  }, [initialMessages]);

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(url);
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setError(null);
      };
      
      ws.onmessage = (event) => {
        try {
          const data: WebSocketMessage = JSON.parse(event.data);
          
          switch (data.type) {
            case 'message_start':
              setIsLoading(true);
              currentMessageRef.current = '';
              setStreamingMessage('');
              break;
            
            case 'content_chunk':
              if (data.chunk) {
                currentMessageRef.current += data.chunk;
                setStreamingMessage(currentMessageRef.current);
              }
              break;
            
            case 'message_complete':
              setIsLoading(false);
              
              console.log('📨 Message complete received:', {
                hasUserMessage: !!data.user_message,
                hasStrategyJson: !!data.strategy_json,
                hasError: !!data.error
              });
              
              // Add assistant message to chat
              const userMessage = data.user_message;
              if (userMessage) {
                console.log('💬 Adding user message to chat:', userMessage.substring(0, 100) + '...');
                setMessages(prev => [
                  ...prev,
                  { role: 'assistant' as const, content: userMessage }
                ]);
              }
              
              // Update strategy JSON if present
              if (data.strategy_json) {
                console.log('🎯 Updating strategy JSON:', data.strategy_json);
                setStrategyJson(data.strategy_json);
              }
              
              // Handle errors
              if (data.error) {
                console.error('❌ Error in response:', data.error);
                setError(data.error);
              }
              
              currentMessageRef.current = '';
              setStreamingMessage('');
              break;
            
            case 'error':
              setIsLoading(false);
              setError(data.error || 'Unknown error occurred');
              break;
            
            case 'pong':
              // Heartbeat response
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
        setIsLoading(false);
      };
      
      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        
        // Attempt to reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('Attempting to reconnect...');
          connect();
        }, 3000);
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
  }, [connect]);

  const sendMessage = useCallback((content: string) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      setError('WebSocket is not connected');
      return;
    }
    
    // Add user message to chat
    setMessages(prev => [...prev, { role: 'user', content }]);
    
    // Set loading state immediately
    setIsLoading(true);
    setStreamingMessage('');
    
    // Send message to server
    const message = {
      type: 'message',
      content,
      history: messages
    };
    
    wsRef.current.send(JSON.stringify(message));
    setError(null);
  }, [messages]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setStrategyJson(null);
    setError(null);
  }, []);

  return {
    messages,
    isConnected,
    isLoading,
    error,
    strategyJson,
    streamingMessage,
    sendMessage,
    clearMessages
  };
}
