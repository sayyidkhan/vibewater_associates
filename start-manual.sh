#!/bin/bash

echo "🌊 Starting Vibe Water Associates (Manual Mode)..."
echo ""

# Check if MongoDB is running
if ! nc -z localhost 27017 2>/dev/null; then
    echo "⚠️  MongoDB not detected on port 27017"
    echo "Starting MongoDB with Docker..."
    docker run -d -p 27017:27017 --name vibewater_mongodb mongo:7.0 2>/dev/null || echo "MongoDB container already exists"
    sleep 3
fi

# Start Backend
echo "🚀 Starting Backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
    cp .env.example .env
fi

echo "Backend starting on http://localhost:8000"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

cd ..

# Start Frontend
echo "🚀 Starting Frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies (this may take a few minutes)..."
    npm install
fi

if [ ! -f ".env.local" ]; then
    cp env.example .env.local
fi

echo "Frontend starting on http://localhost:3000"
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "✅ Services started!"
echo ""
echo "📍 Access points:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "🛑 To stop services:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo "   Or press Ctrl+C and run: pkill -f 'uvicorn|next-server'"
echo ""

# Wait for user interrupt
wait
