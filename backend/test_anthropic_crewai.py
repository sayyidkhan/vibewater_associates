#!/usr/bin/env python3
"""
Test script to verify Anthropic API works with CrewAI
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Disable telemetry before importing CrewAI
os.environ['OTEL_SDK_DISABLED'] = 'true'
os.environ['LITELLM_TELEMETRY'] = 'False'

from crewai import Agent, Task, Crew, Process, LLM

def test_anthropic_connection():
    """Test basic Anthropic API connection with CrewAI"""
    print("\n" + "="*80)
    print("🧪 TESTING ANTHROPIC API WITH CREWAI")
    print("="*80 + "\n")
    
    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in .env file")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Create LLM instance
    try:
        print("\n📋 Creating LLM instance...")
        llm = LLM(
            model="anthropic/claude-3-5-haiku-20241022",
            api_key=api_key,
            temperature=0.1,
            timeout=120,
            max_retries=3
        )
        print("✅ LLM instance created successfully")
    except Exception as e:
        print(f"❌ Failed to create LLM: {e}")
        return False
    
    # Create a simple agent
    try:
        print("\n📋 Creating test agent...")
        agent = Agent(
            role='Test Agent',
            goal='Answer a simple question',
            backstory='You are a helpful assistant.',
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        print("✅ Agent created successfully")
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")
        return False
    
    # Create a simple task
    try:
        print("\n📋 Creating test task...")
        task = Task(
            description="What is 2 + 2? Respond with just the number.",
            agent=agent,
            expected_output="A single number"
        )
        print("✅ Task created successfully")
    except Exception as e:
        print(f"❌ Failed to create task: {e}")
        return False
    
    # Create and run crew
    try:
        print("\n📋 Creating crew and executing...")
        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        print("\n🚀 Executing crew...")
        result = crew.kickoff()
        
        print("\n" + "="*80)
        print("✅ TEST SUCCESSFUL!")
        print("="*80)
        print(f"\nResult: {result}")
        return True
        
    except Exception as e:
        print("\n" + "="*80)
        print("❌ TEST FAILED")
        print("="*80)
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_anthropic_connection()
    exit(0 if success else 1)
