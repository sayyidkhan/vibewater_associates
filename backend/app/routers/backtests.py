from fastapi import APIRouter, HTTPException
from typing import List
import json
from ..models import BacktestRun, BacktestRequest, BacktestParams, BacktestMetrics
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
        
        # Store in database (optional - skip if database not available)
        try:
            pool = get_database()
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    INSERT INTO backtests (strategy_id, params, metrics, equity_series, drawdown_series, monthly_returns, trades)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    RETURNING id
                    """,
                    result.strategy_id,
                    json.dumps(result.params.model_dump()),
                    json.dumps(result.metrics.model_dump()),
                    json.dumps([e.model_dump() for e in result.equity_series]),
                    json.dumps(result.drawdown_series),
                    json.dumps(result.monthly_returns),
                    json.dumps([t.model_dump() for t in result.trades])
                )
                result.id = str(row['id'])
            print("✓ Saved to Supabase")
        except Exception as db_error:
            print(f"⚠️  Database not available, skipping save: {db_error}")
        
        return result
    except Exception as e:
        print(f"Backtest error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{backtest_id}", response_model=BacktestRun)
async def get_backtest(backtest_id: str):
    """Get a specific backtest by ID"""
    pool = get_database()
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT id, strategy_id, params, metrics, equity_series, drawdown_series, monthly_returns, trades, created_at
            FROM backtests
            WHERE id = $1
            """,
            backtest_id
        )
    
    if not row:
        raise HTTPException(status_code=404, detail="Backtest not found")
    
    return BacktestRun(
        id=str(row['id']),
        strategy_id=row['strategy_id'],
        params=BacktestParams(**row['params']),
        metrics=BacktestMetrics(**row['metrics']),
        equity_series=row['equity_series'],
        drawdown_series=row['drawdown_series'],
        monthly_returns=row['monthly_returns'],
        trades=row['trades'],
        created_at=row['created_at']
    )

@router.get("/strategy/{strategy_id}", response_model=List[BacktestRun])
async def get_strategy_backtests(strategy_id: str):
    """Get all backtests for a strategy, sorted by creation time (newest first)"""
    try:
        pool = get_database()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, strategy_id, params, metrics, equity_series, drawdown_series, monthly_returns, trades, created_at
                FROM backtests
                WHERE strategy_id = $1
                ORDER BY created_at DESC
                LIMIT 100
                """,
                strategy_id
            )
        
        print(f"Found {len(rows)} backtests for strategy {strategy_id}")
        
        backtests = []
        for row in rows:
            backtests.append(BacktestRun(
                id=str(row['id']),
                strategy_id=row['strategy_id'],
                params=BacktestParams(**row['params']),
                metrics=BacktestMetrics(**row['metrics']),
                equity_series=row['equity_series'],
                drawdown_series=row['drawdown_series'],
                monthly_returns=row['monthly_returns'],
                trades=row['trades'],
                created_at=row['created_at']
            ))
        
        return backtests
    except Exception as e:
        print(f"Error fetching backtests: {e}")
        # Return empty list if database not available
        return []
