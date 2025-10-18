"""
WebSocket endpoint for real-time backtest execution with CrewAI agents.
Streams agent status updates and logs to the frontend.
"""

import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any, Optional
from ..services.strategy_execution_service import strategy_execution_service
from ..database import get_database

router = APIRouter()


class BacktestConnectionManager:
    """Manage WebSocket connections for backtest executions"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, execution_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[execution_id] = websocket
    
    def disconnect(self, execution_id: str):
        if execution_id in self.active_connections:
            del self.active_connections[execution_id]
    
    async def send_message(self, execution_id: str, message: Dict[str, Any]):
        websocket = self.active_connections.get(execution_id)
        if websocket:
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"Error sending message to {execution_id}: {e}")


manager = BacktestConnectionManager()


@router.websocket("/ws/backtest")
async def websocket_backtest_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time backtest execution.
    
    Expected message format from client:
    {
        "type": "execute",
        "strategy_id": "uuid",
        "strategy_schema": {...},  // Optional: if provided, skips database lookup
        "strategy_name": "My Strategy",  // Optional: used if strategy_schema provided
        "params": {
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "initial_capital": 10000,
            "fees": 0.001,
            "slippage": 0.001
        }
    }
    
    Response message types to client:
    - agent_start: Agent begins execution
    - agent_step: Progress update within agent
    - agent_output: Log output from agent
    - agent_complete: Agent finishes
    - execution_complete: Final results with metrics
    - error: Error occurred
    """
    await websocket.accept()
    execution_id = None
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "execute":
                strategy_id = message_data.get("strategy_id")
                params = message_data.get("params", {})
                strategy_schema_provided = message_data.get("strategy_schema")
                strategy_name_provided = message_data.get("strategy_name", "Generated Strategy")
                
                print(f"\n🔍 WebSocket Execute Request:")
                print(f"  - strategy_id: {strategy_id}")
                print(f"  - has strategy_schema: {strategy_schema_provided is not None}")
                print(f"  - strategy_name: {strategy_name_provided}")
                
                if not strategy_id:
                    await websocket.send_json({
                        "type": "error",
                        "error": "strategy_id is required"
                    })
                    continue
                
                # Use provided strategy schema or fetch from database
                strategy = None
                strategy_schema = None
                strategy_name = None
                
                if strategy_schema_provided:
                    # Use provided schema directly
                    print(f"✅ Using provided strategy schema for {strategy_id}")
                    strategy_schema = strategy_schema_provided
                    strategy_name = strategy_name_provided
                else:
                    # Get strategy from database to extract schema
                    try:
                        pool = get_database()
                        async with pool.acquire() as conn:
                            strategy = await conn.fetchrow(
                                "SELECT id, name, schema_json FROM strategies WHERE id = $1",
                                strategy_id
                            )
                        
                        if strategy:
                            strategy_schema = strategy['schema_json']
                            strategy_name = strategy['name']
                            print(f"✅ Retrieved strategy from database: {strategy_name}")
                        else:
                            print(f"⚠️  Strategy {strategy_id} not found in database, using mock strategy for testing")
                            # Use mock strategy for testing
                            strategy_schema = {
                                "nodes": [
                                    {"id": "1", "type": "category", "meta": {"category": "Bitcoin"}},
                                    {"id": "2", "type": "entry_condition", "meta": {
                                        "mode": "manual",
                                        "rules": ["Buy when 10-day moving average crosses above 30-day moving average", "RSI below 30 (oversold)"]
                                    }},
                                    {"id": "3", "type": "stop_loss", "meta": {"stop_pct": 5.0}},
                                    {"id": "4", "type": "take_profit", "meta": {"target_pct": 7.0}}
                                ],
                                "edges": []
                            }
                            strategy_name = "Mock Strategy - MA Crossover"
                            
                    except Exception as db_error:
                        print(f"⚠️  Database error: {db_error}")
                        print(f"📝 Using mock strategy for testing")
                        # Use mock strategy when database not available
                        strategy_schema = {
                            "nodes": [
                                {"id": "1", "type": "category", "meta": {"category": "Bitcoin"}},
                                {"id": "2", "type": "entry_condition", "meta": {
                                    "mode": "manual",
                                    "rules": ["Buy when 10-day moving average crosses above 30-day moving average", "RSI below 30 (oversold)"]
                                }},
                                {"id": "3", "type": "stop_loss", "meta": {"stop_pct": 5.0}},
                                {"id": "4", "type": "take_profit", "meta": {"target_pct": 7.0}}
                            ],
                            "edges": []
                        }
                        strategy_name = "Mock Strategy - MA Crossover"
                
                # Send acknowledgment
                await websocket.send_json({
                    "type": "execution_started",
                    "strategy_id": strategy_id
                })
                
                # Define callback for streaming updates
                async def stream_callback(update: Dict[str, Any]):
                    """Callback to stream updates to WebSocket"""
                    try:
                        await websocket.send_json(update)
                    except Exception as e:
                        print(f"Error streaming update: {e}")
                
                # Execute strategy with streaming
                try:
                    result = await strategy_execution_service.execute_strategy_with_streaming(
                        strategy_id=strategy_id,
                        strategy_schema=strategy_schema,
                        strategy_name=strategy_name,
                        params=params,
                        callback=stream_callback
                    )
                    
                    # Send completion message
                    await websocket.send_json({
                        "type": "execution_complete",
                        "results": result
                    })
                    
                except Exception as e:
                    import traceback
                    error_trace = traceback.format_exc()
                    print(f"Execution error: {error_trace}")
                    
                    await websocket.send_json({
                        "type": "error",
                        "error": str(e),
                        "traceback": error_trace
                    })
            
            elif message_data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        print(f"WebSocket client disconnected")
        if execution_id:
            manager.disconnect(execution_id)
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        try:
            await websocket.send_json({
                "type": "error",
                "error": str(e)
            })
        except:
            pass

