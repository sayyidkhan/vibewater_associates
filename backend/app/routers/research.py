"""
Research Agent Router
API endpoints for autonomous strategy research and generation
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any
import asyncio
from datetime import datetime

from ..models import ResearchRequest, ResearchResult
from ..services.research_agent_service import research_agent_service
from ..database import get_database

router = APIRouter(prefix="/api/research", tags=["research"])


@router.post("/start", response_model=Dict[str, Any])
async def start_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
):
    """
    Start autonomous research agent to generate and test strategies
    
    The research agent will:
    1. Research current market conditions
    2. Generate multiple strategy schemas
    3. Add them to the database
    4. Run backtests on each strategy
    5. Analyze and rank by performance
    
    Returns immediately with a research ID. Use GET /api/research/{id} to check status.
    """
    user_id = "user1"  # TODO: Get from authentication
    
    # Create research record
    pool = get_database()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO research_runs (user_id, num_strategies, market_focus, risk_level, status, started_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
            """,
            user_id,
            request.num_strategies,
            request.market_focus,
            request.risk_level,
            "running",
            datetime.utcnow()
        )
        research_id = str(row['id'])
    
    # Start research in background
    background_tasks.add_task(
        run_research_workflow,
        research_id,
        user_id,
        request.num_strategies,
        request.market_focus,
        request.risk_level
    )
    
    return {
        "research_id": research_id,
        "status": "running",
        "message": f"Research agent started. Generating {request.num_strategies} strategies...",
        "check_status_url": f"/api/research/{research_id}"
    }


async def run_research_workflow(
    research_id: str,
    user_id: str,
    num_strategies: int,
    market_focus: str,
    risk_level: str
):
    """Background task to run the complete research workflow"""
    pool = get_database()
    
    try:
        print(f"\n🔬 Starting research workflow {research_id}")
        
        # Run research agent
        rankings = await research_agent_service.research_and_generate_strategies(
            user_id=user_id,
            num_strategies=num_strategies,
            market_focus=market_focus,
            risk_level=risk_level
        )
        
        # Update research record with results
        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE research_runs 
                SET status = $1, completed_at = $2, rankings = $3
                WHERE id = $4
                """,
                "completed",
                datetime.utcnow(),
                rankings,  # PostgreSQL JSONB field
                research_id
            )
        
        print(f"✅ Research workflow {research_id} completed successfully")
        
    except Exception as e:
        print(f"❌ Research workflow {research_id} failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Update with error
        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE research_runs 
                SET status = $1, completed_at = $2, error_message = $3
                WHERE id = $4
                """,
                "failed",
                datetime.utcnow(),
                str(e),
                research_id
            )


@router.get("/{research_id}", response_model=Dict[str, Any])
async def get_research_status(research_id: str):
    """
    Get status and results of a research run
    """
    pool = get_database()
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM research_runs WHERE id = $1",
            research_id
        )
    
    if not row:
        raise HTTPException(status_code=404, detail="Research run not found")
    
    return {
        "id": str(row['id']),
        "user_id": row['user_id'],
        "num_strategies": row['num_strategies'],
        "market_focus": row['market_focus'],
        "risk_level": row['risk_level'],
        "status": row['status'],
        "started_at": row['started_at'].isoformat() if row['started_at'] else None,
        "completed_at": row['completed_at'].isoformat() if row['completed_at'] else None,
        "rankings": row['rankings'] if row['rankings'] else [],
        "error_message": row['error_message']
    }


@router.get("/", response_model=List[Dict[str, Any]])
async def list_research_runs(limit: int = 10):
    """
    List recent research runs
    """
    pool = get_database()
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM research_runs ORDER BY started_at DESC LIMIT $1",
            limit
        )
    
    return [
        {
            "id": str(row['id']),
            "user_id": row['user_id'],
            "num_strategies": row['num_strategies'],
            "market_focus": row['market_focus'],
            "risk_level": row['risk_level'],
            "status": row['status'],
            "started_at": row['started_at'].isoformat() if row['started_at'] else None,
            "completed_at": row['completed_at'].isoformat() if row['completed_at'] else None,
            "num_results": len(row['rankings']) if row['rankings'] else 0,
            "error_message": row['error_message']
        }
        for row in rows
    ]


@router.get("/{research_id}/top-strategy", response_model=Dict[str, Any])
async def get_top_strategy(research_id: str):
    """
    Get the top-performing strategy from a research run
    """
    pool = get_database()
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT rankings FROM research_runs WHERE id = $1",
            research_id
        )
    
    if not row:
        raise HTTPException(status_code=404, detail="Research run not found")
    
    rankings = row['rankings']
    if not rankings or len(rankings) == 0:
        raise HTTPException(status_code=404, detail="No strategies found in this research run")
    
    # Return top-ranked strategy
    top_strategy = rankings[0]
    
    # Get full strategy details from database
    strategy_id = top_strategy.get('strategy_id')
    if strategy_id:
        async with pool.acquire() as conn:
            strategy_row = await conn.fetchrow(
                "SELECT * FROM strategies WHERE id = $1",
                strategy_id
            )
        
        if strategy_row:
            return {
                "id": str(strategy_row['id']),
                "name": strategy_row['name'],
                "description": strategy_row['description'],
                "schema_json": strategy_row['schema_json'],
                "performance_score": top_strategy.get('performance_score', 0),
                "rank": 1,
                "metrics": top_strategy.get('metrics', {}),
                "strengths": top_strategy.get('strengths', []),
                "weaknesses": top_strategy.get('weaknesses', []),
                "recommendation": top_strategy.get('recommendation', '')
            }
    
    return top_strategy


@router.post("/{research_id}/rerun-top", response_model=Dict[str, Any])
async def rerun_top_strategy(research_id: str):
    """
    Re-run backtest on the top strategy with fresh parameters
    """
    # Get top strategy
    pool = get_database()
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT rankings FROM research_runs WHERE id = $1",
            research_id
        )
    
    if not row or not row['rankings']:
        raise HTTPException(status_code=404, detail="No strategies found")
    
    top_strategy = row['rankings'][0]
    strategy_id = top_strategy.get('strategy_id')
    
    if not strategy_id:
        raise HTTPException(status_code=404, detail="Strategy ID not found")
    
    return {
        "message": "Backtest queued",
        "strategy_id": strategy_id,
        "run_url": f"/api/executions?strategy_id={strategy_id}"
    }
