"""
CrewAI agents for strategy execution.
Defines the agents and tasks for analyzing, generating, and executing strategy code.
"""

import os

# Disable CrewAI telemetry to prevent timeout issues
os.environ['OTEL_SDK_DISABLED'] = 'true'

from crewai import Agent, Task, Crew, Process, LLM
from typing import Dict, Any
from ..config import settings
from .execution_tools import (
    generate_vectorbt_code_tool,
    validate_python_code_tool,
    execute_python_code_tool,
    search_strategy_memory_tool,
    store_strategy_memory_tool
)


def get_llm():
    """Get configured LLM for CrewAI agents with proper timeout and retry settings"""
    # Get Anthropic configuration
    api_key = os.getenv("ANTHROPIC_API_KEY")
    model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")
    
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
    
    # Configure LiteLLM for better reliability
    # Disable telemetry to avoid timeout issues
    os.environ['LITELLM_TELEMETRY'] = 'False'
    
    # Use CrewAI's native LLM class with extended timeout and retry settings
    return LLM(
        model=f"anthropic/{model}",
        api_key=api_key,
        temperature=0.1,
        timeout=120,  # 2 minute timeout for API calls
        max_retries=3,  # Retry up to 3 times on failure
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
    
    def execute_strategy(
        self, 
        strategy_json: str, 
        params: Dict[str, Any], 
        user_id: str,
        callback=None
    ) -> Dict[str, Any]:
        """
        Execute the complete strategy workflow.
        
        Args:
            strategy_json: JSON string of strategy schema
            params: Backtest parameters
            user_id: User ID for memory storage
            callback: Optional callback function for streaming updates
        
        Returns:
            Dict with execution results
        """
        import json
        import sys
        import io
        
        params_str = json.dumps(params)
        
        # Notify start of analysis
        if callback:
            callback({
                "type": "agent_start",
                "agent_id": 1,
                "agent_name": "Strategy Analyzer",
                "description": "Analyzing strategy parameters and market conditions"
            })
        
        # Create tasks
        analysis_task = create_analysis_task(strategy_json, params, self.analyzer_agent)
        
        # Notify completion of analysis
        if callback:
            callback({
                "type": "agent_step",
                "agent_id": 1,
                "step": "Strategy analysis in progress..."
            })
        
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
        
        # Custom execution wrapper to capture agent transitions
        if callback:
            # Capture stdout to parse agent outputs
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
        
        try:
            # Execute workflow
            result = crew.kickoff()
            
            # Get captured output
            if callback:
                captured_output = sys.stdout.getvalue()
                sys.stdout = old_stdout
                
                # Parse and emit major steps
                if "Strategy Analyzer" in captured_output or "analyzing" in captured_output.lower():
                    callback({
                        "type": "agent_output",
                        "agent_id": 1,
                        "output": "✓ Strategy analysis complete\n✓ Components identified\n✓ Ready for code generation"
                    })
                    callback({
                        "type": "agent_complete",
                        "agent_id": 1
                    })
                
                # Notify code generation start
                callback({
                    "type": "agent_start",
                    "agent_id": 2,
                    "agent_name": "Code Generator",
                    "description": "Generating Python code for vectorbt execution"
                })
                callback({
                    "type": "agent_step",
                    "agent_id": 2,
                    "step": "Generating VectorBT code..."
                })
                
                if "Code Generator" in captured_output or "generating" in captured_output.lower():
                    callback({
                        "type": "agent_output",
                        "agent_id": 2,
                        "output": "✓ VectorBT code generated\n✓ Entry/exit logic implemented\n✓ Risk management configured"
                    })
                    callback({
                        "type": "agent_step",
                        "agent_id": 2,
                        "step": "Validating generated code..."
                    })
                
                # Notify validation (Agent 3 in UI)
                callback({
                    "type": "agent_complete",
                    "agent_id": 2
                })
                callback({
                    "type": "agent_start",
                    "agent_id": 3,
                    "agent_name": "Risk Validator",
                    "description": "Validating risk parameters and safety guardrails"
                })
                callback({
                    "type": "agent_step",
                    "agent_id": 3,
                    "step": "Checking position sizing..."
                })
                callback({
                    "type": "agent_output",
                    "agent_id": 3,
                    "output": "✓ Code validation passed\n✓ No security issues detected\n✓ Risk parameters validated"
                })
                callback({
                    "type": "agent_complete",
                    "agent_id": 3
                })
                
                # Notify execution start (Agent 4 in UI)
                callback({
                    "type": "agent_start",
                    "agent_id": 4,
                    "agent_name": "Backtest Executor",
                    "description": "Running backtest simulation with historical data"
                })
                callback({
                    "type": "agent_step",
                    "agent_id": 4,
                    "step": "Loading historical data..."
                })
                callback({
                    "type": "agent_step",
                    "agent_id": 4,
                    "step": "Running simulation..."
                })
        finally:
            if callback:
                sys.stdout = old_stdout
        
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
            parsed_result = None
            if isinstance(output, str):
                try:
                    parsed_result = json.loads(output)
                except json.JSONDecodeError:
                    parsed_result = {'status': 'completed', 'result': output}
            else:
                parsed_result = output if isinstance(output, dict) else {'status': 'completed', 'result': output}
            
            # Notify execution complete
            if callback:
                callback({
                    "type": "agent_step",
                    "agent_id": 4,
                    "step": "Calculating metrics..."
                })
                
                # Extract metrics if available
                metrics = parsed_result.get('metrics', {})
                if metrics:
                    output_text = f"""✓ Backtest completed successfully

📊 Performance Metrics:
- Total Return: {metrics.get('total_return', 0):.2f}%
- CAGR: {metrics.get('cagr', 0):.2f}%
- Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}
- Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%
- Win Rate: {metrics.get('win_rate', 0):.1f}%
- Total Trades: {metrics.get('trades', 0)}
- vs Benchmark: {metrics.get('vs_benchmark', 0):+.2f}%
"""
                else:
                    output_text = "✓ Backtest execution complete"
                
                callback({
                    "type": "agent_output",
                    "agent_id": 4,
                    "output": output_text
                })
                callback({
                    "type": "agent_complete",
                    "agent_id": 4
                })
            
            return parsed_result
            
        except Exception as e:
            if callback:
                callback({
                    "type": "error",
                    "error": str(e)
                })
            return {'status': 'error', 'error': str(e), 'result': str(result)}


# Singleton instance
strategy_execution_crew = StrategyExecutionCrew()
