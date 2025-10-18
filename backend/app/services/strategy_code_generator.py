import json
import re
from typing import Dict, Any, List, Optional


class StrategyCodeGenerator:
    """
    Transforms strategy JSON schema into executable VectorBT Python code.
    This is the core transformation logic that CrewAI agents will use.
    """
    
    def __init__(self):
        self.code_template = self._load_code_template()
    
    def generate_vectorbt_code(self, strategy_schema: Dict[str, Any], params: Dict[str, Any]) -> str:
        """
        Main method: Converts strategy JSON to VectorBT code
        
        Args:
            strategy_schema: The strategy flowchart schema with nodes and connections
            params: Backtest parameters (symbols, dates, capital, etc.)
        
        Returns:
            Executable Python code as string
        """
        # Parse strategy nodes
        nodes = strategy_schema.get('nodes', [])
        nodes_dict = {node['id']: node for node in nodes}
        
        # Extract strategy components
        category = self._extract_category(nodes_dict)
        entry_logic = self._extract_entry_logic(nodes_dict)
        exit_logic = self._extract_exit_logic(nodes_dict)
        risk_management = self._extract_risk_management(nodes_dict)
        
        # Generate code sections
        imports = self._generate_imports()
        data_fetching = self._generate_data_fetching(category, params)
        indicators = self._generate_indicators(entry_logic)
        signals = self._generate_signals(entry_logic, exit_logic, risk_management)
        portfolio = self._generate_portfolio(params, risk_management, exit_logic)
        metrics = self._generate_metrics()
        
        # Combine into full code
        full_code = f"""{imports}

# Strategy Configuration
STRATEGY_NAME = "{params.get('strategy_name', 'Generated Strategy')}"
CATEGORY = "{category}"

{data_fetching}

{indicators}

{signals}

{portfolio}

{metrics}
"""
        
        return full_code
    
    def _extract_category(self, nodes: Dict[str, Any]) -> str:
        """Extract crypto category from nodes"""
        for node in nodes.values():
            node_type = node.get('type', '')
            if node_type in ["category", "crypto_category"]:
                meta = node.get('meta', {})
                return meta.get('category', 'Bitcoin')
        return 'Bitcoin'
    
    def _extract_entry_logic(self, nodes: Dict[str, Any]) -> Dict[str, Any]:
        """Extract entry condition logic"""
        for node in nodes.values():
            node_type = node.get('type', '')
            if node_type in ["entry_condition", "entry"]:
                meta = node.get('meta', {})
                rules = meta.get('rules', [])
                return {
                    'mode': meta.get('mode', 'manual'),
                    'rules': rules,
                    'indicators': self._parse_indicators_from_rules(rules)
                }
        return {'mode': 'manual', 'rules': [], 'indicators': []}
    
    def _extract_exit_logic(self, nodes: Dict[str, Any]) -> Dict[str, Any]:
        """Extract exit/take profit logic"""
        exit_data = {}
        for node in nodes.values():
            node_type = node.get('type', '')
            if node_type in ["take_profit", "exit_target"]:
                meta = node.get('meta', {})
                exit_data['take_profit_pct'] = meta.get('target_pct', 5.0)
        return exit_data
    
    def _extract_risk_management(self, nodes: Dict[str, Any]) -> Dict[str, Any]:
        """Extract risk management (stop loss) logic"""
        risk_data = {}
        for node in nodes.values():
            node_type = node.get('type', '')
            if node_type == "stop_loss":
                meta = node.get('meta', {})
                risk_data['stop_loss_pct'] = meta.get('stop_pct', 5.0)
        return risk_data
    
    def _parse_indicators_from_rules(self, rules: List[str]) -> List[Dict[str, Any]]:
        """Parse technical indicators from rule text"""
        indicators = []
        
        for rule in rules:
            rule_lower = rule.lower()
            
            # Detect moving averages
            ma_match = re.search(r'(\d+)[-\s]?day\s+moving\s+average', rule_lower)
            if ma_match:
                period = int(ma_match.group(1))
                indicators.append({"type": "MA", "period": period})
            
            # Detect RSI
            if "rsi" in rule_lower:
                rsi_match = re.search(r'rsi[^\d]*(\d+)', rule_lower)
                period = int(rsi_match.group(1)) if rsi_match else 14
                indicators.append({"type": "RSI", "period": period})
            
            # Detect MACD
            if "macd" in rule_lower:
                indicators.append({"type": "MACD", "fast": 12, "slow": 26, "signal": 9})
            
            # Detect Bollinger Bands
            if "bollinger" in rule_lower:
                indicators.append({"type": "BBANDS", "period": 20, "std": 2})
        
        return indicators
    
    def _generate_imports(self) -> str:
        """Generate import statements"""
        return """import vectorbt as vbt
import pandas as pd
import numpy as np
from datetime import datetime
import json"""
    
    def _generate_data_fetching(self, category: str, params: Dict[str, Any]) -> str:
        """Generate data fetching code using CoinGecko API"""
        from .coingecko_service import TOP_20_TOKENS, get_days_from_period, calculate_days_from_dates
        
        # Determine token_id
        if params.get("token_id"):
            token_id = params["token_id"]
        elif category in TOP_20_TOKENS:
            token_id = TOP_20_TOKENS[category]
        else:
            token_id = "bitcoin"  # Default fallback
        
        # Determine number of days
        if params.get("period"):
            days = get_days_from_period(params["period"])
            if days is None:
                days = 90  # Default to 90 days
        else:
            start_date = params.get("start_date", "2024-01-01")
            end_date = params.get("end_date", "2024-12-31")
            days = calculate_days_from_dates(start_date, end_date)
        
        return f"""# Fetch price data from CoinGecko
from app.services.coingecko_service import fetch_crypto_data

print(f"Fetching {{CATEGORY}} data from CoinGecko...")
try:
    price_data = fetch_crypto_data('{token_id}', {days})
    price = price_data['Close']
    print(f"Downloaded {{len(price)}} data points for {token_id}")
    print(f"Date range: {{price.index[0]}} to {{price.index[-1]}}")
except Exception as e:
    print(f"Error fetching data: {{e}}")
    raise"""
    
    def _generate_indicators(self, entry_logic: Dict[str, Any]) -> str:
        """Generate indicator calculation code"""
        indicators = entry_logic.get("indicators", [])
        
        if not indicators:
            # Default to simple MA crossover
            return """# Calculate indicators
fast_ma = vbt.MA.run(price, 10, short_name='fast')
slow_ma = vbt.MA.run(price, 30, short_name='slow')
print(f"Calculated moving averages: 10-day and 30-day")"""
        
        code_lines = ["# Calculate indicators"]
        
        for ind in indicators:
            if ind["type"] == "MA":
                period = ind["period"]
                code_lines.append(f"ma_{period} = vbt.MA.run(price, {period}, short_name='ma_{period}')")
            
            elif ind["type"] == "RSI":
                period = ind["period"]
                code_lines.append(f"rsi = vbt.RSI.run(price, window={period})")
            
            elif ind["type"] == "MACD":
                fast, slow, signal = ind["fast"], ind["slow"], ind["signal"]
                code_lines.append(f"macd = vbt.MACD.run(price, fast_window={fast}, slow_window={slow}, signal_window={signal})")
            
            elif ind["type"] == "BBANDS":
                period, std = ind["period"], ind["std"]
                code_lines.append(f"bbands = vbt.BBANDS.run(price, window={period}, alpha={std})")
        
        return "\n".join(code_lines)
    
    def _generate_signals(self, entry_logic: Dict[str, Any], exit_logic: Dict[str, Any], risk_mgmt: Dict[str, Any]) -> str:
        """Generate entry/exit signal code"""
        indicators = entry_logic.get("indicators", [])
        
        if not indicators:
            # Default MA crossover strategy
            return """# Generate signals
entries = fast_ma.ma_crossed_above(slow_ma)
exits = fast_ma.ma_crossed_below(slow_ma)
print(f"Entry signals: {entries.sum()}")
print(f"Exit signals: {exits.sum()}")"""
        
        # Generate custom signal logic based on indicators
        code_lines = ["# Generate signals"]
        
        # Entry signals
        if any(ind["type"] == "MA" for ind in indicators):
            ma_inds = [ind for ind in indicators if ind["type"] == "MA"]
            if len(ma_inds) >= 2:
                fast = min(ma_inds, key=lambda x: x["period"])
                slow = max(ma_inds, key=lambda x: x["period"])
                code_lines.append(f"entries = ma_{fast['period']}.ma_crossed_above(ma_{slow['period']})")
                code_lines.append(f"exits = ma_{fast['period']}.ma_crossed_below(ma_{slow['period']})")
        
        elif any(ind["type"] == "RSI" for ind in indicators):
            code_lines.append("entries = rsi.rsi_crossed_below(30)  # Oversold")
            code_lines.append("exits = rsi.rsi_crossed_above(70)  # Overbought")
        
        else:
            # Fallback
            code_lines.append("entries = price.pct_change() < -0.05  # 5% drop")
            code_lines.append("exits = price.pct_change() > 0.05  # 5% gain")
        
        code_lines.append("print(f'Entry signals: {entries.sum()}')")
        code_lines.append("print(f'Exit signals: {exits.sum()}')")
        
        return "\n".join(code_lines)
    
    def _generate_portfolio(self, params: Dict[str, Any], risk_mgmt: Dict[str, Any], exit_logic: Dict[str, Any]) -> str:
        """Generate portfolio backtest code"""
        initial_capital = params.get("initial_capital", 10000)
        fees = params.get("fees", 0.001)
        slippage = params.get("slippage", 0.001)
        
        # Get stop loss and take profit
        sl_stop = risk_mgmt.get('stop_loss_pct', 5.0) / 100
        tp_stop = exit_logic.get('take_profit_pct', 7.0) / 100
        
        return f"""# Run portfolio simulation
pf = vbt.Portfolio.from_signals(
    close=price,
    entries=entries,
    exits=exits,
    init_cash={initial_capital},
    fees={fees},
    slippage={slippage},
    sl_stop={sl_stop},  # Stop loss
    tp_stop={tp_stop},  # Take profit
    freq='1D'
)
print(f"Portfolio simulation complete")"""
    
    def _generate_metrics(self) -> str:
        """Generate metrics calculation code"""
        return """# Calculate metrics
total_return = pf.total_return() * 100
sharpe_ratio = pf.sharpe_ratio()
max_drawdown = pf.max_drawdown() * 100
win_rate = pf.trades.win_rate() * 100 if pf.trades.count() > 0 else 0
total_trades = pf.trades.count()

# Calculate CAGR
years = (price.index[-1] - price.index[0]).days / 365.25
cagr = ((pf.final_value() / pf.init_cash) ** (1 / years) - 1) * 100 if years > 0 else 0

# Benchmark comparison
benchmark_pf = vbt.Portfolio.from_holding(price, init_cash=pf.init_cash)
benchmark_return = benchmark_pf.total_return() * 100
vs_benchmark = total_return - benchmark_return

print(f"\\nBacktest Results:")
print(f"Total Return: {total_return:.2f}%")
print(f"CAGR: {cagr:.2f}%")
print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
print(f"Max Drawdown: {max_drawdown:.2f}%")
print(f"Win Rate: {win_rate:.1f}%")
print(f"Total Trades: {total_trades}")
print(f"vs Benchmark: {vs_benchmark:+.2f}%")

# Return results as dict
results = {
    'total_return': round(total_return, 2),
    'cagr': round(cagr, 2),
    'sharpe_ratio': round(sharpe_ratio, 2),
    'max_drawdown': round(max_drawdown, 2),
    'win_rate': round(win_rate, 1),
    'trades': int(total_trades),
    'vs_benchmark': round(vs_benchmark, 2)
}

# Output results as JSON for parsing
print("===RESULTS_START===")
print(json.dumps(results))
print("===RESULTS_END===")"""
    
    def _load_code_template(self) -> str:
        """Load base code template"""
        return """# Auto-generated VectorBT Strategy Code
# Generated by Vibe Water Associates Strategy Execution Agent
"""

# Singleton instance
strategy_code_generator = StrategyCodeGenerator()
