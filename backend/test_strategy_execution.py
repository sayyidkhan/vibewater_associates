"""
Test script for strategy execution with CrewAI agents.
This creates a sample strategy and tests the execution workflow.
"""

import asyncio
import json
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.services.strategy_execution_service import strategy_execution_service


async def create_test_strategy():
    """Create a test strategy in MongoDB"""
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    
    # Sample strategy: Simple MA Crossover
    strategy = {
        "user_id": "test_user",
        "name": "MA Crossover Test Strategy",
        "description": "Simple moving average crossover strategy for testing",
        "status": "Backtest",
        "schema_json": {
            "nodes": [
                {
                    "id": "category_1",
                    "type": "crypto_category",
                    "data": {"label": "Bitcoin"},
                    "position": {"x": 100, "y": 100},
                    "meta": {"category": "Bitcoin"}
                },
                {
                    "id": "entry_1",
                    "type": "entry_condition",
                    "data": {"label": "Entry"},
                    "position": {"x": 300, "y": 100},
                    "meta": {
                        "mode": "auto",
                        "rules": [
                            "Enter when 10-day moving average crosses above 30-day moving average",
                            "Price must be above 20-day moving average"
                        ]
                    }
                },
                {
                    "id": "tp_1",
                    "type": "take_profit",
                    "data": {"label": "Take Profit"},
                    "position": {"x": 500, "y": 100},
                    "meta": {"target_pct": 7.0}
                },
                {
                    "id": "sl_1",
                    "type": "stop_loss",
                    "data": {"label": "Stop Loss"},
                    "position": {"x": 500, "y": 200},
                    "meta": {"stop_pct": 5.0}
                }
            ],
            "connections": [
                {"id": "e1", "source": "category_1", "target": "entry_1"},
                {"id": "e2", "source": "entry_1", "target": "tp_1"},
                {"id": "e3", "source": "entry_1", "target": "sl_1"}
            ]
        },
        "guardrails": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert strategy
    result = await db.strategies.insert_one(strategy)
    strategy_id = str(result.inserted_id)
    
    print(f"✅ Created test strategy with ID: {strategy_id}")
    
    client.close()  # Not async in motor
    return strategy_id


async def test_strategy_execution(strategy_id: str):
    """Test the strategy execution workflow"""
    from app.models import BacktestParams
    
    print("\n" + "="*80)
    print("🚀 TESTING STRATEGY EXECUTION WITH CREWAI AGENTS")
    print("="*80 + "\n")
    
    # Define backtest parameters
    params = BacktestParams(
        symbols=["BTC"],
        timeframe="1d",
        start_date="2024-01-01",
        end_date="2024-03-31",
        initial_capital=10000,
        benchmark="BTC",
        fees=0.001,
        slippage=0.001,
        position_sizing="equal",
        exposure=1.0
    )
    
    print("📋 Backtest Parameters:")
    print(f"   Symbol: BTC-USD")
    print(f"   Period: {params.start_date} to {params.end_date}")
    print(f"   Capital: ${params.initial_capital:,}")
    print(f"   Fees: {params.fees*100}%")
    print(f"   Slippage: {params.slippage*100}%\n")
    
    # Start execution
    print("🤖 Starting CrewAI agent workflow...")
    print("   Agent 1: Strategy Analyzer")
    print("   Agent 2: Code Generator")
    print("   Agent 3: Code Executor\n")
    
    try:
        execution = await strategy_execution_service.execute_strategy(
            strategy_id=strategy_id,
            user_id="test_user",
            params=params
        )
        
        print(f"✅ Execution started!")
        print(f"   Execution ID: {execution.id}")
        print(f"   Status: {execution.status}")
        print(f"   Created: {execution.created_at}\n")
        
        # Poll for completion
        print("⏳ Waiting for agents to complete (this may take 1-2 minutes)...\n")
        
        max_attempts = 60  # 5 minutes max
        attempt = 0
        
        while attempt < max_attempts:
            await asyncio.sleep(5)  # Check every 5 seconds
            attempt += 1
            
            execution = await strategy_execution_service.get_execution(execution.id)
            
            if execution.status == "completed":
                print("\n" + "="*80)
                print("✅ EXECUTION COMPLETED SUCCESSFULLY!")
                print("="*80 + "\n")
                
                # Show results
                if execution.backtest_run_id:
                    from app.database import get_database
                    db = get_database()
                    
                    backtest_run = await db.backtest_runs.find_one({"_id": execution.backtest_run_id})
                    
                    if backtest_run and backtest_run.get('metrics'):
                        metrics = backtest_run['metrics']
                        print("📊 Backtest Results:")
                        print(f"   Total Return: {metrics.get('total_return', 0):.2f}%")
                        print(f"   CAGR: {metrics.get('cagr', 0):.2f}%")
                        print(f"   Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
                        print(f"   Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%")
                        print(f"   Win Rate: {metrics.get('win_rate', 0):.1f}%")
                        print(f"   Total Trades: {metrics.get('trades', 0)}")
                        print(f"   vs Benchmark: {metrics.get('vs_benchmark', 0):+.2f}%")
                
                # Show generated code
                if execution.generated_code:
                    print(f"\n📝 Generated Code Preview:")
                    code_lines = execution.generated_code.split('\n')[:10]
                    for line in code_lines:
                        print(f"   {line}")
                    print(f"   ... ({len(execution.generated_code.split(chr(10)))} lines total)")
                
                # Show logs
                if execution.execution_logs:
                    print(f"\n📋 Execution Logs:")
                    for log in execution.execution_logs[:5]:
                        print(f"   {log}")
                
                break
                
            elif execution.status == "failed":
                print("\n" + "="*80)
                print("❌ EXECUTION FAILED")
                print("="*80 + "\n")
                print(f"Error: {execution.error_message}")
                
                if execution.execution_logs:
                    print(f"\n📋 Logs:")
                    for log in execution.execution_logs:
                        print(f"   {log}")
                break
                
            else:
                # Show progress
                status_emoji = {
                    "queued": "⏸️",
                    "analyzing": "🔍",
                    "generating_code": "⚙️",
                    "executing": "▶️"
                }
                emoji = status_emoji.get(execution.status, "⏳")
                print(f"{emoji} Status: {execution.status} (attempt {attempt}/{max_attempts})")
        
        if attempt >= max_attempts:
            print("\n⚠️ Timeout: Execution taking longer than expected")
            print(f"   Current status: {execution.status}")
            print(f"   Check execution ID: {execution.id}")
    
    except Exception as e:
        print(f"\n❌ Error during execution: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """Main test function"""
    from app.database import connect_to_mongo, close_mongo_connection
    
    print("\n" + "="*80)
    print("🧪 CREWAI STRATEGY EXECUTION TEST")
    print("="*80 + "\n")
    
    # Connect to MongoDB
    print("Connecting to MongoDB...")
    try:
        await connect_to_mongo()
        print("✅ Connected to MongoDB\n")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        print("Make sure MongoDB is running and MONGODB_URL is set in .env\n")
        return
    
    try:
        # Step 1: Create test strategy
        print("Step 1: Creating test strategy in MongoDB...")
        strategy_id = await create_test_strategy()
        
        # Step 2: Execute strategy
        print("\nStep 2: Executing strategy with CrewAI agents...")
        await test_strategy_execution(strategy_id)
        
        print("\n" + "="*80)
        print("✅ TEST COMPLETE")
        print("="*80 + "\n")
    
    finally:
        # Close MongoDB connection
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())
