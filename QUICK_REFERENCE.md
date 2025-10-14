# Quick Reference Guide

## 🚀 Start the Application

```bash
# Option 1: One-command start (Docker)
./start.sh

# Option 2: Docker Compose
docker-compose up -d

# Option 3: Manual (requires MongoDB running)
# Terminal 1 - Backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend && npm run dev
```

## 🌐 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Main application |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| MongoDB | mongodb://localhost:27017 | Database |

## 📄 Key Pages

| Route | Description |
|-------|-------------|
| `/` | Dashboard - Chat interface for strategy creation |
| `/builder` | Visual strategy builder with drag-and-drop |
| `/strategies` | Strategy library with filters |
| `/strategies/[id]` | Detailed analytics for a strategy |

## 🔧 Common Commands

### Frontend
```bash
cd frontend
npm install              # Install dependencies
npm run dev             # Start dev server
npm run build           # Build for production
npm run lint            # Run linter
```

### Backend
```bash
cd backend
pip install -r requirements.txt    # Install dependencies
uvicorn app.main:app --reload      # Start dev server
python -m pytest                   # Run tests (when added)
```

### Docker
```bash
docker-compose up -d              # Start all services
docker-compose down               # Stop all services
docker-compose logs -f            # View logs
docker-compose restart backend    # Restart backend only
```

## 📊 API Endpoints Quick Reference

### Chat
- `POST /chat/parse` - Parse strategy from text

### Strategies
- `POST /strategies` - Create
- `GET /strategies` - List all
- `GET /strategies/{id}` - Get one
- `PUT /strategies/{id}` - Update
- `DELETE /strategies/{id}` - Delete
- `POST /strategies/{id}/duplicate` - Duplicate

### Backtests
- `POST /backtests` - Run backtest
- `GET /backtests/{id}` - Get results

## 🔐 Environment Variables

### Backend (.env)
```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=vibewater_db
OPENAI_API_KEY=sk-...
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🐛 Troubleshooting

### Frontend won't start
```bash
cd frontend
rm -rf node_modules .next
npm install
npm run dev
```

### Backend errors
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### MongoDB connection issues
```bash
# Check if MongoDB is running
docker ps | grep mongo

# Start MongoDB
docker run -d -p 27017:27017 --name mongodb mongo:7.0
```

### Port already in use
```bash
# Find and kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

## 📚 Documentation Files

- `README.md` - Project overview and quick start
- `PROJECT_README.md` - Complete documentation
- `IMPLEMENTATION_SUMMARY.md` - What was built
- `frontend/README.md` - Frontend docs
- `backend/README.md` - Backend docs

## 🎨 Design Files

Located in `design/` folder:
- `dashboard.png` - Main dashboard
- `strategy_building_chat_dragdrop.png` - Builder view
- `strategies.png` - Strategy list
- `individual_strategy.png` - Analytics view

## 💻 Development Workflow

1. **Start services**: `./start.sh` or `docker-compose up -d`
2. **Make changes**: Edit files in `frontend/` or `backend/`
3. **Hot reload**: Both frontend and backend auto-reload
4. **Test**: Open http://localhost:3000
5. **Check API**: Visit http://localhost:8000/docs
6. **Stop**: `docker-compose down` or Ctrl+C

## 🔍 Useful Queries

### MongoDB
```javascript
// Connect
mongosh mongodb://localhost:27017/vibewater_db

// List strategies
db.strategies.find().pretty()

// Count strategies
db.strategies.countDocuments()

// Find by status
db.strategies.find({status: "Live"})
```

## 📦 Project Structure

```
vibewater_associates/
├── frontend/          # Next.js app
├── backend/           # FastAPI app
├── design/            # Design mockups
├── docker-compose.yml # Docker config
└── start.sh          # Quick start
```

## ⚡ Quick Tips

1. **Always check logs**: `docker-compose logs -f`
2. **API testing**: Use http://localhost:8000/docs
3. **Hot reload**: Changes auto-refresh in dev mode
4. **Clean restart**: `docker-compose down && docker-compose up -d`
5. **Database reset**: `docker-compose down -v` (removes volumes)

---

For detailed information, see [PROJECT_README.md](./PROJECT_README.md)
