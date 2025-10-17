import os
import json
import boto3
from typing import Dict, Any, AsyncGenerator
from ..config import settings

class BedrockService:
    """Service for AWS Bedrock LLM integration"""
    
    SYSTEM_PROMPT = """You are an AI trading strategy assistant for Vibe Water Associates. Your role is to help users build algorithmic trading strategies through natural conversation.

When a user describes their trading goals, you must respond with TWO components:

1. **User-facing message**: A friendly, conversational response that will be shown in the chat interface
2. **Backend JSON**: A structured JSON object that will populate the strategy builder interface

Your responses MUST follow this exact format using XML-style tags:

<user_message>
[Your friendly, conversational response here explaining what you've created]
</user_message>

<backend>
{
  "account": {
    "workspace": "Vibe Water Associates",
    "section": "My Strategies"
  },
  "assistant_panel": {
    "greeting": "Hello",
    "user_request": "[User's original request]",
    "assistant_reply": "[Brief summary of your recommendation]"
  },
  "flowchart": {
    "nodes": [
      {
        "id": "start",
        "type": "start",
        "label": "Start Strategy"
      },
      {
        "id": "category",
        "type": "category",
        "label": "Crypto Category: ",
        "meta": {
          "category": "DeFi"
        }
      },
      {
        "id": "entry",
        "type": "entry_condition",
        "label": "Set Entry Condition: ",
        "meta": {
          "mode": "ai_optimized",
          "rules": ["Enter on a 5% price drop from the 20-day moving average"]
        }
      },
      {
        "id": "profit_target",
        "type": "take_profit",
        "label": "Profit Target: ",
        "meta": {
          "target_pct": 7.0
        }
      },
      {
        "id": "stop_loss",
        "type": "stop_loss",
        "label": "Stop Loss: ",
        "meta": {
          "stop_pct": 5.0,
          "added": true
        }
      },
      {
        "id": "end",
        "type": "end",
        "label": "End Strategy"
      }
    ],
    "edges": [
      ["start", "category"],
      ["category", "entry"],
      ["entry", "profit_target"],
      ["profit_target", "stop_loss"],
      ["stop_loss", "end"]
    ]
  },
  "toolbox": {
    "modules": ["Crypto Category", "Set Entry Condition", "Define Exit Target", "Manage Capital", "Degen Class", "Profit Target"],
    "quick_profit_targets": [0.5, 2, 4]
  },
  "degen_class": {
    "options": ["High", "Medium", "Low"],
    "selected": "High"
  },
  "strategy_metrics": {
    "impact_monthly_return_delta_pct": 7.0,
    "estimated_capital_required_usd": 1000
  },
  "guardrails": {
    "enabled": [
      {
        "key": "no_short_selling",
        "label": "No short selling",
        "status": "ok"
      },
      {
        "key": "max_drawdown_10",
        "label": "Max 10% Drawdown",
        "status": "ok"
      },
      {
        "key": "high_risk_class",
        "label": "High risk asset class selected",
        "status": "warning"
      }
    ],
    "violations": []
  },
  "actions": {
    "explain_button": {
      "label": "Explain",
      "enabled": true
    },
    "run_backtest_button": {
      "label": "Run Backtest",
      "enabled": true
    }
  },
  "versioning": {
    "comments_enabled": true,
    "version_history_enabled": true
  }
}
</backend>

Key guidelines:
- ALWAYS include both <user_message> and <backend> tags in your response
- The <user_message> should be conversational, friendly, and explain what strategy you've created
- The <backend> JSON must be valid JSON that will populate the strategy builder page
- Adjust the strategy parameters based on user's risk tolerance, capital, and return expectations
- Set appropriate guardrails based on the strategy risk level
- Use "High" degen_class for aggressive strategies, "Medium" for balanced, "Low" for conservative
- Always include a stop_loss node for risk management unless user explicitly requests otherwise
- The flowchart nodes should flow logically: start -> category -> entry -> profit_target -> stop_loss -> end
- The user_message will be displayed in the chat interface
- The backend JSON will update the global state for the strategy builder page (flowchart, metrics, guardrails, etc.)

Example response:
<user_message>
I've created a high-return crypto strategy tailored to your $1000 capital with a target of 7% monthly returns. This is classified as a high-risk strategy with appropriate stop-loss protection at 5% to manage downside risk. The strategy uses AI-optimized entry conditions and focuses on the DeFi category.
</user_message>

<backend>
{JSON structure as shown above}
</backend>
"""

    def __init__(self):
        """Initialize Bedrock client"""
        # Set AWS bearer token if provided
        if settings.aws_bearer_token_bedrock:
            os.environ['AWS_BEARER_TOKEN_BEDROCK'] = settings.aws_bearer_token_bedrock
        
        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name=settings.aws_region
        )
        # Use aws_model_id if provided, otherwise fall back to bedrock_model_id
        self.model_id = settings.aws_model_id or settings.bedrock_model_id
    
    async def chat_stream(self, messages: list[Dict[str, Any]]) -> AsyncGenerator[str, None]:
        """
        Stream chat responses from Bedrock
        
        Args:
            messages: List of message dicts with 'role' and 'content'
        
        Yields:
            Chunks of the response text
        """
        # Convert messages to Bedrock format
        bedrock_messages = []
        for msg in messages:
            if msg["role"] in ["user", "assistant"]:
                bedrock_messages.append({
                    "role": msg["role"],
                    "content": [{"text": msg["content"]}]
                })
        
        print("\n" + "="*80)
        print("🚀 BEDROCK REQUEST")
        print("="*80)
        print(f"Model ID: {self.model_id}")
        print(f"Number of messages: {len(bedrock_messages)}")
        print("\nMessages:")
        for i, msg in enumerate(bedrock_messages):
            print(f"\n[{i+1}] Role: {msg['role']}")
            print(f"Content: {msg['content'][0]['text'][:200]}...")
        print("\nSystem Prompt (first 500 chars):")
        print(self.SYSTEM_PROMPT[:500] + "...")
        print("="*80)
        
        try:
            # Call Bedrock converse API
            response = self.client.converse(
                modelId=self.model_id,
                messages=bedrock_messages,
                system=[{"text": self.SYSTEM_PROMPT}]
            )
            
            print("\n" + "="*80)
            print("📥 BEDROCK RESPONSE")
            print("="*80)
            print(f"Response keys: {response.keys()}")
            
            # Extract response text
            if "output" in response and "message" in response["output"]:
                content = response["output"]["message"]["content"]
                if content and len(content) > 0:
                    text = content[0].get("text", "")
                    print(f"\nResponse length: {len(text)} characters")
                    print("\nFull Response:")
                    print(text)
                    print("="*80 + "\n")
                    
                    # Don't stream the raw response - we'll parse it first and stream only the user_message
                    # Just yield the complete response for parsing
                    yield text
            else:
                error_msg = "Error: No response from model"
                print(f"\n❌ {error_msg}")
                print(f"Response structure: {response}")
                print("="*80 + "\n")
                yield error_msg
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"\n❌ BEDROCK ERROR")
            print("="*80)
            print(error_msg)
            print("="*80 + "\n")
            yield error_msg
    
    def parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse the LLM response into user message and strategy JSON using XML-style tags
        
        Args:
            response_text: The full response from the LLM with <user_message> and <backend> tags
        
        Returns:
            Dict with 'user_message' and 'strategy_json' keys
        """
        print("\n" + "="*80)
        print("🔍 PARSING RESPONSE")
        print("="*80)
        print(f"Response text length: {len(response_text)} characters")
        
        try:
            user_message = ""
            strategy_json = None
            
            # Extract user_message content
            user_msg_start = response_text.find("<user_message>")
            user_msg_end = response_text.find("</user_message>")
            
            print(f"\n<user_message> tag found at: {user_msg_start}")
            print(f"</user_message> tag found at: {user_msg_end}")
            
            if user_msg_start != -1 and user_msg_end != -1:
                user_message = response_text[user_msg_start + 14:user_msg_end].strip()
                print(f"✅ Extracted user_message ({len(user_message)} chars):")
                print(user_message[:200] + "..." if len(user_message) > 200 else user_message)
            else:
                print("❌ No <user_message> tags found")
            
            # Extract backend JSON content
            backend_start = response_text.find("<backend>")
            backend_end = response_text.find("</backend>")
            
            print(f"\n<backend> tag found at: {backend_start}")
            print(f"</backend> tag found at: {backend_end}")
            
            if backend_start != -1 and backend_end != -1:
                json_content = response_text[backend_start + 9:backend_end].strip()
                
                print(f"✅ Extracted backend content ({len(json_content)} chars)")
                print("First 300 chars of JSON content:")
                print(json_content[:300] + "...")
                
                # Remove markdown code blocks if present
                if json_content.startswith("```json"):
                    json_content = json_content[7:]
                    print("Removed ```json prefix")
                if json_content.startswith("```"):
                    json_content = json_content[3:]
                    print("Removed ``` prefix")
                if json_content.endswith("```"):
                    json_content = json_content[:-3]
                    print("Removed ``` suffix")
                
                # Parse JSON
                strategy_json = json.loads(json_content.strip())
                print(f"✅ Successfully parsed JSON with keys: {list(strategy_json.keys())}")
            else:
                print("❌ No <backend> tags found")
            
            # If no tags found, treat entire response as user message
            if not user_message and not strategy_json:
                user_message = response_text.strip()
                print("\n⚠️  No XML tags found, using entire response as user_message")
            
            result = {
                "user_message": user_message,
                "strategy_json": strategy_json
            }
            
            print("\n📤 PARSE RESULT:")
            print(f"  - Has user_message: {bool(user_message)}")
            print(f"  - Has strategy_json: {bool(strategy_json)}")
            print("="*80 + "\n")
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON PARSE ERROR: {str(e)}")
            print("="*80 + "\n")
            return {
                "user_message": response_text,
                "strategy_json": None,
                "error": f"Failed to parse JSON: {str(e)}"
            }
        except Exception as e:
            print(f"\n❌ PARSE ERROR: {str(e)}")
            print("="*80 + "\n")
            return {
                "user_message": response_text,
                "strategy_json": None,
                "error": str(e)
            }

bedrock_service = BedrockService()
