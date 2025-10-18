from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import json
from ..models import Strategy, StrategyMetrics, StrategySchema, Guardrail
from ..database import get_database

router = APIRouter(prefix="/strategies", tags=["strategies"])

@router.post("", response_model=Strategy)
async def create_strategy(strategy: Strategy):
    """Create a new trading strategy"""
    pool = get_database()
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO strategies (user_id, name, description, status, schema_json, guardrails, metrics)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id, user_id, name, description, status, schema_json, guardrails, metrics, created_at, updated_at
            """,
            strategy.user_id,
            strategy.name,
            strategy.description,
            strategy.status,
            json.dumps(strategy.schema_json.model_dump()),
            json.dumps([g.model_dump() for g in strategy.guardrails]),
            json.dumps(strategy.metrics.model_dump()) if strategy.metrics else None
        )
    
    # Parse JSON fields if they're strings
    schema_data = row['schema_json'] if isinstance(row['schema_json'], dict) else json.loads(row['schema_json'])
    metrics_data = row['metrics'] if isinstance(row['metrics'], dict) else (json.loads(row['metrics']) if row['metrics'] else None)
    guardrails_data = row['guardrails'] if isinstance(row['guardrails'], dict) else json.loads(row['guardrails'])
    
    return Strategy(
        id=str(row['id']),
        user_id=row['user_id'],
        name=row['name'],
        description=row['description'],
        status=row['status'],
        schema_json=StrategySchema(**schema_data),
        guardrails=[Guardrail(**g) for g in guardrails_data],
        metrics=StrategyMetrics(**metrics_data) if metrics_data else None,
        created_at=row['created_at'],
        updated_at=row['updated_at']
    )

@router.get("", response_model=List[Strategy])
async def get_strategies(
    status: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None)
):
    """Get all strategies with optional filters"""
    pool = get_database()
    
    # Build query with filters
    conditions = []
    params = []
    param_count = 1
    
    if status:
        conditions.append(f"status = ${param_count}")
        params.append(status)
        param_count += 1
    if user_id:
        conditions.append(f"user_id = ${param_count}")
        params.append(user_id)
        param_count += 1
    
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            f"""
            SELECT id, user_id, name, description, status, schema_json, guardrails, metrics, created_at, updated_at
            FROM strategies
            {where_clause}
            ORDER BY created_at DESC
            """,
            *params
        )
    
    strategies = []
    for row in rows:
        # Parse JSON fields if they're strings
        schema_data = row['schema_json'] if isinstance(row['schema_json'], dict) else json.loads(row['schema_json'])
        metrics_data = row['metrics'] if isinstance(row['metrics'], dict) else (json.loads(row['metrics']) if row['metrics'] else None)
        guardrails_data = row['guardrails'] if isinstance(row['guardrails'], dict) else json.loads(row['guardrails'])
        
        strategies.append(Strategy(
            id=str(row['id']),
            user_id=row['user_id'],
            name=row['name'],
            description=row['description'],
            status=row['status'],
            schema_json=StrategySchema(**schema_data),
            guardrails=[Guardrail(**g) for g in guardrails_data],
            metrics=StrategyMetrics(**metrics_data) if metrics_data else None,
            created_at=row['created_at'],
            updated_at=row['updated_at']
        ))
    
    return strategies

@router.get("/{strategy_id}", response_model=Strategy)
async def get_strategy(strategy_id: str):
    """Get a specific strategy by ID"""
    pool = get_database()
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT id, user_id, name, description, status, schema_json, guardrails, metrics, created_at, updated_at
            FROM strategies
            WHERE id = $1
            """,
            strategy_id
        )
    
    if not row:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Parse JSON fields if they're strings
    schema_data = row['schema_json'] if isinstance(row['schema_json'], dict) else json.loads(row['schema_json'])
    metrics_data = row['metrics'] if isinstance(row['metrics'], dict) else (json.loads(row['metrics']) if row['metrics'] else None)
    guardrails_data = row['guardrails'] if isinstance(row['guardrails'], dict) else json.loads(row['guardrails'])
    
    return Strategy(
        id=str(row['id']),
        user_id=row['user_id'],
        name=row['name'],
        description=row['description'],
        status=row['status'],
        schema_json=StrategySchema(**schema_data),
        guardrails=[Guardrail(**g) for g in guardrails_data],
        metrics=StrategyMetrics(**metrics_data) if metrics_data else None,
        created_at=row['created_at'],
        updated_at=row['updated_at']
    )

@router.put("/{strategy_id}", response_model=Strategy)
async def update_strategy(strategy_id: str, strategy: Strategy):
    """Update an existing strategy"""
    pool = get_database()
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            UPDATE strategies
            SET user_id = $1, name = $2, description = $3, status = $4,
                schema_json = $5, guardrails = $6, metrics = $7, updated_at = NOW()
            WHERE id = $8
            RETURNING id, user_id, name, description, status, schema_json, guardrails, metrics, created_at, updated_at
            """,
            strategy.user_id,
            strategy.name,
            strategy.description,
            strategy.status,
            json.dumps(strategy.schema_json.model_dump()),
            json.dumps([g.model_dump() for g in strategy.guardrails]),
            json.dumps(strategy.metrics.model_dump()) if strategy.metrics else None,
            strategy_id
        )
    
    if not row:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Parse JSON fields if they're strings
    schema_data = row['schema_json'] if isinstance(row['schema_json'], dict) else json.loads(row['schema_json'])
    metrics_data = row['metrics'] if isinstance(row['metrics'], dict) else (json.loads(row['metrics']) if row['metrics'] else None)
    guardrails_data = row['guardrails'] if isinstance(row['guardrails'], dict) else json.loads(row['guardrails'])
    
    return Strategy(
        id=str(row['id']),
        user_id=row['user_id'],
        name=row['name'],
        description=row['description'],
        status=row['status'],
        schema_json=StrategySchema(**schema_data),
        guardrails=[Guardrail(**g) for g in guardrails_data],
        metrics=StrategyMetrics(**metrics_data) if metrics_data else None,
        created_at=row['created_at'],
        updated_at=row['updated_at']
    )

@router.delete("/{strategy_id}")
async def delete_strategy(strategy_id: str):
    """Delete a strategy"""
    pool = get_database()
    
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM strategies WHERE id = $1",
            strategy_id
        )
    
    if result == "DELETE 0":
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
