"""
Test script for research agent
Tests the research agent service and API endpoints
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.research_agent_service import research_agent_service
from app.database import connect_to_postgres, close_postgres_connection


async def test_market_research():
    """Test market research functionality"""
    print("\n" + "="*80)
    print("TEST 1: Market Research")
    print("="*80)
    
    try:
        insights = await research_agent_service._research_market(market_focus="Bitcoin")
        print(f"\n✅ Market research completed")
        print(f"Market Condition: {insights.get('market_condition')}")
        print(f"Volatility: {insights.get('volatility_level')}")
        print(f"Recommended Categories: {insights.get('recommended_categories')}")
        print(f"Strategy Concepts: {len(insights.get('strategy_concepts', []))}")
        return True
    except Exception as e:
        print(f"\n❌ Market research failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_strategy_generation():
    """Test strategy generation"""
    print("\n" + "="*80)
    print("TEST 2: Strategy Generation")
    print("="*80)
    
    try:
        # First do market research
        insights = await research_agent_service._research_market(market_focus="Bitcoin")
        
        # Generate 2 test strategies
        strategies = await research_agent_service._generate_strategies(
            user_id="test_user",
            market_insights=insights,
            num_strategies=2,
            risk_level="Medium"
        )
        
        print(f"\n✅ Generated {len(strategies)} strategies")
        for strategy in strategies:
            print(f"  - {strategy['name']} (ID: {strategy['id']})")
        
        return len(strategies) > 0
    except Exception as e:
        print(f"\n❌ Strategy generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_full_research_workflow():
    """Test the complete research workflow"""
    print("\n" + "="*80)
    print("TEST 3: Full Research Workflow (2 strategies)")
    print("="*80)
    
    try:
        rankings = await research_agent_service.research_and_generate_strategies(
            user_id="test_user",
            num_strategies=2,
            market_focus="Bitcoin",
            risk_level="Medium"
        )
        
        print(f"\n✅ Research workflow completed")
        print(f"Total strategies ranked: {len(rankings)}")
        
        if rankings:
            print("\nTop 3 Strategies:")
            for i, strategy in enumerate(rankings[:3], 1):
                print(f"\n{i}. {strategy.get('strategy_name', 'Unnamed')}")
                print(f"   Rank: {strategy.get('rank', 'N/A')}")
                print(f"   Performance Score: {strategy.get('performance_score', 0)}/100")
                metrics = strategy.get('metrics', {})
                if metrics:
                    print(f"   Total Return: {metrics.get('total_return', 0):.2f}%")
                    print(f"   Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
                    print(f"   Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%")
        
        return len(rankings) > 0
    except Exception as e:
        print(f"\n❌ Full workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 RESEARCH AGENT TEST SUITE")
    print("="*80)
    
    # Connect to database
    print("\n📦 Connecting to database...")
    try:
        await connect_to_postgres()
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Some tests may fail without database connection")
    
    # Run tests
    results = {}
    
    # Test 1: Market Research (doesn't need DB)
    results['market_research'] = await test_market_research()
    
    # Test 2: Strategy Generation (needs DB)
    results['strategy_generation'] = await test_strategy_generation()
    
    # Test 3: Full Workflow (needs DB)
    # Note: This will take several minutes and make API calls
    if input("\n⚠️  Run full workflow test? This will take 5-10 minutes (y/n): ").lower() == 'y':
        results['full_workflow'] = await test_full_research_workflow()
    else:
        print("\nSkipping full workflow test")
        results['full_workflow'] = None
    
    # Close database
    try:
        await close_postgres_connection()
        print("\n✅ Closed database connection")
    except:
        pass
    
    # Print summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    for test_name, result in results.items():
        if result is None:
            status = "⏭️  SKIPPED"
        elif result:
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for r in results.values() if r is True)
    total = sum(1 for r in results.values() if r is not None)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
