# Research Agent

## 🎯 What It Does

The Research Agent is an autonomous AI system that:
- ✅ Researches trading strategies based on market conditions
- ✅ Generates multiple strategy schemas automatically
- ✅ Adds them to the database
- ✅ Runs backtests on all strategies
- ✅ Identifies the highest probability performers

## 🚀 Quick Start

### Prerequisites

1. **Backend running**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Database connected** (Supabase or local PostgreSQL)
   - Run migration: `add_research_table.sql`

3. **Environment variables set**
   ```bash
   ANTHROPIC_API_KEY=your_key_here
   DATABASE_URL=your_database_url
   ```

### Run Research Agent

**Option 1: Interactive Script (Recommended)**
```bash
cd backend
python quick_start_research.py
```

This will:
- Generate 3 strategies (configurable)
- Focus on Bitcoin market
- Use Medium risk level
- Show real-time progress
- Display ranked results

**Option 2: API Calls**
```bash
# Start research
curl -X POST http://localhost:8000/api/research/start \
  -H "Content-Type: application/json" \
  -d '{
    "num_strategies": 5,
    "market_focus": "Bitcoin",
    "risk_level": "Medium"
  }'

# Get results (after 10-15 minutes)
curl http://localhost:8000/api/research/{research_id}

# Get top strategy
curl http://localhost:8000/api/research/{research_id}/top-strategy
```

**Option 3: Python SDK**
```python
import requests
import time

# Start research
r = requests.post("http://localhost:8000/api/research/start", json={
    "num_strategies": 5,
    "market_focus": "DeFi",
    "risk_level": "High"
})

research_id = r.json()["research_id"]

# Wait for completion
while True:
    status = requests.get(f"http://localhost:8000/api/research/{research_id}")
    if status.json()["status"] == "completed":
        break
    time.sleep(30)

# Get results
results = status.json()
print(f"Top strategy: {results['rankings'][0]['strategy_name']}")
```

## ⚙️ Configuration

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `num_strategies` | int | 5 | Number of strategies to generate (2-20 recommended) |
| `market_focus` | string | null | Target market: "Bitcoin", "Ethereum", "DeFi", "Altcoins", etc. |
| `risk_level` | string | "Medium" | Risk tolerance: "Low", "Medium", "High" |

### Examples

**Conservative Bitcoin strategies:**
```json
{
  "num_strategies": 3,
  "market_focus": "Bitcoin",
  "risk_level": "Low"
}
```

**Aggressive DeFi strategies:**
```json
{
  "num_strategies": 10,
  "market_focus": "DeFi",
  "risk_level": "High"
}
```

**Auto-detect best market:**
```json
{
  "num_strategies": 5,
  "market_focus": null,
  "risk_level": "Medium"
}
```

## 📊 Output

### Rankings Format

```json
{
  "rankings": [
    {
      "strategy_id": "uuid",
      "strategy_name": "BTC Mean Reversion Strategy",
      "performance_score": 85,
      "rank": 1,
      "metrics": {
        "total_return": 45.2,
        "cagr": 38.5,
        "sharpe_ratio": 2.1,
        "max_drawdown": -12.5,
        "win_rate": 68.5,
        "trades": 156
      },
      "strengths": [
        "High Sharpe ratio",
        "Low drawdown",
        "Consistent returns"
      ],
      "weaknesses": [
        "Moderate win rate"
      ],
      "recommendation": "Excellent risk-adjusted returns"
    }
  ]
}
```

### Performance Scores

Strategies are scored 0-100 based on:
- **Total Return & CAGR** (30%) - Absolute performance
- **Sharpe Ratio** (30%) - Risk-adjusted returns
- **Max Drawdown** (20%) - Downside protection
- **Win Rate** (10%) - Consistency
- **Trade Count** (10%) - Statistical significance

## 🕐 Execution Time

| Strategies | Estimated Time |
|-----------|----------------|
| 2-3 | 5-8 minutes |
| 5 | 10-15 minutes |
| 10 | 20-30 minutes |
| 20 | 40-60 minutes |

**Breakdown per strategy:**
- Market research: 30-60s (shared)
- Strategy generation: 20-40s
- Backtest execution: 1-2 min
- Performance analysis: 30-60s (shared)

## 🧪 Testing

Run the test suite:
```bash
cd backend
python test_research_agent.py
```

Tests:
1. ✅ Market research functionality
2. ✅ Strategy generation
3. ✅ Full workflow (optional)

## 📖 API Reference

### POST /api/research/start
Start new research run

**Request:**
```json
{
  "num_strategies": 5,
  "market_focus": "Bitcoin",
  "risk_level": "Medium"
}
```

**Response:**
```json
{
  "research_id": "uuid",
  "status": "running",
  "message": "Research agent started. Generating 5 strategies...",
  "check_status_url": "/api/research/{id}"
}
```

### GET /api/research/{id}
Get research status and results

**Response:**
```json
{
  "id": "uuid",
  "status": "completed",
  "rankings": [...],
  "started_at": "2024-10-27T10:00:00Z",
  "completed_at": "2024-10-27T10:15:00Z"
}
```

### GET /api/research
List recent research runs

**Response:**
```json
[
  {
    "id": "uuid",
    "num_strategies": 5,
    "status": "completed",
    "started_at": "2024-10-27T10:00:00Z",
    "num_results": 5
  }
]
```

### GET /api/research/{id}/top-strategy
Get top-performing strategy details

**Response:**
```json
{
  "id": "uuid",
  "name": "Strategy Name",
  "schema_json": {...},
  "performance_score": 85,
  "metrics": {...},
  "recommendation": "..."
}
```

## 🔧 Troubleshooting

### Research doesn't start
**Problem:** POST /api/research/start returns error

**Solutions:**
1. Check backend is running
2. Verify database connection
3. Confirm ANTHROPIC_API_KEY is set
4. Check API rate limits

### Long execution time
**Problem:** Research takes longer than expected

**Solutions:**
1. Reduce `num_strategies` (start with 2-3)
2. Check API response times
3. Verify network connection
4. Monitor backend logs

### No strategies generated
**Problem:** Research completes but rankings are empty

**Solutions:**
1. Check LLM service configuration
2. Verify database write permissions
3. Review agent logs for errors
4. Check strategy schema validation

### Backtest failures
**Problem:** Strategies generate but backtests fail

**Solutions:**
1. Verify VectorBT installation
2. Check data availability
3. Review execution service logs
4. Validate strategy code generation

## 💡 Best Practices

### 1. Start Small
Begin with 2-3 strategies to understand the system:
```bash
python quick_start_research.py  # Uses 3 strategies by default
```

### 2. Use Specific Market Focus
Get better results with focused research:
```json
{"market_focus": "Bitcoin", "num_strategies": 3}
```

### 3. Match Risk to Capital
- **Low Risk**: Small accounts, capital preservation
- **Medium Risk**: Balanced growth
- **High Risk**: Large accounts, aggressive growth

### 4. Review Top 3
Focus on top 3 performers:
```bash
curl http://localhost:8000/api/research/{id}/top-strategy
```

### 5. Iterate and Refine
Use insights from runs to improve future research.

## 📚 Additional Resources

- **Full Documentation:** [RESEARCH_AGENT_GUIDE.md](../RESEARCH_AGENT_GUIDE.md)
- **Implementation Details:** [RESEARCH_AGENT_IMPLEMENTATION.md](../RESEARCH_AGENT_IMPLEMENTATION.md)
- **Database Schema:** [schema.sql](schema.sql)
- **API Router:** [app/routers/research.py](app/routers/research.py)
- **Service Code:** [app/services/research_agent_service.py](app/services/research_agent_service.py)

## 🎓 Examples

### Example 1: Quick Test
```bash
# Generate 2 Bitcoin strategies (fastest test)
curl -X POST http://localhost:8000/api/research/start \
  -H "Content-Type: application/json" \
  -d '{"num_strategies": 2, "market_focus": "Bitcoin", "risk_level": "Medium"}'
```

### Example 2: DeFi Research
```python
import requests

# Generate 5 DeFi strategies
r = requests.post("http://localhost:8000/api/research/start", json={
    "num_strategies": 5,
    "market_focus": "DeFi",
    "risk_level": "High"
})

print(f"Research ID: {r.json()['research_id']}")
```

### Example 3: Comprehensive Analysis
```bash
# Generate 10 strategies across all markets
curl -X POST http://localhost:8000/api/research/start \
  -H "Content-Type: application/json" \
  -d '{"num_strategies": 10, "market_focus": null, "risk_level": "Medium"}'
```

## 🆘 Support

Need help?
1. Check logs: `tail -f backend.log`
2. Run tests: `python test_research_agent.py`
3. Review API docs: http://localhost:8000/docs
4. Check database: Query `research_runs` table

## 🎉 Success!

If you can see ranked strategies with performance metrics, you're all set! 🚀

The research agent is now autonomously finding the highest probability trading strategies for you.
