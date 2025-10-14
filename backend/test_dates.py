"""
Test to verify date order in backtest data
"""

import requests
import json

API_URL = "http://localhost:8000"

print("=" * 60)
print("Testing Date Order in Backtest Data")
print("=" * 60)
print()

# Get backtests for strategy 1
response = requests.get(f"{API_URL}/backtests/strategy/1")

if response.status_code == 200:
    backtests = response.json()
    
    if len(backtests) > 0:
        latest = backtests[0]
        equity_series = latest['equity_series']
        
        print(f"Total equity points: {len(equity_series)}")
        print()
        
        print("First 5 dates:")
        for i in range(min(5, len(equity_series))):
            point = equity_series[i]
            print(f"  {i+1}. {point['date']} - BTC: ${point.get('btc_price', 0):,.2f}")
        
        print()
        print("Last 5 dates:")
        for i in range(max(0, len(equity_series) - 5), len(equity_series)):
            point = equity_series[i]
            print(f"  {i+1}. {point['date']} - BTC: ${point.get('btc_price', 0):,.2f}")
        
        print()
        
        # Check if dates are in order
        dates = [point['date'] for point in equity_series]
        sorted_dates = sorted(dates)
        
        if dates == sorted_dates:
            print("✅ Dates are in ASCENDING order (correct)")
        elif dates == sorted_dates[::-1]:
            print("❌ Dates are in DESCENDING order (reversed)")
        else:
            print("⚠️  Dates are NOT sorted")
        
        print()
        print("Expected order: 2025-07-14 → 2025-10-12")
        print(f"Actual order:   {dates[0]} → {dates[-1]}")
        
    else:
        print("No backtests found")
else:
    print(f"Error: {response.status_code}")

print()
print("=" * 60)
