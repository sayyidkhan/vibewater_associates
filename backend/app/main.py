from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .database import connect_to_mongo, close_mongo_connection
from .routers import chat, strategies, backtests

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await connect_to_mongo()
        print("✓ Connected to MongoDB")
    except Exception as e:
        print(f"⚠️  MongoDB not available: {e}")
        print("   Continuing without database...")
    yield
    # Shutdown
    try:
        await close_mongo_connection()
    except:
        pass

app = FastAPI(
    title="Vibe Water Associates API",
    description="Algorithmic Trading Strategy Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(strategies.router)
app.include_router(backtests.router)

@app.get("/")
async def root():
    return {
        "message": "Vibe Water Associates API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
