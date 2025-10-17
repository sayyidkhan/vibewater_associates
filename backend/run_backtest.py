"""
Run a backtest and send it to the API
This will populate the frontend with real VectorBT data
"""

import asyncio
import requests
from datetime import datetime, timedelta
from app.models import BacktestParams

async def run_and_save_backtest():
    print("=" * 60)
    print("Running Bitcoin Backtest and Saving to API")
    print("=" * 60)
    print()
    
    # Create backtest parameters (past 3 months)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    params = {
        "strategy_id": "1",
        "params": {
            "symbols": ["BTC"],
            "timeframe": "1D",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "initial_capital": 10000,
            "benchmark": "USD",
            "fees": 0.001,
            "slippage": 0.0005,
            "position_sizing": "fixed",
            "exposure": 1.0
        }
    }
    
    print(f"Backtest Parameters:")
    print(f"  Strategy ID: 1 (Bitcoin MA Crossover)")
    print(f"  Period: {params['params']['start_date']} to {params['params']['end_date']}")
    print(f"  Initial Capital: ${params['params']['initial_capital']:,.2f}")
    print()
    
    # Send request to backend
    print("Sending backtest request to API...")
    try:
        response = requests.post(
            "http://localhost:8000/backtests",
            json=params,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print()
            print("=" * 60)
            print("✅ BACKTEST COMPLETED AND SAVED!")
            print("=" * 60)
            print()
            
            metrics = result['metrics']
            print("Performance Metrics:")
            print(f"  Total Return:     {metrics['total_return']:>10.2f}%")
            print(f"  CAGR:             {metrics['cagr']:>10.2f}%")
            print(f"  Sharpe Ratio:     {metrics['sharpe_ratio']:>10.2f}")
            print(f"  Max Drawdown:     {metrics['max_drawdown']:>10.2f}%")
            print(f"  Win Rate:         {metrics['win_rate']:>10.1f}%")
            print(f"  Total Trades:     {metrics['trades']:>10}")
            print()
            
            print(f"Trades: {len(result.get('trades', []))}")
            for trade in result.get('trades', [])[:5]:
                print(f"  {trade['date']} - {trade['type']:4} @ ${trade['price']:,.2f}")
            print()
            
            print("=" * 60)
            print("🎉 View results at: http://localhost:3000/strategies/1")
            print("=" * 60)
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to backend")
        print("Make sure the backend is running:")
        print("  cd backend")
        print("  uv run uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_and_save_backtest())
