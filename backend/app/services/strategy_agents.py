"""
CrewAI agents for strategy execution.
Defines the agents and tasks for analyzing, generating, and executing strategy code.
"""

import os
from crewai import Agent, Task, Crew, Process, LLM
from typing import Dict, Any
from .execution_tools import (
    generate_vectorbt_code_tool,
    validate_python_code_tool,
    execute_python_code_tool,
    search_strategy_memory_tool,
    store_strategy_memory_tool
)


def get_llm():
    """Get configured LLM for CrewAI agents"""
    # Use CrewAI's native LLM class which properly integrates with LiteLLM
    return LLM(
        model="anthropic/claude-3-5-sonnet-20241022",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0.1
    )


def create_strategy_analyzer_agent() -> Agent:
    """
    Creates the Strategy Analyzer agent.
    Analyzes strategy JSON and extracts key components.
    """
    return Agent(
        role='Strategy Analyzer',
        goal='Analyze trading strategy schema and extract key components for code generation',
        backstory="""You are an expert quantitative analyst who understands
        trading strategies deeply. You can break down complex strategy schemas
        into clear, executable components including entry/exit conditions,
        indicators, and risk management parameters.""",
        verbose=True,
        allow_delegation=False,
        tools=[search_strategy_memory_tool],
        llm=get_llm()
    )


def create_code_generator_agent() -> Agent:
    """
    Creates the Code Generator agent.
    Generates VectorBT Python code from strategy analysis.
    """
    return Agent(
        role='VectorBT Code Generator',
        goal='Generate clean, efficient, and executable VectorBT Python code',
        backstory="""You are a Python expert specializing in the VectorBT library
        for backtesting trading strategies. You write well-documented, efficient code
        that follows best practices. You understand technical indicators, portfolio
        management, and risk controls.""",
        verbose=True,
        allow_delegation=False,
        tools=[
            generate_vectorbt_code_tool,
            validate_python_code_tool,
            search_strategy_memory_tool
        ],
        llm=get_llm()
    )


def create_code_executor_agent() -> Agent:
    """
    Creates the Code Executor agent.
    Validates and executes generated code safely.
    """
    return Agent(
        role='Code Executor and Validator',
        goal='Safely execute VectorBT code and return accurate backtest results',
        backstory="""You are a code execution specialist who ensures code runs
        safely and correctly. You validate code for security issues, execute it
        in sandboxed environments, and handle errors gracefully. You also store
        successful patterns for future learning.""",
        verbose=True,
        allow_delegation=False,
        tools=[
            validate_python_code_tool,
            execute_python_code_tool,
            store_strategy_memory_tool
        ],
        llm=get_llm()
    )


def create_analysis_task(strategy_json: str, params: Dict[str, Any], agent: Agent) -> Task:
    """
    Creates the strategy analysis task.
    """
    return Task(
        description=f"""Analyze the following trading strategy schema and extract key components:

Strategy JSON:
{strategy_json}

Parameters:
{params}

Your analysis should identify:
1. The trading asset/category (Bitcoin, Ethereum, DeFi, etc.)
2. Entry conditions and required technical indicators
3. Exit conditions (take profit, stop loss)
4. Risk management parameters
5. Any special considerations or patterns

Search memory for similar successful strategies to inform your analysis.

Provide a clear, structured analysis that will be used for code generation.
""",
        agent=agent,
        expected_output="Structured analysis with all strategy components clearly identified"
    )


def create_code_generation_task(analysis_result: str, strategy_json: str, params: str, agent: Agent) -> Task:
    """
    Creates the code generation task.
    """
    return Task(
        description=f"""Generate VectorBT Python code based on the strategy analysis:

Analysis:
{analysis_result}

Strategy JSON:
{strategy_json}

Parameters:
{params}

Generate complete, executable Python code that:
1. Imports all necessary libraries (vectorbt, pandas, numpy, json)
2. Fetches price data for the specified asset
3. Calculates required technical indicators
4. Implements entry and exit logic based on the strategy
5. Runs portfolio backtest with proper risk management (stop loss, take profit)
6. Calculates and returns metrics (total return, CAGR, Sharpe ratio, etc.)
7. Outputs results as JSON between ===RESULTS_START=== and ===RESULTS_END=== markers

Use the generate_vectorbt_code_tool to create the code.
Then validate it using validate_python_code_tool.

If validation fails, fix the issues and validate again.

Return only the final, validated Python code.
""",
        agent=agent,
        expected_output="Complete, validated VectorBT Python code as a string"
    )


def create_execution_task(generated_code: str, agent: Agent) -> Task:
    """
    Creates the code execution task.
    """
    return Task(
        description=f"""Execute the generated VectorBT code and return results:

Code to execute:
{generated_code}

Steps:
1. First, validate the code using validate_python_code_tool
2. If validation passes, execute using execute_python_code_tool with 300 second timeout
3. Parse the execution results
4. If successful, store the results in memory using store_strategy_memory_tool
5. Return the execution results

If execution fails:
- Analyze the error
- Suggest fixes if possible
- Return error details

Return the execution results as JSON.
""",
        agent=agent,
        expected_output="Execution results with metrics or detailed error information"
    )


class StrategyExecutionCrew:
    """
    Orchestrates the strategy execution workflow using CrewAI.
    """
    
    def __init__(self):
        self.analyzer_agent = create_strategy_analyzer_agent()
        self.generator_agent = create_code_generator_agent()
        self.executor_agent = create_code_executor_agent()
    
    def execute_strategy(self, strategy_json: str, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Execute the complete strategy workflow.
        
        Args:
            strategy_json: JSON string of strategy schema
            params: Backtest parameters
            user_id: User ID for memory storage
        
        Returns:
            Dict with execution results
        """
        import json
        
        params_str = json.dumps(params)
        
        # Create tasks
        analysis_task = create_analysis_task(strategy_json, params, self.analyzer_agent)
        
        # For code generation, we'll pass the analysis result
        # Note: In CrewAI, tasks can access previous task outputs via context
        code_gen_task = Task(
            description=f"""Generate VectorBT Python code for the strategy.

Strategy JSON: {strategy_json}
Parameters: {params_str}

Use the analysis from the previous task to inform your code generation.

Steps:
1. Use generate_vectorbt_code_tool with the strategy JSON and parameters
2. Validate the generated code with validate_python_code_tool
3. If validation fails, regenerate and validate again
4. Return the final validated code

Return only the Python code as a string.
""",
            agent=self.generator_agent,
            expected_output="Complete, validated VectorBT Python code",
            context=[analysis_task]  # Uses analysis task output
        )
        
        execution_task = Task(
            description=f"""Execute the generated code and return results.

User ID: {user_id}

Steps:
1. Validate the code from the previous task
2. Execute it using execute_python_code_tool
3. If successful, store results in memory with user_id: {user_id}
4. Return execution results as JSON

Return the complete execution results.
""",
            agent=self.executor_agent,
            expected_output="Execution results with metrics",
            context=[code_gen_task]  # Uses code generation task output
        )
        
        # Create crew
        crew = Crew(
            agents=[self.analyzer_agent, self.generator_agent, self.executor_agent],
            tasks=[analysis_task, code_gen_task, execution_task],
            process=Process.sequential,
            verbose=True
        )
        
        # Execute workflow
        result = crew.kickoff()
        
        # Parse and return result
        try:
            # Handle CrewOutput object
            if hasattr(result, 'raw'):
                output = result.raw
            elif hasattr(result, 'result'):
                output = result.result
            elif hasattr(result, 'output'):
                output = result.output
            else:
                output = str(result)
            
            # Try to parse as JSON
            if isinstance(output, str):
                try:
                    return json.loads(output)
                except json.JSONDecodeError:
                    return {'status': 'completed', 'result': output}
            
            return output if isinstance(output, dict) else {'status': 'completed', 'result': output}
            
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'result': str(result)}


# Singleton instance
strategy_execution_crew = StrategyExecutionCrew()
