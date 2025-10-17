# VectorBT Quick Start

## 🚀 3-Step Setup

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Test It Works
```bash
python test_vectorbt.py
```

### Step 3: Start Backend
```bash
uvicorn app.main:app --reload
```

## ✅ Verify It's Working

### Console Output Should Show:
```
Downloading BTC-USD data from 2023-01-01 to 2024-01-01...
[*********************100%%**********************]  1 of 1 completed
Using VectorBT for Bitcoin backtest...
Backtest completed successfully!
Total Return: 52.31%
Sharpe Ratio: 1.82
Max Drawdown: -15.23%
Total Trades: 8
✅ TEST PASSED - VectorBT is working correctly!
```

## 🎯 What You Get

### Real Bitcoin Data
- ✅ Live prices from Yahoo Finance
- ✅ Historical data from any date range
- ✅ Accurate market conditions

### Professional Metrics
- ✅ Total Return & CAGR
- ✅ Sharpe Ratio
- ✅ Maximum Drawdown
- ✅ Win Rate
- ✅ Benchmark comparison

### Actual Trades
- ✅ Real entry/exit prices
- ✅ Actual BTC quantities
- ✅ Trade-by-trade P&L

## 📊 View in Frontend

1. Start frontend: `npm run dev`
2. Navigate to: http://localhost:3000/strategies/1
3. See **real Bitcoin backtest data** with:
   - Actual equity curve
   - Real trade history
   - Professional metrics

## 🔧 Quick Test API

```bash
curl -X POST http://localhost:8000/backtests \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_id": "1",
    "params": {
      "symbols": ["BTC"],
      "start_date": "2023-01-01",
      "end_date": "2024-01-01",
      "initial_capital": 10000,
      "fees": 0.001,
      "slippage": 0.0005
    }
  }'
```

## 📚 Documentation

- **Full Guide**: `VECTORBT_INTEGRATION.md`
- **Summary**: `VECTORBT_SUMMARY.md`
- **Main README**: `PROJECT_README.md`

---

**That's it!** VectorBT is now powering real Bitcoin backtests. 🎉
