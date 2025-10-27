#!/usr/bin/env python3
"""
Test script for the Research Agent functionality.

This script tests:
1. Strategy research and discovery
2. Database integration
3. Autonomous backtesting
4. Performance ranking
5. Full pipeline execution
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models import ResearchRequest, AutonomousBacktestRequest
from app.services.research_agent_service import research_agent_service
from app.database import connect_to_postgres, close_postgres_connection


async def test_strategy_research():
    """Test strategy research functionality"""
    print("\n" + "="*80)
    print("🔍 TESTING STRATEGY RESEARCH")
    print("="*80)
    
    # Create research request
    request = ResearchRequest(
        market_focus="crypto",
        strategy_types=["momentum", "mean_reversion"],
        risk_tolerance="medium",
        max_strategies=3,
        research_depth="quick"
    )
    
    try:
        # Research strategies
        strategies = await research_agent_service.research_strategies(request, "test_user")
        
        print(f"✅ Successfully researched {len(strategies)} strategies:")
        for i, strategy in enumerate(strategies, 1):
            print(f"  {i}. {strategy.name}")
            print(f"     Category: {strategy.category}")
            print(f"     Expected Return: {strategy.expected_return}%")
            print(f"     Risk Level: {strategy.risk_level}")
            print(f"     Confidence: {strategy.confidence_score:.2f}")
            print(f"     ID: {strategy.id}")
            print()
        
        return strategies
        
    except Exception as e:
        print(f"❌ Strategy research failed: {e}")
        return []


async def test_autonomous_backtesting(strategy_ids=None):
    """Test autonomous backtesting functionality"""
    print("\n" + "="*80)
    print("🚀 TESTING AUTONOMOUS BACKTESTING")
    print("="*80)
    
    # Create backtest request
    request = AutonomousBacktestRequest(
        strategy_ids=strategy_ids,
        max_concurrent_tests=3,
        performance_criteria={"min_sharpe": 1.0, "min_return": 10.0}
    )
    
    try:
        # Run autonomous backtests
        rankings = await research_agent_service.run_autonomous_backtests(request, "test_user")
        
        print(f"✅ Successfully backtested strategies. Rankings:")
        for ranking in rankings:
            print(f"  #{ranking.rank}. {ranking.strategy_name}")
            print(f"      Performance Score: {ranking.performance_score:.1f}/100")
            print(f"      Total Return: {ranking.metrics.total_return:.1f}%")
            print(f"      Sharpe Ratio: {ranking.metrics.sharpe_ratio:.2f}")
            print(f"      Max Drawdown: {ranking.metrics.max_drawdown:.1f}%")
            print(f"      Win Rate: {ranking.metrics.win_rate:.1f}%")
            print()
        
        return rankings
        
    except Exception as e:
        print(f"❌ Autonomous backtesting failed: {e}")
        return []


async def test_full_pipeline():
    """Test the complete research and backtest pipeline"""
    print("\n" + "="*80)
    print("🔄 TESTING FULL RESEARCH PIPELINE")
    print("="*80)
    
    try:
        # Step 1: Research strategies
        print("Step 1: Researching strategies...")
        research_request = ResearchRequest(
            market_focus="crypto",
            max_strategies=3,
            research_depth="quick"
        )
        strategies = await research_agent_service.research_strategies(research_request, "pipeline_test")
        print(f"✅ Researched {len(strategies)} strategies")
        
        # Step 2: Run autonomous backtests
        print("\nStep 2: Running autonomous backtests...")
        backtest_request = AutonomousBacktestRequest(
            strategy_ids=[s.id for s in strategies if s.id],
            max_concurrent_tests=3
        )
        rankings = await research_agent_service.run_autonomous_backtests(backtest_request, "pipeline_test")
        print(f"✅ Completed backtests with {len(rankings)} rankings")
        
        # Step 3: Display results
        print("\n📊 PIPELINE RESULTS:")
        print(f"Strategies Researched: {len(strategies)}")
        print(f"Strategies Backtested: {len(rankings)}")
        
        if rankings:
            top_strategy = rankings[0]
            print(f"\n🏆 TOP PERFORMING STRATEGY:")
            print(f"Name: {top_strategy.strategy_name}")
            print(f"Performance Score: {top_strategy.performance_score:.1f}/100")
            print(f"Expected Return: {top_strategy.metrics.total_return:.1f}%")
            print(f"Risk-Adjusted Return: {top_strategy.risk_adjusted_return:.2f}")
            print(f"Consistency Score: {top_strategy.consistency_score:.2f}")
        
        return {"strategies": strategies, "rankings": rankings}
        
    except Exception as e:
        print(f"❌ Full pipeline test failed: {e}")
        return None


async def test_database_queries():
    """Test database query functionality"""
    print("\n" + "="*80)
    print("💾 TESTING DATABASE QUERIES")
    print("="*80)
    
    try:
        from app.database import get_database
        
        db = get_database()
        
        # Test strategies query
        async with db.acquire() as conn:
            # Count total strategies
            total_strategies = await conn.fetchval("SELECT COUNT(*) FROM strategies")
            print(f"✅ Total strategies in database: {total_strategies}")
            
            # Count research sessions
            total_sessions = await conn.fetchval("SELECT COUNT(*) FROM research_sessions")
            print(f"✅ Total research sessions: {total_sessions}")
            
            # Get recent strategies
            recent_strategies = await conn.fetch("""
                SELECT name, metrics->>'category' as category, 
                       metrics->>'expected_return' as expected_return,
                       created_at
                FROM strategies 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            
            print(f"✅ Recent strategies:")
            for strategy in recent_strategies:
                print(f"  - {strategy['name']} ({strategy['category']}) - {strategy['expected_return']}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Database query test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🚀 STARTING RESEARCH AGENT TESTS")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Connect to database
    try:
        await connect_to_postgres()
        print("✅ Connected to database")
    except Exception as e:
        print(f"⚠️  Database connection failed: {e}")
        print("Tests will continue with limited functionality...")
    
    # Run tests
    test_results = {}
    
    # Test 1: Strategy Research
    strategies = await test_strategy_research()
    test_results["research"] = len(strategies) > 0
    
    # Test 2: Autonomous Backtesting (using researched strategies)
    strategy_ids = [s.id for s in strategies if s.id]
    rankings = await test_autonomous_backtesting(strategy_ids)
    test_results["backtesting"] = len(rankings) > 0
    
    # Test 3: Full Pipeline
    pipeline_result = await test_full_pipeline()
    test_results["pipeline"] = pipeline_result is not None
    
    # Test 4: Database Queries
    db_result = await test_database_queries()
    test_results["database"] = db_result
    
    # Summary
    print("\n" + "="*80)
    print("📋 TEST SUMMARY")
    print("="*80)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.upper()}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Research Agent is working correctly.")
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