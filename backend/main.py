"""
Anime Reality AI — FastAPI Server Master Entrypoint.
Provides REST and WebSocket endpoints for Flutter mobile client and local AI inference.
"""

import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.database import init_db
from backend.routes.health import router as health_router
from backend.routes.image import router as image_router
from backend.routes.video import router as video_router
from backend.routes.jobs import router as jobs_router
from backend.routes.styles import router as styles_router
from backend.routes.models import router as models_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("AnimeReality.API")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle startup and shutdown tasks."""
    logger.info("Starting Anime Reality AI Backend Engine...")
    init_db()
    # Ensure outputs directory exists
    Path("outputs/jobs").mkdir(parents=True, exist_ok=True)
    Path("outputs/uploads").mkdir(parents=True, exist_ok=True)
    logger.info("Database initialized and storage workspaces verified.")
    yield
    logger.info("Shutting down Anime Reality AI Backend Engine...")


app = FastAPI(
    title="Anime Reality AI Backend API",
    description="High-performance AI backend for Real-World Photo & Video Anime Transformation.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration for Flutter Mobile & Web Clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health_router)
app.include_router(image_router)
app.include_router(video_router)
app.include_router(jobs_router)
app.include_router(styles_router)
app.include_router(models_router)


@app.get("/")
async def root_endpoint():
    """Welcome and quick health check."""
    from inference.memory_manager import VRAMManager
    hw = VRAMManager.get_hardware_status()
    return {
        "message": "Anime Reality AI Backend Engine is Running!",
        "version": "1.0.0",
        "docs_url": "/docs",
        "hardware": hw
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred in Anime Reality AI engine."}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
