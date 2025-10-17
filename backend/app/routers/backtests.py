from fastapi import APIRouter, HTTPException
from typing import List
from ..models import BacktestRun, BacktestRequest
from ..services.backtest_service import backtest_service
from ..services.vectorbt_service import vectorbt_service
from ..database import get_database

router = APIRouter(prefix="/backtests", tags=["backtests"])

@router.post("", response_model=BacktestRun)
async def run_backtest(request: BacktestRequest):
    """Run a backtest for a strategy"""
    try:
        # Use VectorBT for Bitcoin/crypto strategies (strategy_id "1")
        # Use mock backtest for other strategies
        if request.strategy_id == "1" or "BTC" in str(request.params.symbols):
            print("Using VectorBT for Bitcoin backtest...")
            result = await vectorbt_service.run_bitcoin_backtest(
                request.strategy_id,
                request.params
            )
        else:
            print("Using mock backtest service...")
            result = await backtest_service.run_backtest(
                request.strategy_id,
                request.params
            )
        
        # Store in database (optional - skip if MongoDB not available)
        try:
            db = get_database()
            backtest_dict = result.model_dump(exclude={"id"})
            await db.backtests.insert_one(backtest_dict)
            print("✓ Saved to MongoDB")
        except Exception as db_error:
            print(f"⚠️  MongoDB not available, skipping save: {db_error}")
        
        return result
    except Exception as e:
        print(f"Backtest error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{backtest_id}", response_model=BacktestRun)
async def get_backtest(backtest_id: str):
    """Get a specific backtest by ID"""
    db = get_database()
    
    backtest = await db.backtests.find_one({"_id": backtest_id})
    
    if not backtest:
        raise HTTPException(status_code=404, detail="Backtest not found")
    
    return BacktestRun(**backtest)

@router.get("/strategy/{strategy_id}", response_model=List[BacktestRun])
async def get_strategy_backtests(strategy_id: str):
    """Get all backtests for a strategy, sorted by creation time (newest first)"""
    try:
        db = get_database()
        cursor = db.backtests.find({"strategy_id": strategy_id}).sort("_id", -1)
        backtests = await cursor.to_list(length=100)
        
        print(f"Found {len(backtests)} backtests for strategy {strategy_id}")
        
        return [BacktestRun(**bt) for bt in backtests]
    except Exception as e:
        print(f"Error fetching backtests: {e}")
        # Return empty list if database not available
        return []
