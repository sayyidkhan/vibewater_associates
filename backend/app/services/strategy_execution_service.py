"""
Strategy Execution Service
Orchestrates the complete strategy execution workflow using CrewAI agents.
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from bson import ObjectId
from ..models import StrategyExecution, BacktestParams, BacktestRun, BacktestMetrics, EquityPoint, Trade
from ..database import get_database
from .strategy_agents import strategy_execution_crew


class StrategyExecutionService:
    """
    Main service for executing strategies using CrewAI agents.
    Handles the complete workflow from strategy analysis to code execution.
    """
    
    async def execute_strategy(
        self,
        strategy_id: str,
        user_id: str,
        params: BacktestParams
    ) -> StrategyExecution:
        """
        Execute a strategy using CrewAI agents.
        
        Args:
            strategy_id: ID of the strategy to execute
            user_id: ID of the user executing the strategy
            params: Backtest parameters
        
        Returns:
            StrategyExecution object with execution details
        """
        db = get_database()
        
        # Create execution record
        execution = StrategyExecution(
            strategy_id=strategy_id,
            user_id=user_id,
            status="queued",
            created_at=datetime.utcnow()
        )
        
        execution_dict = execution.model_dump(exclude={"id"})
        result = await db.strategy_executions.insert_one(execution_dict)
        execution_id = str(result.inserted_id)
        execution.id = execution_id
        
        # Execute asynchronously
        asyncio.create_task(
            self._execute_workflow(execution_id, strategy_id, user_id, params)
        )
        
        return execution
    
    async def _execute_workflow(
        self,
        execution_id: str,
        strategy_id: str,
        user_id: str,
        params: BacktestParams
    ):
        """
        Internal method that runs the complete execution workflow.
        This runs asynchronously so the API can return immediately.
        """
        db = get_database()
        
        try:
            # Update status to analyzing
            await self._update_execution_status(
                execution_id,
                "analyzing",
                started_at=datetime.utcnow()
            )
            
            # Get strategy from database
            # Convert string ID to ObjectId for MongoDB query
            try:
                strategy_object_id = ObjectId(strategy_id)
            except:
                strategy_object_id = strategy_id  # In case it's already an ObjectId
            
            strategy = await db.strategies.find_one({"_id": strategy_object_id})
            if not strategy:
                raise ValueError(f"Strategy {strategy_id} not found")
            
            # Extract strategy schema
            strategy_schema = strategy.get('schema_json', {})
            strategy_json = json.dumps(strategy_schema)
            
            # Prepare parameters
            params_dict = {
                'strategy_name': strategy.get('name', 'Generated Strategy'),
                'start_date': params.start_date,
                'end_date': params.end_date,
                'initial_capital': params.initial_capital,
                'fees': params.fees,
                'slippage': params.slippage
            }
            
            # Execute with CrewAI agents
            print(f"Starting CrewAI workflow for execution {execution_id}")
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                strategy_execution_crew.execute_strategy,
                strategy_json,
                params_dict,
                user_id
            )
            
            print(f"CrewAI workflow completed for execution {execution_id}")
            print(f"Result: {result}")
            
            # Parse result
            if isinstance(result, str):
                result = json.loads(result)
            
            # Check if execution was successful
            if result.get('status') == 'success':
                metrics_data = result.get('metrics', {})
                logs = result.get('logs', '')
                
                # Create BacktestRun
                backtest_run = await self._create_backtest_run(
                    strategy_id,
                    params,
                    metrics_data,
                    logs
                )
                
                # Update execution as completed
                await self._update_execution_status(
                    execution_id,
                    "completed",
                    backtest_run_id=backtest_run.id,
                    completed_at=datetime.utcnow(),
                    execution_logs=[logs]
                )
                
            else:
                # Execution failed
                error_msg = result.get('error', 'Unknown error')
                await self._update_execution_status(
                    execution_id,
                    "failed",
                    error_message=error_msg,
                    completed_at=datetime.utcnow(),
                    execution_logs=[result.get('logs', '')]
                )
        
        except Exception as e:
            print(f"Error in execution workflow: {str(e)}")
            import traceback
            traceback.print_exc()
            
            await self._update_execution_status(
                execution_id,
                "failed",
                error_message=str(e),
                completed_at=datetime.utcnow()
            )
    
    async def _update_execution_status(
        self,
        execution_id: str,
        status: str,
        **kwargs
    ):
        """Update execution status in database"""
        db = get_database()
        
        update_data = {"status": status}
        update_data.update(kwargs)
        
        await db.strategy_executions.update_one(
            {"_id": execution_id},
            {"$set": update_data}
        )
    
    async def _create_backtest_run(
        self,
        strategy_id: str,
        params: BacktestParams,
        metrics_data: Dict[str, Any],
        logs: str
    ) -> BacktestRun:
        """Create a BacktestRun from execution results"""
        db = get_database()
        
        # Create metrics
        metrics = BacktestMetrics(
            total_amount_invested=params.initial_capital,
            total_gain=max(0, metrics_data.get('total_return', 0) * params.initial_capital / 100),
            total_loss=0,  # Calculate from trades if available
            total_return=metrics_data.get('total_return', 0),
            cagr=metrics_data.get('cagr', 0),
            sharpe_ratio=metrics_data.get('sharpe_ratio', 0),
            max_drawdown=metrics_data.get('max_drawdown', 0),
            max_drawdown_duration=0,  # Not available from simple execution
            win_rate=metrics_data.get('win_rate', 0),
            trades=metrics_data.get('trades', 0),
            vs_benchmark=metrics_data.get('vs_benchmark', 0)
        )
        
        # Create backtest run
        backtest_run = BacktestRun(
            id=f"exec-{datetime.utcnow().timestamp()}",
            strategy_id=strategy_id,
            params=params,
            metrics=metrics,
            equity_series=[],  # Would need to extract from execution
            drawdown_series=[],
            monthly_returns=[],
            trades=[],
            created_at=datetime.utcnow()
        )
        
        # Store in database
        backtest_dict = backtest_run.model_dump(exclude={"id"})
        result = await db.backtest_runs.insert_one(backtest_dict)
        backtest_run.id = str(result.inserted_id)
        
        return backtest_run
    
    async def get_execution(self, execution_id: str) -> Optional[StrategyExecution]:
        """Get execution by ID"""
        db = get_database()
        
        execution_dict = await db.strategy_executions.find_one({"_id": execution_id})
        if not execution_dict:
            return None
        
        execution_dict['id'] = str(execution_dict.pop('_id'))
        return StrategyExecution(**execution_dict)
    
    async def get_executions_for_strategy(self, strategy_id: str) -> list[StrategyExecution]:
        """Get all executions for a strategy"""
        db = get_database()
        
        cursor = db.strategy_executions.find({"strategy_id": strategy_id})
        executions = []
        
        async for doc in cursor:
            doc['id'] = str(doc.pop('_id'))
            executions.append(StrategyExecution(**doc))
        
        return executions
    
    async def get_generated_code(self, execution_id: str) -> Optional[str]:
        """Get the generated code for an execution"""
        execution = await self.get_execution(execution_id)
        if execution:
            return execution.generated_code
        return None


# Singleton instance
strategy_execution_service = StrategyExecutionService()
