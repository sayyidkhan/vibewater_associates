"""
Test script for VectorBT integration
Run this to verify – is working correctly
"""

import asyncio
from app.services.vectorbt_service import vectorbt_service
from app.models import BacktestParams

async def test_bitcoin_backtest():
    print("=" * 60)
    print("Testing VectorBT Bitcoin Backtest")
    print("=" * 60)
    print()
    
    # Create test parameters (using past 3 months for free API compatibility)
    from datetime import datetime, timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)  # 3 months ago
    
    params = BacktestParams(
        symbols=["BTC"],
        timeframe="1D",
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        initial_capital=10000,
        benchmark="USD",
        fees=0.001,
        slippage=0.0005,
        position_sizing="fixed",
        exposure=1.0
    )
    
    print("Test Parameters:")
    print(f"  Symbol: BTC-USD")
    print(f"  Period: {params.start_date} to {params.end_date}")
    print(f"  Initial Capital: ${params.initial_capital:,.2f}")
    print(f"  Fees: {params.fees * 100}%")
    print(f"  Slippage: {params.slippage * 100}%")
    print()
    
    try:
        # Run backtest
        print("Running backtest...")
        result = await vectorbt_service.run_bitcoin_backtest("test-1", params)
        
        print()
        print("=" * 60)
        print("BACKTEST RESULTS")
        print("=" * 60)
        print()
        
        # Display metrics
        metrics = result.metrics
        print("Performance Metrics:")
        print(f"  Total Return:     {metrics.total_return:>10.2f}%")
        print(f"  CAGR:             {metrics.cagr:>10.2f}%")
        print(f"  Sharpe Ratio:     {metrics.sharpe_ratio:>10.2f}")
        print(f"  Max Drawdown:     {metrics.max_drawdown:>10.2f}%")
        print(f"  Win Rate:         {metrics.win_rate:>10.1f}%")
        print(f"  Total Trades:     {metrics.trades:>10}")
        print(f"  vs Benchmark:     {metrics.vs_benchmark:>10.2f}%")
        print()
        
        print("Financial Summary:")
        print(f"  Initial Capital:  ${metrics.total_amount_invested:>10,.2f}")
        print(f"  Total Gains:      ${metrics.total_gain:>10,.2f}")
        print(f"  Total Losses:     ${metrics.total_loss:>10,.2f}")
        print(f"  Final Value:      ${metrics.total_amount_invested + metrics.total_gain - metrics.total_loss:>10,.2f}")
        print()
        
        # Display equity curve sample
        print("Equity Curve (first 5 points):")
        for point in result.equity_series[:5]:
            print(f"  {point.date}: ${point.value:,.2f} (Benchmark: ${point.benchmark:,.2f})")
        print(f"  ... ({len(result.equity_series)} total points)")
        print()
        
        # Display trades
        print(f"Recent Trades ({len(result.trades)} total):")
        for trade in result.trades[:5]:
            return_str = f" ({trade.return_pct:+.2f}%)" if trade.return_pct else ""
            print(f"  {trade.date} - {trade.type:4} {trade.quantity:.6f} BTC @ ${trade.price:,.2f}{return_str}")
        print()
        
        print("=" * 60)
        print("✅ TEST PASSED - VectorBT is working correctly!")
        print("=" * 60)
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ TEST FAILED")
        print("=" * 60)
        print(f"Error: {str(e)}")
        print()
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_bitcoin_backtest())
