# Research Agent Guide

## Overview

The Research Agent is an autonomous system that researches trading strategies, generates them, runs backtests, and identifies the highest probability performers. It uses CrewAI agents powered by Claude to perform intelligent market analysis and strategy design.

## Features

✅ **Autonomous Strategy Research**
- Analyzes current market conditions
- Identifies promising trading patterns
- Researches optimal entry/exit conditions

✅ **Intelligent Strategy Generation**
- Creates multiple strategy schemas automatically
- Customizes strategies based on market focus and risk level
- Generates structured strategies with entry/exit rules

✅ **Automated Backtesting**
- Runs backtests on all generated strategies
- Executes strategies using VectorBT
- Collects performance metrics

✅ **Performance Analysis & Ranking**
- Analyzes backtest results
- Ranks strategies by performance score
- Identifies highest probability winners
- Provides detailed insights and recommendations

## Architecture

### CrewAI Agents

The research agent uses three specialized AI agents:

1. **Market Researcher**
   - Role: Crypto Market Researcher
   - Analyzes market conditions and identifies opportunities
   - Outputs: Market insights, strategy concepts, optimal timeframes

2. **Strategy Designer**
   - Role: Trading Strategy Designer
   - Designs complete strategy schemas
   - Outputs: Strategy specifications with entry/exit rules

3. **Performance Analyzer**
   - Role: Performance Analyst
   - Evaluates backtest results
   - Outputs: Performance scores, rankings, recommendations

### Workflow

```
1. Research Market
   └─> Analyze conditions
   └─> Identify patterns
   └─> Generate concepts

2. Generate Strategies
   └─> Design schemas
   └─> Add to database
   └─> Create structures

3. Run Backtests
   └─> Execute strategies
   └─> Collect metrics
   └─> Store results

4. Analyze & Rank
   └─> Calculate scores
   └─> Rank by performance
   └─> Identify top performers
```

## API Endpoints

### Start Research Run

```http
POST /api/research/start
```

**Request Body:**
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
  "check_status_url": "/api/research/{research_id}"
}
```

### Get Research Status

```http
GET /api/research/{research_id}
```

**Response:**
```json
{
  "id": "uuid",
  "user_id": "user1",
  "num_strategies": 5,
  "market_focus": "Bitcoin",
  "risk_level": "Medium",
  "status": "completed",
  "started_at": "2024-10-27T10:00:00Z",
  "completed_at": "2024-10-27T10:15:00Z",
  "rankings": [
    {
      "strategy_id": "uuid",
      "strategy_name": "BTC Mean Reversion",
      "performance_score": 85,
      "rank": 1,
      "metrics": {
        "total_return": 45.2,
        "sharpe_ratio": 2.1,
        "max_drawdown": -12.5,
        "win_rate": 68.5
      },
      "strengths": ["High Sharpe ratio", "Low drawdown"],
      "weaknesses": ["Moderate win rate"],
      "recommendation": "Excellent risk-adjusted returns"
    }
  ]
}
```

### List Research Runs

```http
GET /api/research?limit=10
```

**Response:**
```json
[
  {
    "id": "uuid",
    "user_id": "user1",
    "num_strategies": 5,
    "status": "completed",
    "started_at": "2024-10-27T10:00:00Z",
    "completed_at": "2024-10-27T10:15:00Z",
    "num_results": 5
  }
]
```

### Get Top Strategy

```http
GET /api/research/{research_id}/top-strategy
```

**Response:**
```json
{
  "id": "uuid",
  "name": "BTC Mean Reversion Strategy",
  "description": "Mean reversion strategy for Bitcoin",
  "schema_json": {...},
  "performance_score": 85,
  "rank": 1,
  "metrics": {...},
  "strengths": [...],
  "weaknesses": [...],
  "recommendation": "..."
}
```

## Usage Examples

### Python

```python
import requests

# Start research
response = requests.post("http://localhost:8000/api/research/start", json={
    "num_strategies": 5,
    "market_focus": "Bitcoin",
    "risk_level": "High"
})
research_id = response.json()["research_id"]

# Check status
status = requests.get(f"http://localhost:8000/api/research/{research_id}")
print(status.json())

# Get top performer
top = requests.get(f"http://localhost:8000/api/research/{research_id}/top-strategy")
print(f"Top Strategy: {top.json()['name']}")
```

### cURL

```bash
# Start research
curl -X POST http://localhost:8000/api/research/start \
  -H "Content-Type: application/json" \
  -d '{"num_strategies": 3, "market_focus": "DeFi", "risk_level": "Medium"}'

# Check status
curl http://localhost:8000/api/research/{research_id}

# Get top strategy
curl http://localhost:8000/api/research/{research_id}/top-strategy
```

## Configuration

### Parameters

- **num_strategies** (int, default: 5)
  - Number of strategies to generate and test
  - Recommended: 3-10 strategies
  - More strategies = longer execution time

- **market_focus** (string, optional)
  - Target market category
  - Options: "Bitcoin", "Ethereum", "DeFi", "Altcoins", "NFT", "Memecoins"
  - If not specified, agent analyzes all categories

- **risk_level** (string, default: "Medium")
  - Risk tolerance for strategies
  - Options: "Low", "Medium", "High"
  - Affects stop loss, position sizing, and strategy aggressiveness

### Performance Metrics

Strategies are evaluated on:

1. **Total Return & CAGR** (higher is better)
   - Absolute and annualized returns

2. **Sharpe Ratio** (higher is better)
   - Risk-adjusted returns
   - Measures return per unit of risk

3. **Maximum Drawdown** (lower is better)
   - Largest peak-to-trough decline
   - Indicates downside risk

4. **Win Rate** (higher is better)
   - Percentage of profitable trades
   - Consistency indicator

5. **Number of Trades** (balanced is best)
   - Too few = insufficient data
   - Too many = overtrading

## Database Schema

### research_runs Table

```sql
CREATE TABLE research_runs (
    id UUID PRIMARY KEY,
    user_id TEXT NOT NULL,
    num_strategies INTEGER NOT NULL,
    market_focus TEXT,
    risk_level TEXT NOT NULL,
    status TEXT NOT NULL,
    rankings JSONB,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    error_message TEXT
);
```

## Testing

Run the test suite:

```bash
cd backend
python test_research_agent.py
```

Tests include:
1. Market research functionality
2. Strategy generation
3. Full workflow (optional, takes 5-10 minutes)

## Performance Considerations

### Execution Time

- **Market Research**: ~30-60 seconds
- **Strategy Generation**: ~20-40 seconds per strategy
- **Backtesting**: ~1-2 minutes per strategy
- **Performance Analysis**: ~30-60 seconds

**Total time for 5 strategies**: ~10-15 minutes

### API Rate Limits

The research agent makes multiple API calls to Anthropic/Bedrock:
- Market research: 1 call
- Strategy generation: N calls (where N = num_strategies)
- Performance analysis: 1 call

**Total API calls**: N + 2

### Cost Optimization

To reduce costs and execution time:
1. Start with fewer strategies (2-3) for testing
2. Use specific market_focus to reduce research scope
3. Run during off-peak hours if rate-limited
4. Cache market research results for similar runs

## Best Practices

### 1. Start Small
Begin with 2-3 strategies to understand the system before scaling up.

### 2. Use Specific Market Focus
Specify market_focus to get more targeted strategies:
```json
{"market_focus": "Bitcoin", "num_strategies": 3}
```

### 3. Monitor Progress
Check research status periodically:
```bash
while true; do
  curl http://localhost:8000/api/research/{id} | jq '.status'
  sleep 30
done
```

### 4. Review Top Performers
After completion, analyze the top 3 strategies:
```bash
curl http://localhost:8000/api/research/{id}/top-strategy | jq
```

### 5. Iterate and Refine
Use insights from completed runs to inform future research parameters.

## Troubleshooting

### Research Agent Fails to Start

**Problem**: API returns error when starting research

**Solutions**:
- Check database connection
- Verify ANTHROPIC_API_KEY is set
- Check API rate limits
- Review backend logs

### Strategies Not Generating

**Problem**: Research completes but no strategies created

**Solutions**:
- Check LLM service configuration
- Verify database write permissions
- Review agent logs for errors
- Ensure schema_json format is correct

### Backtests Failing

**Problem**: Strategies generate but backtests fail

**Solutions**:
- Verify VectorBT is installed
- Check data availability
- Review generated strategy code
- Check execution service logs

### Performance Analysis Incomplete

**Problem**: Rankings not calculated or incomplete

**Solutions**:
- Ensure backtest metrics are collected
- Check performance analyzer agent logs
- Verify JSON parsing in analysis
- Review ranking algorithm

## Future Enhancements

Planned improvements:

- [ ] Real-time progress streaming
- [ ] Custom performance criteria
- [ ] Multi-timeframe analysis
- [ ] Strategy combination recommendations
- [ ] Historical performance tracking
- [ ] A/B testing framework
- [ ] Portfolio optimization
- [ ] Risk parity balancing
- [ ] Walk-forward analysis
- [ ] Monte Carlo simulations

## Support

For issues or questions:
1. Check logs in `/workspace/backend/`
2. Review test results
3. Consult API documentation
4. Check database schema

## License

Part of Vibe Water Associates Trading Platform
