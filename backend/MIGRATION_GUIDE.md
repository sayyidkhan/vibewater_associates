# MongoDB to Supabase Migration Guide

This guide explains how to migrate from MongoDB to Supabase PostgreSQL.

## Prerequisites

1. A Supabase account and project
2. Your Supabase connection string (DATABASE_URL)

## Migration Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install `asyncpg` instead of `motor` and `pymongo`.

### 2. Set Up Supabase Database

1. Log in to your Supabase dashboard
2. Go to the SQL Editor
3. Run the schema from `schema.sql` to create all necessary tables:
   - `strategies`
   - `backtests`
   - `strategy_executions`
   - `backtest_runs`

### 3. Configure Environment Variables

Update your `.env` file with your Supabase connection string.

**Recommended: Use Transaction Pooler (Port 6543)**

```env
DATABASE_URL=postgresql://postgres.[YOUR-PROJECT-REF]:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

**Alternative: Direct Connection (Port 5432)**

```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
```

You can find your connection string in:
- Supabase Dashboard → Settings → Database → Connection String
- Choose "Transaction" mode for the pooler (port 6543)
- Choose "Direct connection" for port 5432

#### Why Use Transaction Pooler?

The transaction pooler (port 6543) is recommended because:
- **Better Performance**: Handles connection pooling at the server level
- **More Connections**: Supports more concurrent connections
- **Lower Latency**: Faster connection establishment
- **Automatic Scaling**: Supabase manages the pool for you

Our asyncpg pool settings are optimized for the transaction pooler with:
- Connection recycling after 50,000 queries
- 5-minute inactive connection lifetime
- JIT disabled for faster query execution

#### When to Use Each Connection Type

**Use Transaction Pooler (6543) for:**
- Production applications
- High-traffic APIs
- Applications with many concurrent users
- Standard CRUD operations

**Use Direct Connection (5432) for:**
- Running database migrations
- Admin tasks requiring prepared statements
- Long-running transactions
- Database schema changes

### 4. Verify Connection

The application will automatically connect to Supabase on startup. Check the logs for:

```
✓ Successfully connected to Supabase PostgreSQL!
```

## Key Changes

### Database Client
- **Before**: Motor (MongoDB async driver)
- **After**: asyncpg (PostgreSQL async driver)

### Connection Pattern
- **Before**: `db.collection.find_one()`
- **After**: `pool.acquire() → conn.fetchrow()`

### Query Syntax
- **Before**: MongoDB query language `{"field": "value"}`
- **After**: SQL with parameterized queries `SELECT * FROM table WHERE field = $1`

### Data Types
- **Before**: BSON/JSON documents with `_id` ObjectId
- **After**: PostgreSQL with UUID primary keys and JSONB columns

## Database Schema

All tables use:
- **UUID** for primary keys (auto-generated)
- **JSONB** for complex nested data (schema_json, metrics, etc.)
- **TIMESTAMPTZ** for timestamps with timezone support
- **Indexes** on frequently queried columns

## Troubleshooting

### Connection Issues

If you see connection errors:

1. Verify your DATABASE_URL is correct
2. Check that your IP is allowed in Supabase (Settings → Database → Connection Pooling)
3. Ensure you're using the connection pooler port (6543) for production

### Query Errors

If you see SQL syntax errors:
- PostgreSQL uses `$1, $2, $3` for parameters (not `?` or named parameters)
- JSONB columns need to be accessed with `->` or `->>`
- UUIDs are stored as strings in the application layer

### Performance

For better performance:
- Use connection pooling (already configured)
- Add indexes on frequently queried columns (already in schema.sql)
- Use JSONB operators for efficient JSON queries

## Rollback

If you need to rollback to MongoDB:

1. Restore the original files from git
2. Update `.env` with MongoDB connection string
3. Reinstall dependencies: `pip install motor pymongo`

## Support

For issues:
- Check Supabase logs in Dashboard → Logs
- Review application logs for detailed error messages
- Consult asyncpg documentation: https://magicstack.github.io/asyncpg/
