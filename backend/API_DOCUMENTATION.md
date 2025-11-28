# API Documentation

Complete API reference for Describe My Environment backend.

## Base URL

```
http://localhost:8000
```

## Interactive Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Endpoints

### 1. Root Endpoint

**GET** `/`

Get API information and available endpoints.

**Response:**
```json
{
  "status": "running",
  "message": "Describe My Environment API",
  "version": "1.0.0-beta",
  "docs": "/docs",
  "endpoints": {
    "status": "/api/status",
    "health": "/api/health",
    "narration": "/api/narration",
    "websocket": "/api/ws/camera"
  }
}
```

---

### 2. Health Check

**GET** `/api/health`

Simple health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "message": "System is running"
}
```

---

### 3. System Status

**GET** `/api/status`

Get detailed system status including model loading and GPU availability.

**Response:**
```json
{
  "initialized": true,
  "models": {
    "yolo": "loaded",
    "blip": "loaded",
    "ollama": "connected"
  },
  "gpu": {
    "available": true,
    "type": "mps"
  }
}
```

**Status Values:**
- `initialized`: `true` if models are loaded, `false` otherwise
- `models.yolo`: `"loaded"` or `"not_loaded"`
- `models.blip`: `"loaded"` or `"not_loaded"`
- `models.ollama`: `"connected"`, `"disconnected"`, or `"unknown"`
- `gpu.available`: `true` or `false`
- `gpu.type`: `"mps"` (Apple Silicon), `"cuda"` (NVIDIA), or `"cpu"`

**Example:**
```bash
curl http://localhost:8000/api/status
```

---

### 4. Generate Narration

**POST** `/api/narration`

Generate natural language narration for an image using the cognitive loop.

**Request Body:**
```json
{
  "frame": "base64_encoded_jpeg_image"
}
```

**Response:**
```json
{
  "narration": "A person is walking towards you from the left.",
  "scene_description": "A living room with a couch and TV.",
  "object_movements": [
    "Person (ID: 4): Moving Left -> Right (Passing by)."
  ],
  "processing_time_ms": 1500.23
}
```

**Status Codes:**
- `200` - Success
- `400` - Bad request (invalid image data)
- `422` - Validation error (missing frame field)
- `503` - Service unavailable (system initialization failed)
- `500` - Internal server error

**Example:**
```bash
# Encode image
base64_image=$(base64 -i test_images/test_image_0.jpg)

# Send request
curl -X POST http://localhost:8000/api/narration \
  -H "Content-Type: application/json" \
  -d "{\"frame\": \"$base64_image\"}"
```

**Processing Time:**
- Typically 1-3 seconds
- Includes BLIP scene captioning + trajectory analysis + LLM narration
- Measured in milliseconds

---

### 5. WebSocket Camera Feed

**WebSocket** `/api/ws/camera`

Real-time camera frame processing via WebSocket.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/camera');
```

**Client → Server Message:**
```json
{
  "type": "frame",
  "data": "base64_encoded_jpeg_image",
  "timestamp": 1234567890.123
}
```

**Server → Client Response:**
```json
{
  "type": "frame_result",
  "frame_id": 1,
  "timestamp": 1234567890.123,
  "detections": [
    {
      "track_id": 1,
      "class_name": "person",
      "confidence": 0.95,
      "box": [100, 200, 300, 400],
      "center": [200, 300],
      "area": 20000
    }
  ],
  "hazards": [
    {
      "object_id": 1,
      "class_name": "person",
      "priority": "high",
      "reason": "approaching, in center zone"
    }
  ],
  "annotated_frame": "base64_encoded_jpeg"  // Optional
}
```

**Message Types:**

**Client:**
- `"frame"` - Send frame for processing
- `"ping"` - Heartbeat/ping

**Server:**
- `"frame_result"` - Frame processing result
- `"pong"` - Response to ping
- `"error"` - Error message

**Example (Python):**
```python
import asyncio
import websockets
import json
import base64
import cv2

async def test():
    uri = "ws://localhost:8000/api/ws/camera"
    async with websockets.connect(uri) as websocket:
        # Read and encode image
        img = cv2.imread("test_image.jpg")
        _, buffer = cv2.imencode('.jpg', img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Send frame
        await websocket.send(json.dumps({
            "type": "frame",
            "data": img_base64,
            "timestamp": 1234567890.123
        }))
        
        # Receive response
        response = await websocket.recv()
        result = json.loads(response)
        print(result)

asyncio.run(test())
```

**Error Response:**
```json
{
  "type": "error",
  "message": "Error description"
}
```

---

## Error Responses

All endpoints return consistent error format:

```json
{
  "error": "Error message",
  "detail": "Additional details",
  "status_code": 400,
  "path": "/api/narration"
}
```

**Common Status Codes:**
- `400` - Bad Request (invalid input)
- `422` - Validation Error (missing/invalid fields)
- `500` - Internal Server Error
- `503` - Service Unavailable (system not initialized)

---

## Rate Limiting

Currently no rate limiting implemented. Consider adding for production use.

---

## Performance

- **First Request:** 5-10 seconds (model loading)
- **Subsequent Requests:** Much faster (models cached)
- **Narration:** 1-3 seconds per request
- **Frame Processing:** ~50-100ms per frame (WebSocket)

---

## Authentication

Currently no authentication required. Consider adding for production use.

---

## CORS

CORS is enabled for all origins (`*`). In production, specify actual frontend URL:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    ...
)
```

---

## Examples

See test scripts:
- `backend/test_narration.py` - Narration endpoint example
- `backend/test_websocket.py` - WebSocket example

---

**Last Updated:** December 2024

