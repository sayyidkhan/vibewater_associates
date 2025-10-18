import asyncpg
from .config import settings

class Database:
    pool: asyncpg.Pool = None
    
db = Database()

async def connect_to_postgres():
    """Connect to Supabase PostgreSQL using asyncpg with transaction pooler support"""
    try:
        # Optimized settings for Supabase transaction pooler (port 6543)
        # For direct connection (port 5432), these settings also work well
        db.pool = await asyncpg.create_pool(
            dsn=settings.database_url,
            min_size=2,              # Minimum connections in pool
            max_size=10,             # Maximum connections (transaction pooler handles this efficiently)
            max_queries=50000,       # Max queries per connection before recycling
            max_inactive_connection_lifetime=300,  # 5 minutes
            command_timeout=60,      # Command timeout in seconds
            timeout=30,              # Connection establishment timeout (30 seconds)
            statement_cache_size=0,  # Disable prepared statements for pgbouncer compatibility
            server_settings={
                'application_name': 'vibewater_associates',
                'jit': 'off'         # Disable JIT for faster query execution
            }
        )
        
        # Test the connection
        async with db.pool.acquire() as conn:
            await conn.fetchval('SELECT 1')
        
        print("✓ Successfully connected to Supabase PostgreSQL!")
        print(f"  Pool: min={2}, max={10} connections")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        raise

async def close_postgres_connection():
    """Close the PostgreSQL connection pool"""
    if db.pool:
        await db.pool.close()
        print("✓ Closed PostgreSQL connection pool")

def get_database():
    """Get the database pool instance"""
    if db.pool is None:
        raise Exception("Database not connected. Call connect_to_postgres() first.")
    return db.pool
