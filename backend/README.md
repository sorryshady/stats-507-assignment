# Backend API

FastAPI backend implementation for the Describe My Environment project.

## Implementation Status

The backend API is fully implemented with:
- FastAPI application setup
- Status endpoint (`/api/status`)
- Health check endpoint (`/api/health`)
- WebSocket endpoint (`/api/ws/camera`)
- System manager wrapper
- Error handling and logging

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Note:** Ensure the main project dependencies are installed:
```bash
# From project root
pip install -r requirements.txt
```

### 2. Start the Server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

The server will start on `http://localhost:8000`

### 3. Test the API

**Status Endpoint:**
```bash
curl http://localhost:8000/api/status
```

**Health Check:**
```bash
curl http://localhost:8000/api/health
```

**API Documentation:**
Visit `http://localhost:8000/docs` for interactive API documentation.

**WebSocket Test:**
```bash
python backend/test_websocket.py
```

**Narration Endpoint Test:**
```bash
python backend/test_narration.py
```

Or with curl:
```bash
# First encode an image to base64
base64_image=$(base64 -i test_images/test_image_0.jpg)

# Send request
curl -X POST http://localhost:8000/api/narration \
  -H "Content-Type: application/json" \
  -d "{\"frame\": \"$base64_image\"}"
```

## API Endpoints

### REST Endpoints

- `GET /` - Root endpoint (API info)
- `GET /api/status` - System status (models, GPU, Ollama)
- `GET /api/health` - Health check
- `POST /api/narration` - Generate narration for a frame (cognitive loop)

### WebSocket Endpoint

- `WS /api/ws/camera` - Real-time camera frame processing

**Message Format (Client → Server):**
```json
{
  "type": "frame",
  "data": "base64_encoded_jpeg",
  "timestamp": 1234567890.123
}
```

**Response Format (Server → Client):**
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

## Architecture

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── api/
│   │   ├── routes/
│   │   │   ├── status.py    # Status endpoints
│   │   │   └── camera.py    # WebSocket endpoint
│   │   └── models.py        # Pydantic models
│   └── core/
│       └── system.py        # System manager (wraps ML components)
├── requirements.txt
└── test_websocket.py        # Test script
```

## System Manager

The `SystemManager` class wraps the existing ML components:
- Initializes YOLO tracker, BLIP, Ollama narrator
- Processes frames on-demand (not continuous like CLI)
- Manages frame IDs and history buffer
- Returns structured results for API responses

## Troubleshooting

### Import Errors
Ensure you're running from the backend directory and the project root is in Python path.

### Ollama Not Connected
The status endpoint will show `"ollama": "disconnected"` if Ollama isn't running. Start it with:
```bash
ollama serve
```

### GPU Not Available
The system will fall back to CPU automatically. Check status endpoint to see GPU status.

### WebSocket Connection Refused
Ensure the server is running:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

## Implementation Status

**Completed:**
- Comprehensive API tests (pytest)
- API documentation (FastAPI auto-docs + manual docs)
- Setup guide (`SETUP.md`)
- Performance logging (initialization time tracking)
- Test configuration (`pytest.ini`)

## Documentation

- Main guide: [`docs/DAY1_BACKEND_GUIDE.md`](../docs/DAY1_BACKEND_GUIDE.md)
- API docs: Visit `http://localhost:8000/docs` when server is running
- API Documentation: [`API_DOCUMENTATION.md`](./API_DOCUMENTATION.md)
