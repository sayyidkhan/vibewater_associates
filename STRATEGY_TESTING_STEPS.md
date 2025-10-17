# 🧪 How to Test Strategy Execution

Step-by-step guide to test your CrewAI strategy execution system.

---

## Quick Start (5 minutes)

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- ✅ CrewAI (0.86.0)
- ✅ CrewAI Tools (0.12.1)
- ✅ LangChain Anthropic (0.1.23)
- ✅ VectorBT (0.26.2)
- ✅ mem0 (0.1.29)

### Step 2: Verify Environment

Check your `.env` file has:

```bash
ANTHROPIC_API_KEY=sk-ant-...
MONGODB_URL=mongodb+srv://...
```

### Step 3: Run Quick Validation

```bash
python quick_test.py
```

This will:
1. ✅ Check environment variables
2. ✅ Test imports
3. ✅ Initialize agents
4. ✅ Test tools
5. ✅ (Optional) Test LLM connection

**Expected Output:**
```
🧪 QUICK CREWAI VALIDATION TEST
================================

1️⃣ Checking environment variables...
   ✅ ANTHROPIC_API_KEY is set (sk-ant-api...)

2️⃣ Testing imports...
   ✅ CrewAI imported successfully
   ✅ LangChain Anthropic imported successfully

3️⃣ Initializing CrewAI agents...
   ✅ Strategy Analyzer Agent: Strategy Analyzer
   ✅ Code Generator Agent: VectorBT Code Generator
   ✅ Code Executor Agent: Code Executor and Validator

4️⃣ Testing agent tools...
   ✅ Code generation tool working
   ✅ Code validation tool working

✅ VALIDATION COMPLETE
```

---

## Full Integration Test (2-3 minutes)

### Step 4: Run Full Test

```bash
python test_strategy_execution.py
```

This will:
1. Create a test MA crossover strategy in MongoDB
2. Execute it using CrewAI agents
3. Show real-time progress
4. Display backtest results

**Expected Output:**
```
🧪 CREWAI STRATEGY EXECUTION TEST
==================================

Step 1: Creating test strategy in MongoDB...
✅ Created test strategy with ID: 67123abc...

Step 2: Executing strategy with CrewAI agents...

🚀 TESTING STRATEGY EXECUTION WITH CREWAI AGENTS
=================================================

📋 Backtest Parameters:
   Symbol: BTC-USD
   Period: 2024-01-01 to 2024-03-31
   Capital: $10,000
   Fees: 0.1%
   Slippage: 0.1%

🤖 Starting CrewAI agent workflow...
   Agent 1: Strategy Analyzer
   Agent 2: Code Generator
   Agent 3: Code Executor

✅ Execution started!
   Execution ID: exec_123...
   Status: queued
   Created: 2024-10-17 23:35:00

⏳ Waiting for agents to complete...

🔍 Status: analyzing (attempt 1/60)
⚙️ Status: generating_code (attempt 3/60)
▶️ Status: executing (attempt 5/60)

✅ EXECUTION COMPLETED SUCCESSFULLY!
====================================

📊 Backtest Results:
   Total Return: 12.45%
   CAGR: 54.23%
   Sharpe Ratio: 1.85
   Max Drawdown: -8.32%
   Win Rate: 58.3%
   Total Trades: 12
   vs Benchmark: +3.21%

📝 Generated Code Preview:
   import vectorbt as vbt
   import pandas as pd
   import numpy as np
   ...

✅ TEST COMPLETE
```

---

## API Testing (via HTTP)

### Step 5: Start the Server

```bash
uvicorn app.main:app --reload
```

Server starts at: http://localhost:8000

### Step 6: Create a Strategy via API

```bash
curl -X POST http://localhost:8000/strategies \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "name": "Test MA Crossover",
    "description": "Simple moving average crossover",
    "status": "Backtest",
    "schema_json": {
      "nodes": [
        {
          "id": "cat1",
          "type": "crypto_category",
          "meta": {"category": "Bitcoin"}
        },
        {
          "id": "entry1",
          "type": "entry_condition",
          "meta": {
            "rules": ["Enter on 10-day MA crossing above 30-day MA"]
          }
        },
        {
          "id": "tp1",
          "type": "take_profit",
          "meta": {"target_pct": 7.0}
        },
        {
          "id": "sl1",
          "type": "stop_loss",
          "meta": {"stop_pct": 5.0}
        }
      ],
      "connections": [
        {"id": "e1", "source": "cat1", "target": "entry1"},
        {"id": "e2", "source": "entry1", "target": "tp1"},
        {"id": "e3", "source": "entry1", "target": "sl1"}
      ]
    },
    "guardrails": []
  }'
```

**Response:**
```json
{
  "id": "strategy_abc123",
  "name": "Test MA Crossover",
  "status": "Backtest",
  ...
}
```

### Step 7: Execute the Strategy

```bash
curl -X POST http://localhost:8000/executions/strategies/strategy_abc123/execute \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "symbols": ["BTC"],
      "timeframe": "1d",
      "start_date": "2024-01-01",
      "end_date": "2024-03-31",
      "initial_capital": 10000,
      "benchmark": "BTC",
      "fees": 0.001,
      "slippage": 0.001,
      "position_sizing": "equal",
      "exposure": 1.0
    }
  }'
```

**Response:**
```json
{
  "id": "exec_xyz789",
  "strategy_id": "strategy_abc123",
  "user_id": "test_user",
  "status": "queued",
  "created_at": "2024-10-17T23:35:00Z"
}
```

### Step 8: Check Execution Status

```bash
# Poll every 5 seconds
curl http://localhost:8000/executions/exec_xyz789
```

**Status progression:**
```json
{"status": "queued"}      // Initial
{"status": "analyzing"}   // Agent 1 working
{"status": "generating_code"}  // Agent 2 working
{"status": "executing"}   // Agent 3 working
{"status": "completed"}   // Done!
```

### Step 9: Get Results

```bash
curl http://localhost:8000/executions/exec_xyz789/results
```

**Response:**
```json
{
  "id": "bt_run_123",
  "strategy_id": "strategy_abc123",
  "metrics": {
    "total_return": 12.45,
    "cagr": 54.23,
    "sharpe_ratio": 1.85,
    "max_drawdown": -8.32,
    "win_rate": 58.3,
    "trades": 12,
    "vs_benchmark": 3.21
  },
  "equity_series": [...],
  "trades": [...]
}
```

### Step 10: View Generated Code

```bash
curl http://localhost:8000/executions/exec_xyz789/code
```

**Response:**
```json
{
  "execution_id": "exec_xyz789",
  "language": "python",
  "code": "import vectorbt as vbt\nimport pandas as pd\n..."
}
```

---

## Troubleshooting

### Issue: "ANTHROPIC_API_KEY not found"

**Solution:**
```bash
# Add to .env
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" >> .env
```

### Issue: "ModuleNotFoundError: No module named 'crewai'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "Failed to import LangChain Anthropic"

**Solution:**
```bash
pip install langchain-anthropic langchain-core
```

### Issue: Execution stuck in "analyzing" status

**Possible causes:**
1. Anthropic API rate limit
2. Invalid API key
3. Network issues

**Solution:**
```bash
# Check logs
tail -f logs/app.log

# Verify API key works
python quick_test.py
# Choose 'y' to test LLM connection
```

### Issue: "No module named 'vectorbt'"

**Solution:**
```bash
# VectorBT requires specific versions
pip install numpy>=1.26.0,<2.0.0
pip install pandas>=2.0.0,<3.0.0
pip install vectorbt==0.26.2
```

### Issue: Code execution timeout

**Solution:**
Reduce date range in params:
```json
{
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"  // Just 1 month
}
```

---

## What Each Test Validates

### `quick_test.py` validates:
- ✅ Environment configuration
- ✅ Package installations
- ✅ Agent initialization
- ✅ Tool functionality
- ✅ LLM connectivity

### `test_strategy_execution.py` validates:
- ✅ MongoDB connection
- ✅ Strategy creation
- ✅ CrewAI workflow execution
- ✅ Agent collaboration
- ✅ Code generation
- ✅ Code execution
- ✅ Result storage

### API tests validate:
- ✅ REST endpoints
- ✅ Request/response formats
- ✅ Async execution
- ✅ Status tracking
- ✅ Error handling

---

## Expected Execution Time

| Test | Duration | What it does |
|------|----------|--------------|
| quick_test.py | 5-10 sec | Validates setup |
| test_strategy_execution.py | 1-2 min | Full workflow |
| API execution | 1-2 min | Same as above |

**Why 1-2 minutes?**
- Agent 1 (Analyzer): 10-20 seconds
- Agent 2 (Generator): 20-30 seconds
- Agent 3 (Executor): 30-60 seconds (VectorBT backtest)

---

## Success Criteria

✅ **All tests pass if you see:**

1. **quick_test.py:**
   - All 5 checks show ✅
   - No import errors
   - Agents initialize successfully

2. **test_strategy_execution.py:**
   - Strategy created in MongoDB
   - Execution completes with status "completed"
   - Backtest metrics returned
   - Generated code visible

3. **API tests:**
   - POST returns execution ID
   - GET shows status progression
   - Results endpoint returns metrics
   - Code endpoint returns Python code

---

## Next Steps After Testing

1. **Integrate with Frontend**
   - Add "Execute Strategy" button
   - Show real-time status updates
   - Display results in dashboard

2. **Monitor in Production**
   - Track execution times
   - Monitor LLM costs
   - Log agent decisions

3. **Optimize Performance**
   - Cache similar strategies
   - Optimize LLM prompts
   - Parallel execution for multiple strategies

---

## Quick Reference

```bash
# Install
pip install -r requirements.txt

# Quick validation
python quick_test.py

# Full test
python test_strategy_execution.py

# Start server
uvicorn app.main:app --reload

# Test API
curl -X POST http://localhost:8000/executions/strategies/{id}/execute \
  -H "Content-Type: application/json" \
  -d '{"params": {...}}'
```

---

## Support

If tests fail, check:
1. `.env` file has correct API keys
2. MongoDB is running and accessible
3. All dependencies installed
4. Python 3.12 is being used

For detailed validation report, see: `CREWAI_VALIDATION_REPORT.md`
