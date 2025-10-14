from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from ..models import Strategy, StrategyMetrics
from ..database import get_database

router = APIRouter(prefix="/strategies", tags=["strategies"])

@router.post("", response_model=Strategy)
async def create_strategy(strategy: Strategy):
    """Create a new trading strategy"""
    db = get_database()
    
    strategy_dict = strategy.model_dump(exclude={"id"})
    strategy_dict["created_at"] = datetime.utcnow()
    strategy_dict["updated_at"] = datetime.utcnow()
    
    result = await db.strategies.insert_one(strategy_dict)
    strategy_dict["id"] = str(result.inserted_id)
    
    return Strategy(**strategy_dict)

@router.get("", response_model=List[Strategy])
async def get_strategies(
    status: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None)
):
    """Get all strategies with optional filters"""
    db = get_database()
    
    query = {}
    if status:
        query["status"] = status
    if user_id:
        query["user_id"] = user_id
    
    # For demo, return mock data
    mock_strategies = [
        Strategy(
            id="1",
            user_id="user1",
            name="Buy low, sell high",
            description="A simple strategy that buys when the price is low and sells when the price is high.",
            status="Live",
            schema_json={"nodes": [], "connections": []},
            guardrails=[],
            metrics=StrategyMetrics(
                total_return=12.5,
                cagr=8.5,
                sharpe_ratio=1.8,
                max_drawdown=-5.2,
                win_rate=62,
                trades=125,
                vs_benchmark=3.1
            )
        ),
        Strategy(
            id="2",
            user_id="user1",
            name="Trend following",
            description="A strategy that follows the trend of the market.",
            status="Paper",
            schema_json={"nodes": [], "connections": []},
            guardrails=[],
            metrics=StrategyMetrics(
                total_return=25.1,
                cagr=18.3,
                sharpe_ratio=2.3,
                max_drawdown=-8.9,
                win_rate=58,
                trades=87,
                vs_benchmark=5.2
            )
        ),
        Strategy(
            id="3",
            user_id="user1",
            name="Mean reversion",
            description="A strategy that bets on price reverting to its mean.",
            status="Backtest",
            schema_json={"nodes": [], "connections": []},
            guardrails=[],
            metrics=StrategyMetrics(
                total_return=-2.3,
                cagr=-1.5,
                sharpe_ratio=-0.4,
                max_drawdown=-15.7,
                win_rate=45,
                trades=203,
                vs_benchmark=-8.1
            )
        )
    ]
    
    return mock_strategies

@router.get("/{strategy_id}", response_model=Strategy)
async def get_strategy(strategy_id: str):
    """Get a specific strategy by ID"""
    db = get_database()
    
    # For demo, return mock data
    return Strategy(
        id=strategy_id,
        user_id="user1",
        name="Bitcoin (BTC) Performance",
        description="Bitcoin trading strategy",
        status="Live",
        schema_json={"nodes": [], "connections": []},
        guardrails=[],
        metrics=StrategyMetrics(
            total_return=15.2,
            cagr=8.5,
            sharpe_ratio=1.2,
            max_drawdown=-7.3,
            win_rate=62,
            trades=125,
            vs_benchmark=3.1
        )
    )

@router.put("/{strategy_id}", response_model=Strategy)
async def update_strategy(strategy_id: str, strategy: Strategy):
    """Update an existing strategy"""
    db = get_database()
    
    strategy_dict = strategy.model_dump(exclude={"id", "created_at"})
    strategy_dict["updated_at"] = datetime.utcnow()
    
    result = await db.strategies.update_one(
        {"_id": strategy_id},
        {"$set": strategy_dict}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    return strategy

@router.delete("/{strategy_id}")
async def delete_strategy(strategy_id: str):
    """Delete a strategy"""
    db = get_database()
    
    result = await db.strategies.delete_one({"_id": strategy_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    return {"message": "Strategy deleted successfully"}

@router.post("/{strategy_id}/duplicate", response_model=Strategy)
async def duplicate_strategy(strategy_id: str):
    """Duplicate an existing strategy"""
    db = get_database()
    
    # Get original strategy
    original = await get_strategy(strategy_id)
    
    # Create duplicate
    duplicate = original.model_copy()
    duplicate.id = None
    duplicate.name = f"{original.name} (Copy)"
    duplicate.created_at = datetime.utcnow()
    duplicate.updated_at = datetime.utcnow()
    
    return await create_strategy(duplicate)

@router.get("/{strategy_id}/trades")
async def get_strategy_trades(strategy_id: str):
    """Get recent trades for a strategy"""
    # Return mock trades
    return [
        {
            "id": "1",
            "date": "2024-01-15",
            "type": "BUY",
            "symbol": "BTC",
            "price": 62650,
            "quantity": 0.15,
            "amount": 62650,
            "return": 12.5
        },
        {
            "id": "2",
            "date": "2024-01-12",
            "type": "SELL",
            "symbol": "BTC",
            "price": 59500,
            "quantity": 0.15,
            "amount": 59500,
            "return": -5.2
        }
    ]
