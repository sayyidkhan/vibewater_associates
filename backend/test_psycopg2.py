#!/usr/bin/env python3
"""
Simple synchronous test using psycopg2 to verify Supabase connection.
This helps diagnose if the issue is with asyncpg or the connection itself.
"""

import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Parse DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in .env file")
    exit(1)

print("🔍 Testing Supabase connection with psycopg2...")
print(f"Connection string: {DATABASE_URL[:50]}...")
print()

# Connect to the database
try:
    connection = psycopg2.connect(DATABASE_URL)
    print("✅ Connection successful!")
    
    # Create a cursor to execute SQL queries
    cursor = connection.cursor()
    
    # Test basic query
    cursor.execute("SELECT 1 as test;")
    result = cursor.fetchone()
    print(f"✓ Basic query successful: {result[0]}")
    
    # Get current time
    cursor.execute("SELECT NOW();")
    result = cursor.fetchone()
    print(f"✓ Current Time: {result[0]}")
    
    # Get PostgreSQL version
    cursor.execute("SELECT version();")
    result = cursor.fetchone()
    version = result[0].split(',')[0]
    print(f"✓ PostgreSQL version: {version}")
    
    # Check tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        AND table_name IN ('strategies', 'backtests', 'strategy_executions', 'backtest_runs')
        ORDER BY table_name
    """)
    tables = cursor.fetchall()
    
    if tables:
        print(f"✓ Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
    else:
        print("⚠️  No tables found")

    # Close the cursor and connection
    cursor.close()
    connection.close()
    print("\n✅ Connection test successful!")
    print("Connection closed.")

except psycopg2.OperationalError as e:
    print(f"❌ Connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Check your DATABASE_URL format")
    print("2. Verify your password is correct")
    print("3. Ensure Supabase project is active")
    print("4. Check if your IP is allowed in Supabase settings")
    exit(1)
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
