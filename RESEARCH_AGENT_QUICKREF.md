# Research Agent - Quick Reference

## 🎯 What Is It?

An autonomous AI agent that:
- Researches crypto trading strategies
- Generates multiple strategy schemas
- Runs backtests automatically
- Identifies highest probability performers

## 🚀 Quick Start (60 seconds)

1. **Start backend** (if not running)
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Run research agent**
   ```bash
   cd backend
   python quick_start_research.py
   ```

3. **Wait 5-10 minutes** for results

4. **View top strategy** in the output

## 📋 Files Overview

| File | Purpose |
|------|---------|
| `backend/RESEARCH_AGENT_README.md` | **Start here** - Complete usage guide |
| `backend/quick_start_research.py` | Interactive script to run research |
| `backend/test_research_agent.py` | Test suite |
| `backend/app/services/research_agent_service.py` | Core service |
| `backend/app/routers/research.py` | API endpoints |
| `backend/add_research_table.sql` | Database migration |
| `RESEARCH_AGENT_GUIDE.md` | Comprehensive documentation |
| `RESEARCH_AGENT_IMPLEMENTATION.md` | Technical implementation details |

## 🔗 Key Endpoints

```bash
# Start research
POST /api/research/start

# Check status
GET /api/research/{id}

# Get top strategy
GET /api/research/{id}/top-strategy

# List all runs
GET /api/research
```

## ⚡ Examples

**Generate 3 Bitcoin strategies:**
```bash
curl -X POST http://localhost:8000/api/research/start \
  -H "Content-Type: application/json" \
  -d '{"num_strategies": 3, "market_focus": "Bitcoin", "risk_level": "Medium"}'
```

**Check status:**
```bash
curl http://localhost:8000/api/research/{research_id}
```

## 📊 What You Get

Ranked strategies with:
- Performance score (0-100)
- Backtest metrics (return, Sharpe, drawdown)
- Strengths and weaknesses
- Actionable recommendations

## ⏱️ Timing

| Strategies | Time |
|-----------|------|
| 2-3 | 5-8 min |
| 5 | 10-15 min |
| 10 | 20-30 min |

## 🛠️ Setup

### One-Time Setup

1. **Add database table**
   ```bash
   psql -h <host> -U postgres -d postgres -f backend/add_research_table.sql
   ```

2. **Set environment variables**
   ```bash
   export ANTHROPIC_API_KEY=your_key_here
   export DATABASE_URL=your_database_url
   ```

## 🧪 Test It

```bash
cd backend
python test_research_agent.py
```

## 📖 Full Documentation

Read these in order:
1. `backend/RESEARCH_AGENT_README.md` - Usage guide
2. `RESEARCH_AGENT_GUIDE.md` - Complete reference
3. `RESEARCH_AGENT_IMPLEMENTATION.md` - Technical details

## 🎓 Learn By Example

**Beginner:**
```bash
python backend/quick_start_research.py
```

**Intermediate:**
```python
import requests
r = requests.post("http://localhost:8000/api/research/start", 
                  json={"num_strategies": 5})
research_id = r.json()["research_id"]
```

**Advanced:**
See `backend/app/services/research_agent_service.py`

## ✅ Checklist

Before using research agent:
- [ ] Backend running on port 8000
- [ ] Database connected
- [ ] ANTHROPIC_API_KEY set
- [ ] research_runs table exists
- [ ] Test suite passes

## 🆘 Troubleshooting

**Can't connect to API?**
→ Check backend is running: `uvicorn app.main:app`

**No strategies generated?**
→ Check logs and API key

**Slow execution?**
→ Reduce num_strategies to 2-3

**Database error?**
→ Run migration: `add_research_table.sql`

## 🎉 Success Criteria

You're successful when you see:
```
TOP 3 STRATEGIES:
----------------
#1. BTC Mean Reversion Strategy
    Performance Score: 85/100
    Total Return: 45.2%
    Sharpe Ratio: 2.1
```

## 🔗 Related Features

- Strategy Builder: `/builder`
- Backtest Simulator: `/backtest-simulator`
- Strategy Execution: `/api/executions`

## 💡 Pro Tips

1. Start with 2-3 strategies for testing
2. Use specific market_focus for better results
3. Review top 3 performers, not just #1
4. Re-run top strategies with different parameters
5. Track research_runs in database for history

## 📞 Need Help?

1. Check `backend/RESEARCH_AGENT_README.md`
2. Run test suite: `python test_research_agent.py`
3. Review logs in backend console
4. Check API docs: http://localhost:8000/docs

---

**Status:** ✅ Production Ready

**Version:** 1.0.0

**Last Updated:** October 27, 2025
