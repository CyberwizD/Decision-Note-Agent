"""
DecisionNote Agent - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_database
from routes import a2a, triggers
from app.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events - runs on startup and shutdown
    """
    # Startup
    print("🚀 Starting DecisionNote Agent...")
    await init_database()
    print("✅ DecisionNote Agent ready!")
    
    yield
    
    # Shutdown
    print("👋 Shutting down DecisionNote Agent...")


# Create FastAPI app
app = FastAPI(
    title="DecisionNote Agent",
    description="AI-powered team decision tracking agent for Telex",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(a2a.router, tags=["A2A Protocol"])
app.include_router(triggers.router, tags=["Triggers"])


@app.get("/")
async def root():
    """
    Root endpoint - health check
    """
    return {
        "service": "DecisionNote Agent",
        "status": "running",
        "version": "1.0.0",
        "description": "AI-powered team decision tracking agent for Telex"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "decisionnote-agent"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
