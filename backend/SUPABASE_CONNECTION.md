# Supabase Connection Configuration

## Quick Reference

### Transaction Pooler (Recommended)
```
Port: 6543
Mode: Transaction
Format: postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

### Direct Connection
```
Port: 5432
Mode: Direct
Format: postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

## How to Get Your Connection String

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Navigate to: **Settings** → **Database** → **Connection String**
4. Choose your connection mode:
   - **Transaction** (port 6543) - for production
   - **Direct connection** (port 5432) - for migrations

## Connection Pool Settings

Our application uses these optimized settings for asyncpg:

```python
min_size=2                              # Minimum connections
max_size=10                             # Maximum connections
max_queries=50000                       # Queries before recycling
max_inactive_connection_lifetime=300   # 5 minutes timeout
command_timeout=60                      # Query timeout
```

### Why These Settings?

- **min_size=2**: Keeps 2 connections warm for instant queries
- **max_size=10**: Limits total connections (Supabase pooler handles scaling)
- **max_queries=50000**: Prevents connection staleness
- **max_inactive_connection_lifetime=300**: Closes idle connections after 5 minutes
- **command_timeout=60**: Prevents hung queries

## Connection Limits

### Free Tier
- **Direct**: 60 connections
- **Pooler**: 200 connections

### Pro Tier
- **Direct**: 200 connections
- **Pooler**: 3000 connections

## Troubleshooting

### "Too many connections" Error

**Solution 1**: Use transaction pooler (port 6543)
```env
DATABASE_URL=postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

**Solution 2**: Reduce max_size in database.py
```python
max_size=5  # Reduce from 10 to 5
```

### Connection Timeout

**Check 1**: Verify your IP is allowed
- Dashboard → Settings → Database → Connection Pooling
- Add your IP to allowlist

**Check 2**: Test connection
```bash
python test_supabase_connection.py
```

### SSL/TLS Issues

Supabase requires SSL by default. asyncpg handles this automatically, but if you encounter issues:

```python
# In database.py, add ssl parameter
db.pool = await asyncpg.create_pool(
    dsn=settings.database_url,
    ssl='require'  # Force SSL
)
```

## Performance Tips

### 1. Use Transaction Pooler
Always use port 6543 for production applications.

### 2. Connection Reuse
The pool automatically reuses connections. Don't create new pools per request.

### 3. Proper Cleanup
Always use `async with pool.acquire()` to ensure connections are returned:

```python
async with pool.acquire() as conn:
    result = await conn.fetchrow("SELECT * FROM table")
# Connection automatically returned to pool
```

### 4. Monitor Usage
Check connection usage in Supabase Dashboard:
- Dashboard → Database → Connection Pooling

## Region-Specific Poolers

Supabase provides regional poolers for lower latency:

- **US East**: `aws-0-us-east-1.pooler.supabase.com`
- **US West**: `aws-0-us-west-1.pooler.supabase.com`
- **EU Central**: `aws-0-eu-central-1.pooler.supabase.com`
- **AP Southeast**: `aws-0-ap-southeast-1.pooler.supabase.com`

Choose the region closest to your application deployment.

## Security Best Practices

1. **Never commit .env**: Already in .gitignore
2. **Use environment variables**: Don't hardcode credentials
3. **Rotate passwords**: Change database password periodically
4. **Limit IP access**: Restrict to known IPs in production
5. **Use SSL**: Always enabled by default

## Additional Resources

- [Supabase Connection Pooling Docs](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)
- [PostgreSQL Connection Pooling](https://www.postgresql.org/docs/current/runtime-config-connection.html)
