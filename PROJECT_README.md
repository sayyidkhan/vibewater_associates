# Vibe Water Associates - Algorithmic Trading Platform

A modern, chat-first algorithmic trading strategy builder that allows users to create, backtest, and manage trading strategies through natural language and visual flowcharts.

## 🎯 Features

### Core Functionality
- **Conversational Strategy Builder**: Describe trading strategies in plain English
- **Visual Flowchart Editor**: Drag-and-drop interface to build and edit strategies
- **Backtesting Engine**: Run historical simulations with configurable parameters
- **Rich Analytics Dashboard**: Equity curves, drawdown analysis, monthly heatmaps, and KPIs
- **Strategy Management**: Filter, sort, duplicate, and share strategies
- **Trade Blotter**: View recent trade executions and performance

### Key Components
1. **Dashboard** (`/`) - Chat interface + strategy parsing + quick backtest
2. **Strategy Builder** (`/builder`) - Visual drag-and-drop flowchart editor
3. **Strategies Library** (`/strategies`) - List and manage all strategies
4. **Strategy Details** (`/strategies/[id]`) - Detailed analytics and performance metrics

## 🏗️ Architecture

### Frontend (Next.js 14 + TypeScript)
- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS v3
- **UI Components**: Custom components with Lucide icons
- **Charts**: Recharts for data visualization
- **Flow Editor**: ReactFlow for visual strategy building
- **State Management**: React hooks

### Backend (FastAPI + Python)
- **Framework**: FastAPI
- **Database**: MongoDB with Motor (async driver)
- **AI Integration**: OpenAI API for strategy parsing (configurable)
- **Backtesting**: Custom simulation engine

### Database Schema
```
- strategies: Strategy documents with schema, guardrails, metrics
- backtests: Backtest run results with equity curves and trades
- users: User accounts and preferences
- comments: Strategy comments and collaboration
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- MongoDB 7.0+
- Docker & Docker Compose (optional)

### Option 1: Docker Compose (Recommended)

1. **Clone the repository**
```bash
cd vibewater_associates
```

2. **Set up environment variables**
```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env and add your OpenAI API key if needed

# Frontend
cp frontend/env.example frontend/.env.local
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- MongoDB: mongodb://localhost:27017

### Option 2: Manual Setup

#### Backend Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Start MongoDB**
```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:7.0

# Or use local MongoDB installation
```

6. **Run the backend**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Set up environment variables**
```bash
cp env.example .env.local
# Edit .env.local if needed
```

4. **Run the development server**
```bash
npm run dev
```

5. **Open your browser**
```
http://localhost:3000
```

## 📁 Project Structure

```
vibewater_associates/
├── frontend/                 # Next.js frontend application
│   ├── app/                 # App router pages
│   │   ├── page.tsx        # Dashboard (chat + strategy creation)
│   │   ├── builder/        # Visual strategy builder
│   │   └── strategies/     # Strategy list and details
│   ├── components/          # Reusable React components
│   │   ├── Header.tsx
│   │   ├── StrategyBuilder.tsx
│   │   └── ui/             # UI primitives (Button, Card, etc.)
│   ├── lib/                # Utilities and API client
│   │   ├── api.ts          # API client functions
│   │   └── utils.ts        # Helper functions
│   ├── types/              # TypeScript type definitions
│   └── public/             # Static assets
│
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── main.py         # FastAPI app entry point
│   │   ├── config.py       # Configuration settings
│   │   ├── database.py     # MongoDB connection
│   │   ├── models.py       # Pydantic models
│   │   ├── routers/        # API route handlers
│   │   │   ├── chat.py     # Chat/parsing endpoints
│   │   │   ├── strategies.py # Strategy CRUD
│   │   │   └── backtests.py  # Backtest endpoints
│   │   └── services/       # Business logic
│   │       ├── chat_service.py
│   │       └── backtest_service.py
│   └── requirements.txt    # Python dependencies
│
├── design/                  # Design mockups and screenshots
├── docker-compose.yml       # Docker orchestration
└── PROJECT_README.md        # This file
```

## 🔌 API Endpoints

### Chat
- `POST /chat/parse` - Parse natural language into strategy schema

### Strategies
- `POST /strategies` - Create new strategy
- `GET /strategies` - List all strategies (with filters)
- `GET /strategies/{id}` - Get strategy details
- `PUT /strategies/{id}` - Update strategy
- `DELETE /strategies/{id}` - Delete strategy
- `POST /strategies/{id}/duplicate` - Duplicate strategy
- `GET /strategies/{id}/trades` - Get strategy trades

### Backtests
- `POST /backtests` - Run new backtest
- `GET /backtests/{id}` - Get backtest results
- `GET /backtests/strategy/{id}` - Get all backtests for strategy

## 🎨 Design System

### Colors
- **Background**: `#0A0E1A` (Dark navy)
- **Card**: `#1A1F2E` (Lighter navy)
- **Primary**: `#3B82F6` (Blue)
- **Success**: `#10B981` (Green)
- **Danger**: `#EF4444` (Red)
- **Warning**: `#F59E0B` (Orange)

### Components
- Custom Button component with variants (primary, secondary, outline, ghost, danger)
- Card component for content containers
- Header with navigation
- Responsive grid layouts

## 🧪 Development

### Frontend Development
```bash
cd frontend
npm run dev      # Start dev server
npm run build    # Build for production
npm run lint     # Run ESLint
```

### Backend Development
```bash
cd backend
uvicorn app.main:app --reload  # Start with hot reload
```

### Database Management
```bash
# Connect to MongoDB
mongosh mongodb://localhost:27017/vibewater_db

# View collections
show collections

# Query strategies
db.strategies.find()
```

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=vibewater_db
OPENAI_API_KEY=your_api_key_here
CORS_ORIGINS=http://localhost:3000
```

**Frontend (.env.local)**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📊 Data Models

### Strategy
```typescript
{
  id: string
  user_id: string
  name: string
  description: string
  status: "Live" | "Paper" | "Backtest"
  schema_json: StrategySchema
  guardrails: Guardrail[]
  metrics?: StrategyMetrics
  created_at: datetime
  updated_at: datetime
}
```

### Backtest Run
```typescript
{
  id: string
  strategy_id: string
  params: BacktestParams
  metrics: BacktestMetrics
  equity_series: EquityPoint[]
  trades: Trade[]
  created_at: datetime
}
```

## 🚢 Deployment

### Production Build

**Frontend**
```bash
cd frontend
npm run build
npm start
```

**Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is proprietary software for Vibe Water Associates.

## 🙏 Acknowledgments

- Next.js team for the amazing framework
- FastAPI for the high-performance Python backend
- MongoDB for the flexible NoSQL database
- Recharts for beautiful data visualizations
- ReactFlow for the visual flowchart editor

## 📞 Support

For support, email support@vibewaterassociates.com or open an issue in the repository.

---

Built with ❤️ by Vibe Water Associates
