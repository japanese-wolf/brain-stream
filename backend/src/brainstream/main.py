"""FastAPI application entry point."""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from brainstream import __version__
from brainstream.api.v1.router import router as api_router
from brainstream.core.config import settings
from brainstream.core.database import close_db, init_db
from brainstream.core.scheduler import setup_scheduler, start_scheduler, stop_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info(f"Starting BrainStream v{__version__}")
    await init_db()

    # Start scheduler if enabled
    enable_scheduler = os.environ.get("BRAINSTREAM_SCHEDULER", "true").lower() == "true"
    fetch_interval = int(os.environ.get("BRAINSTREAM_FETCH_INTERVAL", "30"))

    if enable_scheduler:
        setup_scheduler(
            fetch_interval_minutes=fetch_interval,
            start_immediately=True,
        )
        start_scheduler()
        logger.info(f"Scheduler enabled (fetch every {fetch_interval} minutes)")
    else:
        logger.info("Scheduler disabled")

    yield

    # Shutdown
    stop_scheduler()
    await close_db()
    logger.info("BrainStream shutdown complete")


app = FastAPI(
    title="BrainStream",
    description="Intelligence hub for cloud and AI updates",
    version=__version__,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from brainstream.core.scheduler import get_scheduler_status

    return {
        "status": "healthy",
        "version": __version__,
        "scheduler": get_scheduler_status(),
    }


@app.get("/")
async def root():
    """Root endpoint - returns API info or serves frontend."""
    # Check if frontend build exists
    frontend_path = Path(__file__).parent.parent.parent.parent / "frontend" / "dist" / "index.html"
    if frontend_path.exists():
        return FileResponse(frontend_path)

    # Return API info
    return {
        "name": "BrainStream API",
        "version": __version__,
        "docs": "/docs",
        "health": "/health",
    }


# Serve static frontend files if they exist
frontend_dist = Path(__file__).parent.parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
