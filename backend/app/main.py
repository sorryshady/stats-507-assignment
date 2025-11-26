"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes import status, camera, narration
from app.middleware.error_handler import (
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Create FastAPI app with lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    logger.info("Starting Describe My Environment API...")
    logger.info("API documentation available at /docs")
    logger.info("API endpoints:")
    logger.info("  GET  /api/status - System status")
    logger.info("  GET  /api/health - Health check")
    logger.info("  POST /api/narration - Generate narration")
    logger.info("  WS   /api/ws/camera - Real-time frame processing")

    # Pre-initialize system manager (optional - can be lazy loaded)
    try:
        from app.core.system import get_system_manager

        logger.info("Pre-initializing system manager (loading models)...")
        system_manager = get_system_manager()
        system_manager.initialize()
        logger.info("✅ System manager initialized successfully")
    except Exception as e:
        logger.warning(
            f"⚠️  System manager initialization deferred (will initialize on first request): {e}"
        )
        logger.info(
            "   This is normal if models are still downloading or Ollama is not running"
        )

    yield

    # Shutdown
    logger.info("Shutting down Describe My Environment API...")


app = FastAPI(
    title="Describe My Environment API",
    description="Backend API for dual-loop vision system",
    version="1.0.0-beta",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(status.router, prefix="/api", tags=["status"])
app.include_router(camera.router, prefix="/api", tags=["camera"])
app.include_router(narration.router, prefix="/api", tags=["narration"])


@app.get("/")
def root():
    """Root endpoint - API information."""
    return {
        "status": "running",
        "message": "Describe My Environment API",
        "version": "1.0.0-beta",
        "docs": "/docs",
        "endpoints": {
            "status": "/api/status",
            "health": "/api/health",
            "narration": "/api/narration",
            "websocket": "/api/ws/camera",
        },
    }
