import random
from datetime import datetime, timedelta
from typing import List
from ..models import BacktestRun, BacktestParams, BacktestMetrics, EquityPoint, Trade

class BacktestService:
    """Service for running backtests on trading strategies"""
    
    async def run_backtest(self, strategy_id: str, params: BacktestParams) -> BacktestRun:
        """
        Run a backtest simulation.
        In production, this would use historical data and execute the strategy logic.
        For now, returns mock backtest results.
        """
        
        # Generate mock equity curve
        equity_series = self._generate_equity_curve(
            params.initial_capital,
            params.start_date,
            params.end_date
        )
        
        # Generate mock trades
        trades = self._generate_trades(params.symbols[0] if params.symbols else "BTC")
        
        # Calculate metrics
        final_value = equity_series[-1].value
        total_return = ((final_value - params.initial_capital) / params.initial_capital) * 100
        
        metrics = BacktestMetrics(
            total_amount_invested=params.initial_capital,
            total_gain=max(0, final_value - params.initial_capital),
            total_loss=max(0, params.initial_capital - final_value) if final_value < params.initial_capital else 0,
            total_return=total_return,
            cagr=self._calculate_cagr(params.initial_capital, final_value, 1),
            sharpe_ratio=round(random.uniform(0.5, 2.5), 1),
            max_drawdown=round(random.uniform(-15, -3), 1),
            max_drawdown_duration=random.randint(20, 60),
            win_rate=random.randint(50, 75),
            trades=len(trades),
            vs_benchmark=round(random.uniform(-2, 8), 1)
        )
        
        backtest_run = BacktestRun(
            id=f"bt-{datetime.utcnow().timestamp()}",
            strategy_id=strategy_id,
            params=params,
            metrics=metrics,
            equity_series=equity_series,
            drawdown_series=[],
            monthly_returns=[],
            trades=trades,
            created_at=datetime.utcnow()
        )
        
        return backtest_run
    
    def _generate_equity_curve(self, initial_capital: float, start_date: str, end_date: str) -> List[EquityPoint]:
        """Generate mock equity curve data"""
        points = []
        current_value = initial_capital
        benchmark_value = initial_capital
        
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        days = (end - start).days
        num_points = min(days, 100)  # Max 100 points
        
        for i in range(num_points):
            date = start + timedelta(days=i * (days / num_points))
            
            # Random walk with slight upward bias
            change = random.uniform(-0.03, 0.04)
            current_value *= (1 + change)
            
            benchmark_change = random.uniform(-0.02, 0.03)
            benchmark_value *= (1 + benchmark_change)
            
            points.append(EquityPoint(
                date=date.strftime("%Y-%m-%d"),
                value=round(current_value, 2),
                benchmark=round(benchmark_value, 2)
            ))
        
        return points
    
    def _generate_trades(self, symbol: str) -> List[Trade]:
        """Generate mock trade history"""
        trades = []
        num_trades = random.randint(50, 150)
        
        for i in range(num_trades):
            trade_type = "BUY" if i % 2 == 0 else "SELL"
            price = random.uniform(30000, 70000)
            quantity = random.uniform(0.01, 0.5)
            
            trade = Trade(
                id=f"trade-{i}",
                date=(datetime.utcnow() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d"),
                type=trade_type,
                symbol=symbol,
                price=round(price, 2),
                quantity=round(quantity, 4),
                amount=round(price * quantity, 2),
                return_pct=round(random.uniform(-10, 20), 1) if trade_type == "SELL" else None
            )
            trades.append(trade)
        
        # Sort by date
        trades.sort(key=lambda x: x.date, reverse=True)
        return trades[:10]  # Return only recent 10
    
    def _calculate_cagr(self, initial: float, final: float, years: float) -> float:
        """Calculate Compound Annual Growth Rate"""
        if years <= 0 or initial <= 0:
            return 0.0
        return round(((final / initial) ** (1 / years) - 1) * 100, 1)

backtest_service = BacktestService()
