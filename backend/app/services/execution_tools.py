"""
Agent tools for strategy code generation and execution.
These tools are used by CrewAI agents to transform and execute strategies.
"""

import subprocess
import tempfile
import json
import ast
import re
import traceback
from pathlib import Path
from typing import Dict, Any, List
from crewai.tools import tool


@tool
def generate_vectorbt_code_tool(strategy_json: str, params: str) -> str:
    """Generate VectorBT Code
    
    Generates executable VectorBT Python code from strategy JSON.
    
    Args:
        strategy_json: JSON string of strategy schema with nodes and edges
        params: JSON string of backtest parameters (dates, capital, etc.)
    
    Returns:
        Python code as string
    """
    try:
        from .strategy_code_generator import strategy_code_generator
        
        strategy_dict = json.loads(strategy_json)
        params_dict = json.loads(params)
        
        code = strategy_code_generator.generate_vectorbt_code(
            strategy_dict,
            params_dict
        )
        
        return code
    except Exception as e:
        return f"Error generating code: {str(e)}\n{traceback.format_exc()}"


@tool
def validate_python_code_tool(code: str) -> str:
    """Validate Python Code
    
    Validates Python code for security issues and syntax errors.
    
    Args:
        code: Python code to validate
    
    Returns:
        JSON string with validation results
    """
    try:
        issues = []
        
        # Check for dangerous operations
        dangerous_patterns = [
            (r'\bos\.system\b', 'os.system() - can execute shell commands'),
            (r'\bsubprocess\.(?!run\b)', 'subprocess (except run) - security risk'),
            (r'\beval\b', 'eval() - code injection risk'),
            (r'\bexec\b', 'exec() - code injection risk'),
            (r'\b__import__\b', '__import__() - dynamic imports'),
            (r'\bopen\(.*[\'"]w', 'File writing - not allowed'),
            (r'\brequests\.', 'Network requests - not allowed'),
            (r'\burllib', 'Network requests - not allowed'),
        ]
        
        for pattern, reason in dangerous_patterns:
            if re.search(pattern, code):
                issues.append(f"Security issue: {reason}")
        
        # Check syntax
        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append(f"Syntax error: {e}")
        
        # Check for required imports
        required_imports = ['vectorbt', 'pandas', 'numpy']
        for imp in required_imports:
            if f'import {imp}' not in code:
                issues.append(f"Warning: Missing import '{imp}'")
        
        result = {
            'valid': len([i for i in issues if 'Security' in i or 'Syntax' in i]) == 0,
            'issues': issues
        }
        
        return json.dumps(result)
    except Exception as e:
        return json.dumps({
            'valid': False,
            'issues': [f"Validation error: {str(e)}"]
        })


@tool
def execute_python_code_tool(code: str, timeout: int = 300) -> str:
    """Execute Python Code
    
    Executes Python code in a sandboxed environment and returns results.
    
    Args:
        code: Python code to execute
        timeout: Maximum execution time in seconds (default: 300)
    
    Returns:
        JSON string with execution results or error
    """
    try:
        # Create temporary file for code
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False
        ) as f:
            f.write(code)
            code_file = f.name
        
        # Execute in subprocess (sandboxed)
        result = subprocess.run(
            ['python', code_file],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd='/tmp'  # Run in temp directory for isolation
        )
        
        # Parse results
        if result.returncode == 0:
            stdout = result.stdout
            
            # Extract JSON results
            if "===RESULTS_START===" in stdout:
                start = stdout.index("===RESULTS_START===") + len("===RESULTS_START===")
                end = stdout.index("===RESULTS_END===")
                results_json = stdout[start:end].strip()
                results = json.loads(results_json)
                
                return json.dumps({
                    'status': 'success',
                    'metrics': results,
                    'logs': stdout[:start].strip()
                })
            else:
                return json.dumps({
                    'status': 'error',
                    'error': 'No results found in output',
                    'logs': stdout
                })
        else:
            return json.dumps({
                'status': 'error',
                'error': result.stderr,
                'logs': result.stdout
            })
            
    except subprocess.TimeoutExpired:
        return json.dumps({
            'status': 'error',
            'error': f'Execution timeout after {timeout}s'
        })
    except Exception as e:
        return json.dumps({
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        })
    finally:
        # Cleanup
        try:
            Path(code_file).unlink(missing_ok=True)
        except:
            pass


@tool
def search_strategy_memory_tool(query: str, user_id: str, limit: int = 5) -> str:
    """Search Strategy Memory
    
    Searches mem0 for relevant strategy patterns and code examples.
    
    Args:
        query: Search query
        user_id: User ID for personalized results
        limit: Maximum number of results (default: 5)
    
    Returns:
        JSON string with list of relevant memories
    """
    try:
        from mem0 import Memory
        
        memory = Memory()
        
        results = memory.search(
            query=query,
            user_id=user_id,
            limit=limit
        )
        
        memories = [
            {
                'content': r.get('memory', ''),
                'metadata': r.get('metadata', {}),
                'relevance': r.get('score', 0)
            }
            for r in results
        ]
        
        return json.dumps(memories)
    except Exception as e:
        # If mem0 not configured, return empty results
        print(f"Warning: mem0 search failed: {e}")
        return json.dumps([])


@tool
def store_strategy_memory_tool(content: str, user_id: str, metadata: str) -> str:
    """Store Strategy Memory
    
    Stores strategy execution results in mem0 for future learning.
    
    Args:
        content: Memory content to store
        user_id: User ID
        metadata: JSON string of additional metadata
    
    Returns:
        JSON string with memory ID
    """
    try:
        from mem0 import Memory
        
        memory = Memory()
        metadata_dict = json.loads(metadata)
        
        result = memory.add(
            messages=[{"role": "assistant", "content": content}],
            user_id=user_id,
            metadata=metadata_dict
        )
        
        return json.dumps({
            'success': True,
            'memory_id': result.get('id', '')
        })
    except Exception as e:
        # If mem0 not configured, just log and continue
        print(f"Warning: mem0 storage failed: {e}")
        return json.dumps({
            'success': False,
            'error': str(e)
        })


@tool
def get_available_tokens_tool() -> str:
    """Get Available Tokens
    
    Returns list of available cryptocurrency tokens for backtesting.
    
    Returns:
        JSON string with token names and their CoinGecko IDs
    """
    try:
        from .coingecko_service import TOP_20_TOKENS
        
        return json.dumps({
            'tokens': TOP_20_TOKENS,
            'count': len(TOP_20_TOKENS),
            'description': 'Top 20 cryptocurrencies available for backtesting'
        })
    except Exception as e:
        return json.dumps({
            'error': str(e),
            'tokens': {}
        })


@tool
def get_period_mappings_tool() -> str:
    """Get Period Mappings
    
    Returns mapping of period shortcuts to number of days.
    
    Returns:
        JSON string with period mappings
    """
    try:
        from .coingecko_service import PERIOD_TO_DAYS
        
        # Convert to a more readable format
        period_info = {}
        for period, days in PERIOD_TO_DAYS.items():
            if days == "max":
                period_info[period] = "Maximum available data (5 years)"
            elif days is None:
                period_info[period] = "Year to date (calculated dynamically)"
            else:
                period_info[period] = f"{days} days"
        
        return json.dumps({
            'periods': PERIOD_TO_DAYS,
            'descriptions': period_info,
            'example': 'Use period="3M" for 90 days of data'
        })
    except Exception as e:
        return json.dumps({
            'error': str(e),
            'periods': {}
        })


# Export all tools
__all__ = [
    'generate_vectorbt_code_tool',
    'validate_python_code_tool',
    'execute_python_code_tool',
    'search_strategy_memory_tool',
    'store_strategy_memory_tool',
    'get_available_tokens_tool',
    'get_period_mappings_tool'
]
