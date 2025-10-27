#!/usr/bin/env python3
"""
Quick Start Script for Research Agent

This script demonstrates the research agent by:
1. Starting a research run with 3 strategies
2. Polling for completion
3. Displaying results

Usage:
    python quick_start_research.py
"""

import requests
import time
import json
import sys

# Configuration
API_BASE = "http://localhost:8000"
NUM_STRATEGIES = 3
MARKET_FOCUS = "Bitcoin"
RISK_LEVEL = "Medium"
POLL_INTERVAL = 30  # seconds


def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*80)
    print(text)
    print("="*80 + "\n")


def start_research():
    """Start a new research run"""
    print_header("🔬 STARTING RESEARCH AGENT")
    
    payload = {
        "num_strategies": NUM_STRATEGIES,
        "market_focus": MARKET_FOCUS,
        "risk_level": RISK_LEVEL
    }
    
    print(f"Configuration:")
    print(f"  - Strategies to generate: {NUM_STRATEGIES}")
    print(f"  - Market focus: {MARKET_FOCUS}")
    print(f"  - Risk level: {RISK_LEVEL}")
    print(f"\nSending request to {API_BASE}/api/research/start...")
    
    try:
        response = requests.post(f"{API_BASE}/api/research/start", json=payload)
        response.raise_for_status()
        data = response.json()
        
        research_id = data["research_id"]
        print(f"\n✅ Research started successfully!")
        print(f"Research ID: {research_id}")
        print(f"Status: {data['status']}")
        print(f"\nEstimated completion time: ~{NUM_STRATEGIES * 2 + 2} minutes")
        
        return research_id
    
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to API server")
        print("Make sure the backend is running:")
        print("  cd backend && uvicorn app.main:app --reload")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Error starting research: {e}")
        sys.exit(1)


def poll_status(research_id):
    """Poll research status until completion"""
    print_header("⏳ WAITING FOR COMPLETION")
    
    start_time = time.time()
    iteration = 0
    
    while True:
        iteration += 1
        elapsed = int(time.time() - start_time)
        elapsed_str = f"{elapsed//60}m {elapsed%60}s"
        
        print(f"\n[{iteration}] Checking status... (Elapsed: {elapsed_str})")
        
        try:
            response = requests.get(f"{API_BASE}/api/research/{research_id}")
            response.raise_for_status()
            data = response.json()
            
            status = data["status"]
            print(f"Status: {status}")
            
            if status == "completed":
                print(f"\n✅ Research completed in {elapsed_str}!")
                return data
            
            elif status == "failed":
                error = data.get("error_message", "Unknown error")
                print(f"\n❌ Research failed: {error}")
                sys.exit(1)
            
            elif status == "running":
                # Show progress indicator
                dots = "." * (iteration % 4)
                print(f"⏳ Still running{dots}")
                print(f"Waiting {POLL_INTERVAL} seconds before next check...")
                time.sleep(POLL_INTERVAL)
            
            else:
                print(f"⚠️  Unknown status: {status}")
                time.sleep(POLL_INTERVAL)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
            print(f"Research is still running with ID: {research_id}")
            print(f"Check status at: {API_BASE}/api/research/{research_id}")
            sys.exit(0)
        
        except Exception as e:
            print(f"❌ Error checking status: {e}")
            time.sleep(POLL_INTERVAL)


def display_results(data):
    """Display research results"""
    print_header("📊 RESEARCH RESULTS")
    
    rankings = data.get("rankings", [])
    
    if not rankings:
        print("⚠️  No strategies generated")
        return
    
    print(f"Total Strategies Generated: {len(rankings)}\n")
    
    # Display top 3 strategies
    print("TOP 3 STRATEGIES:")
    print("-" * 80)
    
    for i, strategy in enumerate(rankings[:3], 1):
        print(f"\n#{i}. {strategy.get('strategy_name', 'Unnamed Strategy')}")
        print(f"    ID: {strategy.get('strategy_id', 'N/A')}")
        
        score = strategy.get('performance_score', 0)
        print(f"    Performance Score: {score}/100")
        
        metrics = strategy.get('metrics', {})
        if metrics:
            print(f"\n    📈 Metrics:")
            print(f"       Total Return: {metrics.get('total_return', 0):.2f}%")
            print(f"       CAGR: {metrics.get('cagr', 0):.2f}%")
            print(f"       Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
            print(f"       Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%")
            print(f"       Win Rate: {metrics.get('win_rate', 0):.1f}%")
            print(f"       Total Trades: {metrics.get('trades', 0)}")
        
        strengths = strategy.get('strengths', [])
        if strengths:
            print(f"\n    ✅ Strengths:")
            for strength in strengths[:3]:
                print(f"       - {strength}")
        
        weaknesses = strategy.get('weaknesses', [])
        if weaknesses:
            print(f"\n    ⚠️  Weaknesses:")
            for weakness in weaknesses[:3]:
                print(f"       - {weakness}")
        
        recommendation = strategy.get('recommendation', '')
        if recommendation:
            print(f"\n    💡 Recommendation: {recommendation}")
        
        print("-" * 80)


def get_top_strategy(research_id):
    """Get detailed information about top strategy"""
    print_header("🏆 TOP STRATEGY DETAILS")
    
    try:
        response = requests.get(f"{API_BASE}/api/research/{research_id}/top-strategy")
        response.raise_for_status()
        data = response.json()
        
        print(f"Strategy Name: {data.get('name', 'N/A')}")
        print(f"Description: {data.get('description', 'N/A')}")
        print(f"Category: {data.get('category', 'N/A')}")
        print(f"\nView full strategy at:")
        print(f"{API_BASE}/api/strategies/{data.get('id')}")
        
    except Exception as e:
        print(f"Error getting top strategy: {e}")


def main():
    """Main execution flow"""
    print_header("🚀 RESEARCH AGENT QUICK START")
    
    print("This script will:")
    print("  1. Start a research run")
    print(f"  2. Generate {NUM_STRATEGIES} {RISK_LEVEL.lower()}-risk strategies")
    print(f"  3. Focus on {MARKET_FOCUS} market")
    print("  4. Run backtests on each strategy")
    print("  5. Analyze and rank results")
    print(f"\nEstimated time: ~{NUM_STRATEGIES * 2 + 2} minutes")
    
    # Confirm before starting
    confirm = input("\nProceed? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Aborted.")
        sys.exit(0)
    
    # Step 1: Start research
    research_id = start_research()
    
    # Step 2: Poll for completion
    results = poll_status(research_id)
    
    # Step 3: Display results
    display_results(results)
    
    # Step 4: Get top strategy details
    get_top_strategy(research_id)
    
    # Final summary
    print_header("✅ QUICK START COMPLETE")
    print(f"Research ID: {research_id}")
    print(f"\nYou can access results anytime at:")
    print(f"{API_BASE}/api/research/{research_id}")
    print(f"\nTo use the top strategy:")
    print(f"1. View at: {API_BASE}/api/research/{research_id}/top-strategy")
    print(f"2. Run backtest: POST {API_BASE}/api/research/{research_id}/rerun-top")
    print("\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(0)
