"""
Research Agent Service
Autonomously researches strategies, generates them, runs backtests, and identifies highest performers.
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from crewai import Agent, Task, Crew, Process, LLM

# Disable CrewAI telemetry
os.environ['OTEL_SDK_DISABLED'] = 'true'
os.environ['LITELLM_TELEMETRY'] = 'False'

from ..models import Strategy, StrategySchema, StrategyNode, Connection, Guardrail, BacktestParams
from ..database import get_database
from .strategy_agents import get_llm
from .strategy_execution_service import strategy_execution_service


class ResearchAgent:
    """
    Research Agent that autonomously:
    1. Researches trading strategies based on market conditions
    2. Generates strategy schemas
    3. Adds them to the database
    4. Runs backtests
    5. Analyzes performance and identifies best strategies
    """
    
    def __init__(self):
        """Initialize research agent with CrewAI agents"""
        self.llm = get_llm()
        
        # Create research agents
        self.market_researcher = self._create_market_researcher()
        self.strategy_designer = self._create_strategy_designer()
        self.performance_analyzer = self._create_performance_analyzer()
    
    def _create_market_researcher(self) -> Agent:
        """Creates agent that researches market conditions and strategy patterns"""
        return Agent(
            role='Crypto Market Researcher',
            goal='Research current crypto market conditions and identify promising strategy patterns',
            backstory="""You are an expert cryptocurrency market researcher with deep knowledge 
            of DeFi, Bitcoin, Ethereum, and emerging crypto assets. You analyze market trends, 
            volatility patterns, correlation structures, and identify profitable trading opportunities. 
            You understand technical analysis, on-chain metrics, and market sentiment.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_strategy_designer(self) -> Agent:
        """Creates agent that designs trading strategy schemas"""
        return Agent(
            role='Trading Strategy Designer',
            goal='Design robust trading strategies based on market research with clear entry/exit rules',
            backstory="""You are a quantitative trading strategy designer specializing in 
            cryptocurrency markets. You create structured trading strategies with well-defined 
            entry conditions, exit targets, risk management rules, and position sizing. You 
            understand technical indicators like RSI, MACD, moving averages, Bollinger Bands, 
            and can design strategies for different market conditions (trending, ranging, volatile).""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_performance_analyzer(self) -> Agent:
        """Creates agent that analyzes backtest performance and ranks strategies"""
        return Agent(
            role='Performance Analyst',
            goal='Analyze backtest results and identify strategies with highest probability of success',
            backstory="""You are a quantitative performance analyst specializing in evaluating 
            trading strategies. You analyze metrics like Sharpe ratio, maximum drawdown, win rate, 
            profit factor, and risk-adjusted returns. You can identify robust strategies that 
            perform well across different market conditions and have sustainable edge.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    async def research_and_generate_strategies(
        self,
        user_id: str,
        num_strategies: int = 5,
        market_focus: Optional[str] = None,
        risk_level: str = "Medium"
    ) -> List[Dict[str, Any]]:
        """
        Main method: Research market and generate multiple strategies
        
        Args:
            user_id: User ID to associate strategies with
            num_strategies: Number of strategies to generate
            market_focus: Optional market focus (e.g., "Bitcoin", "DeFi", "Altcoins")
            risk_level: Risk level for strategies ("Low", "Medium", "High")
        
        Returns:
            List of generated strategy results with performance metrics
        """
        print(f"\n{'='*80}")
        print(f"🔬 STARTING RESEARCH AGENT")
        print(f"{'='*80}")
        print(f"Target: {num_strategies} strategies")
        print(f"Market Focus: {market_focus or 'Auto-detect'}")
        print(f"Risk Level: {risk_level}")
        print(f"{'='*80}\n")
        
        # Step 1: Research market conditions
        market_insights = await self._research_market(market_focus)
        
        # Step 2: Generate multiple strategies based on research
        strategies = await self._generate_strategies(
            user_id=user_id,
            market_insights=market_insights,
            num_strategies=num_strategies,
            risk_level=risk_level
        )
        
        # Step 3: Run backtests on all strategies
        backtest_results = await self._run_backtests(strategies)
        
        # Step 4: Analyze performance and rank strategies
        ranked_strategies = await self._analyze_and_rank(backtest_results)
        
        print(f"\n{'='*80}")
        print(f"✅ RESEARCH AGENT COMPLETE")
        print(f"{'='*80}")
        print(f"Generated: {len(strategies)} strategies")
        print(f"Backtested: {len(backtest_results)} strategies")
        print(f"Top performer: {ranked_strategies[0]['name'] if ranked_strategies else 'None'}")
        print(f"{'='*80}\n")
        
        return ranked_strategies
    
    async def _research_market(self, market_focus: Optional[str] = None) -> Dict[str, Any]:
        """Research current market conditions"""
        print("\n📊 Researching market conditions...")
        
        research_task = Task(
            description=f"""Research the current cryptocurrency market and identify promising trading opportunities.
            
            Market Focus: {market_focus or 'Analyze all major crypto categories (Bitcoin, Ethereum, DeFi, Altcoins)'}
            
            Your research should cover:
            1. Current market trends (bull/bear/sideways)
            2. Volatility levels and patterns
            3. Best performing asset categories
            4. Common technical patterns (breakouts, reversals, consolidations)
            5. Optimal timeframes for trading
            6. Risk factors and market conditions to consider
            
            Based on your research, identify 3-5 promising strategy concepts that could work well in current conditions.
            
            Return your findings as a structured JSON with keys:
            - market_condition: "bull"/"bear"/"sideways"
            - volatility_level: "low"/"medium"/"high"
            - recommended_categories: list of crypto categories
            - strategy_concepts: list of strategy ideas with descriptions
            - optimal_timeframes: list of good timeframes (e.g., "1h", "4h", "1d")
            """,
            agent=self.market_researcher,
            expected_output="Market research findings with strategy concepts as structured JSON"
        )
        
        # Execute research task
        crew = Crew(
            agents=[self.market_researcher],
            tasks=[research_task],
            process=Process.sequential,
            verbose=True
        )
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, crew.kickoff)
        
        # Parse result
        try:
            if hasattr(result, 'raw'):
                output = result.raw
            else:
                output = str(result)
            
            # Try to parse as JSON
            insights = json.loads(output)
        except json.JSONDecodeError:
            # If not JSON, create default insights
            insights = {
                "market_condition": "sideways",
                "volatility_level": "medium",
                "recommended_categories": ["Bitcoin", "Ethereum", "DeFi"],
                "strategy_concepts": [
                    {"name": "Mean Reversion", "description": "Buy dips, sell rallies"},
                    {"name": "Breakout Trading", "description": "Trade range breakouts"},
                    {"name": "Trend Following", "description": "Follow momentum"}
                ],
                "optimal_timeframes": ["4h", "1d"]
            }
        
        print(f"✅ Market research complete: {insights.get('market_condition', 'unknown')} market")
        return insights
    
    async def _generate_strategies(
        self,
        user_id: str,
        market_insights: Dict[str, Any],
        num_strategies: int,
        risk_level: str
    ) -> List[Dict[str, Any]]:
        """Generate multiple strategy schemas based on market research"""
        print(f"\n🎨 Generating {num_strategies} strategies...")
        
        strategies = []
        
        for i in range(num_strategies):
            print(f"\nGenerating strategy {i+1}/{num_strategies}...")
            
            # Get a strategy concept if available
            concepts = market_insights.get('strategy_concepts', [])
            concept = concepts[i % len(concepts)] if concepts else {"name": "Custom Strategy", "description": "Custom trading strategy"}
            
            design_task = Task(
                description=f"""Design a complete trading strategy schema based on market research.
                
                Market Conditions:
                {json.dumps(market_insights, indent=2)}
                
                Strategy Concept: {concept.get('name', 'Custom')}
                Description: {concept.get('description', 'Create a profitable trading strategy')}
                Risk Level: {risk_level}
                
                Create a detailed strategy with:
                1. A unique strategy name
                2. Category (choose from: Bitcoin, Ethereum, DeFi, Altcoins, NFT, Memecoins)
                3. Entry conditions using technical indicators (RSI, MACD, Moving Averages, etc.)
                4. Take profit target (percentage)
                5. Stop loss (percentage)
                6. Timeframe (1m, 5m, 15m, 1h, 4h, 1d)
                
                Return ONLY a JSON object with this exact structure:
                {{
                    "name": "Strategy Name",
                    "description": "Brief strategy description",
                    "category": "Bitcoin",
                    "entry_conditions": ["Condition 1", "Condition 2"],
                    "indicators": ["RSI", "MACD"],
                    "take_profit_pct": 5.0,
                    "stop_loss_pct": 2.5,
                    "timeframe": "4h",
                    "risk_level": "{risk_level}"
                }}
                """,
                agent=self.strategy_designer,
                expected_output="Strategy schema as JSON"
            )
            
            crew = Crew(
                agents=[self.strategy_designer],
                tasks=[design_task],
                process=Process.sequential,
                verbose=False  # Less verbose for multiple strategies
            )
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, crew.kickoff)
            
            # Parse result
            try:
                if hasattr(result, 'raw'):
                    output = result.raw
                else:
                    output = str(result)
                
                # Clean up output (remove markdown if present)
                output = output.strip()
                if output.startswith('```json'):
                    output = output[7:]
                if output.startswith('```'):
                    output = output[3:]
                if output.endswith('```'):
                    output = output[:-3]
                output = output.strip()
                
                strategy_data = json.loads(output)
                
                # Convert to database schema
                strategy = await self._create_strategy_in_db(user_id, strategy_data)
                strategies.append(strategy)
                
                print(f"✅ Created strategy: {strategy_data.get('name', 'Unnamed')}")
                
            except Exception as e:
                print(f"❌ Failed to create strategy {i+1}: {e}")
                continue
        
        print(f"\n✅ Generated {len(strategies)} strategies")
        return strategies
    
    async def _create_strategy_in_db(self, user_id: str, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create strategy in database"""
        pool = get_database()
        
        # Build strategy schema
        nodes = [
            {"id": "start", "type": "start", "data": {"label": "Start"}, "position": {"x": 0, "y": 0}},
            {"id": "category", "type": "category", "data": {"label": strategy_data.get("category", "Bitcoin")}, "position": {"x": 0, "y": 100}},
            {"id": "entry", "type": "entry", "data": {
                "label": "Entry Conditions",
                "conditions": strategy_data.get("entry_conditions", []),
                "indicators": strategy_data.get("indicators", [])
            }, "position": {"x": 0, "y": 200}},
            {"id": "take_profit", "type": "take_profit", "data": {"target_pct": strategy_data.get("take_profit_pct", 5.0)}, "position": {"x": 0, "y": 300}},
            {"id": "stop_loss", "type": "stop_loss", "data": {"stop_pct": strategy_data.get("stop_loss_pct", 2.5)}, "position": {"x": 0, "y": 400}},
            {"id": "end", "type": "end", "data": {"label": "End"}, "position": {"x": 0, "y": 500}}
        ]
        
        connections = [
            {"id": "e1", "source": "start", "target": "category"},
            {"id": "e2", "source": "category", "target": "entry"},
            {"id": "e3", "source": "entry", "target": "take_profit"},
            {"id": "e4", "source": "take_profit", "target": "stop_loss"},
            {"id": "e5", "source": "stop_loss", "target": "end"}
        ]
        
        schema_json = {
            "nodes": nodes,
            "connections": connections
        }
        
        guardrails = [
            {"type": "max_drawdown", "level": "warning", "message": "Maximum drawdown limit"},
            {"type": "risk_level", "level": "info", "message": f"Risk level: {strategy_data.get('risk_level', 'Medium')}"}
        ]
        
        # Insert into database
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO strategies (user_id, name, description, status, schema_json, guardrails, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
                """,
                user_id,
                strategy_data.get("name", "Research Generated Strategy"),
                strategy_data.get("description", "Autonomously generated strategy"),
                "Backtest",
                json.dumps(schema_json),
                json.dumps(guardrails),
                datetime.utcnow()
            )
            strategy_id = str(row['id'])
        
        return {
            "id": strategy_id,
            "user_id": user_id,
            "name": strategy_data.get("name"),
            "description": strategy_data.get("description"),
            "schema_json": schema_json,
            "guardrails": guardrails,
            "timeframe": strategy_data.get("timeframe", "4h"),
            "category": strategy_data.get("category", "Bitcoin")
        }
    
    async def _run_backtests(self, strategies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run backtests on all generated strategies"""
        print(f"\n🧪 Running backtests on {len(strategies)} strategies...")
        
        results = []
        
        for i, strategy in enumerate(strategies):
            print(f"\nBacktesting strategy {i+1}/{len(strategies)}: {strategy['name']}")
            
            try:
                # Create backtest parameters
                params = BacktestParams(
                    symbols=[strategy.get('category', 'BTC')],
                    timeframe=strategy.get('timeframe', '4h'),
                    start_date="2024-01-01T00:00:00Z",
                    end_date="2024-10-27T00:00:00Z",
                    initial_capital=10000.0,
                    benchmark="BTC",
                    fees=0.001,
                    slippage=0.001,
                    position_sizing="fixed",
                    exposure=1.0
                )
                
                # Execute strategy with backtesting
                execution_result = await strategy_execution_service.execute_strategy_with_streaming(
                    strategy_id=strategy['id'],
                    strategy_schema=strategy['schema_json'],
                    strategy_name=strategy['name'],
                    params=params.model_dump(),
                    callback=lambda x: asyncio.sleep(0)  # Dummy callback
                )
                
                # Extract metrics from result
                metrics = execution_result.get('metrics', {})
                
                results.append({
                    "strategy_id": strategy['id'],
                    "strategy_name": strategy['name'],
                    "description": strategy['description'],
                    "category": strategy.get('category', 'Unknown'),
                    "metrics": metrics,
                    "execution_result": execution_result
                })
                
                print(f"✅ Backtest complete: Total Return = {metrics.get('total_return', 0):.2f}%")
                
            except Exception as e:
                print(f"❌ Backtest failed for {strategy['name']}: {e}")
                results.append({
                    "strategy_id": strategy['id'],
                    "strategy_name": strategy['name'],
                    "description": strategy['description'],
                    "category": strategy.get('category', 'Unknown'),
                    "metrics": {},
                    "error": str(e)
                })
        
        print(f"\n✅ Completed {len(results)} backtests")
        return results
    
    async def _analyze_and_rank(self, backtest_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze backtest results and rank strategies by performance"""
        print(f"\n📈 Analyzing and ranking {len(backtest_results)} strategies...")
        
        analysis_task = Task(
            description=f"""Analyze the following backtest results and rank strategies by performance.
            
            Backtest Results:
            {json.dumps(backtest_results, indent=2)}
            
            Analyze each strategy based on:
            1. Total Return and CAGR (higher is better)
            2. Sharpe Ratio (risk-adjusted returns, higher is better)
            3. Maximum Drawdown (lower is better)
            4. Win Rate (higher is better)
            5. Number of trades (should be reasonable, not too few or too many)
            6. Consistency and robustness
            
            Calculate a performance score (0-100) for each strategy considering all factors.
            Identify the top 3 strategies with highest probability of continued success.
            
            Return a JSON object with:
            {{
                "rankings": [
                    {{
                        "strategy_id": "...",
                        "strategy_name": "...",
                        "performance_score": 85,
                        "rank": 1,
                        "strengths": ["High Sharpe ratio", "Low drawdown"],
                        "weaknesses": ["Lower total return"],
                        "recommendation": "Excellent risk-adjusted returns"
                    }}
                ],
                "summary": "Overall analysis summary",
                "top_performer": "strategy_id of best strategy"
            }}
            """,
            agent=self.performance_analyzer,
            expected_output="Performance analysis with rankings as JSON"
        )
        
        crew = Crew(
            agents=[self.performance_analyzer],
            tasks=[analysis_task],
            process=Process.sequential,
            verbose=True
        )
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, crew.kickoff)
        
        # Parse result
        try:
            if hasattr(result, 'raw'):
                output = result.raw
            else:
                output = str(result)
            
            # Clean up output
            output = output.strip()
            if output.startswith('```json'):
                output = output[7:]
            if output.startswith('```'):
                output = output[3:]
            if output.endswith('```'):
                output = output[:-3]
            output = output.strip()
            
            analysis = json.loads(output)
            rankings = analysis.get('rankings', [])
            
            # Enhance with original data
            for ranking in rankings:
                strategy_id = ranking.get('strategy_id')
                for result in backtest_results:
                    if result['strategy_id'] == strategy_id:
                        ranking['metrics'] = result.get('metrics', {})
                        ranking['category'] = result.get('category', 'Unknown')
                        ranking['description'] = result.get('description', '')
                        break
            
            print(f"\n✅ Performance analysis complete")
            print(f"Top performer: {analysis.get('top_performer', 'Unknown')}")
            
            return rankings
            
        except Exception as e:
            print(f"❌ Failed to parse analysis: {e}")
            # Fallback: simple ranking by total return
            ranked = sorted(
                backtest_results,
                key=lambda x: x.get('metrics', {}).get('total_return', -999999),
                reverse=True
            )
            return [
                {
                    "strategy_id": r['strategy_id'],
                    "strategy_name": r['strategy_name'],
                    "performance_score": 0,
                    "rank": i + 1,
                    "metrics": r.get('metrics', {}),
                    "category": r.get('category', 'Unknown'),
                    "description": r.get('description', '')
                }
                for i, r in enumerate(ranked)
            ]


# Singleton instance
research_agent_service = ResearchAgent()
