"""
Research Agent API Router

Provides endpoints for:
- Strategy research and discovery
- Autonomous backtesting
- Performance ranking and analysis
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
import asyncio
from datetime import datetime

from ..models import (
    ResearchRequest, ResearchedStrategy, AutonomousBacktestRequest,
    StrategyPerformanceRanking, BacktestParams
)
from ..services.research_agent_service import research_agent_service

router = APIRouter(prefix="/research", tags=["research"])

# Store for background task results
research_results = {}
backtest_results = {}


@router.post("/strategies", response_model=List[ResearchedStrategy])
async def research_strategies(
    request: ResearchRequest,
    user_id: str = "research_agent"
):
    """
    Research and discover new trading strategies based on specified criteria.
    
    This endpoint uses AI agents to:
    - Analyze current market conditions
    - Research profitable strategy patterns
    - Generate strategy schemas
    - Assess risk profiles
    - Store strategies in database
    """
    try:
        strategies = await research_agent_service.research_strategies(request, user_id)
        return strategies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Strategy research failed: {str(e)}")


@router.post("/strategies/background")
async def research_strategies_background(
    request: ResearchRequest,
    background_tasks: BackgroundTasks,
    user_id: str = "research_agent"
):
    """
    Start strategy research as a background task.
    Returns a task ID that can be used to check progress.
    """
    task_id = f"research_{datetime.now().timestamp()}"
    
    async def research_task():
        try:
            strategies = await research_agent_service.research_strategies(request, user_id)
            research_results[task_id] = {
                "status": "completed",
                "strategies": strategies,
                "completed_at": datetime.now().isoformat()
            }
        except Exception as e:
            research_results[task_id] = {
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.now().isoformat()
            }
    
    background_tasks.add_task(research_task)
    research_results[task_id] = {
        "status": "running",
        "started_at": datetime.now().isoformat()
    }
    
    return {"task_id": task_id, "status": "started"}


@router.get("/strategies/background/{task_id}")
async def get_research_status(task_id: str):
    """
    Get the status of a background research task.
    """
    if task_id not in research_results:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return research_results[task_id]


@router.post("/backtest/autonomous", response_model=List[StrategyPerformanceRanking])
async def run_autonomous_backtests(
    request: AutonomousBacktestRequest,
    user_id: str = "research_agent"
):
    """
    Run autonomous backtests on strategies and return performance rankings.
    
    This endpoint will:
    - Research new strategies (if no strategy_ids provided)
    - Run concurrent backtests
    - Calculate performance metrics
    - Rank strategies by performance
    """
    try:
        rankings = await research_agent_service.run_autonomous_backtests(request, user_id)
        return rankings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Autonomous backtesting failed: {str(e)}")


@router.post("/backtest/autonomous/background")
async def run_autonomous_backtests_background(
    request: AutonomousBacktestRequest,
    background_tasks: BackgroundTasks,
    user_id: str = "research_agent"
):
    """
    Start autonomous backtesting as a background task.
    """
    task_id = f"backtest_{datetime.now().timestamp()}"
    
    async def backtest_task():
        try:
            rankings = await research_agent_service.run_autonomous_backtests(request, user_id)
            backtest_results[task_id] = {
                "status": "completed",
                "rankings": rankings,
                "completed_at": datetime.now().isoformat()
            }
        except Exception as e:
            backtest_results[task_id] = {
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.now().isoformat()
            }
    
    background_tasks.add_task(backtest_task)
    backtest_results[task_id] = {
        "status": "running",
        "started_at": datetime.now().isoformat()
    }
    
    return {"task_id": task_id, "status": "started"}


@router.get("/backtest/autonomous/background/{task_id}")
async def get_backtest_status(task_id: str):
    """
    Get the status of a background autonomous backtest task.
    """
    if task_id not in backtest_results:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return backtest_results[task_id]


@router.post("/pipeline/full")
async def run_full_research_pipeline(
    research_request: Optional[ResearchRequest] = None,
    backtest_request: Optional[AutonomousBacktestRequest] = None,
    user_id: str = "research_agent"
):
    """
    Run the complete research and backtesting pipeline:
    1. Research strategies
    2. Run autonomous backtests
    3. Return ranked results
    """
    try:
        # Set defaults
        if research_request is None:
            research_request = ResearchRequest(max_strategies=5, research_depth="quick")
        
        if backtest_request is None:
            backtest_request = AutonomousBacktestRequest(max_concurrent_tests=3)
        
        # Step 1: Research strategies
        print("🔍 Step 1: Researching strategies...")
        strategies = await research_agent_service.research_strategies(research_request, user_id)
        
        # Step 2: Run backtests on researched strategies
        print("🚀 Step 2: Running autonomous backtests...")
        backtest_request.strategy_ids = [s.id for s in strategies if s.id]
        rankings = await research_agent_service.run_autonomous_backtests(backtest_request, user_id)
        
        return {
            "researched_strategies": len(strategies),
            "backtested_strategies": len(rankings),
            "top_strategy": rankings[0] if rankings else None,
            "all_rankings": rankings,
            "pipeline_completed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Full pipeline failed: {str(e)}")


@router.get("/strategies/database")
async def get_researched_strategies(
    user_id: Optional[str] = None,
    category: Optional[str] = None,
    market_type: Optional[str] = None,
    risk_level: Optional[str] = None,
    limit: int = 20
):
    """
    Get researched strategies from the database with optional filters.
    """
    try:
        from ..database import get_database
        import json
        
        db = get_database()
        
        # Build query with filters
        where_conditions = []
        params = []
        param_count = 0
        
        if user_id:
            param_count += 1
            where_conditions.append(f"user_id = ${param_count}")
            params.append(user_id)
        
        if category:
            param_count += 1
            where_conditions.append(f"metrics->>'category' = ${param_count}")
            params.append(category)
        
        if market_type:
            param_count += 1
            where_conditions.append(f"metrics->>'market_type' = ${param_count}")
            params.append(market_type)
        
        if risk_level:
            param_count += 1
            where_conditions.append(f"metrics->>'risk_level' = ${param_count}")
            params.append(risk_level)
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        param_count += 1
        query = f"""
            SELECT * FROM strategies 
            {where_clause}
            ORDER BY created_at DESC 
            LIMIT ${param_count}
        """
        params.append(limit)
        
        async with db.acquire() as conn:
            rows = await conn.fetch(query, *params)
        
        strategies = []
        for row in rows:
            metrics = json.loads(row['metrics']) if row['metrics'] else {}
            strategies.append({
                "id": str(row['id']),
                "name": row['name'],
                "description": row['description'],
                "category": metrics.get('category'),
                "market_type": metrics.get('market_type'),
                "risk_level": metrics.get('risk_level'),
                "expected_return": metrics.get('expected_return'),
                "confidence_score": metrics.get('confidence_score'),
                "research_source": metrics.get('research_source'),
                "created_at": row['created_at'].isoformat()
            })
        
        return {
            "strategies": strategies,
            "total": len(strategies),
            "filters_applied": {
                "user_id": user_id,
                "category": category,
                "market_type": market_type,
                "risk_level": risk_level
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch strategies: {str(e)}")


@router.delete("/strategies/{strategy_id}")
async def delete_researched_strategy(strategy_id: str):
    """
    Delete a researched strategy from the database.
    """
    try:
        from ..database import get_database
        
        db = get_database()
        
        async with db.acquire() as conn:
            # Check if strategy exists
            exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM strategies WHERE id = $1)",
                strategy_id
            )
            
            if not exists:
                raise HTTPException(status_code=404, detail="Strategy not found")
            
            # Delete strategy
            await conn.execute(
                "DELETE FROM strategies WHERE id = $1",
                strategy_id
            )
        
        return {"message": f"Strategy {strategy_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete strategy: {str(e)}")


@router.get("/health")
async def research_health_check():
    """
    Health check endpoint for the research agent service.
    """
    try:
        # Test basic functionality
        test_request = ResearchRequest(max_strategies=1, research_depth="quick")
        
        return {
            "status": "healthy",
            "service": "Research Agent",
            "capabilities": [
                "Strategy Research",
                "Autonomous Backtesting", 
                "Performance Ranking",
                "Risk Analysis"
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }