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
    """Decode base64 image to numpy array (BGR format)."""
    # Remove data URL prefix if present
    if "," in image_data:
        image_data = image_data.split(",")[1]

    image_bytes = base64.b64decode(image_data)
    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if frame is None:
        raise ValueError("Failed to decode image")

    return frame


def encode_image_to_base64(frame: np.ndarray) -> str:
    """Encode numpy array to base64 string."""
    success, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])

    if not success:
        raise ValueError("Failed to encode image")

    image_bytes = buffer.tobytes()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    return image_base64


@router.websocket("/ws/camera")
async def websocket_camera(websocket: WebSocket):
    """WebSocket endpoint for real-time frame processing."""
    await websocket.accept()
    logger.info("WebSocket client connected")

    system_manager = get_system_manager()

    try:
        system_manager.initialize()
    except Exception as e:
        logger.error(f"Failed to initialize system: {e}")
        await websocket.send_json(
            {"type": "error", "message": f"System initialization failed: {str(e)}"}
        )
        await websocket.close()
        return

    frame_id = 0
    processing = False
    pending_frame = None  # latest frame while processing

    async def process_frame_async(frame_data, current_frame_id, timestamp):
        """Process frame in thread pool (non-blocking)."""
        nonlocal processing
        try:
            frame = decode_base64_image(frame_data)

            # Run CPU-bound processing in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, system_manager.process_frame, frame, current_frame_id, timestamp
            )

            response = {
                "type": "frame_result",
                "frame_id": result["frame_id"],
                "timestamp": result["timestamp"],
                "detections": result["detections"],
                "hazards": result["hazards"],
            }

            if result["annotated_frame"] is not None:
                annotated_base64 = encode_image_to_base64(result["annotated_frame"])
                response["annotated_frame"] = annotated_base64

            await websocket.send_json(response)
        except Exception as e:
            logger.error(f"Error processing frame: {e}", exc_info=True)
            try:
                await websocket.send_json(
                    {"type": "error", "message": f"Frame processing error: {str(e)}"}
                )
            except:
                pass
        finally:
            processing = False

    try:
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json(
                    {"type": "error", "message": "Invalid JSON format"}
                )
                continue

            if message.get("type") == "frame":
                image_data = message.get("data", "")
                timestamp = message.get("timestamp", None)

                if not image_data:
                    await websocket.send_json(
                        {"type": "error", "message": "No image data provided"}
                    )
                    continue

                # Skip if already processing, store latest frame
                if processing:
                    pending_frame = (image_data, frame_id, timestamp)
                    frame_id += 1
                    continue

                processing = True
                current_frame_id = frame_id
                frame_id += 1

                asyncio.create_task(
                    process_frame_async(image_data, current_frame_id, timestamp)
                )

                # Process pending frame if exists
                if pending_frame:
                    pending_data, pending_id, pending_ts = pending_frame
                    pending_frame = None
                    processing = True
                    current_frame_id = frame_id
                    frame_id += 1
                    asyncio.create_task(
                        process_frame_async(pending_data, current_frame_id, pending_ts)
                    )

            elif message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

            else:
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": f"Unknown message type: {message.get('type')}",
                    }
                )

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json(
                {"type": "error", "message": f"Server error: {str(e)}"}
            )
        except:
            pass
