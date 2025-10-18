"""
API endpoints for strategy execution using CrewAI agents.
"""

from fastapi import APIRouter, HTTPException
from typing import List
from ..models import StrategyExecution, ExecuteStrategyRequest
from ..services.strategy_execution_service import strategy_execution_service

router = APIRouter(prefix="/executions", tags=["executions"])


@router.post("/strategies/{strategy_id}/execute", response_model=StrategyExecution)
async def execute_strategy(strategy_id: str, request: ExecuteStrategyRequest):
    """
    Execute a strategy using CrewAI agents.
    
    This endpoint:
    1. Creates an execution record
    2. Triggers the CrewAI workflow asynchronously
    3. Returns immediately with execution ID
    
    The workflow:
    - Agent 1: Analyzes strategy schema
    - Agent 2: Generates VectorBT code
    - Agent 3: Executes code and stores results
    
    Poll GET /executions/{execution_id} to check status.
    """
    # TODO: Get user_id from authentication
    user_id = "user1"  # Placeholder
    
    try:
        execution = await strategy_execution_service.execute_strategy(
            strategy_id=strategy_id,
            user_id=user_id,
            params=request.params
        )
        return execution
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{execution_id}", response_model=StrategyExecution)
async def get_execution(execution_id: str):
    """
    Get execution status and details.
    
    Status values:
    - queued: Waiting to start
    - analyzing: Agent analyzing strategy
    - generating_code: Agent generating VectorBT code
    - executing: Running backtest
    - completed: Successfully completed
    - failed: Execution failed (check error_message)
    """
    execution = await strategy_execution_service.get_execution(execution_id)
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return execution


@router.get("/strategies/{strategy_id}/executions", response_model=List[StrategyExecution])
async def get_strategy_executions(strategy_id: str):
    """
    Get all executions for a strategy.
    """
    executions = await strategy_execution_service.get_executions_for_strategy(strategy_id)
    return executions


@router.get("/{execution_id}/code")
async def get_execution_code(execution_id: str):
    """
    Get the generated VectorBT code for an execution.
    """
    code = await strategy_execution_service.get_generated_code(execution_id)
    
    if code is None:
        raise HTTPException(
            status_code=404,
            detail="Execution not found or code not yet generated"
        )
    
    return {
        "execution_id": execution_id,
        "code": code,
        "language": "python"
    }


@router.get("/{execution_id}/results")
async def get_execution_results(execution_id: str):
    """
    Get the backtest results for a completed execution.
    """
    execution = await strategy_execution_service.get_execution(execution_id)
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    if execution.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Execution not completed. Current status: {execution.status}"
        )
    
    if not execution.backtest_run_id:
        raise HTTPException(
            status_code=404,
            detail="No backtest results available"
        )
    
    # Get backtest run
    from ..database import get_database
    pool = get_database()
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT id, strategy_id, params, metrics, equity_series, drawdown_series, monthly_returns, trades, created_at
            FROM backtest_runs
            WHERE id = $1
            """,
            execution.backtest_run_id
        )
    
    if not row:
        raise HTTPException(status_code=404, detail="Backtest results not found")
    
    # Convert row to dict
    backtest_run = {
        'id': str(row['id']),
        'strategy_id': row['strategy_id'],
        'params': row['params'],
        'metrics': row['metrics'],
        'equity_series': row['equity_series'],
        'drawdown_series': row['drawdown_series'],
        'monthly_returns': row['monthly_returns'],
        'trades': row['trades'],
        'created_at': row['created_at'].isoformat() if row['created_at'] else None
    }
    
    return backtest_run
