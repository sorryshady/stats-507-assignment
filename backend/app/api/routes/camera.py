"""WebSocket endpoint for camera frame processing."""

import json
import base64
import logging
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
                try:
                    # Extract frame data
                    image_data = message.get("data", "")
                    timestamp = message.get("timestamp", None)
                    
                    if not image_data:
                        await websocket.send_json({
                            "type": "error",
                            "message": "No image data provided"
                        })
                        continue
                    
                    # Decode image
                    frame = decode_base64_image(image_data)
                    
                    # Process frame
                    result = system_manager.process_frame(frame, frame_id=frame_id, timestamp=timestamp)
                    frame_id += 1
                    
                    # Prepare response
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
                    
                    # Send response
                    await websocket.send_json(response)
                    
                except Exception as e:
                    logger.error(f"Error processing frame: {e}", exc_info=True)
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Frame processing error: {str(e)}"
                    })
            
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

