"""
Development server launcher
"""
import uvicorn
from app.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    
    print("=" * 60)
    print("🚀 Starting DecisionNote Agent Development Server")
    print("=" * 60)
    print(f"📍 URL: http://{settings.host}:{settings.port}")
    print(f"📖 Docs: http://{settings.host}:{settings.port}/docs")
    print(f"🔧 Debug Mode: {settings.debug}")
    print("=" * 60)
    print()
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
