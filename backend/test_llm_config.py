#!/usr/bin/env python3
"""
Test script to verify LLM configuration (Anthropic vs Bedrock)
"""
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("="*80)
print("🔍 LLM CONFIGURATION CHECK")
print("="*80)

# Check Anthropic API Key
anthropic_key = os.getenv('ANTHROPIC_API_KEY', '').strip()
anthropic_model = os.getenv('ANTHROPIC_MODEL', 'claude-3-5-haiku-20241022').strip()
print("\n📋 Anthropic API Configuration:")
if anthropic_key:
    key_preview = anthropic_key[:10] + "..." if len(anthropic_key) > 10 else anthropic_key
    print(f"  ✅ API Key: {key_preview}")
    print(f"  Length: {len(anthropic_key)} characters")
    print(f"  Model: {anthropic_model}")
else:
    print(f"  ❌ API Key not found or blank")

# Check Bedrock Configuration
aws_token = os.getenv('AWS_BEARER_TOKEN_BEDROCK', '').strip()
print("\n📋 AWS Bedrock Token:")
if aws_token:
    token_preview = aws_token[:10] + "..." if len(aws_token) > 10 else aws_token
    print(f"  ✅ Found: {token_preview}")
else:
    print(f"  ❌ Not found or blank")

print(f"\n📋 AWS Region: {os.getenv('AWS_REGION', 'us-east-1')}")
print(f"📋 Bedrock Model ID: {os.getenv('BEDROCK_MODEL_ID', 'us.anthropic.claude-3-5-haiku-20241022-v1:0')}")

# Determine which service will be used
print("\n" + "="*80)
print("🎯 SERVICE SELECTION")
print("="*80)
if anthropic_key:
    print("  ✅ Will use: Anthropic API")
else:
    print("  ℹ️  Will use: AWS Bedrock (fallback)")

print("\n" + "="*80)
print("💡 NEXT STEPS")
print("="*80)
if anthropic_key:
    print("✅ Anthropic API key is configured!")
    print("   Restart your server to use Anthropic API:")
    print("   uv run uvicorn app.main:app --reload")
else:
    print("ℹ️  Using Bedrock fallback")
    print("   To use Anthropic API instead:")
    print("   1. Add ANTHROPIC_API_KEY=your_key to .env file")
    print("   2. Restart the server")

print("="*80)
