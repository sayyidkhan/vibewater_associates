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
    store_strategy_memory_tool,
    get_available_tokens_tool,
    get_period_mappings_tool
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
        indicators, and risk management parameters. You have access to information
        about available tokens and time periods for backtesting.""",
        verbose=True,
        allow_delegation=False,
        tools=[
            search_strategy_memory_tool,
            get_available_tokens_tool,
            get_period_mappings_tool
        ],
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
        management, and risk controls. You use CoinGecko API for fetching crypto data.""",
        verbose=True,
        allow_delegation=False,
        tools=[
            generate_vectorbt_code_tool,
            validate_python_code_tool,
            search_strategy_memory_tool,
            get_available_tokens_tool,
            get_period_mappings_tool
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
            print("🔔 Sending agent_start notification for Agent 1")
            callback({
                "type": "agent_start",
                "agent_id": 1,
                "agent_name": "Strategy Analyzer",
                "description": "Analyzing strategy parameters and market conditions"
            })
            callback({
                "type": "agent_step",
                "agent_id": 1,
                "step": "Loading strategy configuration..."
            })
        
        # Create tasks
        analysis_task = create_analysis_task(strategy_json, params, self.analyzer_agent)
        
        # Notify analysis progress
        if callback:
            callback({
                "type": "agent_step",
                "agent_id": 1,
                "step": "Analyzing market conditions..."
            })
            callback({
                "type": "agent_step",
                "agent_id": 1,
                "step": "Validating parameters..."
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
4. Return ONLY the final validated Python code as a plain string

IMPORTANT: Your final answer must be ONLY the Python code, nothing else. No explanations, no markdown, just the raw Python code.
""",
            agent=self.generator_agent,
            expected_output="Complete, validated VectorBT Python code as plain text",
            context=[analysis_task]  # Uses analysis task output
        )
        
        execution_task = Task(
            description=f"""You will receive Python code from the Code Generator agent.

Your task is to execute this code and return the backtest results.

Steps:
1. Take the Python code output from the previous Code Generator task
2. Validate it using validate_python_code_tool(code)
3. If validation passes, execute using execute_python_code_tool(code, timeout=300)
4. Parse the execution results
5. If successful, store in memory using store_strategy_memory_tool(content, user_id="{user_id}", metadata)
6. Return the complete execution results as JSON

IMPORTANT: The code is in the context from the previous task. Use it directly.

User ID for memory storage: {user_id}

Return the execution results with metrics.
""",
            agent=self.executor_agent,
            expected_output="Execution results with metrics in JSON format",
            context=[code_gen_task]  # Uses code generation task output
        )
        
        # Create crew
        crew = Crew(
            agents=[self.analyzer_agent, self.generator_agent, self.executor_agent],
            tasks=[analysis_task, code_gen_task, execution_task],
            process=Process.sequential,
            verbose=True,  # Enable verbose output
            memory=False  # Disable memory to avoid issues
        )
        
        # Custom execution wrapper to capture and stream agent outputs in real-time
        class StreamingOutput:
            """Custom stdout that streams output to callback"""
            def __init__(self, original_stdout, callback_fn):
                self.original_stdout = original_stdout
                self.callback = callback_fn
                self.buffer = ""
                self.current_agent_id = 1
                
            def write(self, text):
                self.original_stdout.write(text)  # Still print to console
                self.buffer += text
                
                # Only stream important logs to frontend
                if not text.strip() or not self.callback:
                    return
                
                # Filter: only send important CrewAI events
                important_keywords = [
                    "# Agent:",
                    "Working on task:",
                    "Thought:",
                    "Action:",
                    "Action Input:",
                    "Observation:",
                    "Final Answer:",
                    "Strategy Analyzer",
                    "Code Generator", 
                    "VectorBT",
                    "Executor",
                    "Validator",
                    "Tool:",
                    "Result:",
                    "STARTING CREWAI",
                    "EXECUTION COMPLETE"
                ]
                
                is_important = any(keyword in text for keyword in important_keywords)
                
                if is_important:
                    # Detect agent transitions
                    if "Strategy Analyzer" in text or "# Agent:" in text:
                        self.current_agent_id = 1
                        self.callback({
                            "type": "agent_output",
                            "agent_id": 1,
                            "output": text.strip()
                        })
                    elif "Code Generator" in text or "VectorBT" in text:
                        if self.current_agent_id == 1:
                            self.callback({"type": "agent_complete", "agent_id": 1})
                            self.callback({
                                "type": "agent_start",
                                "agent_id": 2,
                                "agent_name": "Code Generator",
                                "description": "Generating Python code for vectorbt execution"
                            })
                        self.current_agent_id = 2
                        self.callback({
                            "type": "agent_output",
                            "agent_id": 2,
                            "output": text.strip()
                        })
                    elif "Executor" in text or "Validator" in text or "executing" in text.lower():
                        if self.current_agent_id == 2:
                            self.callback({"type": "agent_complete", "agent_id": 2})
                            self.callback({
                                "type": "agent_start",
                                "agent_id": 3,
                                "agent_name": "Code Validator",
                                "description": "Validating risk parameters"
                            })
                        self.current_agent_id = 3
                        self.callback({
                            "type": "agent_output",
                            "agent_id": 3,
                            "output": text.strip()
                        })
                    elif self.current_agent_id > 0:
                        # Stream important output to current agent
                        self.callback({
                            "type": "agent_output",
                            "agent_id": self.current_agent_id,
                            "output": text.strip()
                        })
                
            def flush(self):
                self.original_stdout.flush()
        
        old_stdout = None
        if callback:
            old_stdout = sys.stdout
            sys.stdout = StreamingOutput(old_stdout, callback)
        
        try:
            print("=" * 80)
            print("🚀 STARTING CREWAI EXECUTION")
            print("=" * 80)
            
            # Execute workflow
            result = crew.kickoff()
            
            print("=" * 80)
            print("✅ CREWAI EXECUTION COMPLETE")
            print("=" * 80)
            
            # Send final completion notifications
            if callback:
                callback({"type": "agent_complete", "agent_id": 3})
                callback({
                    "type": "agent_start",
                    "agent_id": 4,
                    "agent_name": "Backtest Executor",
                    "description": "Running backtest simulation"
                })
                
        finally:
            if old_stdout:
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
