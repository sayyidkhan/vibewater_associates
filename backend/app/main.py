from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .database import connect_to_postgres, close_postgres_connection
from .routers import chat, strategies, backtests, websocket_chat, executions

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("\n" + "="*80)
    print("🚀 STARTING VIBE WATER ASSOCIATES API")
    print("="*80)
    
    # Show LLM service configuration
    from .services.llm_service import llm_service
    if llm_service.use_anthropic:
        print("🤖 LLM Service: Anthropic API")
    else:
        print("🤖 LLM Service: AWS Bedrock")
    
    try:
        await connect_to_postgres()
        print("✓ Connected to Supabase PostgreSQL")
    except Exception as e:
        print(f"⚠️  Supabase not available: {e}")
        print("   Continuing without database...")
    
    print("="*80 + "\n")
    yield
    # Shutdown
    try:
        await close_postgres_connection()
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
app.include_router(websocket_chat.router)
app.include_router(executions.router)

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
