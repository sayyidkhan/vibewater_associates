from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime

class StrategyNode(BaseModel):
    id: str
    type: str
    data: Dict[str, Any]
    position: Dict[str, float]

class Connection(BaseModel):
    id: str
    source: str
    target: str

class StrategySchema(BaseModel):
    nodes: List[StrategyNode]
    connections: List[Connection]

class Guardrail(BaseModel):
    type: str
    level: Literal["info", "warning", "error"]
    message: str

class StrategyMetrics(BaseModel):
    total_return: float
    cagr: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    trades: int
    vs_benchmark: float

class Strategy(BaseModel):
    id: Optional[str] = None
    user_id: str
    name: str
    description: str
    status: Literal["Live", "Paper", "Backtest"] = "Backtest"
    schema_json: StrategySchema
    guardrails: List[Guardrail]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metrics: Optional[StrategyMetrics] = None

class BacktestParams(BaseModel):
    symbols: List[str]
    timeframe: str
    start_date: str
    end_date: str
    initial_capital: float
    benchmark: str
    fees: float
    slippage: float
    position_sizing: str
    exposure: float

class BacktestMetrics(BaseModel):
    total_amount_invested: float
    total_gain: float
    total_loss: float
    total_return: float
    cagr: float
    sharpe_ratio: float
    max_drawdown: float
    max_drawdown_duration: int
    win_rate: float
    trades: int
    vs_benchmark: float

class EquityPoint(BaseModel):
    date: str
    value: float
    benchmark: Optional[float] = None
    btc_price: Optional[float] = None

class Trade(BaseModel):
    id: str
    date: str
    type: Literal["BUY", "SELL"]
    symbol: str
    price: float
    quantity: float
    amount: float
    return_pct: Optional[float] = None

class BacktestRun(BaseModel):
    id: Optional[str] = None
    strategy_id: str
    params: BacktestParams
    metrics: BacktestMetrics
    equity_series: List[EquityPoint]
    drawdown_series: List[Dict[str, Any]]
    monthly_returns: List[List[Dict[str, Any]]]
    trades: List[Trade]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ParsedStrategy(BaseModel):
    strategy_schema: StrategySchema
    guardrails: List[Guardrail]
    rationale: str
    estimated_return: float
    required_capital: float

class ChatRequest(BaseModel):
    text: str

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class ChatHistoryRequest(BaseModel):
    messages: List[ChatMessage]

class StrategyBuilderResponse(BaseModel):
    user_message: str
    strategy_json: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class BacktestRequest(BaseModel):
    strategy_id: str
    params: BacktestParams

class StrategyExecution(BaseModel):
    """Tracks the execution of a strategy through the agent workflow"""
    id: Optional[str] = None
    strategy_id: str
    user_id: str
    status: Literal[
        "queued",
        "analyzing",
        "generating_code",
        "executing",
        "completed",
        "failed"
    ] = "queued"
    generated_code: Optional[str] = None
    execution_logs: List[str] = []
    backtest_run_id: Optional[str] = None
    error_message: Optional[str] = None
    agent_insights: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class ExecuteStrategyRequest(BaseModel):
    """Request to execute a strategy"""
    params: BacktestParams
