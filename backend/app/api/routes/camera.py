"""WebSocket endpoint for camera frame processing."""

import json
import base64
import logging
import asyncio
import numpy as np
import cv2
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.system import get_system_manager

logger = logging.getLogger(__name__)

router = APIRouter()


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


def encode_image_to_base64(frame: np.ndarray) -> str:
    """
    Encode numpy array image to base64 string.
    
    Args:
        frame: Numpy array in BGR format
    
    Returns:
        Base64 encoded string
    """
    # Encode image as JPEG
    success, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    
    if not success:
        raise ValueError("Failed to encode image")
    
    # Convert to base64
    image_bytes = buffer.tobytes()
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    return image_base64


@router.websocket("/ws/camera")
async def websocket_camera(websocket: WebSocket):
    """
    WebSocket endpoint for real-time camera frame processing.
    
    Client sends: {"type": "frame", "data": "base64_image", "timestamp": 123.456}
    Server responds: {"type": "frame_result", "detections": [...], "hazards": [...], ...}
    """
    await websocket.accept()
    logger.info("WebSocket client connected")
    
    # Get shared system manager instance
    system_manager = get_system_manager()
    
    # Initialize system manager
    try:
        system_manager.initialize()
    except Exception as e:
        logger.error(f"Failed to initialize system: {e}")
        await websocket.send_json({
            "type": "error",
            "message": f"System initialization failed: {str(e)}"
        })
        await websocket.close()
        return
    
    frame_id = 0
    processing = False
    pending_frame = None  # Store latest frame while processing
    
    async def process_frame_async(frame_data, current_frame_id, timestamp):
        """Process frame asynchronously in thread pool to avoid blocking event loop."""
        nonlocal processing
        try:
            # Decode image (fast, can stay in async)
            frame = decode_base64_image(frame_data)
            
            # Run CPU-bound processing in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,  # Use default thread pool
                system_manager.process_frame,
                frame,
                current_frame_id,
                timestamp
            )
            
            response = {
                "type": "frame_result",
                "frame_id": result["frame_id"],
                "timestamp": result["timestamp"],
                "detections": result["detections"],
                "hazards": result["hazards"],
            }
            
            # Include annotated frame if available
            if result["annotated_frame"] is not None:
                annotated_base64 = encode_image_to_base64(result["annotated_frame"])
                response["annotated_frame"] = annotated_base64
            
            await websocket.send_json(response)
        except Exception as e:
            logger.error(f"Error processing frame: {e}", exc_info=True)
            try:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Frame processing error: {str(e)}"
                })
            except:
                pass
        finally:
            processing = False
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
                continue
            
            # Process frame message
            if message.get("type") == "frame":
                image_data = message.get("data", "")
                timestamp = message.get("timestamp", None)
                
                if not image_data:
                    await websocket.send_json({
                        "type": "error",
                        "message": "No image data provided"
                    })
                    continue
                
                # If already processing, store the latest frame and skip
                if processing:
                    pending_frame = (image_data, frame_id, timestamp)
                    frame_id += 1
                    continue
                
                # Start processing this frame
                processing = True
                current_frame_id = frame_id
                frame_id += 1
                
                # Process in background (non-blocking)
                asyncio.create_task(process_frame_async(image_data, current_frame_id, timestamp))
                
                # If there's a pending frame, process it next
                if pending_frame:
                    pending_data, pending_id, pending_ts = pending_frame
                    pending_frame = None
                    processing = True
                    current_frame_id = frame_id
                    frame_id += 1
                    asyncio.create_task(process_frame_async(pending_data, current_frame_id, pending_ts))
            
            elif message.get("type") == "ping":
                # Heartbeat/ping message
                await websocket.send_json({"type": "pong"})
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {message.get('type')}"
                })
    
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Server error: {str(e)}"
            })
        except:
            pass  # Connection may already be closed

