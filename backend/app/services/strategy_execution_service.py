"""
Strategy Execution Service
Orchestrates the complete strategy execution workflow using CrewAI agents.
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
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
        pool = get_database()
        
        # Create execution record
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO strategy_executions (strategy_id, user_id, status, created_at)
                VALUES ($1, $2, $3, $4)
                RETURNING id
                """,
                strategy_id,
                user_id,
                "queued",
                datetime.utcnow()
            )
            execution_id = str(row['id'])
        
        execution = StrategyExecution(
            id=execution_id,
            strategy_id=strategy_id,
            user_id=user_id,
            status="queued",
            created_at=datetime.utcnow()
        )
        
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
        pool = get_database()
        
        try:
            # Update status to analyzing
            await self._update_execution_status(
                execution_id,
                "analyzing",
                started_at=datetime.utcnow()
            )
            
            # Get strategy from database
            async with pool.acquire() as conn:
                strategy = await conn.fetchrow(
                    "SELECT * FROM strategies WHERE id = $1",
                    strategy_id
                )
            
            if not strategy:
                raise ValueError(f"Strategy {strategy_id} not found")
            
            # Extract strategy schema
            strategy_schema = strategy['schema_json']
            strategy_json = json.dumps(strategy_schema)
            
            # Prepare parameters
            params_dict = {
                'strategy_name': strategy['name'] if strategy['name'] else 'Generated Strategy',
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
            execution_status = result.get('execution_status', result.get('status', ''))
            
            # Consider both 'success' and 'completed' as successful executions
            if execution_status.lower() in ['success', 'completed']:
                # Handle different result formats
                # Format 1: metrics are nested in 'metrics' key
                # Format 2: metrics are at top level (total_return, cagr, etc as direct keys)
                # Format 3: result is a markdown string with embedded JSON
                
                metrics_data = result.get('metrics', {})
                
                # If metrics is empty, check if metrics are at top level
                if not metrics_data and 'total_return' in result:
                    metrics_data = result
                
                # If still no metrics, try to extract from 'result' markdown string
                if not metrics_data or (isinstance(metrics_data, dict) and not metrics_data):
                    result_str = result.get('result', '')
                    if result_str and '```json' in result_str:
                        # Extract JSON from markdown
                        try:
                            import re
                            json_match = re.search(r'```json\s*\n(.*?)\n```', result_str, re.DOTALL)
                            if json_match:
                                metrics_data = json.loads(json_match.group(1))
                        except Exception as e:
                            print(f"Warning: Could not extract metrics from markdown: {e}")
                
                # Convert metrics to the expected format
                # Handle various key formats (camelCase, Title Case, snake_case)
                # Use a helper function that properly handles None vs 0
                def get_metric(data, *keys, default=0):
                    """Get metric value, distinguishing between None and 0"""
                    for key in keys:
                        value = data.get(key)
                        if value is not None:
                            return value
                    return default
                
                formatted_metrics = {
                    'total_return': get_metric(
                        metrics_data,
                        'total_return', 'Total Return %', 'Total Return'
                    ),
                    'cagr': get_metric(
                        metrics_data,
                        'cagr', 'Annual Return %', 'CAGR'
                    ),
                    'sharpe_ratio': get_metric(
                        metrics_data,
                        'sharpe_ratio', 'Sharpe Ratio'
                    ),
                    'max_drawdown': get_metric(
                        metrics_data,
                        'max_drawdown', 'Max Drawdown %', 'Maximum Drawdown'
                    ),
                    'win_rate': get_metric(
                        metrics_data,
                        'win_rate', 'Win Rate %', 'Win Rate'
                    ),
                    'trades': get_metric(
                        metrics_data,
                        'trades', 'Total Trades', 'total_trades'
                    ),
                    'vs_benchmark': get_metric(
                        metrics_data,
                        'vs_benchmark', 'vs Benchmark'
                    )
                }
                
                # Create execution log entry
                log_entry = f"Execution completed successfully. Strategy: {result.get('strategy_name', 'Unknown')}"
                if result.get('strategy_description'):
                    log_entry += f"\nDescription: {result['strategy_description']}"
                if result.get('summary'):
                    log_entry += f"\nSummary: {result['summary']}"
                log_entry += f"\nMetrics: {json.dumps(formatted_metrics, indent=2)}"
                
                # Create BacktestRun
                backtest_run = await self._create_backtest_run(
                    strategy_id,
                    params,
                    formatted_metrics,
                    log_entry
                )
                
                # Update execution as completed
                await self._update_execution_status(
                    execution_id,
                    "completed",
                    backtest_run_id=backtest_run.id,
                    completed_at=datetime.utcnow(),
                    execution_logs=[log_entry]
                )
                
            else:
                # Execution failed
                error_msg = result.get('error', result.get('error_message', 'Unknown error'))
                logs = result.get('logs', result.get('result', ''))
                log_entry = f"Execution failed: {error_msg}"
                if logs:
                    log_entry += f"\nLogs: {logs}"
                
                await self._update_execution_status(
                    execution_id,
                    "failed",
                    error_message=error_msg,
                    completed_at=datetime.utcnow(),
                    execution_logs=[log_entry]
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
        pool = get_database()
        
        # Build update query dynamically
        update_fields = ["status = $2"]
        params = [execution_id, status]
        param_count = 3
        
        # JSONB fields that need to be serialized
        jsonb_fields = {'execution_logs', 'agent_insights'}
        
        for key, value in kwargs.items():
            update_fields.append(f"{key} = ${param_count}")
            
            # Serialize JSONB fields to JSON strings
            if key in jsonb_fields and value is not None:
                if isinstance(value, (list, dict)):
                    params.append(json.dumps(value))
                else:
                    params.append(value)
            else:
                params.append(value)
            
            param_count += 1
        
        query = f"UPDATE strategy_executions SET {', '.join(update_fields)} WHERE id = $1"
        
        async with pool.acquire() as conn:
            await conn.execute(query, *params)
    
    async def _create_backtest_run(
        self,
        strategy_id: str,
        params: BacktestParams,
        metrics_data: Dict[str, Any],
        logs: str
    ) -> BacktestRun:
        """Create a BacktestRun from execution results"""
        pool = get_database()
        
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
        
        # Store in database
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO backtest_runs (strategy_id, params, metrics, equity_series, drawdown_series, monthly_returns, trades, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
                """,
                strategy_id,
                json.dumps(params.model_dump()),
                json.dumps(metrics.model_dump()),
                json.dumps([]),  # equity_series
                json.dumps([]),  # drawdown_series
                json.dumps([]),  # monthly_returns
                json.dumps([]),  # trades
                datetime.utcnow()
            )
            backtest_run_id = str(row['id'])
        
        # Create backtest run object
        backtest_run = BacktestRun(
            id=backtest_run_id,
            strategy_id=strategy_id,
            params=params,
            metrics=metrics,
            equity_series=[],
            drawdown_series=[],
            monthly_returns=[],
            trades=[],
            created_at=datetime.utcnow()
        )
        
        return backtest_run
    
    async def get_execution(self, execution_id: str) -> Optional[StrategyExecution]:
        """Get execution by ID"""
        pool = get_database()
        
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM strategy_executions WHERE id = $1",
                execution_id
            )
        
        if not row:
            return None
        
        # Parse execution_logs - it comes from JSONB as a list or string
        execution_logs = row['execution_logs']
        if isinstance(execution_logs, str):
            import json
            try:
                execution_logs = json.loads(execution_logs) if execution_logs and execution_logs.strip() else []
            except json.JSONDecodeError:
                execution_logs = []
        elif execution_logs is None:
            execution_logs = []
        elif not isinstance(execution_logs, list):
            execution_logs = []
        
        return StrategyExecution(
            id=str(row['id']),
            strategy_id=row['strategy_id'],
            user_id=row['user_id'],
            status=row['status'],
            generated_code=row['generated_code'],
            execution_logs=execution_logs,
            backtest_run_id=row['backtest_run_id'],
            error_message=row['error_message'],
            agent_insights=row['agent_insights'],
            created_at=row['created_at'],
            started_at=row['started_at'],
            completed_at=row['completed_at']
        )
    
    async def get_executions_for_strategy(self, strategy_id: str) -> list[StrategyExecution]:
        """Get all executions for a strategy"""
        pool = get_database()
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM strategy_executions WHERE strategy_id = $1 ORDER BY created_at DESC",
                strategy_id
            )
        
        executions = []
        for row in rows:
            # Parse execution_logs - it comes from JSONB as a list or string
            execution_logs = row['execution_logs']
            if isinstance(execution_logs, str):
                import json
                execution_logs = json.loads(execution_logs) if execution_logs else []
            elif execution_logs is None:
                execution_logs = []
            
            executions.append(StrategyExecution(
                id=str(row['id']),
                strategy_id=row['strategy_id'],
                user_id=row['user_id'],
                status=row['status'],
                generated_code=row['generated_code'],
                execution_logs=execution_logs,
                backtest_run_id=row['backtest_run_id'],
                error_message=row['error_message'],
                agent_insights=row['agent_insights'],
                created_at=row['created_at'],
                started_at=row['started_at'],
                completed_at=row['completed_at']
            ))
        
        return executions
    
    async def get_generated_code(self, execution_id: str) -> Optional[str]:
        """Get the generated code for an execution"""
        execution = await self.get_execution(execution_id)
        if execution:
            return execution.generated_code
        return None


# Singleton instance
strategy_execution_service = StrategyExecutionService()
