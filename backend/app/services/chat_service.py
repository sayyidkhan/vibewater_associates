import json
from typing import Dict, Any
from ..models import ParsedStrategy, StrategySchema, Guardrail, StrategyNode, Connection

class ChatService:
    """Service for parsing natural language into trading strategies"""
    
    async def parse_strategy(self, text: str) -> ParsedStrategy:
        """
        Parse natural language trading strategy description into structured format.
        In production, this would use OpenAI or another LLM.
        For now, returns a mock parsed strategy.
        """
        
        # Mock parsing logic - in production, use OpenAI API
        nodes = [
            StrategyNode(
                id="start-1",
                type="start",
                data={"label": "Start Strategy", "value": None, "config": None},
                position={"x": 250, "y": 50}
            ),
            StrategyNode(
                id="crypto-1",
                type="crypto_category",
                data={"label": "Crypto Category: High Degen Class", "value": "high_degen", "config": None},
                position={"x": 250, "y": 150}
            ),
            StrategyNode(
                id="entry-1",
                type="entry_condition",
                data={"label": "Set Entry Condition: AI-optimized", "value": "ai_optimized", "config": None},
                position={"x": 250, "y": 250}
            ),
            StrategyNode(
                id="exit-1",
                type="exit_target",
                data={"label": "Profit Target: 2%", "value": 0.02, "config": None},
                position={"x": 250, "y": 350}
            ),
            StrategyNode(
                id="stop-1",
                type="stop_loss",
                data={"label": "Stop Loss: 0.5% (Added)", "value": 0.005, "config": None},
                position={"x": 250, "y": 450}
            ),
            StrategyNode(
                id="end-1",
                type="end",
                data={"label": "End Strategy", "value": None, "config": None},
                position={"x": 250, "y": 550}
            ),
        ]
        
        connections = [
            Connection(id="e1", source="start-1", target="crypto-1"),
            Connection(id="e2", source="crypto-1", target="entry-1"),
            Connection(id="e3", source="entry-1", target="exit-1"),
            Connection(id="e4", source="exit-1", target="stop-1"),
            Connection(id="e5", source="stop-1", target="end-1"),
        ]
        
        schema = StrategySchema(nodes=nodes, connections=connections)
        
        guardrails = [
            Guardrail(type="no_short_selling", level="info", message="No short selling"),
            Guardrail(type="no_leverage", level="info", message="No leverage"),
            Guardrail(type="no_stop_loss", level="warning", message="No stop loss"),
        ]
        
        # Extract capital requirement from text
        capital = 1000  # Default
        if "$" in text:
            try:
                # Simple extraction - in production use better parsing
                parts = text.split("$")
                for part in parts[1:]:
                    num_str = ""
                    for char in part:
                        if char.isdigit():
                            num_str += char
                        else:
                            break
                    if num_str:
                        capital = int(num_str)
                        break
            except:
                pass
        
        # Extract return target
        return_target = 7.0  # Default
        if "%" in text:
            try:
                parts = text.split("%")
                for i, part in enumerate(parts[:-1]):
                    words = part.split()
                    if words:
                        last_word = words[-1]
                        if last_word.replace(".", "").isdigit():
                            return_target = float(last_word)
                            break
            except:
                pass
        
        rationale = f"Great! I'm parsing your request for a high-return strategy with ${capital} capital targeting {return_target}% monthly returns. I'll outline the key components and potential risks."
        
        return ParsedStrategy(
            strategy_schema=schema,
            guardrails=guardrails,
            rationale=rationale,
            estimated_return=return_target,
            required_capital=capital
        )

chat_service = ChatService()
