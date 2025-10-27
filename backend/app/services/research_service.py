"""
StrategyResearchService: autonomously generate strategy candidates, persist them,
run backtests, and rank the best performers.
"""

from __future__ import annotations

import json
import itertools
from typing import List, Dict, Any, Tuple
from datetime import datetime

from ..models import (
    Strategy,
    StrategySchema,
    StrategyNode,
    Connection,
    Guardrail,
    StrategyMetrics,
    BacktestParams,
    BacktestRun,
    BacktestMetrics,
    ResearchRequest,
    ResearchCandidateSummary,
    ResearchResult,
)
from ..database import get_database
from .vectorbt_service import vectorbt_service


def _build_strategy_schema_ma(fast: int, slow: int) -> StrategySchema:
    nodes = [
        StrategyNode(id="start", type="start", data={}, position={"x": 0, "y": 0}),
        StrategyNode(id="category", type="category", data={"meta": {"category": "Bitcoin"}}, position={"x": 100, "y": 0}),
        StrategyNode(
            id="entry",
            type="entry_condition",
            data={"meta": {"mode": "manual", "rules": [f"Enter when {fast}-day MA crosses above {slow}-day moving average"]}},
            position={"x": 200, "y": 0},
        ),
        StrategyNode(
            id="profit_target",
            type="take_profit",
            data={"meta": {"target_pct": 7.0}},
            position={"x": 300, "y": 0},
        ),
        StrategyNode(
            id="stop_loss",
            type="stop_loss",
            data={"meta": {"stop_pct": 5.0}},
            position={"x": 400, "y": 0},
        ),
        StrategyNode(id="end", type="end", data={}, position={"x": 500, "y": 0}),
    ]
    connections = [
        Connection(id="c1", source="start", target="category"),
        Connection(id="c2", source="category", target="entry"),
        Connection(id="c3", source="entry", target="profit_target"),
        Connection(id="c4", source="profit_target", target="stop_loss"),
        Connection(id="c5", source="stop_loss", target="end"),
    ]
    return StrategySchema(nodes=nodes, connections=connections)


def _build_strategy_schema_rsi(period: int, buy_level: int, sell_level: int) -> StrategySchema:
    nodes = [
        StrategyNode(id="start", type="start", data={}, position={"x": 0, "y": 0}),
        StrategyNode(id="category", type="category", data={"meta": {"category": "Bitcoin"}}, position={"x": 100, "y": 0}),
        StrategyNode(
            id="entry",
            type="entry_condition",
            data={"meta": {"mode": "manual", "rules": [f"Enter when RSI {period} crosses below {buy_level} and exit above {sell_level}"]}},
            position={"x": 200, "y": 0},
        ),
        StrategyNode(
            id="profit_target",
            type="take_profit",
            data={"meta": {"target_pct": 7.0}},
            position={"x": 300, "y": 0},
        ),
        StrategyNode(
            id="stop_loss",
            type="stop_loss",
            data={"meta": {"stop_pct": 5.0}},
            position={"x": 400, "y": 0},
        ),
        StrategyNode(id="end", type="end", data={}, position={"x": 500, "y": 0}),
    ]
    connections = [
        Connection(id="c1", source="start", target="category"),
        Connection(id="c2", source="category", target="entry"),
        Connection(id="c3", source="entry", target="profit_target"),
        Connection(id="c4", source="profit_target", target="stop_loss"),
        Connection(id="c5", source="stop_loss", target="end"),
    ]
    return StrategySchema(nodes=nodes, connections=connections)


class StrategyResearchService:
    """Generate candidate strategies and backtest them to rank by performance."""

    async def research(self, req: ResearchRequest) -> ResearchResult:
        # Generate candidate parameter grids
        candidates: List[Tuple[str, Dict[str, Any]]] = []

        if "ma" in req.families:
            ma_periods = [(5, 20), (10, 30), (20, 50), (20, 100), (50, 200)]
            for fast, slow in ma_periods[: req.num_candidates]:
                schema = _build_strategy_schema_ma(fast, slow)
                candidates.append((f"MA Crossover {fast}/{slow}", schema))

        if "rsi" in req.families:
            rsi_params = [(14, 30, 70), (10, 25, 75), (21, 35, 65)]
            for period, buy, sell in rsi_params[: max(0, req.num_candidates - len(candidates))]:
                schema = _build_strategy_schema_rsi(period, buy, sell)
                candidates.append((f"RSI {period} < {buy} > {sell}", schema))

        # Backtest each candidate, persist strategy and record score
        results: List[ResearchCandidateSummary] = []
        params = BacktestParams(
            symbols=req.symbols,
            timeframe=req.timeframe,
            start_date=req.start_date,
            end_date=req.end_date,
            initial_capital=req.initial_capital,
            benchmark="BTC",
            fees=req.fees,
            slippage=req.slippage,
            position_sizing="full",
            exposure=1.0,
        )

        pool = None
        try:
            pool = get_database()
        except Exception:
            pool = None

        for name, schema in candidates:
            # Persist strategy first (if DB available)
            strategy_id = None
            if pool:
                try:
                    async with pool.acquire() as conn:
                        row = await conn.fetchrow(
                            """
                            INSERT INTO strategies (user_id, name, description, status, schema_json, guardrails)
                            VALUES ($1, $2, $3, $4, $5, $6)
                            RETURNING id
                            """,
                            req.user_id,
                            name,
                            f"Auto-researched candidate: {name}",
                            "Backtest",
                            json.dumps(schema.model_dump()),
                            json.dumps([Guardrail(type="risk", level="info", message="Auto-generated").model_dump()])
                        )
                        strategy_id = str(row["id"])
                except Exception as e:
                    # Skip persistence if DB error
                    strategy_id = None

            if strategy_id is None:
                strategy_id = f"cand-{name}-{datetime.utcnow().timestamp()}"

            # Run VectorBT backtest using the generated schema
            try:
                backtest: BacktestRun = await vectorbt_service.run_schema_backtest(strategy_id, schema, params)
            except Exception as e:
                # If backtest fails, skip this candidate
                continue

            # Optionally also persist backtest
            backtest_id = None
            if pool and backtest is not None:
                try:
                    async with pool.acquire() as conn:
                        row = await conn.fetchrow(
                            """
                            INSERT INTO backtests (strategy_id, params, metrics, equity_series, drawdown_series, monthly_returns, trades)
                            VALUES ($1, $2, $3, $4, $5, $6, $7)
                            RETURNING id
                            """,
                            backtest.strategy_id,
                            json.dumps(backtest.params.model_dump()),
                            json.dumps(backtest.metrics.model_dump()),
                            json.dumps([e.model_dump() for e in backtest.equity_series]),
                            json.dumps(backtest.drawdown_series),
                            json.dumps(backtest.monthly_returns),
                            json.dumps([t.model_dump() for t in backtest.trades])
                        )
                        backtest_id = str(row["id"])
                except Exception:
                    backtest_id = None

            # Define a score prioritizing high total_return, penalizing drawdown, rewarding Sharpe
            m: BacktestMetrics = backtest.metrics
            score = float(m.total_return) - 0.5 * float(m.max_drawdown) + 10.0 * float(m.sharpe_ratio)

            results.append(
                ResearchCandidateSummary(
                    strategy_id=strategy_id,
                    backtest_id=backtest_id,
                    strategy_name=name,
                    metrics=m,
                    score=round(score, 4),
                )
            )

        # Rank
        results.sort(key=lambda r: r.score, reverse=True)
        top = results[: req.top_n]

        return ResearchResult(top_candidates=top, all_candidates=results)


# Singleton
research_service = StrategyResearchService()
