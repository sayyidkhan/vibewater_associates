export interface Strategy {
  id: string;
  user_id: string;
  name: string;
  description: string;
  status: "Live" | "Paper" | "Backtest";
  schema_json: StrategySchema;
  guardrails: Guardrail[];
  created_at: string;
  updated_at: string;
  metrics?: StrategyMetrics;
}

export interface StrategySchema {
  nodes: StrategyNode[];
  connections: Connection[];
}

export interface StrategyNode {
  id: string;
  type: "start" | "crypto_category" | "entry_condition" | "exit_target" | "stop_loss" | "capital" | "risk_class" | "end";
  data: {
    label: string;
    value?: any;
    config?: any;
  };
  position: { x: number; y: number };
}

export interface Connection {
  id: string;
  source: string;
  target: string;
}

export interface Guardrail {
  type: "no_short_selling" | "no_leverage" | "no_stop_loss" | "max_drawdown" | "high_risk_asset";
  level: "info" | "warning" | "error";
  message: string;
}

export interface StrategyMetrics {
  total_return: number;
  cagr: number;
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
  trades: number;
  vs_benchmark: number;
}

export interface BacktestRun {
  id: string;
  strategy_id: string;
  params: BacktestParams;
  metrics: BacktestMetrics;
  equity_series: EquityPoint[];
  drawdown_series: DrawdownPoint[];
  monthly_returns: MonthlyReturn[][];
  trades: Trade[];
  created_at: string;
}

export interface BacktestParams {
  symbols: string[];
  timeframe: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  benchmark: string;
  fees: number;
  slippage: number;
  position_sizing: string;
  exposure: number;
  token_id?: string;  // CoinGecko token ID (e.g., "bitcoin", "ethereum")
  period?: string;    // Period shorthand (e.g., "1M", "3M", "6M", "1Y")
}

export interface BacktestMetrics {
  total_amount_invested: number;
  total_gain: number;
  total_loss: number;
  total_return: number;
  cagr: number;
  sharpe_ratio: number;
  max_drawdown: number;
  max_drawdown_duration: number;
  win_rate: number;
  trades: number;
  vs_benchmark: number;
}

export interface EquityPoint {
  date: string;
  value: number;
  benchmark?: number;
  btc_price?: number;
}

export interface DrawdownPoint {
  date: string;
  value: number;
}

export interface MonthlyReturn {
  month: string;
  year: number;
  return: number;
}

export interface Trade {
  id: string;
  date: string;
  type: "BUY" | "SELL";
  symbol: string;
  price: number;
  quantity: number;
  amount: number;
  return?: number;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export interface ParsedStrategy {
  strategy_schema: StrategySchema;
  guardrails: Guardrail[];
  rationale: string;
  estimated_return: number;
  required_capital: number;
}
