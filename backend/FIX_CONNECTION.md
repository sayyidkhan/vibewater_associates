# Fix Connection Timeout Issue

## Problem
The transaction pooler (port 6543) is timing out. This can happen due to:
- Network/firewall restrictions
- VPN blocking the pooler port
- Regional pooler availability

## Solution: Use Direct Connection

Update your `.env` file to use the **direct connection** (port 5432):

```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.itgbimeueuwwujfhpxls.supabase.co:5432/postgres
```

### Why Direct Connection?

The direct connection (port 5432) is more reliable for:
- Development environments
- Networks with restrictive firewalls
- VPN connections
- Local testing

It still provides excellent performance with our asyncpg connection pool settings.

## Steps to Fix

1. **Update your .env file** with the direct connection string above
2. **Replace [YOUR-PASSWORD]** with your actual database password
3. **Test the connection**:
   ```bash
   uv run test_supabase_connection.py
   ```

## Expected Output

```
🔍 Testing Supabase connection...
Connection string: postgresql://postgres:[PASSWORD]@db.itgbimeueuwwujfhpxls...
✓ Connection pool created
✓ Basic query successful: 1
✓ Found 4 tables:
  - backtests
  - backtest_runs
  - strategies
  - strategy_executions
✓ PostgreSQL version: PostgreSQL 17.6

✅ Connection test successful!
```

## Your Database is Ready!

All tables have been created via Supabase MCP:
- ✅ strategies
- ✅ backtests
- ✅ strategy_executions
- ✅ backtest_runs

Once the connection test passes, you can start your application:
```bash
uvicorn app.main:app --reload
```
