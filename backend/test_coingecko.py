"""
Test script for CoinGecko API integration
"""

from app.services.coingecko_service import (
    fetch_crypto_data,
    get_token_id,
    calculate_days_from_dates,
    get_days_from_period,
    TOP_20_TOKENS,
    PERIOD_TO_DAYS
)


def test_coingecko_integration():
    print("=" * 60)
    print("Testing CoinGecko API Integration")
    print("=" * 60)
    print()
    
    # Test 1: Display available tokens
    print("1. Available Tokens:")
    print("-" * 60)
    for name, token_id in list(TOP_20_TOKENS.items())[:5]:  # Show first 5
        print(f"   {name}: {token_id}")
    print(f"   ... and {len(TOP_20_TOKENS) - 5} more")
    print()
    
    # Test 2: Display period mappings
    print("2. Period Mappings:")
    print("-" * 60)
    for period, days in PERIOD_TO_DAYS.items():
        print(f"   {period}: {days}")
    print()
    
    # Test 3: Test token ID lookup
    print("3. Token ID Lookup:")
    print("-" * 60)
    try:
        token_id = get_token_id("Bitcoin")
        print(f"   Bitcoin -> {token_id}")
        token_id = get_token_id("Ethereum")
        print(f"   Ethereum -> {token_id}")
        token_id = get_token_id("DeFi")
        print(f"   DeFi -> {token_id}")
        print("   ✓ Token lookup successful")
    except Exception as e:
        print(f"   ✗ Token lookup failed: {e}")
    print()
    
    # Test 4: Test period conversion
    print("4. Period to Days Conversion:")
    print("-" * 60)
    for period in ["1M", "3M", "6M", "1Y"]:
        days = get_days_from_period(period)
        print(f"   {period} -> {days} days")
    print()
    
    # Test 5: Test date range calculation
    print("5. Date Range Calculation:")
    print("-" * 60)
    days = calculate_days_from_dates("2024-01-01", "2024-03-31")
    print(f"   2024-01-01 to 2024-03-31 -> {days} days")
    print()
    
    # Test 6: Fetch actual data from CoinGecko
    print("6. Fetching Bitcoin Data (last 90 days):")
    print("-" * 60)
    try:
        df = fetch_crypto_data("bitcoin", 90)
        print(f"   ✓ Successfully fetched {len(df)} data points")
        print(f"   Date range: {df.index[0]} to {df.index[-1]}")
        print(f"   First price: ${df['Close'].iloc[0]:.2f}")
        print(f"   Last price: ${df['Close'].iloc[-1]:.2f}")
        print(f"   Price change: {((df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100):.2f}%")
    except Exception as e:
        print(f"   ✗ Failed to fetch data: {e}")
    print()
    
    # Test 7: Test with Dogecoin
    print("7. Fetching Dogecoin Data (last 30 days):")
    print("-" * 60)
    try:
        df = fetch_crypto_data("dogecoin", 30)
        print(f"   ✓ Successfully fetched {len(df)} data points")
        print(f"   Date range: {df.index[0]} to {df.index[-1]}")
        print(f"   First price: ${df['Close'].iloc[0]:.6f}")
        print(f"   Last price: ${df['Close'].iloc[-1]:.6f}")
        print(f"   Price change: {((df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100):.2f}%")
    except Exception as e:
        print(f"   ✗ Failed to fetch data: {e}")
    print()
    
    print("=" * 60)
    print("CoinGecko Integration Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    test_coingecko_integration()

