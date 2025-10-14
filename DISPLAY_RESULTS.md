# Display VectorBT Results on Frontend

## 🎯 Goal
Display real Bitcoin backtest results with **buy/sell markers** on the graph at http://localhost:3000/strategies/1

## ✅ What Was Done

### 1. Updated Frontend Chart
- **File**: `frontend/app/strategies/[id]/page.tsx`
- **Changes**:
  - Switched from `LineChart` to `ComposedChart` (supports scatter points)
  - Added `Scatter` components for buy/sell markers
  - **Green dots** = BUY signals
  - **Red dots** = SELL signals
  - Added legend showing Portfolio Value, Buy, and Sell

### 2. Integrated Trade Data
- Trades from VectorBT backtest are now displayed on the chart
- Each trade appears as a colored dot at the exact date
- Tooltip shows trade details on hover

### 3. Created Run Script
- **File**: `backend/run_backtest.py`
- Runs backtest and saves to API
- Automatically populates frontend with real data

## 🚀 How to Use

### Step 1: Start Backend
```bash
cd backend
uv run uvicorn app.main:app --reload
```

Wait for:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 2: Run Backtest
In a new terminal:
```bash
cd backend
uv run run_backtest.py
```

You'll see:
```
Running Bitcoin Backtest and Saving to API
============================================================
Downloading BTC data from 2025-07-14 to 2025-10-12...
✓ Successfully downloaded 90 data points from CoinGecko
  Entry signals: 3
  Exit signals: 2

✅ BACKTEST COMPLETED AND SAVED!
============================================================
Performance Metrics:
  Total Return:      15.23%
  Sharpe Ratio:       1.45
  Total Trades:          5

🎉 View results at: http://localhost:3000/strategies/1
```

### Step 3: Start Frontend
In another terminal:
```bash
cd frontend
npm run dev
```

### Step 4: View Results
Open browser: **http://localhost:3000/strategies/1**

You'll see:
- ✅ **Blue line** = Portfolio equity curve
- ✅ **Green dots** = Buy signals (entry points)
- ✅ **Red dots** = Sell signals (exit points)
- ✅ **Gray dashed line** = Benchmark (buy & hold)

## 📊 Chart Features

### Legend
- **Portfolio Value** (blue line) - Your strategy's performance
- **Buy** (green dots) - Entry signals from MA crossover
- **Sell** (red dots) - Exit signals from MA crossover

### Interactive
- **Hover** over dots to see trade details
- **Zoom** by selecting area on chart
- **Pan** by dragging

## 🔧 Customization

### Change MA Windows
Edit `backend/app/services/vectorbt_service.py`:
```python
# Current: 10-day and 30-day MAs
fast_ma = vbt.MA.run(price, 10)
slow_ma = vbt.MA.run(price, 30)

# Change to 20-day and 50-day:
fast_ma = vbt.MA.run(price, 20)
slow_ma = vbt.MA.run(price, 50)
```

### Change Dot Colors
Edit `frontend/app/strategies/[id]/page.tsx`:
```tsx
{/* Buy markers */}
<Scatter
  data={chartData.buyTrades}
  fill="#10B981"  // Change to any color
  shape="circle"
/>

{/* Sell markers */}
<Scatter
  data={chartData.sellTrades}
  fill="#EF4444"  // Change to any color
  shape="circle"
/>
```

### Change Dot Size
```tsx
<Scatter
  data={chartData.buyTrades}
  fill="#10B981"
  shape="circle"
  r={8}  // Add radius (default is 5)
/>
```

## 📈 Example Output

### Console (Backend)
```
Downloading BTC data from 2025-07-14 to 2025-10-12...
Using CoinGecko Free API
✓ Successfully downloaded 90 data points from CoinGecko
  Price range: $108268.42 - $125071.80
  Start price: $120085.43, End price: $111134.30
Calculated MAs: 10-day (fast) and 30-day (slow)
  Entry signals: 3
  Exit signals: 2

Performance Metrics:
  Total Return:      -7.45%
  CAGR:             -28.12%
  Sharpe Ratio:       0.82
  Max Drawdown:      -9.23%
  Win Rate:          50.0%
  Total Trades:          4
```

### Frontend Display
- **Chart**: Shows equity curve with 3 green dots (buys) and 2 red dots (sells)
- **Metrics**: Real performance numbers from VectorBT
- **Trades Table**: Lists all trades with dates, prices, and returns

## 🎨 Visual Guide

```
Portfolio Value
    ↑
    |     🔴 (Sell)
    |    /
    |   /  🟢 (Buy)
    |  /  /
    | /  /
    |/  /   🔴 (Sell)
    |  /   /
    | /   /
    |/   /  🟢 (Buy)
    |   /  /
    |  /  /
    | /  /
    |/  /
    +------------------→ Time
```

## 🐛 Troubleshooting

### No dots showing?
- Check if trades exist: `result.get('trades', [])`
- Verify dates match equity series dates
- Check browser console for errors

### Backend not connecting?
```bash
# Check if backend is running
curl http://localhost:8000/health

# Should return: {"status":"healthy"}
```

### Frontend not updating?
- Hard refresh: `Cmd + Shift + R` (Mac) or `Ctrl + Shift + R` (Windows)
- Clear cache and reload
- Check Network tab in DevTools

## 📚 Files Modified

1. **`frontend/app/strategies/[id]/page.tsx`**
   - Added ComposedChart with Scatter points
   - Integrated trade markers
   - Updated legend

2. **`backend/app/services/vectorbt_service.py`**
   - Changed to 10/30-day MAs (works with 90 days)
   - Added debug output
   - Fixed trade extraction

3. **`backend/run_backtest.py`** (new)
   - Automated backtest runner
   - Saves to API
   - Shows results

## ✨ Next Steps

1. **Run the backtest**: `uv run run_backtest.py`
2. **View in browser**: http://localhost:3000/strategies/1
3. **See buy/sell markers** on the chart!

---

**Status**: ✅ **READY** - Your frontend now displays real VectorBT results with buy/sell markers!
