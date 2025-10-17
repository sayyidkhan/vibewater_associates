"""
Test API endpoints to verify data flow
"""

import requests
import json

API_URL = "http://localhost:8000"

print("=" * 60)
print("Testing API Endpoints")
print("=" * 60)
print()

# Test 1: Health check
print("1. Testing health endpoint...")
try:
    response = requests.get(f"{API_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print("   ✓ Health check passed")
except Exception as e:
    print(f"   ❌ Error: {e}")
print()

# Test 2: Get backtests for strategy 1
print("2. Getting backtests for strategy 1...")
try:
    response = requests.get(f"{API_URL}/backtests/strategy/1")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        backtests = response.json()
        print(f"   Found {len(backtests)} backtest(s)")
        
        if len(backtests) > 0:
            latest = backtests[0]
            print()
            print("   Latest Backtest:")
            print(f"     Strategy ID: {latest['strategy_id']}")
            print(f"     Total Return: {latest['metrics']['total_return']}%")
            print(f"     Trades: {latest['metrics']['trades']}")
            print(f"     Equity Points: {len(latest['equity_series'])}")
            print(f"     Trade Records: {len(latest.get('trades', []))}")
            
            # Show first few trades
            if latest.get('trades'):
                print()
                print("   Recent Trades:")
                for trade in latest['trades'][:3]:
                    print(f"     {trade['date']} - {trade['type']:4} @ ${trade['price']:,.2f}")
            
            print("   ✓ Backtest data retrieved successfully")
        else:
            print("   ⚠️  No backtests found. Run: uv run run_backtest.py")
    else:
        print(f"   ❌ Error: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")
print()

print("=" * 60)
print("API Test Complete")
print("=" * 60)
