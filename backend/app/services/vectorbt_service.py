import vectorbt as vbt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pycoingecko import CoinGeckoAPI
from ..models import BacktestRun, BacktestParams, BacktestMetrics, EquityPoint, Trade
from ..config import settings

class VectorBTBacktestService:
    """Service for running backtests using VectorBT library"""
    
    async def run_bitcoin_backtest(self, strategy_id: str, params: BacktestParams) -> BacktestRun:
        """
        Run a backtest for Bitcoin using VectorBT with moving average crossover strategy.
        This implements the first strategy: "Buy low, sell high" using MA crossover.
        """
        
        try:
            # Download Bitcoin price data - Try multiple sources
            print(f"Downloading BTC data from {params.start_date} to {params.end_date}...")
            
            # Try CoinGecko first (more reliable, free API)
            try:
                print("Attempting to fetch from CoinGecko API...")
                price = self._fetch_coingecko_data(params.start_date, params.end_date)
                print(f"✓ Successfully downloaded {len(price)} data points from CoinGecko")
                print(f"  Price range: ${price.min():.2f} - ${price.max():.2f}")
                print(f"  Start price: ${price.iloc[0]:.2f}, End price: ${price.iloc[-1]:.2f}")
                
            except Exception as e1:
                print(f"CoinGecko failed: {str(e1)}")
                
                # Fallback to Yahoo Finance
                try:
                    print("Attempting to fetch from Yahoo Finance...")
                    price_data = vbt.YFData.download(
                        'BTC-USD',
                        start=params.start_date,
                        end=params.end_date,
                        missing_index='drop'
                    )
                    price = price_data.get('Close')
                    
                    if price is None or len(price) == 0:
                        raise ValueError("No price data received")
                        
                    print(f"✓ Successfully downloaded {len(price)} data points from Yahoo Finance")
                    
                except Exception as e2:
                    print(f"Yahoo Finance failed: {str(e2)}")
                    print("Using generated mock data for demonstration...")
                    price = self._generate_mock_btc_data(params.start_date, params.end_date)
            
            # Generate moving average crossover signals
            # Use shorter MAs for recent data (10-day and 30-day)
            # This works better with 90 days of data
            fast_ma = vbt.MA.run(price, 10, short_name='fast_ma')
            slow_ma = vbt.MA.run(price, 30, short_name='slow_ma')
            
            print(f"Calculated MAs: 10-day (fast) and 30-day (slow)")
            
            # Entry when fast MA crosses above slow MA (bullish signal)
            entries = fast_ma.ma_crossed_above(slow_ma)
            # Exit when fast MA crosses below slow MA (bearish signal)
            exits = fast_ma.ma_crossed_below(slow_ma)
            
            # Debug: Show signal counts
            num_entries = entries.sum()
            num_exits = exits.sum()
            print(f"  Entry signals: {num_entries}")
            print(f"  Exit signals: {num_exits}")
            
            # Run portfolio simulation
            pf = vbt.Portfolio.from_signals(
                close=price,
                entries=entries,
                exits=exits,
                init_cash=params.initial_capital,
                fees=params.fees,
                slippage=params.slippage,
                freq='1D'
            )
            
            # Extract portfolio metrics
            total_return = pf.total_return() * 100  # Convert to percentage
            sharpe_ratio = pf.sharpe_ratio()
            max_drawdown = pf.max_drawdown() * 100  # Convert to percentage
            win_rate = pf.trades.win_rate() * 100 if pf.trades.count() > 0 else 0
            total_trades = pf.trades.count()
            
            # Calculate CAGR
            years = (pd.to_datetime(params.end_date) - pd.to_datetime(params.start_date)).days / 365.25
            cagr = ((pf.final_value() / params.initial_capital) ** (1 / years) - 1) * 100 if years > 0 else 0
            
            # Calculate total gain and loss
            total_pnl = pf.total_profit()
            if pf.trades.count() > 0:
                trades_pnl = pf.trades.pnl.values  # Get PnL as array
                winning_trades_pnl = trades_pnl[trades_pnl > 0].sum()
                losing_trades_pnl = abs(trades_pnl[trades_pnl < 0].sum())
            else:
                winning_trades_pnl = 0
                losing_trades_pnl = 0
            
            # Get benchmark (buy and hold) performance
            benchmark_pf = vbt.Portfolio.from_holding(price, init_cash=params.initial_capital)
            benchmark_return = benchmark_pf.total_return() * 100
            vs_benchmark = total_return - benchmark_return
            
            # Extract equity curve
            portfolio_value = pf.value()
            equity_series = self._create_equity_series(portfolio_value, benchmark_pf.value(), price)
            
            # Extract trades
            trades = self._extract_trades(pf)
            
            # Calculate drawdown duration
            try:
                drawdowns = pf.drawdowns.records_readable
                if len(drawdowns) > 0:
                    # Try different possible column names
                    if 'Duration' in drawdowns.columns:
                        max_dd_duration = int(drawdowns['Duration'].max())
                    elif 'Duration [ns]' in drawdowns.columns:
                        max_dd_duration = int(drawdowns['Duration [ns]'].max() / 86400000000000)  # Convert ns to days
                    else:
                        max_dd_duration = 0
                else:
                    max_dd_duration = 0
            except Exception as e:
                print(f"Warning: Could not calculate drawdown duration: {e}")
                max_dd_duration = 0
            
            # Create metrics
            metrics = BacktestMetrics(
                total_amount_invested=params.initial_capital,
                total_gain=winning_trades_pnl,
                total_loss=losing_trades_pnl,
                total_return=round(total_return, 2),
                cagr=round(cagr, 2),
                sharpe_ratio=round(sharpe_ratio, 2),
                max_drawdown=round(max_drawdown, 2),
                max_drawdown_duration=max_dd_duration,
                win_rate=round(win_rate, 1),
                trades=total_trades,
                vs_benchmark=round(vs_benchmark, 2)
            )
            
            # Create backtest run
            backtest_run = BacktestRun(
                id=f"vbt-{datetime.utcnow().timestamp()}",
                strategy_id=strategy_id,
                params=params,
                metrics=metrics,
                equity_series=equity_series,
                drawdown_series=[],
                monthly_returns=[],
                trades=trades,
                created_at=datetime.utcnow()
            )
            
            print(f"Backtest completed successfully!")
            print(f"Total Return: {total_return:.2f}%")
            print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
            print(f"Max Drawdown: {max_drawdown:.2f}%")
            print(f"Total Trades: {total_trades}")
            
            return backtest_run
            
        except Exception as e:
            print(f"Error running VectorBT backtest: {str(e)}")
            raise Exception(f"VectorBT backtest failed: {str(e)}")
    
    def _create_equity_series(self, portfolio_value: pd.Series, benchmark_value: pd.Series, btc_price: pd.Series) -> List[EquityPoint]:
        """Convert portfolio value series to equity points with BTC price"""
        equity_points = []
        
        # Ensure all series have the same index
        total_points = len(portfolio_value)
        
        print(f"Creating equity series with {total_points} points")
        print(f"BTC price range: ${btc_price.min():.2f} - ${btc_price.max():.2f}")
        
        for i in range(total_points):
            date = portfolio_value.index[i]
            value = portfolio_value.iloc[i]
            benchmark = benchmark_value.iloc[i] if i < len(benchmark_value) else None
            btc = btc_price.iloc[i] if i < len(btc_price) else None
            
            equity_points.append(EquityPoint(
                date=date.strftime("%Y-%m-%d"),
                value=round(float(value), 2),
                benchmark=round(float(benchmark), 2) if benchmark is not None else None,
                btc_price=round(float(btc), 2) if btc is not None and not pd.isna(btc) else None
            ))
        
        # Debug: Check how many points have BTC price
        btc_count = sum(1 for p in equity_points if p.btc_price is not None and p.btc_price > 0)
        print(f"Equity points with BTC price: {btc_count}/{len(equity_points)}")
        
        # Show first few points for debugging
        if len(equity_points) > 0:
            print(f"Sample equity points:")
            for i in range(min(3, len(equity_points))):
                p = equity_points[i]
                print(f"  {p.date}: value=${p.value:.2f}, btc=${p.btc_price}")
        
        return equity_points
    
    def _extract_trades(self, pf) -> List[Trade]:
        """Extract trade records from portfolio"""
        trades = []
        
        try:
            trades_df = pf.trades.records_readable
            
            if len(trades_df) == 0:
                return trades
            
            # Get only the most recent 10 trades
            recent_trades = trades_df.tail(10)
            
            for idx, trade in recent_trades.iterrows():
                entry_date = trade['Entry Timestamp']
                exit_date = trade['Exit Timestamp']
                
                # Entry trade (BUY)
                trades.append(Trade(
                    id=f"trade-{idx}-entry",
                    date=entry_date.strftime("%Y-%m-%d") if pd.notna(entry_date) else "",
                    type="BUY",
                    symbol="BTC",
                    price=round(float(trade['Avg Entry Price']), 2),
                    quantity=round(float(trade['Size']), 6),
                    amount=round(float(trade['Avg Entry Price'] * trade['Size']), 2),
                    return_pct=None
                ))
                
                # Exit trade (SELL) - only if position is closed
                if pd.notna(exit_date):
                    return_pct = (trade['Return [%]']) if 'Return [%]' in trade else 0
                    trades.append(Trade(
                        id=f"trade-{idx}-exit",
                        date=exit_date.strftime("%Y-%m-%d"),
                        type="SELL",
                        symbol="BTC",
                        price=round(float(trade['Avg Exit Price']), 2),
                        quantity=round(float(trade['Size']), 6),
                        amount=round(float(trade['Avg Exit Price'] * trade['Size']), 2),
                        return_pct=round(float(return_pct), 2)
                    ))
            
            # Sort by date descending
            trades.sort(key=lambda x: x.date, reverse=True)
            
        except Exception as e:
            print(f"Error extracting trades: {str(e)}")
        
        return trades[:10]  # Return only 10 most recent
    
    def _fetch_coingecko_data(self, start_date: str, end_date: str) -> pd.Series:
        """Fetch Bitcoin price data from CoinGecko API"""
        # Initialize CoinGecko API with API key if available
        api_key = settings.coingecko_api_key
        if api_key:
            cg = CoinGeckoAPI(api_key=api_key)
            print(f"Using CoinGecko Pro API (authenticated)")
        else:
            cg = CoinGeckoAPI()
            print(f"Using CoinGecko Free API")
        
        # Convert dates to timestamps
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        
        # CoinGecko uses Unix timestamps
        from_timestamp = int(start_dt.timestamp())
        to_timestamp = int(end_dt.timestamp())
        
        # Fetch market chart data (price in USD)
        # CoinGecko ID for Bitcoin is 'bitcoin'
        data = cg.get_coin_market_chart_range_by_id(
            id='bitcoin',
            vs_currency='usd',
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp
        )
        
        # Extract prices
        prices = data['prices']  # List of [timestamp, price]
        
        if not prices or len(prices) == 0:
            raise ValueError("No price data received from CoinGecko")
        
        # Convert to DataFrame
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.set_index('date')
        
        # Resample to daily data (CoinGecko returns hourly for short periods)
        daily_prices = df['price'].resample('D').last().dropna()
        
        # Create pandas Series
        price_series = pd.Series(daily_prices.values, index=daily_prices.index, name='Close')
        
        return price_series
    
    def _generate_mock_btc_data(self, start_date: str, end_date: str) -> pd.Series:
        """Generate realistic mock Bitcoin price data for testing"""
        import numpy as np
        
        # Create date range
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Generate realistic Bitcoin-like price movement
        # Starting price around $30,000
        np.random.seed(42)  # For reproducibility
        n_days = len(dates)
        
        # Generate price with trend and volatility
        returns = np.random.normal(0.001, 0.03, n_days)  # Daily returns with drift
        prices = 30000 * np.exp(np.cumsum(returns))
        
        # Add some realistic volatility spikes
        for i in range(0, n_days, 50):
            if i < n_days:
                prices[i:i+10] *= np.random.uniform(0.95, 1.05)
        
        # Create pandas Series
        price_series = pd.Series(prices, index=dates, name='Close')
        
        print(f"Generated {len(price_series)} mock data points from ${prices[0]:.2f} to ${prices[-1]:.2f}")
        
        return price_series

vectorbt_service = VectorBTBacktestService()
