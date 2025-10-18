"""
CoinGecko API service for fetching cryptocurrency historical price data.
"""

import requests
import pandas as pd
from datetime import datetime
from typing import Optional
from ..config import settings

# Top 20 cryptocurrencies by market cap
TOP_20_TOKENS = {
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum",
    "Tether": "tether",
    "BNB": "binancecoin",
    "Solana": "solana",
    "XRP": "ripple",
    "Cardano": "cardano",
    "Dogecoin": "dogecoin",
    "Avalanche": "avalanche-2",
    "Polkadot": "polkadot",
    "TRON": "tron",
    "Chainlink": "chainlink",
    "Polygon": "matic-network",
    "Litecoin": "litecoin",
    "Shiba Inu": "shiba-inu",
    "Uniswap": "uniswap",
    "Dai": "dai",
    "Wrapped Bitcoin": "wrapped-bitcoin",
    "Cosmos": "cosmos",
    "Ethereum Classic": "ethereum-classic",
    # Additional categories
    "DeFi": "uniswap",  # Representative DeFi token
    "Layer1": "ethereum",  # Representative Layer1
}

# Period to days mapping (matching frontend timeframes)
PERIOD_TO_DAYS = {
    "1M": 30,
    "3M": 90,
    "6M": 180,
    "1Y": 365,
    "YTD": None,  # Calculated dynamically
    "Max": "max",
}


def fetch_crypto_data(token_id: str, days: int) -> pd.DataFrame:
    """
    Fetch historical price data from CoinGecko API.
    
    Args:
        token_id: CoinGecko token ID (e.g., "bitcoin", "ethereum")
        days: Number of days of historical data to fetch
    
    Returns:
        DataFrame with datetime index and 'Close' column containing prices
    
    Raises:
        Exception: If API request fails or returns invalid data
    """
    # Build API URL
    base_url = "https://api.coingecko.com/api/v3/coins"
    url = f"{base_url}/{token_id}/market_chart"
    
    params = {
        "vs_currency": "usd",
        "days": days
    }
    
    # Add API key if available
    if settings.coingecko_api_key:
        params["x_cg_pro_api_key"] = settings.coingecko_api_key
    
    try:
        # Make API request
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract prices array
        if "prices" not in data:
            raise ValueError(f"No price data returned for {token_id}")
        
        prices = data["prices"]
        
        if not prices:
            raise ValueError(f"Empty price data returned for {token_id}")
        
        # Convert to DataFrame
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        
        # Convert timestamp from milliseconds to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        
        # Set timestamp as index
        df.set_index("timestamp", inplace=True)
        
        # Rename price column to match VectorBT expectations
        df.rename(columns={"price": "Close"}, inplace=True)
        
        # Sort by date
        df.sort_index(inplace=True)
        
        return df
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch data from CoinGecko: {str(e)}")
    except (KeyError, ValueError) as e:
        raise Exception(f"Invalid data format from CoinGecko: {str(e)}")


def get_token_id(category_or_name: str) -> str:
    """
    Get CoinGecko token ID from category or token name.
    
    Args:
        category_or_name: Category (e.g., "Bitcoin", "DeFi") or token name
    
    Returns:
        CoinGecko token ID
    
    Raises:
        ValueError: If token is not found in TOP_20_TOKENS
    """
    if category_or_name in TOP_20_TOKENS:
        return TOP_20_TOKENS[category_or_name]
    
    # Try case-insensitive match
    for key, value in TOP_20_TOKENS.items():
        if key.lower() == category_or_name.lower():
            return value
    
    raise ValueError(
        f"Token '{category_or_name}' not found. "
        f"Available tokens: {', '.join(TOP_20_TOKENS.keys())}"
    )


def calculate_days_from_dates(start_date: str, end_date: str) -> int:
    """
    Calculate number of days between two dates.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        Number of days between dates
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    return (end - start).days


def get_days_from_period(period: str) -> Optional[int]:
    """
    Convert period string to number of days.
    
    Args:
        period: Period string (e.g., "1M", "3M", "6M", "1Y")
    
    Returns:
        Number of days or None if period not recognized
    """
    if period in PERIOD_TO_DAYS:
        days = PERIOD_TO_DAYS[period]
        if days == "max":
            return 365 * 5  # 5 years for "max"
        elif period == "YTD":
            # Calculate days from start of year
            now = datetime.now()
            start_of_year = datetime(now.year, 1, 1)
            return (now - start_of_year).days
        return days
    return None

