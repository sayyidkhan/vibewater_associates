#!/usr/bin/env python3
"""
Test script to verify Supabase PostgreSQL connection.
Run this to ensure your DATABASE_URL is configured correctly.
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

async def test_connection():
    """Test the Supabase connection"""
    
    # Load environment variables
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in .env file")
        print("Please add your Supabase connection string to .env")
        return False
    
    print("🔍 Testing Supabase connection...")
    print(f"Connection string: {database_url[:50]}...")
    
    try:
        # Create connection pool
        pool = await asyncpg.create_pool(
            dsn=database_url,
            min_size=1,
            max_size=2,
            command_timeout=60,
            timeout=30  # Connection establishment timeout (30 seconds)
        )
        
        print("✓ Connection pool created")
        
        # Test basic query
        async with pool.acquire() as conn:
            result = await conn.fetchval('SELECT 1')
            print(f"✓ Basic query successful: {result}")
            
            # Check if tables exist
            tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_name IN ('strategies', 'backtests', 'strategy_executions', 'backtest_runs')
                ORDER BY table_name
            """)
            
            if tables:
                print(f"✓ Found {len(tables)} tables:")
                for table in tables:
                    print(f"  - {table['table_name']}")
            else:
                print("⚠️  No tables found. Please run the schema.sql file in Supabase SQL Editor")
                print("   Tables needed: strategies, backtests, strategy_executions, backtest_runs")
            
            # Get PostgreSQL version
            version = await conn.fetchval('SELECT version()')
            print(f"✓ PostgreSQL version: {version.split(',')[0]}")
        
        await pool.close()
        print("\n✅ Connection test successful!")
        return True
        
    except asyncpg.InvalidPasswordError as e:
        print(f"❌ Invalid password: {e}")
        print("Check your DATABASE_URL credentials")
        return False
    except asyncpg.InvalidCatalogNameError as e:
        print(f"❌ Database not found: {e}")
        print("Check your DATABASE_URL")
        return False
    except asyncpg.exceptions.ConnectionDoesNotExistError as e:
        print(f"❌ Connection does not exist: {e}")
        print("The connection string format may be incorrect")
        return False
    except TimeoutError as e:
        print(f"❌ Connection timeout: {e}")
        print("Check your network connection and Supabase status")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {type(e).__name__}: {e}")
        import traceback
        print("\nFull error:")
        traceback.print_exc()
        print("\nTroubleshooting:")
        print("1. Verify DATABASE_URL in .env file")
        print("2. Check Supabase dashboard for connection string")
        print("3. Ensure your IP is allowed in Supabase settings")
        print("4. Try using the direct connection (port 5432) instead of pooler")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    exit(0 if success else 1)
