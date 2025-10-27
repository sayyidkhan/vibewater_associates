#!/usr/bin/env python3
"""
Simple test script for the Research Agent API endpoints.

This script tests the API endpoints without requiring LLM configuration.
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models import ResearchRequest, AutonomousBacktestRequest
from app.database import connect_to_postgres, close_postgres_connection


async def test_database_schema():
    """Test that the database schema is properly set up"""
    print("\n" + "="*80)
    print("💾 TESTING DATABASE SCHEMA")
    print("="*80)
    
    try:
        from app.database import get_database
        
        db = get_database()
        
        # Test that all required tables exist
        async with db.acquire() as conn:
            # Check strategies table
            strategies_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'strategies'
                )
            """)
            print(f"✅ Strategies table exists: {strategies_exists}")
            
            # Check research_sessions table
            sessions_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'research_sessions'
                )
            """)
            print(f"✅ Research sessions table exists: {sessions_exists}")
            
            # Check strategy_performance_rankings table
            rankings_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'strategy_performance_rankings'
                )
            """)
            print(f"✅ Performance rankings table exists: {rankings_exists}")
            
            # Check research_insights table
            insights_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'research_insights'
                )
            """)
            print(f"✅ Research insights table exists: {insights_exists}")
            
            return all([strategies_exists, sessions_exists, rankings_exists, insights_exists])
        
    except Exception as e:
        print(f"❌ Database schema test failed: {e}")
        return False


async def test_models():
    """Test that the Pydantic models are properly defined"""
    print("\n" + "="*80)
    print("📋 TESTING PYDANTIC MODELS")
    print("="*80)
    
    try:
        # Test ResearchRequest model
        research_request = ResearchRequest(
            market_focus="crypto",
            strategy_types=["momentum", "mean_reversion"],
            risk_tolerance="medium",
            max_strategies=5,
            research_depth="quick"
        )
        print(f"✅ ResearchRequest model: {research_request.market_focus}")
        
        # Test AutonomousBacktestRequest model
        backtest_request = AutonomousBacktestRequest(
            strategy_ids=["test-id-1", "test-id-2"],
            max_concurrent_tests=3
        )
        print(f"✅ AutonomousBacktestRequest model: {len(backtest_request.strategy_ids)} strategies")
        
        # Test model serialization
        research_dict = research_request.dict()
        backtest_dict = backtest_request.dict()
        
        print(f"✅ Model serialization works")
        print(f"   Research request keys: {list(research_dict.keys())}")
        print(f"   Backtest request keys: {list(backtest_dict.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Models test failed: {e}")
        return False


async def test_api_router_import():
    """Test that the API router can be imported"""
    print("\n" + "="*80)
    print("🔌 TESTING API ROUTER IMPORT")
    print("="*80)
    
    try:
        from app.routers.research import router
        
        print(f"✅ Research router imported successfully")
        print(f"   Router prefix: {router.prefix}")
        print(f"   Router tags: {router.tags}")
        
        # Check that routes are defined
        routes = [route.path for route in router.routes]
        print(f"   Available routes: {routes}")
        
        expected_routes = [
            "/strategies",
            "/strategies/background",
            "/strategies/background/{task_id}",
            "/backtest/autonomous",
            "/backtest/autonomous/background",
            "/backtest/autonomous/background/{task_id}",
            "/pipeline/full",
            "/strategies/database",
            "/strategies/{strategy_id}",
            "/health"
        ]
        
        missing_routes = [route for route in expected_routes if route not in routes]
        if missing_routes:
            print(f"⚠️  Missing routes: {missing_routes}")
        else:
            print(f"✅ All expected routes are defined")
        
        return True
        
    except Exception as e:
        print(f"❌ API router import test failed: {e}")
        return False


async def test_database_operations():
    """Test basic database operations"""
    print("\n" + "="*80)
    print("💾 TESTING DATABASE OPERATIONS")
    print("="*80)
    
    try:
        from app.database import get_database
        
        db = get_database()
        
        # Test inserting a mock strategy
        async with db.acquire() as conn:
            # Insert test strategy
            strategy_id = await conn.fetchval("""
                INSERT INTO strategies (user_id, name, description, status, schema_json, guardrails)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
            """, 
            "test_user",
            "Test Research Strategy",
            "A strategy created by the research agent test",
            "Backtest",
            json.dumps({"nodes": [], "connections": []}),
            json.dumps([])
            )
            
            print(f"✅ Inserted test strategy with ID: {strategy_id}")
            
            # Test inserting a research session
            session_id = await conn.fetchval("""
                INSERT INTO research_sessions (user_id, session_type, parameters, status)
                VALUES ($1, $2, $3, $4)
                RETURNING id
            """,
            "test_user",
            "strategy_research", 
            json.dumps({"max_strategies": 5}),
            "completed"
            )
            
            print(f"✅ Inserted test research session with ID: {session_id}")
            
            # Test querying strategies
            strategies = await conn.fetch("""
                SELECT id, name, user_id FROM strategies 
                WHERE user_id = $1 
                ORDER BY created_at DESC 
                LIMIT 5
            """, "test_user")
            
            print(f"✅ Retrieved {len(strategies)} strategies for test_user")
            
            # Clean up test data
            await conn.execute("DELETE FROM strategies WHERE user_id = $1", "test_user")
            await conn.execute("DELETE FROM research_sessions WHERE user_id = $1", "test_user")
            
            print(f"✅ Cleaned up test data")
        
        return True
        
    except Exception as e:
        print(f"❌ Database operations test failed: {e}")
        return False


async def test_research_agent_structure():
    """Test the research agent service structure without running it"""
    print("\n" + "="*80)
    print("🤖 TESTING RESEARCH AGENT STRUCTURE")
    print("="*80)
    
    try:
        # Test that we can import the service class (but not instantiate it without API keys)
        from app.services.research_agent_service import ResearchAgentService
        
        print(f"✅ ResearchAgentService class imported successfully")
        
        # Check that required methods exist
        required_methods = [
            'research_strategies',
            'run_autonomous_backtests',
            '_parse_research_results',
            '_store_strategy',
            '_create_research_session',
            '_complete_research_session',
            '_fail_research_session',
            '_store_performance_rankings'
        ]
        
        for method_name in required_methods:
            if hasattr(ResearchAgentService, method_name):
                print(f"✅ Method {method_name} exists")
            else:
                print(f"❌ Method {method_name} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Research agent structure test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🚀 STARTING RESEARCH AGENT SIMPLE TESTS")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Connect to database
    try:
        await connect_to_postgres()
        print("✅ Connected to database")
    except Exception as e:
        print(f"⚠️  Database connection failed: {e}")
        print("Some tests will be skipped...")
        return False
    
    # Run tests
    test_results = {}
    
    # Test 1: Database Schema
    test_results["database_schema"] = await test_database_schema()
    
    # Test 2: Pydantic Models
    test_results["models"] = await test_models()
    
    # Test 3: API Router Import
    test_results["api_router"] = await test_api_router_import()
    
    # Test 4: Database Operations
    test_results["database_operations"] = await test_database_operations()
    
    # Test 5: Research Agent Structure
    test_results["research_agent_structure"] = await test_research_agent_structure()
    
    # Summary
    print("\n" + "="*80)
    print("📋 TEST SUMMARY")
    print("="*80)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.upper().replace('_', ' ')}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Research Agent infrastructure is working correctly.")
        print("\n📝 NEXT STEPS:")
        print("1. Set up ANTHROPIC_API_KEY environment variable")
        print("2. Test the full research pipeline with: python3 test_research_agent.py")
        print("3. Start the API server and test the endpoints")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
    
    # Cleanup
    try:
        await close_postgres_connection()
        print("✅ Database connection closed")
    except:
        pass
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)