"""
Quick test to verify CrewAI agents are working correctly.
Tests agent initialization and tool functionality without full execution.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("\n" + "="*80)
print("🧪 QUICK CREWAI VALIDATION TEST")
print("="*80 + "\n")

# Test 1: Check environment
print("1️⃣ Checking environment variables...")
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
if anthropic_key:
    print(f"   ✅ ANTHROPIC_API_KEY is set ({anthropic_key[:10]}...)")
else:
    print("   ❌ ANTHROPIC_API_KEY not found in .env")
    print("   Please add: ANTHROPIC_API_KEY=your_key_here")
    exit(1)

# Test 2: Import CrewAI components
print("\n2️⃣ Testing imports...")
try:
    from crewai import Agent, Task, Crew, Process
    print("   ✅ CrewAI imported successfully")
except ImportError as e:
    print(f"   ❌ Failed to import CrewAI: {e}")
    print("   Run: pip install -r requirements.txt")
    exit(1)

try:
    from langchain_anthropic import ChatAnthropic
    print("   ✅ LangChain Anthropic imported successfully")
except ImportError as e:
    print(f"   ❌ Failed to import LangChain Anthropic: {e}")
    print("   Run: pip install langchain-anthropic")
    exit(1)

# Test 3: Initialize agents
print("\n3️⃣ Initializing CrewAI agents...")
try:
    from app.services.strategy_agents import (
        create_strategy_analyzer_agent,
        create_code_generator_agent,
        create_code_executor_agent
    )
    
    analyzer = create_strategy_analyzer_agent()
    print(f"   ✅ Strategy Analyzer Agent: {analyzer.role}")
    
    generator = create_code_generator_agent()
    print(f"   ✅ Code Generator Agent: {generator.role}")
    
    executor = create_code_executor_agent()
    print(f"   ✅ Code Executor Agent: {executor.role}")
    
except Exception as e:
    print(f"   ❌ Failed to initialize agents: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 4: Test tools
print("\n4️⃣ Testing agent tools...")
try:
    from app.services.execution_tools import (
        generate_vectorbt_code_tool,
        validate_python_code_tool
    )
    
    # Tools are CrewAI Tool objects, not directly callable
    # They work when used by agents, but we can test the underlying functions
    print("   ✅ Tools imported successfully")
    print(f"      - generate_vectorbt_code_tool: {type(generate_vectorbt_code_tool).__name__}")
    print(f"      - validate_python_code_tool: {type(validate_python_code_tool).__name__}")
    
    # Test the underlying code generator directly
    from app.services.strategy_code_generator import strategy_code_generator
    
    test_strategy = {
        "nodes": [
            {"id": "1", "type": "entry_condition", "meta": {"rules": ["Enter on 5% drop"]}}
        ]
    }
    test_params = {
        "start_date": "2024-01-01",
        "end_date": "2024-03-31",
        "initial_capital": 10000
    }
    
    code = strategy_code_generator.generate_vectorbt_code(test_strategy, test_params)
    
    if "import vectorbt" in code:
        print("   ✅ Code generation logic working")
    else:
        print(f"   ⚠️ Code generation may have issues")
    
except Exception as e:
    print(f"   ❌ Tool test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Test LLM connection (optional, costs tokens)
print("\n5️⃣ Testing LLM connection...")
test_llm = input("   Test Anthropic API connection? This will use a few tokens (y/n): ")

if test_llm.lower() == 'y':
    try:
        from app.services.strategy_agents import get_llm
        
        llm = get_llm()
        response = llm.invoke("Say 'Hello from CrewAI!' in exactly 4 words.")
        
        print(f"   ✅ LLM Response: {response.content}")
        
    except Exception as e:
        print(f"   ❌ LLM test failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print("   ⏭️ Skipped LLM connection test")

# Summary
print("\n" + "="*80)
print("✅ VALIDATION COMPLETE")
print("="*80)
print("\n📋 Next Steps:")
print("   1. Run full test: python test_strategy_execution.py")
print("   2. Or start API server: uvicorn app.main:app --reload")
print("   3. Then test via API: POST /executions/strategies/{id}/execute\n")
