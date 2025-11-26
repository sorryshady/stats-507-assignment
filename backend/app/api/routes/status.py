"""Status and health check endpoints."""

from fastapi import APIRouter
from app.core.system import get_system_manager

router = APIRouter()


@router.get("/status")
async def get_status():
    """
    Get system status including model loading and GPU availability.

    Returns:
        JSON with system status, model status, and GPU information
    """
    system_manager = get_system_manager()

    # Initialize if not already initialized (lazy initialization)
    if not system_manager.initialized:
        try:
            system_manager.initialize()
        except Exception as e:
            # Return status even if initialization fails
            return {
                "initialized": False,
                "error": str(e),
                "models": {
                    "yolo": "not_loaded",
                    "blip": "not_loaded",
                    "ollama": "unknown",
                },
                "gpu": {"available": False, "type": "unknown"},
            }

    return system_manager.get_status()


@router.get("/health")
async def health_check():
    """
    Simple health check endpoint.

    Returns:
        Simple status message
    """
    return {"status": "healthy", "message": "System is running"}
