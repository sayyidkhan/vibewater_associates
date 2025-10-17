"""
Test script to call Ollama with the Strategy Builder prompt
"""

import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gpt-oss:20b"  # Full model name with tag

# System prompt defining the JSON schema and rules
SYSTEM_PROMPT = """Provide a single JSON object (no extra text) representing the complete state of a crypto strategy in the Strategy Builder UI. Follow this schema and constraints exactly.

Schema:
{
"account": {
"workspace": "string", // e.g., "Vibe Water Associates"
"section": "My Strategies" // static label in navbar
},
"assistant_panel": {
"greeting": "string",
"user_request": "string", // last message from user
"assistant_reply": "string" // summarizing intent and risks
},
"flowchart": {
"nodes": [
// ordered top to bottom
{ "id": "start", "type": "start", "label": "Start Strategy" },
{ "id": "category", "type": "category", "label": "Crypto Category: ", "meta": { "category": "string" } },
{ "id": "entry", "type": "entry_condition", "label": "Set Entry Condition: ", "meta": { "mode": "manual|ai_optimized", "rules": ["string"] } },
{ "id": "profit_target", "type": "take_profit", "label": "Profit Target: ", "meta": { "target_pct": number } },
{ "id": "stop_loss", "type": "stop_loss", "label": "Stop Loss: ", "meta": { "stop_pct": number, "added": true } },
{ "id": "end", "type": "end", "label": "End Strategy" }
],
"edges": [
["start","category"], ["category","entry"], ["entry","profit_target"], ["profit_target","stop_loss"], ["stop_loss","end"]
]
},
"toolbox": {
"modules": [
"Crypto Category",
"Set Entry Condition",
"Define Exit Target",
"Manage Capital",
"Degen Class",
"Profit Target"
],
"quick_profit_targets": [0.5, 2, 4] // percents shown as buttons
},
"degen_class": {
"options": ["High","Medium","Low"],
"selected": "High"
},
"strategy_metrics": {
"impact_monthly_return_delta_pct": 0.5, // positive or negative number
"estimated_capital_required_usd": 1000
},
"guardrails": {
"enabled": [
{ "key": "no_short_selling", "label": "No short selling", "status": "ok" },
{ "key": "max_drawdown_10", "label": "Max 10% Drawdown", "status": "ok" },
{ "key": "high_risk_class", "label": "High risk asset class selected", "status": "warning" }
],
"violations": [
{ "key": "no_stop_loss", "label": "No stop loss", "status": "error", "critical": true }
]
},
"actions": {
"explain_button": { "label": "Explain", "enabled": true },
"run_backtest_button": { "label": "Run Backtest", "enabled": true }
},
"versioning": {
"comments_enabled": true,
"version_history_enabled": true
}
}

Rules:
- Percent values are numbers, not strings. Example: 2 for 2%.
- Labels should mirror the flowchart text.
- The stop_loss node must exist; if stop loss is present, remove the "no_stop_loss" violation automatically or set stop_loss.meta.added = true but keep violation only if stop loss is missing.
- Ensure edges form a valid linear path from start to end in the given order.
- Only output valid JSON. Do not include comments or trailing commas."""

# User query
USER_QUERY = "I have $1000, please choose a high-return strategy that gives at least 7% returns monthly"

def call_ollama(prompt: str, stream: bool = False, use_json_format: bool = False):
    """Call Ollama API with the given prompt"""
    
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": stream
    }
    
    # Only add format constraint if requested
    if use_json_format:
        payload["format"] = "json"
    
    print("=" * 80)
    print(f"Calling Ollama with model: {MODEL}")
    print(f"URL: {OLLAMA_URL}")
    print("=" * 80)
    print()
    
    try:
        print(f"Sending request to Ollama...")
        response = requests.post(OLLAMA_URL, json=payload, stream=stream, timeout=120)
        print(f"Response status: {response.status_code}")
        response.raise_for_status()
        
        if stream:
            # Handle streaming response
            full_response = ""
            thinking_output = ""
            print("Streaming response:")
            line_count = 0
            
            for line in response.iter_lines():
                line_count += 1
                if line:
                    try:
                        chunk = json.loads(line)
                        
                        # Handle thinking output (gpt-oss shows reasoning)
                        if 'thinking' in chunk and chunk['thinking']:
                            thinking_output += chunk['thinking']
                        
                        # Handle actual response
                        if 'response' in chunk and chunk['response']:
                            full_response += chunk['response']
                            print(chunk['response'], end='', flush=True)
                        
                        if chunk.get('done', False):
                            print()
                            if thinking_output:
                                print(f"\n[Model thinking: {thinking_output[:100]}...]")
                            print(f"[Received {line_count} lines, {len(full_response)} chars]")
                            break
                            
                    except json.JSONDecodeError as e:
                        print(f"\n⚠️  JSON decode error on line {line_count}: {e}")
                        print(f"Raw line: {line[:200]}")  # Show first 200 chars
            
            if line_count == 0:
                print("⚠️  No lines received from stream")
            elif not full_response:
                print(f"⚠️  Received {line_count} lines but no response content")
                if thinking_output:
                    print(f"   Model was thinking: {thinking_output[:200]}")
            
            return full_response if full_response else None
        else:
            # Handle non-streaming response
            result = response.json()
            return result.get('response', '')
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out after 120 seconds")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error calling Ollama: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response text: {e.response.text}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def test_ollama_connection():
    """Test if Ollama is accessible"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✓ Ollama is running with {len(models)} model(s)")
            for model in models:
                print(f"  - {model.get('name', 'unknown')}")
            return True
        else:
            print(f"⚠️  Ollama responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        return False

def main():
    # Test connection first
    print("Testing Ollama connection...")
    if not test_ollama_connection():
        print("\nMake sure Ollama is running with: ollama serve")
        return
    print()
    
    # Combine system prompt and user query
    full_prompt = f"{SYSTEM_PROMPT}\n\nUser Query:\n{USER_QUERY}"
    
    print("User Query:")
    print(f"  {USER_QUERY}")
    print()
    
    # Call Ollama (streaming for better UX)
    # Note: Not using format="json" as it interferes with gpt-oss thinking/response flow
    print("Ollama Response:")
    print("-" * 80)
    response = call_ollama(full_prompt, stream=True, use_json_format=False)
    print("-" * 80)
    print()
    
    if response:
        # Try to parse and pretty-print the JSON
        try:
            strategy_json = json.loads(response)
            print("✓ Valid JSON received!")
            print()
            print("Parsed Strategy:")
            print("=" * 80)
            print(json.dumps(strategy_json, indent=2))
            print("=" * 80)
            print()
            
            # Display key information
            print("Key Strategy Details:")
            print(f"  Workspace: {strategy_json.get('account', {}).get('workspace', 'N/A')}")
            print(f"  User Request: {strategy_json.get('assistant_panel', {}).get('user_request', 'N/A')}")
            
            metrics = strategy_json.get('strategy_metrics', {})
            print(f"  Monthly Return Impact: {metrics.get('impact_monthly_return_delta_pct', 'N/A')}%")
            print(f"  Capital Required: ${metrics.get('estimated_capital_required_usd', 'N/A')}")
            
            flowchart = strategy_json.get('flowchart', {})
            nodes = flowchart.get('nodes', [])
            print(f"  Strategy Nodes: {len(nodes)}")
            
            # Show flowchart nodes
            print()
            print("Flowchart Nodes:")
            for node in nodes:
                node_type = node.get('type', 'unknown')
                label = node.get('label', 'N/A')
                meta = node.get('meta', {})
                print(f"    [{node_type}] {label}")
                if meta:
                    for key, value in meta.items():
                        print(f"      - {key}: {value}")
            
            # Show guardrails
            guardrails = strategy_json.get('guardrails', {})
            violations = guardrails.get('violations', [])
            if violations:
                print()
                print("⚠️  Guardrail Violations:")
                for v in violations:
                    print(f"    - {v.get('label', 'N/A')} ({v.get('status', 'N/A')})")
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            print()
            print("Raw Response:")
            print(response)
    else:
        print("❌ No response received from Ollama")

if __name__ == "__main__":
    main()
