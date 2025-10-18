# Strategy Execution with CrewAI Agents

## Overview

This guide explains the new strategy execution feature that uses **CrewAI agents** and **mem0** to automatically generate and execute VectorBT backtesting code from strategy schemas.

---

## Architecture

### Flow Diagram

```
User Finalizes Strategy
         ↓
POST /executions/strategies/{id}/execute
         ↓
Create StrategyExecution (status: queued)
         ↓
┌─────────────────────────────────────┐
│   CrewAI Agent Workflow (Async)    │
├─────────────────────────────────────┤
│                                     │
│  1. Strategy Analyzer Agent         │
│     - Parses strategy JSON          │
│     - Extracts indicators           │
│     - Searches mem0 for patterns    │
│     Status: analyzing               │
│          ↓                          │
│  2. Code Generator Agent            │
│     - Generates VectorBT code       │
│     - Validates code                │
│     - Uses mem0 templates           │
│     Status: generating_code         │
│          ↓                          │
│  3. Code Executor Agent             │
│     - Validates security            │
│     - Executes in sandbox           │
│     - Stores results in mem0        │
│     Status: executing               │
│          ↓                          │
└─────────────────────────────────────┘
         ↓
Create BacktestRun with metrics
         ↓
Update StrategyExecution (status: completed)
         ↓
Frontend displays results
```

---

## Components

### 1. Strategy Code Generator (`strategy_code_generator.py`)

Transforms strategy JSON into VectorBT Python code.

**Key Methods:**
- `generate_vectorbt_code()` - Main transformation method
- `_extract_category()` - Extracts crypto asset
- `_extract_entry_logic()` - Parses entry conditions
- `_parse_indicators_from_rules()` - Extracts technical indicators from natural language

**Example Transformation:**

```json
{
  "nodes": [
    {
      "type": "entry_condition",
      "meta": {
        "rules": ["Enter on a 5% price drop from the 20-day moving average"]
      }
    }
  ]
}
```

↓ Transforms to ↓

```python
ma_20 = vbt.MA.run(price, 20, short_name='ma_20')
entries = price < (ma_20.ma * 0.95)
```

### 2. Execution Tools (`execution_tools.py`)

CrewAI tools that agents use to perform actions.

**Tools:**
- `generate_vectorbt_code_tool` - Generates code from JSON
- `validate_python_code_tool` - Checks security and syntax
- `execute_python_code_tool` - Runs code in sandbox
- `search_strategy_memory_tool` - Queries mem0 for patterns
- `store_strategy_memory_tool` - Saves results to mem0

### 3. Strategy Agents (`strategy_agents.py`)

Defines the three CrewAI agents and their tasks.

**Agents:**

1. **Strategy Analyzer**
   - Role: Analyze strategy schema
   - Tools: search_strategy_memory_tool
   - Output: Structured analysis

2. **Code Generator**
   - Role: Generate VectorBT code
   - Tools: generate_vectorbt_code_tool, validate_python_code_tool, search_strategy_memory_tool
   - Output: Valid Python code

3. **Code Executor**
   - Role: Execute code safely
   - Tools: validate_python_code_tool, execute_python_code_tool, store_strategy_memory_tool
   - Output: Execution results

### 4. Strategy Execution Service (`strategy_execution_service.py`)

Orchestrates the complete workflow.

**Key Methods:**
- `execute_strategy()` - Starts execution workflow
- `_execute_workflow()` - Runs CrewAI agents asynchronously
- `get_execution()` - Get execution status
- `get_generated_code()` - Retrieve generated code

### 5. API Endpoints (`executions.py`)

REST API for strategy execution.

**Endpoints:**
- `POST /executions/strategies/{id}/execute` - Start execution
- `GET /executions/{id}` - Get execution status
- `GET /executions/{id}/code` - Get generated code
- `GET /executions/{id}/results` - Get backtest results
- `GET /executions/strategies/{id}/executions` - List all executions

---

## Usage

### 1. Execute a Strategy

```bash
POST /executions/strategies/strategy_123/execute
Content-Type: application/json

{
  "params": {
    "symbols": ["BTC"],
    "timeframe": "1d",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "initial_capital": 10000,
    "benchmark": "BTC",
    "fees": 0.001,
    "slippage": 0.001,
    "position_sizing": "equal",
    "exposure": 1.0
  }
}
```

**Response:**
```json
{
  "id": "exec_abc123",
  "strategy_id": "strategy_123",
  "user_id": "user1",
  "status": "queued",
  "created_at": "2024-10-17T15:00:00Z"
}
```

### 2. Check Execution Status

```bash
GET /executions/exec_abc123
```

**Response:**
```json
{
  "id": "exec_abc123",
  "strategy_id": "strategy_123",
  "status": "executing",
  "execution_logs": [
    "Analyzing strategy schema...",
    "Generating VectorBT code...",
    "Running backtest..."
  ],
  "started_at": "2024-10-17T15:00:01Z"
}
```

**Status Values:**
- `queued` - Waiting to start
- `analyzing` - Agent analyzing strategy
- `generating_code` - Agent generating code
- `executing` - Running backtest
- `completed` - Successfully completed
- `failed` - Execution failed

### 3. Get Generated Code

```bash
GET /executions/exec_abc123/code
```

**Response:**
```json
{
  "execution_id": "exec_abc123",
  "language": "python",
  "code": "import vectorbt as vbt\nimport pandas as pd\n..."
}
```

### 4. Get Results

```bash
GET /executions/exec_abc123/results
```

**Response:**
```json
{
  "id": "bt_456",
  "strategy_id": "strategy_123",
  "metrics": {
    "total_return": 25.5,
    "cagr": 18.3,
    "sharpe_ratio": 2.1,
    "max_drawdown": -8.5,
    "win_rate": 62.5,
    "trades": 87,
    "vs_benchmark": 5.2
  },
  "equity_series": [...],
  "trades": [...]
}
```

---

## mem0 Integration

### What mem0 Stores

1. **Successful Strategy Patterns**
```python
mem0.add(
    messages=[{
        "role": "assistant",
        "content": "MA crossover strategy with 10/30 periods achieved 2.1 Sharpe ratio"
    }],
    user_id=user_id,
    metadata={
        "strategy_type": "ma_crossover",
        "sharpe_ratio": 2.1,
        "indicators": ["MA(10)", "MA(30)"]
    }
)
```

2. **Code Templates**
```python
mem0.add(
    messages=[{
        "role": "assistant",
        "content": "VectorBT RSI strategy template: ..."
    }],
    user_id="system",
    metadata={
        "code_type": "rsi_strategy",
        "tested": True
    }
)
```

3. **User Preferences**
```python
mem0.add(
    messages=[{
        "role": "user",
        "content": "User prefers conservative strategies"
    }],
    user_id=user_id,
    metadata={
        "risk_tolerance": "conservative",
        "max_drawdown": 10
    }
)
```

### How Agents Use mem0

**Code Generator Agent:**
```python
# Search for similar successful strategies
memories = search_strategy_memory_tool(
    query="MA crossover Bitcoin strategies",
    user_id=user_id
)

# Use patterns to inform code generation
# Agent considers: What worked before? What indicators? What parameters?
```

**Code Executor Agent:**
```python
# After successful execution, store results
store_strategy_memory_tool(
    content=f"Strategy achieved {sharpe_ratio} Sharpe with {indicators}",
    user_id=user_id,
    metadata={
        "sharpe_ratio": sharpe_ratio,
        "indicators": indicators,
        "success": True
    }
)
```

---

## Code Execution Security

### Sandbox Approach

Code runs in an isolated subprocess:

```python
subprocess.run(
    ['python', code_file],
    capture_output=True,
    timeout=300,
    cwd='/tmp'  # Isolated directory
)
```

### Validation Checks

Before execution, code is validated for:
- ❌ `os.system()` - Shell command execution
- ❌ `eval()` / `exec()` - Code injection
- ❌ File writing operations
- ❌ Network requests
- ✅ Required imports (vectorbt, pandas, numpy)
- ✅ Valid Python syntax

---

## Database Models

### StrategyExecution

```python
{
  "id": "exec_123",
  "strategy_id": "strategy_456",
  "user_id": "user1",
  "status": "completed",
  "generated_code": "import vectorbt...",
  "execution_logs": ["Log line 1", "Log line 2"],
  "backtest_run_id": "bt_789",
  "error_message": null,
  "agent_insights": {
    "indicators_used": ["MA(10)", "MA(30)"],
    "execution_time": 45.2
  },
  "created_at": "2024-10-17T15:00:00Z",
  "started_at": "2024-10-17T15:00:01Z",
  "completed_at": "2024-10-17T15:00:46Z"
}
```

---

## Installation

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

New dependencies added:
- `crewai==0.86.0` - Multi-agent orchestration
- `crewai-tools==0.12.1` - Agent tools
- `mem0ai==0.1.29` - Memory storage

### 2. Configure Environment

Add to `.env`:

```bash
# Existing LLM config (used by CrewAI agents)
ANTHROPIC_API_KEY=your_key_here

# Optional: mem0 configuration
# If not configured, mem0 features will be skipped gracefully
MEM0_API_KEY=your_mem0_key_here
```

### 3. Start Server

```bash
uvicorn app.main:app --reload
```

---

## Testing

### Test Code Generator

```python
from app.services.strategy_code_generator import strategy_code_generator

strategy_schema = {
    "nodes": [
        {"id": "entry", "type": "entry_condition", "meta": {
            "rules": ["Enter on 20-day MA crossover"]
        }},
        {"id": "tp", "type": "take_profit", "meta": {"target_pct": 7.0}},
        {"id": "sl", "type": "stop_loss", "meta": {"stop_pct": 5.0}}
    ]
}

params = {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "initial_capital": 10000
}

code = strategy_code_generator.generate_vectorbt_code(strategy_schema, params)
print(code)
```

### Test Execution Tool

```python
from app.services.execution_tools import execute_python_code_tool
import json

code = """
import vectorbt as vbt
import json

price_data = vbt.YFData.download('BTC-USD', start='2024-01-01', end='2024-03-31')
price = price_data.get('Close')

pf = vbt.Portfolio.from_holding(price, init_cash=10000)
results = {
    'total_return': round(pf.total_return() * 100, 2),
    'sharpe_ratio': round(pf.sharpe_ratio(), 2)
}

print("===RESULTS_START===")
print(json.dumps(results))
print("===RESULTS_END===")
"""

result = execute_python_code_tool(code)
print(json.loads(result))
```

---

## Troubleshooting

### Issue: CrewAI agents not responding

**Solution:** Check that ANTHROPIC_API_KEY is set in `.env`

```bash
echo $ANTHROPIC_API_KEY
```

### Issue: Code execution timeout

**Solution:** Increase timeout or reduce date range

```python
execute_python_code_tool(code, timeout=600)  # 10 minutes
```

### Issue: mem0 errors

**Solution:** mem0 is optional. If not configured, features are skipped gracefully.

---

## Future Enhancements

1. **Real-time Progress Updates**
   - WebSocket connection for live agent updates
   - Stream agent thoughts and actions

2. **Code Optimization Agent**
   - Fourth agent that optimizes generated code
   - Suggests parameter improvements

3. **Multi-Asset Support**
   - Generate code for portfolio strategies
   - Handle multiple symbols simultaneously

4. **Custom Indicators**
   - Allow users to define custom indicators
   - Agent learns and reuses custom logic

5. **Backtesting Visualization**
   - Generate interactive Plotly charts
   - Return chart data with results

---

## API Reference

### POST /executions/strategies/{strategy_id}/execute

Execute a strategy using CrewAI agents.

**Request Body:**
```json
{
  "params": {
    "symbols": ["BTC"],
    "timeframe": "1d",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "initial_capital": 10000,
    "benchmark": "BTC",
    "fees": 0.001,
    "slippage": 0.001,
    "position_sizing": "equal",
    "exposure": 1.0
  }
}
```

**Response:** `StrategyExecution` object

### GET /executions/{execution_id}

Get execution status.

**Response:** `StrategyExecution` object with current status

### GET /executions/{execution_id}/code

Get generated VectorBT code.

**Response:**
```json
{
  "execution_id": "string",
  "code": "string",
  "language": "python"
}
```

### GET /executions/{execution_id}/results

Get backtest results (only for completed executions).

**Response:** `BacktestRun` object with metrics and trades

### GET /executions/strategies/{strategy_id}/executions

List all executions for a strategy.

**Response:** Array of `StrategyExecution` objects

---

## Summary

The strategy execution feature provides:

✅ **Automated Code Generation** - Transforms strategy JSON to VectorBT code  
✅ **Multi-Agent Workflow** - CrewAI agents handle analysis, generation, execution  
✅ **Memory & Learning** - mem0 stores patterns for continuous improvement  
✅ **Secure Execution** - Sandboxed subprocess with validation  
✅ **Async Processing** - Non-blocking API with status tracking  
✅ **Full Transparency** - View generated code and execution logs  

This enables users to go from strategy idea → validated backtest results without writing any code!
