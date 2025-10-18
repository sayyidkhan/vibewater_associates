#!/usr/bin/env python3
"""
Helper script to show the correct Supabase connection string format.
Your project: vibewater (itgbimeueuwwujfhpxls)
Region: ap-south-1
"""

print("=" * 80)
print("SUPABASE CONNECTION STRING FOR VIBEWATER PROJECT")
print("=" * 80)
print()

project_ref = "itgbimeueuwwujfhpxls"
region = "ap-south-1"

print("📋 Your Project Details:")
print(f"   Project ID: {project_ref}")
print(f"   Region: {region}")
print(f"   Database Host: db.{project_ref}.supabase.co")
print()

print("🔑 Get your password from:")
print("   Supabase Dashboard → Settings → Database → Database Password")
print()

print("=" * 80)
print("OPTION 1: TRANSACTION POOLER (RECOMMENDED)")
print("=" * 80)
print()
print("Use this for production applications:")
print()
print(f"DATABASE_URL=postgresql://postgres.{project_ref}:[YOUR-PASSWORD]@aws-0-{region}.pooler.supabase.com:6543/postgres")
print()
print("Benefits:")
print("  ✓ Better performance")
print("  ✓ More concurrent connections")
print("  ✓ Lower latency")
print()

print("=" * 80)
print("OPTION 2: DIRECT CONNECTION")
print("=" * 80)
print()
print("Use this for migrations or if pooler doesn't work:")
print()
print(f"DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.{project_ref}.supabase.co:5432/postgres")
print()
print("When to use:")
print("  • Running database migrations")
print("  • Admin tasks")
print("  • If transaction pooler has issues")
print()

print("=" * 80)
print("NEXT STEPS")
print("=" * 80)
print()
print("1. Copy one of the connection strings above")
print("2. Replace [YOUR-PASSWORD] with your actual database password")
print("3. Update your .env file with the DATABASE_URL")
print("4. Run: uv run test_supabase_connection.py")
print()
print("Note: Your database schema is already created! ✅")
print("      Tables: strategies, backtests, strategy_executions, backtest_runs")
print()
