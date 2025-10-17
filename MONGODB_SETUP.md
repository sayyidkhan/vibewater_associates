# MongoDB Atlas Setup Guide

## 🎯 Connect to MongoDB Atlas

Your backend is now configured to use **MongoDB Atlas** (cloud database) instead of local MongoDB.

## 📝 Setup Steps

### Step 1: Update `.env` File

Edit `/backend/.env` and replace the MongoDB connection string with your credentials:

```bash
# Replace <db_username> and <db_password> with your actual credentials
MONGODB_URL=mongodb+srv://<db_username>:<db_password>@promptrade.uoxibp4.mongodb.net/?retryWrites=true&w=majority&appName=promptrade
DATABASE_NAME=vibewater_db
OPENAI_API_KEY=your_openai_api_key_here
COINGECKO_API_KEY=CG-D8KTuE34nPVqfj2NfaDdgred
CORS_ORIGINS=http://localhost:3000
```

**Example** (with actual credentials):
```bash
MONGODB_URL=mongodb+srv://myuser:mypassword123@promptrade.uoxibp4.mongodb.net/?retryWrites=true&w=majority&appName=promptrade
DATABASE_NAME=vibewater_db
```

### Step 2: Install Dependencies

```bash
cd backend
uv pip install -r requirements.txt
```

This will install `pymongo[srv]` which includes support for MongoDB Atlas (SRV connection strings).

### Step 3: Start Backend

```bash
uv run uvicorn app.main:app --reload
```

You should see:
```
✓ Pinged MongoDB deployment. Successfully connected to MongoDB Atlas!
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 4: Run Backtest

```bash
# In a new terminal
cd backend
uv run run_backtest.py
```

You should see:
```
✓ Successfully downloaded 90 data points from CoinGecko
✓ Saved to MongoDB
✅ BACKTEST COMPLETED AND SAVED!
```

## 🔍 What Changed

### 1. Database Connection (`app/database.py`)
```python
from pymongo.server_api import ServerApi

# Now uses ServerApi for MongoDB Atlas
db.client = AsyncIOMotorClient(
    settings.mongodb_url,
    server_api=ServerApi('1')
)

# Tests connection with ping
await db.client.admin.command('ping')
```

### 2. Requirements (`requirements.txt`)
```
pymongo[srv]==4.6.1  # Added [srv] for Atlas support
```

### 3. Environment Variables (`.env`)
```bash
# Changed from local to Atlas
MONGODB_URL=mongodb+srv://...@promptrade.uoxibp4.mongodb.net/...
```

## 📊 Data Storage

When you run a backtest, it saves to MongoDB Atlas:

**Database**: `vibewater_db`  
**Collection**: `backtests`

**Document Structure**:
```json
{
  "_id": "ObjectId(...)",
  "strategy_id": "1",
  "params": {
    "symbols": ["BTC"],
    "start_date": "2025-07-14",
    "end_date": "2025-10-12",
    "initial_capital": 10000
  },
  "metrics": {
    "total_return": 15.23,
    "sharpe_ratio": 1.45,
    "max_drawdown": -9.23,
    "trades": 5
  },
  "equity_series": [...],
  "trades": [...]
}
```

## 🔐 Security Best Practices

### ✅ DO:
- Keep `.env` file in `.gitignore` (already done)
- Use environment variables for credentials
- Rotate passwords regularly
- Use IP whitelist in MongoDB Atlas

### ❌ DON'T:
- Commit `.env` file to git
- Hardcode credentials in code
- Share credentials in chat/email
- Use weak passwords

## 🧪 Test Connection

Create a test script to verify MongoDB connection:

```python
# test_mongo.py
import asyncio
from app.database import connect_to_mongo, get_database

async def test():
    await connect_to_mongo()
    db = get_database()
    
    # Insert test document
    result = await db.test.insert_one({"message": "Hello MongoDB!"})
    print(f"✓ Inserted document with ID: {result.inserted_id}")
    
    # Read it back
    doc = await db.test.find_one({"_id": result.inserted_id})
    print(f"✓ Retrieved: {doc}")
    
    # Clean up
    await db.test.delete_one({"_id": result.inserted_id})
    print("✓ Test completed successfully!")

asyncio.run(test())
```

Run it:
```bash
uv run test_mongo.py
```

## 🐛 Troubleshooting

### Error: "Authentication failed"
- Check username and password in `.env`
- Make sure to URL-encode special characters in password
- Example: `p@ssw0rd` → `p%40ssw0rd`

### Error: "Connection timeout"
- Check internet connection
- Verify IP whitelist in MongoDB Atlas
- Try adding `0.0.0.0/0` (allow all IPs) for testing

### Error: "No module named 'pymongo.srv_resolver'"
- Install with SRV support: `uv pip install "pymongo[srv]"`

### Error: "Database not connected"
- Make sure backend is running
- Check that `connect_to_mongo()` was called on startup

## 📈 View Data in MongoDB Atlas

1. Go to https://cloud.mongodb.com
2. Click on your cluster (promptrade)
3. Click "Browse Collections"
4. Select `vibewater_db` → `backtests`
5. See all your backtest results!

## 🚀 Next Steps

1. **Update `.env`** with your MongoDB credentials
2. **Install dependencies**: `uv pip install -r requirements.txt`
3. **Start backend**: `uv run uvicorn app.main:app --reload`
4. **Run backtest**: `uv run run_backtest.py`
5. **View in frontend**: http://localhost:3000/strategies/1

Your backtests will now be saved to MongoDB Atlas and persist across sessions! 🎉
