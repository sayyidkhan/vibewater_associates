"""
Test database connection with detailed error reporting
"""
import asyncio
import asyncpg
from app.config import settings

async def test_connection():
    print("\n" + "="*80)
    print("🔍 TESTING DATABASE CONNECTION")
    print("="*80)
    
    print(f"\n📋 Connection Details:")
    print(f"   DATABASE_URL: {settings.database_url[:50]}..." if len(settings.database_url) > 50 else f"   DATABASE_URL: {settings.database_url}")
    
    if not settings.database_url:
        print("\n❌ ERROR: DATABASE_URL is empty or not set in .env file")
        return
    
    try:
        print("\n⏳ Attempting to create connection pool...")
        pool = await asyncpg.create_pool(
            dsn=settings.database_url,
            min_size=1,
            max_size=2,
            timeout=30,
            command_timeout=60,
            statement_cache_size=0,
        )
        
        print("✅ Pool created successfully")
        
        print("\n⏳ Testing connection with SELECT 1...")
        async with pool.acquire() as conn:
            result = await conn.fetchval('SELECT 1')
            print(f"✅ Query successful, result: {result}")
        
        print("\n⏳ Testing database access...")
        async with pool.acquire() as conn:
            version = await conn.fetchval('SELECT version()')
            print(f"✅ PostgreSQL version: {version[:80]}...")
        
        await pool.close()
        print("\n✅ CONNECTION TEST PASSED!")
        
    except asyncpg.InvalidPasswordError as e:
        print(f"\n❌ AUTHENTICATION ERROR: {e}")
        print("   Check your password in DATABASE_URL")
        
    except asyncpg.InvalidCatalogNameError as e:
        print(f"\n❌ DATABASE NOT FOUND: {e}")
        print("   Check your database name in DATABASE_URL")
        
    except asyncpg.PostgresConnectionError as e:
        print(f"\n❌ CONNECTION ERROR: {e}")
        print("   Check your host and port in DATABASE_URL")
        
    except asyncpg.PostgresError as e:
        print(f"\n❌ POSTGRES ERROR: {e}")
        print(f"   Error type: {type(e).__name__}")
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        print("\n📋 Full traceback:")
        traceback.print_exc()
    
    print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(test_connection())
