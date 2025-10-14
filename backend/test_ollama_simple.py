"""
Simple test to verify Ollama is working
"""

import requests
import json

# Test with a simple prompt first
def test_simple():
    print("Testing simple prompt...")
    
    payload = {
        "model": "gpt-oss:20b",
        "prompt": "Say hello in JSON format with a 'message' field.",
        "stream": False,
        "format": "json"
    }
    
    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=60)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response keys: {result.keys()}")
            print(f"Full response: {json.dumps(result, indent=2)}")
            
            if 'response' in result:
                print(f"\nGenerated text: {result['response']}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

def test_streaming():
    print("\n" + "="*80)
    print("Testing streaming prompt...")
    
    payload = {
        "model": "gpt-oss:20b",
        "prompt": "Count from 1 to 5, one number per line.",
        "stream": True
    }
    
    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, stream=True, timeout=60)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("Stream output:")
            for i, line in enumerate(response.iter_lines()):
                if line:
                    print(f"Line {i}: {line[:200]}")  # First 200 chars
                    try:
                        chunk = json.loads(line)
                        if 'response' in chunk:
                            print(f"  -> {chunk['response']}", end='', flush=True)
                        if chunk.get('done'):
                            print("\n  -> Done!")
                            break
                    except:
                        pass
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_simple()
    test_streaming()
