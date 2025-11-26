"""Narration endpoint for cognitive loop."""

import logging
import time
import base64
import numpy as np
import cv2
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.core.system import get_system_manager

logger = logging.getLogger(__name__)

router = APIRouter()


class NarrationRequest(BaseModel):
    """Request model for narration endpoint."""
    frame: Optional[str] = None  # Base64 encoded image (optional)


class NarrationResponse(BaseModel):
    """Response model for narration endpoint."""
    narration: Optional[str]
    scene_description: str
    object_movements: list[str]
    processing_time_ms: float


def decode_base64_image(image_data: str) -> np.ndarray:
    """
    Decode base64 encoded image to numpy array.
    
    Args:
        image_data: Base64 encoded image string (may include data URL prefix)
    
    Returns:
        Numpy array in BGR format (OpenCV format)
    """
    # Remove data URL prefix if present (e.g., "data:image/jpeg;base64,...")
    if "," in image_data:
        image_data = image_data.split(",")[1]
    
    # Decode base64
    image_bytes = base64.b64decode(image_data)
    
    # Convert to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    
    # Decode image
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if frame is None:
        raise ValueError("Failed to decode image")
    
    return frame


@router.post("/narration", response_model=NarrationResponse)
async def generate_narration(request: NarrationRequest):
    """
    Generate narration for a frame using the cognitive loop.
    
    This endpoint:
    1. Takes an optional base64-encoded image
    2. Generates scene description using BLIP
    3. Analyzes object trajectories
    4. Generates natural language narration using Llama 3.2
    
    Args:
        request: NarrationRequest with optional frame data
    
    Returns:
        NarrationResponse with narration, scene description, and object movements
    
    Raises:
        HTTPException: If system not initialized or processing fails
    """
    system_manager = get_system_manager()
    
    # Initialize if not already initialized
    if not system_manager.initialized:
        try:
            system_manager.initialize()
        except Exception as e:
            logger.error(f"Failed to initialize system: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"System initialization failed: {str(e)}"
            )
    
    # Check if frame is provided
    if request.frame is None:
        raise HTTPException(
            status_code=400,
            detail="Frame data is required. Please provide 'frame' field with base64-encoded image."
        )
    
    try:
        # Decode image
        frame = decode_base64_image(request.frame)
        
        # Measure processing time
        start_time = time.time()
        
        # Generate narration
        result = system_manager.generate_narration(frame)
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        logger.info(f"Narration generated in {processing_time_ms:.2f}ms")
        
        return NarrationResponse(
            narration=result["narration"],
            scene_description=result["scene_description"],
            object_movements=result["object_movements"],
            processing_time_ms=processing_time_ms
        )
        
    except ValueError as e:
        logger.error(f"Image decoding error: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image data: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error generating narration: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate narration: {str(e)}"
        )

