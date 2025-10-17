# Vibe Water Associates - Backend API

FastAPI backend for the Vibe Water Associates algorithmic trading platform.

## Setup

### Local Development

1. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Start MongoDB**
```bash
docker run -d -p 27017:27017 --name mongodb mongo:7.0
```

5. **Run the server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Access API documentation**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Chat
- `POST /chat/parse` - Parse natural language strategy

### Strategies
- `POST /strategies` - Create strategy
- `GET /strategies` - List strategies
- `GET /strategies/{id}` - Get strategy
- `PUT /strategies/{id}` - Update strategy
- `DELETE /strategies/{id}` - Delete strategy
- `POST /strategies/{id}/duplicate` - Duplicate strategy
- `GET /strategies/{id}/trades` - Get trades

### Backtests
- `POST /backtests` - Run backtest
- `GET /backtests/{id}` - Get backtest
- `GET /backtests/strategy/{id}` - Get strategy backtests

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── database.py          # MongoDB connection
│   ├── models.py            # Pydantic models
│   ├── routers/             # API routes
│   │   ├── chat.py
│   │   ├── strategies.py
│   │   └── backtests.py
│   └── services/            # Business logic
│       ├── chat_service.py
│       └── backtest_service.py
├── requirements.txt         # Dependencies
└── Dockerfile              # Docker configuration
```

## Environment Variables

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=vibewater_db
OPENAI_API_KEY=your_api_key_here
CORS_ORIGINS=http://localhost:3000
```

## Testing

```bash
# Run tests (when implemented)
pytest

# Run with coverage
pytest --cov=app
```

## Deployment

### Docker
```bash
docker build -t vibewater-backend .
docker run -p 8000:8000 vibewater-backend
```

### Production
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```
