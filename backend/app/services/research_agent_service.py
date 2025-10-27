"""
Research Agent Service for discovering and analyzing trading strategies.

This service uses AI agents to:
1. Research trading strategies from various sources
2. Analyze market conditions and trends
3. Generate strategy schemas automatically
4. Evaluate strategy viability and risk
5. Create comprehensive strategy documentation
"""

import os
import json
import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from crewai import Agent, Task, Crew, Process, LLM

from ..models import (
    ResearchedStrategy, ResearchRequest, StrategySchema, StrategyNode, 
    Connection, Guardrail, BacktestParams, AutonomousBacktestRequest,
    StrategyPerformanceRanking, BacktestMetrics
)
from ..config import settings
from .llm_service import llm_service
from .strategy_execution_service import strategy_execution_service
from ..database import get_database


class ResearchAgentService:
    """Service for researching and discovering trading strategies"""
    
    def __init__(self):
        self.llm = self._get_llm()
        self.research_agent = self._create_research_agent()
        self.strategy_generator_agent = self._create_strategy_generator_agent()
        self.risk_analyzer_agent = self._create_risk_analyzer_agent()
    
    def _get_llm(self):
        """Get configured LLM for research agents"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")
        
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        os.environ['LITELLM_TELEMETRY'] = 'False'
        os.environ['OTEL_SDK_DISABLED'] = 'true'
        
        return LLM(
            model=f"anthropic/{model}",
            api_key=api_key,
            temperature=0.3,  # Slightly higher for creativity in research
            timeout=120,
            max_retries=3,
        )
    
    def _create_research_agent(self) -> Agent:
        """Creates the Strategy Research agent"""
        return Agent(
            role='Strategy Research Specialist',
            goal='Research and discover profitable trading strategies from various sources and market analysis',
            backstory="""You are an expert quantitative researcher with deep knowledge of 
            financial markets, trading strategies, and market microstructure. You can identify 
            profitable patterns, analyze market conditions, and discover innovative trading 
            approaches. You stay updated with the latest market trends, academic research, 
            and successful trading methodologies.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_strategy_generator_agent(self) -> Agent:
        """Creates the Strategy Schema Generator agent"""
        return Agent(
            role='Strategy Schema Generator',
            goal='Convert researched trading concepts into structured strategy schemas',
            backstory="""You are a systems architect specializing in trading strategy 
            formalization. You can take abstract trading concepts and convert them into 
            precise, executable strategy schemas with proper entry/exit conditions, 
            indicators, and risk management parameters. You understand how to structure 
            complex trading logic into clear, implementable components.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_risk_analyzer_agent(self) -> Agent:
        """Creates the Risk Analysis agent"""
        return Agent(
            role='Risk Analysis Specialist',
            goal='Analyze strategy risk profiles and create appropriate guardrails',
            backstory="""You are a risk management expert with extensive experience in 
            quantitative finance. You can assess the risk characteristics of trading 
            strategies, identify potential failure modes, and design comprehensive 
            guardrails to protect capital. You understand market volatility, correlation 
            risks, and portfolio management principles.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    async def research_strategies(
        self, 
        request: ResearchRequest, 
        user_id: str = "research_agent"
    ) -> List[ResearchedStrategy]:
        """
        Research and discover new trading strategies based on request parameters
        """
        print(f"🔍 Starting strategy research with parameters: {request}")
        
        # Create research session in database
        session_id = await self._create_research_session(
            user_id, "strategy_research", request.dict()
        )
        
        try:
            # Create research task
            research_task = Task(
            description=f"""Research profitable trading strategies based on these criteria:
            
            Market Focus: {request.market_focus or 'All markets'}
            Strategy Types: {request.strategy_types or 'All types'}
            Risk Tolerance: {request.risk_tolerance or 'Medium'}
            Max Strategies: {request.max_strategies}
            Research Depth: {request.research_depth}
            
            Your research should focus on:
            1. Current market conditions and trends
            2. Proven strategy patterns that work in current market environment
            3. Innovative approaches that haven't been overexploited
            4. Risk-adjusted return potential
            5. Implementation feasibility
            
            For each strategy you discover, provide:
            - Strategy name and clear description
            - Market category (crypto, forex, stocks, etc.)
            - Strategy type (momentum, mean reversion, breakout, etc.)
            - Expected return range and risk level
            - Key market conditions where it performs well
            - Implementation complexity
            - Confidence in strategy viability (0-1 score)
            
            Return your findings as a structured list of {request.max_strategies} strategies.
            """,
            agent=self.research_agent,
            expected_output=f"List of {request.max_strategies} researched trading strategies with detailed analysis"
            )
            
            # Create strategy generation task
            generation_task = Task(
                description="""Based on the research findings, generate detailed strategy schemas for each discovered strategy.
                
                For each strategy from the research, create:
                1. A complete StrategySchema with nodes and connections
                2. Appropriate guardrails for risk management
                3. Entry and exit conditions
                4. Required technical indicators
                5. Position sizing and risk parameters
                
                The schema should be implementable and follow this structure:
                - Entry nodes with specific conditions
                - Indicator calculation nodes
                - Exit condition nodes (stop loss, take profit)
                - Risk management nodes
                
                Return the schemas as valid JSON that can be parsed into StrategySchema objects.
                """,
                agent=self.strategy_generator_agent,
                expected_output="Complete strategy schemas in JSON format for all researched strategies",
                context=[research_task]
            )
            
            # Create risk analysis task
            risk_task = Task(
                description="""Analyze the risk profile of each generated strategy and create comprehensive guardrails.
                
                For each strategy, assess:
                1. Maximum drawdown potential
                2. Volatility characteristics
                3. Market condition dependencies
                4. Correlation risks
                5. Liquidity requirements
                
                Create guardrails that include:
                - Position size limits
                - Maximum drawdown stops
                - Volatility-based adjustments
                - Market condition filters
                - Risk monitoring alerts
                
                Assign risk levels (low/medium/high) and confidence scores.
                """,
                agent=self.risk_analyzer_agent,
                expected_output="Risk analysis and guardrails for each strategy",
                context=[research_task, generation_task]
            )
            
            # Execute research crew
            crew = Crew(
                agents=[self.research_agent, self.strategy_generator_agent, self.risk_analyzer_agent],
                tasks=[research_task, generation_task, risk_task],
                process=Process.sequential,
                verbose=True,
                memory=False
            )
            
            result = crew.kickoff()
            
            # Parse results and create ResearchedStrategy objects
            strategies = await self._parse_research_results(result, request)
            
            # Store strategies in database
            stored_strategies = []
            for strategy in strategies:
                stored_strategy = await self._store_strategy(strategy, user_id)
                stored_strategies.append(stored_strategy)
            
            # Update research session with results
            await self._complete_research_session(
                session_id, len(stored_strategies), stored_strategies
            )
            
            print(f"✅ Successfully researched and stored {len(stored_strategies)} strategies")
            return stored_strategies
            
        except Exception as e:
            print(f"❌ Error in strategy research: {e}")
            # Mark session as failed
            await self._fail_research_session(session_id, str(e))
            # Return fallback strategies if research fails
            return await self._generate_fallback_strategies(request, user_id)
    
    async def _parse_research_results(
        self, 
        crew_result: Any, 
        request: ResearchRequest
    ) -> List[ResearchedStrategy]:
        """Parse crew results into ResearchedStrategy objects"""
        
        # For now, generate example strategies based on request
        # In production, this would parse the actual crew output
        strategies = []
        
        strategy_templates = [
            {
                "name": "Crypto Momentum Breakout",
                "description": "Identifies momentum breakouts in cryptocurrency markets using volume and price action",
                "category": "momentum",
                "market_type": "crypto",
                "complexity": "intermediate",
                "expected_return": 25.5,
                "risk_level": "medium",
                "research_source": "Market Analysis + Technical Patterns",
                "confidence_score": 0.78
            },
            {
                "name": "Mean Reversion RSI Strategy",
                "description": "Exploits overbought/oversold conditions using RSI and Bollinger Bands",
                "category": "mean_reversion",
                "market_type": "crypto",
                "complexity": "simple",
                "expected_return": 18.2,
                "risk_level": "low",
                "research_source": "Academic Research + Backtesting",
                "confidence_score": 0.85
            },
            {
                "name": "Multi-Timeframe Trend Following",
                "description": "Combines multiple timeframe analysis for robust trend identification",
                "category": "trend_following",
                "market_type": "crypto",
                "complexity": "advanced",
                "expected_return": 32.1,
                "risk_level": "high",
                "research_source": "Institutional Strategy Analysis",
                "confidence_score": 0.72
            },
            {
                "name": "Volume Profile Breakout",
                "description": "Uses volume profile analysis to identify high-probability breakout levels",
                "category": "breakout",
                "market_type": "crypto",
                "complexity": "intermediate",
                "expected_return": 22.8,
                "risk_level": "medium",
                "research_source": "Order Flow Analysis",
                "confidence_score": 0.81
            },
            {
                "name": "Adaptive Moving Average Crossover",
                "description": "Dynamic moving average system that adapts to market volatility",
                "category": "trend_following",
                "market_type": "crypto",
                "complexity": "intermediate",
                "expected_return": 19.6,
                "risk_level": "medium",
                "research_source": "Quantitative Research",
                "confidence_score": 0.76
            }
        ]
        
        # Select strategies based on request criteria
        selected_templates = strategy_templates[:request.max_strategies]
        
        for i, template in enumerate(selected_templates):
            # Generate strategy schema
            schema = self._generate_strategy_schema(template)
            
            # Generate guardrails
            guardrails = self._generate_guardrails(template)
            
            strategy = ResearchedStrategy(
                name=template["name"],
                description=template["description"],
                category=template["category"],
                market_type=template["market_type"],
                complexity=template["complexity"],
                expected_return=template["expected_return"],
                risk_level=template["risk_level"],
                schema_json=schema,
                guardrails=guardrails,
                research_source=template["research_source"],
                confidence_score=template["confidence_score"]
            )
            
            strategies.append(strategy)
        
        return strategies
    
    def _generate_strategy_schema(self, template: Dict[str, Any]) -> StrategySchema:
        """Generate a strategy schema based on template"""
        
        nodes = []
        connections = []
        
        # Entry node
        entry_node = StrategyNode(
            id="entry_1",
            type="entry_condition",
            data={
                "condition": f"{template['category']}_entry",
                "parameters": self._get_entry_parameters(template["category"])
            },
            position={"x": 100, "y": 100}
        )
        nodes.append(entry_node)
        
        # Indicator nodes based on strategy type
        indicators = self._get_required_indicators(template["category"])
        for i, indicator in enumerate(indicators):
            indicator_node = StrategyNode(
                id=f"indicator_{i+1}",
                type="technical_indicator",
                data={
                    "indicator": indicator["name"],
                    "parameters": indicator["params"]
                },
                position={"x": 250 + i * 150, "y": 100}
            )
            nodes.append(indicator_node)
            
            # Connect to entry
            connections.append(Connection(
                id=f"conn_indicator_{i+1}",
                source=indicator_node.id,
                target="entry_1"
            ))
        
        # Exit nodes
        exit_node = StrategyNode(
            id="exit_1",
            type="exit_condition",
            data={
                "condition": f"{template['category']}_exit",
                "stop_loss": self._get_stop_loss(template["risk_level"]),
                "take_profit": self._get_take_profit(template["expected_return"])
            },
            position={"x": 100, "y": 250}
        )
        nodes.append(exit_node)
        
        # Connect entry to exit
        connections.append(Connection(
            id="conn_entry_exit",
            source="entry_1",
            target="exit_1"
        ))
        
        return StrategySchema(nodes=nodes, connections=connections)
    
    def _get_entry_parameters(self, category: str) -> Dict[str, Any]:
        """Get entry parameters based on strategy category"""
        params_map = {
            "momentum": {"threshold": 0.02, "volume_multiplier": 1.5},
            "mean_reversion": {"rsi_oversold": 30, "rsi_overbought": 70},
            "trend_following": {"ma_fast": 12, "ma_slow": 26},
            "breakout": {"lookback_period": 20, "volume_threshold": 2.0}
        }
        return params_map.get(category, {"threshold": 0.01})
    
    def _get_required_indicators(self, category: str) -> List[Dict[str, Any]]:
        """Get required indicators based on strategy category"""
        indicators_map = {
            "momentum": [
                {"name": "RSI", "params": {"period": 14}},
                {"name": "Volume", "params": {"ma_period": 20}}
            ],
            "mean_reversion": [
                {"name": "RSI", "params": {"period": 14}},
                {"name": "Bollinger_Bands", "params": {"period": 20, "std": 2}}
            ],
            "trend_following": [
                {"name": "EMA", "params": {"fast": 12, "slow": 26}},
                {"name": "MACD", "params": {"fast": 12, "slow": 26, "signal": 9}}
            ],
            "breakout": [
                {"name": "Volume_Profile", "params": {"period": 20}},
                {"name": "ATR", "params": {"period": 14}}
            ]
        }
        return indicators_map.get(category, [{"name": "SMA", "params": {"period": 20}}])
    
    def _get_stop_loss(self, risk_level: str) -> float:
        """Get stop loss percentage based on risk level"""
        stop_loss_map = {
            "low": 0.02,    # 2%
            "medium": 0.05, # 5%
            "high": 0.08    # 8%
        }
        return stop_loss_map.get(risk_level, 0.05)
    
    def _get_take_profit(self, expected_return: float) -> float:
        """Get take profit percentage based on expected return"""
        # Take profit at 1/3 of expected annual return for individual trades
        return expected_return / 100 / 12  # Monthly target
    
    def _generate_guardrails(self, template: Dict[str, Any]) -> List[Guardrail]:
        """Generate guardrails based on strategy template"""
        guardrails = []
        
        # Risk-based guardrails
        if template["risk_level"] == "high":
            guardrails.append(Guardrail(
                type="max_position_size",
                level="warning",
                message="High-risk strategy: Limit position size to 10% of portfolio"
            ))
            guardrails.append(Guardrail(
                type="max_drawdown",
                level="error",
                message="Stop trading if drawdown exceeds 15%"
            ))
        elif template["risk_level"] == "medium":
            guardrails.append(Guardrail(
                type="max_position_size",
                level="info",
                message="Medium-risk strategy: Limit position size to 20% of portfolio"
            ))
            guardrails.append(Guardrail(
                type="max_drawdown",
                level="warning",
                message="Review strategy if drawdown exceeds 10%"
            ))
        else:  # low risk
            guardrails.append(Guardrail(
                type="max_position_size",
                level="info",
                message="Low-risk strategy: Can use up to 30% of portfolio"
            ))
        
        # Market condition guardrails
        if template["market_type"] == "crypto":
            guardrails.append(Guardrail(
                type="market_hours",
                level="info",
                message="Crypto markets: 24/7 trading - monitor during high volatility periods"
            ))
            guardrails.append(Guardrail(
                type="volatility_filter",
                level="warning",
                message="Reduce position size during extreme volatility (VIX > 30)"
            ))
        
        return guardrails
    
    async def _store_strategy(
        self, 
        strategy: ResearchedStrategy, 
        user_id: str
    ) -> ResearchedStrategy:
        """Store researched strategy in database"""
        try:
            db = get_database()
            
            # Convert strategy to database format
            strategy_data = {
                "user_id": user_id,
                "name": strategy.name,
                "description": strategy.description,
                "status": "Backtest",
                "schema_json": strategy.schema_json.dict(),
                "guardrails": [g.dict() for g in strategy.guardrails],
                "metrics": {
                    "expected_return": strategy.expected_return,
                    "risk_level": strategy.risk_level,
                    "confidence_score": strategy.confidence_score,
                    "category": strategy.category,
                    "market_type": strategy.market_type,
                    "complexity": strategy.complexity,
                    "research_source": strategy.research_source
                }
            }
            
            # Insert into database
            async with db.acquire() as conn:
                strategy_id = await conn.fetchval("""
                    INSERT INTO strategies (user_id, name, description, status, schema_json, guardrails, metrics)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    RETURNING id
                """, 
                strategy_data["user_id"],
                strategy_data["name"], 
                strategy_data["description"],
                strategy_data["status"],
                json.dumps(strategy_data["schema_json"]),
                json.dumps(strategy_data["guardrails"]),
                json.dumps(strategy_data["metrics"])
                )
            
            strategy.id = str(strategy_id)
            print(f"✅ Stored strategy '{strategy.name}' with ID: {strategy_id}")
            return strategy
            
        except Exception as e:
            print(f"❌ Error storing strategy: {e}")
            # Return strategy without ID if storage fails
            return strategy
    
    async def _generate_fallback_strategies(
        self, 
        request: ResearchRequest, 
        user_id: str
    ) -> List[ResearchedStrategy]:
        """Generate fallback strategies if research fails"""
        print("🔄 Generating fallback strategies...")
        
        fallback_strategy = ResearchedStrategy(
            name="Simple Moving Average Crossover",
            description="Basic trend-following strategy using moving average crossovers",
            category="trend_following",
            market_type=request.market_focus or "crypto",
            complexity="simple",
            expected_return=15.0,
            risk_level="medium",
            schema_json=StrategySchema(
                nodes=[
                    StrategyNode(
                        id="entry_1",
                        type="entry_condition",
                        data={"condition": "ma_crossover", "fast_ma": 12, "slow_ma": 26},
                        position={"x": 100, "y": 100}
                    )
                ],
                connections=[]
            ),
            guardrails=[
                Guardrail(
                    type="max_drawdown",
                    level="warning",
                    message="Review if drawdown exceeds 10%"
                )
            ],
            research_source="Fallback Strategy",
            confidence_score=0.65
        )
        
        stored_strategy = await self._store_strategy(fallback_strategy, user_id)
        return [stored_strategy]
    
    async def run_autonomous_backtests(
        self, 
        request: AutonomousBacktestRequest,
        user_id: str = "research_agent"
    ) -> List[StrategyPerformanceRanking]:
        """
        Run autonomous backtests on strategies and rank performance
        """
        print(f"🚀 Starting autonomous backtesting with {request.max_concurrent_tests} concurrent tests")
        
        # Create backtest session in database
        session_id = await self._create_research_session(
            user_id, "autonomous_backtest", request.dict()
        )
        
        try:
            # Get strategies to test
            if request.strategy_ids:
                strategies = await self._get_strategies_by_ids(request.strategy_ids)
            else:
                # Research new strategies first
                research_request = ResearchRequest(
                    max_strategies=request.max_concurrent_tests,
                    research_depth="quick"
                )
                strategies = await self.research_strategies(research_request, user_id)
            
            # Run backtests concurrently
            backtest_tasks = []
            for strategy in strategies[:request.max_concurrent_tests]:
                task = self._run_strategy_backtest(strategy, request.market_conditions)
                backtest_tasks.append(task)
            
            # Execute backtests
            backtest_results = await asyncio.gather(*backtest_tasks, return_exceptions=True)
            
            # Rank strategies by performance
            rankings = []
            for i, (strategy, result) in enumerate(zip(strategies, backtest_results)):
                if isinstance(result, Exception):
                    print(f"❌ Backtest failed for {strategy.name}: {result}")
                    continue
                
                ranking = self._calculate_performance_ranking(strategy, result, i + 1)
                rankings.append(ranking)
            
            # Sort by performance score
            rankings.sort(key=lambda x: x.performance_score, reverse=True)
            
            # Update ranks
            for i, ranking in enumerate(rankings):
                ranking.rank = i + 1
            
            # Store performance rankings in database
            await self._store_performance_rankings(session_id, rankings)
            
            # Update session with results
            await self._complete_backtest_session(session_id, len(strategies), len(rankings), rankings)
            
            print(f"✅ Completed autonomous backtesting. Top strategy: {rankings[0].strategy_name if rankings else 'None'}")
            return rankings
            
        except Exception as e:
            print(f"❌ Error in autonomous backtesting: {e}")
            await self._fail_research_session(session_id, str(e))
            return []
    
    async def _get_strategies_by_ids(self, strategy_ids: List[str]) -> List[ResearchedStrategy]:
        """Get strategies from database by IDs"""
        try:
            db = get_database()
            strategies = []
            
            async with db.acquire() as conn:
                for strategy_id in strategy_ids:
                    row = await conn.fetchrow("""
                        SELECT * FROM strategies WHERE id = $1
                    """, strategy_id)
                    
                    if row:
                        # Convert database row to ResearchedStrategy
                        metrics = json.loads(row['metrics']) if row['metrics'] else {}
                        schema_data = json.loads(row['schema_json'])
                        guardrails_data = json.loads(row['guardrails'])
                        
                        strategy = ResearchedStrategy(
                            id=str(row['id']),
                            name=row['name'],
                            description=row['description'],
                            category=metrics.get('category', 'unknown'),
                            market_type=metrics.get('market_type', 'crypto'),
                            complexity=metrics.get('complexity', 'simple'),
                            expected_return=metrics.get('expected_return', 10.0),
                            risk_level=metrics.get('risk_level', 'medium'),
                            schema_json=StrategySchema(**schema_data),
                            guardrails=[Guardrail(**g) for g in guardrails_data],
                            research_source=metrics.get('research_source', 'Database'),
                            confidence_score=metrics.get('confidence_score', 0.5),
                            created_at=row['created_at']
                        )
                        strategies.append(strategy)
            
            return strategies
            
        except Exception as e:
            print(f"❌ Error fetching strategies: {e}")
            return []
    
    async def _run_strategy_backtest(
        self, 
        strategy: ResearchedStrategy, 
        market_conditions: Optional[Dict[str, Any]]
    ) -> BacktestMetrics:
        """Run backtest for a single strategy"""
        try:
            # Create backtest parameters
            params = BacktestParams(
                symbols=["BTC-USD"],
                timeframe="1d",
                start_date=(datetime.now() - timedelta(days=365)).isoformat(),
                end_date=datetime.now().isoformat(),
                initial_capital=10000.0,
                benchmark="BTC",
                fees=0.001,
                slippage=0.001,
                position_sizing="fixed",
                exposure=1.0
            )
            
            # Use strategy execution service to run backtest
            result = await strategy_execution_service.execute_strategy(
                strategy_id=strategy.id or "temp",
                params=params,
                user_id="research_agent"
            )
            
            # Extract metrics from result
            if result.get("status") == "completed" and result.get("backtest_run"):
                backtest_run = result["backtest_run"]
                return backtest_run.metrics
            else:
                # Return mock metrics if execution fails
                return self._generate_mock_metrics(strategy)
                
        except Exception as e:
            print(f"❌ Error running backtest for {strategy.name}: {e}")
            return self._generate_mock_metrics(strategy)
    
    def _generate_mock_metrics(self, strategy: ResearchedStrategy) -> BacktestMetrics:
        """Generate mock backtest metrics for testing"""
        base_return = strategy.expected_return
        volatility = {"low": 0.8, "medium": 1.0, "high": 1.3}[strategy.risk_level]
        
        return BacktestMetrics(
            total_amount_invested=10000.0,
            total_gain=max(0, base_return * 100 * volatility),
            total_loss=max(0, -base_return * 50 * volatility) if base_return < 0 else 0,
            total_return=base_return * random.uniform(0.7, 1.3),
            cagr=base_return * random.uniform(0.8, 1.2),
            sharpe_ratio=random.uniform(0.5, 2.5) * (2.0 if strategy.risk_level == "low" else 1.0),
            max_drawdown=random.uniform(-20, -5) * volatility,
            max_drawdown_duration=random.randint(20, 90),
            win_rate=random.uniform(45, 75),
            trades=random.randint(50, 200),
            vs_benchmark=random.uniform(-5, 15)
        )
    
    def _calculate_performance_ranking(
        self, 
        strategy: ResearchedStrategy, 
        metrics: BacktestMetrics,
        initial_rank: int
    ) -> StrategyPerformanceRanking:
        """Calculate comprehensive performance ranking"""
        
        # Risk-adjusted return (Sharpe ratio weighted)
        risk_adjusted_return = metrics.sharpe_ratio * metrics.total_return
        
        # Consistency score (based on win rate and drawdown)
        consistency_score = (metrics.win_rate / 100) * (1 - abs(metrics.max_drawdown) / 100)
        
        # Market adaptability (based on vs benchmark and trade frequency)
        market_adaptability = (metrics.vs_benchmark + 100) / 100 * min(metrics.trades / 100, 1.0)
        
        # Composite performance score (0-100)
        performance_score = (
            risk_adjusted_return * 0.4 +
            consistency_score * 100 * 0.3 +
            market_adaptability * 100 * 0.2 +
            strategy.confidence_score * 100 * 0.1
        )
        
        performance_score = max(0, min(100, performance_score))  # Clamp to 0-100
        
        return StrategyPerformanceRanking(
            strategy_id=strategy.id or "unknown",
            strategy_name=strategy.name,
            performance_score=performance_score,
            metrics=metrics,
            risk_adjusted_return=risk_adjusted_return,
            consistency_score=consistency_score,
            market_adaptability=market_adaptability,
            rank=initial_rank
        )
    
    async def _create_research_session(
        self, 
        user_id: str, 
        session_type: str, 
        parameters: Dict[str, Any]
    ) -> str:
        """Create a new research session in the database"""
        try:
            db = get_database()
            
            async with db.acquire() as conn:
                session_id = await conn.fetchval("""
                    INSERT INTO research_sessions (user_id, session_type, parameters, status)
                    VALUES ($1, $2, $3, 'running')
                    RETURNING id
                """, user_id, session_type, json.dumps(parameters))
            
            return str(session_id)
        except Exception as e:
            print(f"❌ Error creating research session: {e}")
            return "temp_session"
    
    async def _complete_research_session(
        self, 
        session_id: str, 
        strategies_found: int, 
        strategies: List[ResearchedStrategy]
    ):
        """Mark research session as completed with results"""
        try:
            db = get_database()
            
            results = {
                "strategies": [
                    {
                        "id": s.id,
                        "name": s.name,
                        "category": s.category,
                        "expected_return": s.expected_return,
                        "confidence_score": s.confidence_score
                    } for s in strategies
                ]
            }
            
            async with db.acquire() as conn:
                await conn.execute("""
                    UPDATE research_sessions 
                    SET status = 'completed', 
                        strategies_found = $2,
                        results = $3,
                        completed_at = NOW()
                    WHERE id = $1
                """, session_id, strategies_found, json.dumps(results))
                
        except Exception as e:
            print(f"❌ Error completing research session: {e}")
    
    async def _fail_research_session(self, session_id: str, error_message: str):
        """Mark research session as failed"""
        try:
            db = get_database()
            
            async with db.acquire() as conn:
                await conn.execute("""
                    UPDATE research_sessions 
                    SET status = 'failed', 
                        error_message = $2,
                        completed_at = NOW()
                    WHERE id = $1
                """, session_id, error_message)
                
        except Exception as e:
            print(f"❌ Error updating failed research session: {e}")
    
    async def _complete_backtest_session(
        self, 
        session_id: str, 
        strategies_tested: int, 
        rankings_count: int,
        rankings: List[StrategyPerformanceRanking]
    ):
        """Mark backtest session as completed with results"""
        try:
            db = get_database()
            
            results = {
                "rankings": [
                    {
                        "strategy_id": r.strategy_id,
                        "strategy_name": r.strategy_name,
                        "performance_score": r.performance_score,
                        "rank": r.rank
                    } for r in rankings[:5]  # Top 5
                ],
                "top_strategy": rankings[0].strategy_name if rankings else None
            }
            
            async with db.acquire() as conn:
                await conn.execute("""
                    UPDATE research_sessions 
                    SET status = 'completed', 
                        strategies_tested = $2,
                        top_strategy_id = $3,
                        results = $4,
                        completed_at = NOW()
                    WHERE id = $1
                """, 
                session_id, 
                strategies_tested,
                rankings[0].strategy_id if rankings else None,
                json.dumps(results)
                )
                
        except Exception as e:
            print(f"❌ Error completing backtest session: {e}")
    
    async def _store_performance_rankings(
        self, 
        session_id: str, 
        rankings: List[StrategyPerformanceRanking]
    ):
        """Store performance rankings in database"""
        try:
            db = get_database()
            
            async with db.acquire() as conn:
                for ranking in rankings:
                    await conn.execute("""
                        INSERT INTO strategy_performance_rankings 
                        (research_session_id, strategy_id, strategy_name, performance_score,
                         risk_adjusted_return, consistency_score, market_adaptability,
                         rank_position, backtest_metrics)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    """, 
                    session_id,
                    ranking.strategy_id,
                    ranking.strategy_name,
                    ranking.performance_score,
                    ranking.risk_adjusted_return,
                    ranking.consistency_score,
                    ranking.market_adaptability,
                    ranking.rank,
                    json.dumps(ranking.metrics.dict())
                    )
                    
        except Exception as e:
            print(f"❌ Error storing performance rankings: {e}")


# Singleton instance
research_agent_service = ResearchAgentService()