from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.database import init_db
from backend.app.api.routes import (
    health,
    signs,
    orchestrator,
    vision,
    speech,
    translation,
    tests,
    auth,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database tables
    init_db()
    yield
    # Shutdown logic if any

app = FastAPI(
    title="Signify API — AI Sign-Language Communication",
    description="Backend services and state-driven agent orchestrator connecting Indian Sign Language (ISL) gestures with multilingual speech and text.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if (origins and "*" not in origins) else ["*"],
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(signs.router, prefix="/api/v1")
app.include_router(orchestrator.router, prefix="/api/v1")
app.include_router(vision.router, prefix="/api/v1")
app.include_router(speech.router, prefix="/api/v1")
app.include_router(translation.router, prefix="/api/v1")
app.include_router(tests.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "service": "Signify Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "OPERATIONAL"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=(settings.ENVIRONMENT == "development")
    )

