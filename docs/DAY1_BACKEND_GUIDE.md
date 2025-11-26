# Day 1: Backend Foundation - Step-by-Step Guide

**Goal:** Create FastAPI backend with WebSocket endpoint for camera frames

---

## 🎯 What We're Building Today

1. **FastAPI Application** - Web server that handles HTTP and WebSocket requests
2. **WebSocket Endpoint** - Real-time bidirectional communication for camera frames
3. **System Wrapper** - Adapts your existing `DualLoopSystem` for web use
4. **REST Endpoints** - Status and health check endpoints

---

## 📚 Concepts to Understand

### FastAPI
- Modern Python web framework (like Flask but faster)
- Automatic API documentation
- Built-in WebSocket support
- Type hints for validation

### WebSocket vs REST
- **REST (HTTP)**: Request → Response (one-way, stateless)
- **WebSocket**: Persistent connection, bidirectional (client ↔ server)
- **Why WebSocket?** Camera frames need real-time, continuous communication

### Base64 Encoding
- Images are binary data
- WebSocket messages are text
- Base64 converts binary → text for transmission
- Frontend sends: `base64_encoded_jpeg`
- Backend decodes: `base64 → numpy array → process → encode back`

---

## 🏗️ Step 1: Create Backend Structure

### Directory Structure

Create this structure:

```
backend/
├── app/
│   ├── __init__.py          # Empty file (makes it a package)
│   ├── main.py              # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── camera.py    # WebSocket endpoint
│   │   │   └── status.py    # REST endpoints
│   │   └── models.py        # Pydantic models (data validation)
│   └── core/
│       ├── __init__.py
│       └── system.py         # Wrapper around DualLoopSystem
└── requirements.txt         # Backend-specific dependencies
```

### Why This Structure?

- **`app/`** - Main application package
- **`api/routes/`** - Separate files for different endpoints (organized)
- **`api/models.py`** - Pydantic models for request/response validation
- **`core/system.py`** - Business logic separate from API routes

**Action:** Create these directories and empty `__init__.py` files.

---

## 🛠️ Step 2: Backend Requirements

### Create `backend/requirements.txt`

**Question:** What dependencies do we need?

Think about:
- FastAPI (web framework)
- WebSocket support (built into FastAPI)
- Image processing (PIL/Pillow for base64 decoding)
- CORS (Cross-Origin Resource Sharing - needed for frontend)

**Hint:** Look at your main `requirements.txt` - we'll reuse most dependencies, but add FastAPI-specific ones.

**Your task:** Create `backend/requirements.txt` with:
- FastAPI
- uvicorn (ASGI server - runs FastAPI)
- python-multipart (for file uploads)
- CORS middleware (already in FastAPI, but note it)

**Note:** Most ML dependencies (torch, ultralytics, etc.) are already in root `requirements.txt`. Backend will import from `src/` which uses those.

---

## 🚀 Step 3: FastAPI Application Setup

### Create `backend/app/main.py`

**Concept:** FastAPI app is the central hub. It:
- Creates the app instance
- Registers routes (endpoints)
- Configures middleware (CORS, etc.)
- Runs the server

### Basic Structure:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app instance
app = FastAPI(
    title="Describe My Environment API",
    description="Backend API for dual-loop vision system",
    version="1.0.0-beta"
)

# Configure CORS (allows frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint (test if server is running)
@app.get("/")
def root():
    return {"status": "running", "message": "Describe My Environment API"}

# Include routers (we'll create these next)
# from app.api.routes import camera, status
# app.include_router(status.router, prefix="/api")
```

**Your task:**
1. Write this file
2. Understand each part:
   - What is `FastAPI()`?
   - What does CORS middleware do?
   - What is `@app.get("/")` decorator?

**Test it:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000` - should see JSON response.

---

## 📡 Step 4: Status Endpoint

### Create `backend/app/api/routes/status.py`

**Purpose:** Check system health, model status, Ollama connection

**Concept:** REST endpoint that returns JSON

### Structure:

```python
from fastapi import APIRouter
from app.core.system import SystemManager  # We'll create this

router = APIRouter()

@router.get("/status")
async def get_status():
    # Check if models are loaded
    # Check Ollama connection
    # Return status JSON
    pass
```

**Your task:**
1. Create the router
2. Think about what status info to return:
   - System running?
   - YOLO model loaded?
   - BLIP model loaded?
   - Ollama connected?
   - GPU available?

3. Import and check your existing components:
   - How do you check if Ollama is connected? (Look at `src/cognitive_loop/narrator.py`)
   - How do you check GPU? (Look at `src/reflex_loop/tracker.py`)

**Hint:** You can import from `src.cognitive_loop.narrator import LLMNarrator` and call `check_connection()`.

**Register the router** in `main.py`:
```python
from app.api.routes import status
app.include_router(status.router, prefix="/api")
```

---

## 🔌 Step 5: System Wrapper

### Create `backend/app/core/system.py`

**Purpose:** Adapt `DualLoopSystem` for web use

**Challenge:** Your `DualLoopSystem` expects:
- Camera handler (continuous frames)
- Keyboard input (SPACE key)
- Runs in threads

**Web needs:**
- Process individual frames (from WebSocket)
- No keyboard input
- No continuous camera

### Approach: Create a Web-Friendly Wrapper

**Concept:** Instead of modifying `DualLoopSystem`, create a wrapper that:
- Uses the same components (tracker, safety monitor, etc.)
- Processes frames on-demand (not continuous)
- Manages state for web requests

### Structure:

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.reflex_loop.tracker import YOLOTracker
from src.reflex_loop.safety import SafetyMonitor
from src.cognitive_loop.history import HistoryBuffer
from src.cognitive_loop.scene_composer import SceneComposer
from src.cognitive_loop.trajectory import TrajectoryAnalyzer
from src.cognitive_loop.narrator import LLMNarrator
from src.config import CAMERA_WIDTH, CAMERA_HEIGHT
import numpy as np
import cv2
import base64
import time

class SystemManager:
    """Manages the ML system for web requests."""
    
    def __init__(self):
        # Initialize components (like DualLoopSystem does)
        self.tracker = None
        self.safety_monitor = None
        self.history_buffer = None
        # ... etc
        
    def initialize(self):
        """Load models and initialize components."""
        # Load YOLO, BLIP, etc.
        pass
    
    def process_frame(self, frame: np.ndarray, frame_id: int, timestamp: float):
        """Process a single frame and return results."""
        # 1. Run tracking
        # 2. Update history buffer
        # 3. Check hazards
        # 4. Return detections + hazards
        pass
    
    def generate_narration(self, frame: np.ndarray):
        """Generate narration for a frame."""
        # 1. Get scene description (BLIP)
        # 2. Analyze trajectories
        # 3. Generate narration (Llama)
        # 4. Return narration text
        pass
```

**Your task:**
1. Understand what components you need (look at `src/main.py` `DualLoopSystem.__init__`)
2. Initialize them in `__init__` or `initialize()` method
3. Think about:
   - Do you need a camera handler? (No - frames come from web)
   - Do you need audio handler? (Maybe later, not for Day 1)
   - How do you track frame_id? (Keep a counter)

**Key insight:** You're reusing the same ML components, just orchestrating them differently for web requests.

---

## 🌐 Step 6: WebSocket Endpoint

### Create `backend/app/api/routes/camera.py`

**Purpose:** Handle real-time camera frame processing

**Concept:** WebSocket allows:
- Client sends frames continuously
- Server processes and responds immediately
- Persistent connection (not request/response)

### Structure:

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.system import SystemManager
import json
import base64
import numpy as np
import cv2

router = APIRouter()
system_manager = SystemManager()  # Shared instance

@router.websocket("/ws/camera")
async def websocket_camera(websocket: WebSocket):
    """WebSocket endpoint for camera frame processing."""
    
    # Accept connection
    await websocket.accept()
    
    frame_id = 0
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Extract frame data
            if message["type"] == "frame":
                # Decode base64 image
                image_data = base64.b64decode(message["data"])
                # Convert to numpy array
                # Process frame
                # Send results back
                
    except WebSocketDisconnect:
        # Client disconnected
        pass
```

**Your task:**
1. Understand WebSocket flow:
   - `await websocket.accept()` - Accept connection
   - `await websocket.receive_text()` - Wait for message
   - `await websocket.send_json()` - Send response
   - `WebSocketDisconnect` - Handle disconnection

2. Implement frame decoding:
   - Base64 decode: `base64.b64decode(message["data"])`
   - Convert to numpy: Use `cv2.imdecode()` or `np.frombuffer()`
   - Process with `system_manager.process_frame()`
   - Encode result back to base64
   - Send JSON response

3. Message format:
   - Client sends: `{"type": "frame", "data": "base64_string", "timestamp": 123.456}`
   - Server sends: `{"type": "frame_result", "detections": [...], "hazards": [...]}`

**Key functions to use:**
- `cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)` - Decode image
- `cv2.imencode('.jpg', frame)[1].tobytes()` - Encode image
- `base64.b64encode(image_bytes).decode('utf-8')` - Base64 encode

---

## 🧪 Step 7: Testing

### Test Status Endpoint

```bash
# Start server
cd backend
uvicorn app.main:app --reload --port 8000

# In another terminal
curl http://localhost:8000/api/status
```

### Test WebSocket

**Option 1: Use Python script**
```python
import asyncio
import websockets
import json
import base64
import cv2

async def test_websocket():
    uri = "ws://localhost:8000/ws/camera"
    async with websockets.connect(uri) as websocket:
        # Read test image
        img = cv2.imread("../../test_images/test_image_0.jpg")
        _, buffer = cv2.imencode('.jpg', img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Send frame
        message = {
            "type": "frame",
            "data": img_base64,
            "timestamp": 1234567890.123
        }
        await websocket.send(json.dumps(message))
        
        # Receive response
        response = await websocket.recv()
        print(json.loads(response))

asyncio.run(test_websocket())
```

**Option 2: Use browser console** (once frontend is ready)

---

## 🎓 Learning Checkpoints

After each step, verify you understand:

1. **FastAPI Setup:**
   - ✅ What is FastAPI?
   - ✅ How does CORS work?
   - ✅ What is a router?

2. **System Wrapper:**
   - ✅ Why do we need a wrapper?
   - ✅ How is it different from `DualLoopSystem`?
   - ✅ What components are reused?

3. **WebSocket:**
   - ✅ How is WebSocket different from REST?
   - ✅ Why use WebSocket for camera frames?
   - ✅ How does base64 encoding work?

4. **Integration:**
   - ✅ How do you import from `src/`?
   - ✅ How do you decode/encode images?
   - ✅ How do you handle errors?

---

## 🐛 Common Issues & Solutions

### Issue: Import errors from `src/`
**Solution:** Add project root to Python path:
```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
```

### Issue: Base64 decoding fails
**Solution:** Check if data includes data URL prefix (`data:image/jpeg;base64,`). Strip it if present.

### Issue: Image format issues
**Solution:** Ensure you're using `cv2.IMREAD_COLOR` and encoding as JPEG consistently.

### Issue: WebSocket connection refused
**Solution:** Check server is running, port is correct, CORS is configured.

---

## 📝 Day 1 Checklist

- [ ] Backend directory structure created
- [ ] `requirements.txt` created
- [ ] FastAPI app runs (`uvicorn app.main:app`)
- [ ] Status endpoint works (`/api/status`)
- [ ] System wrapper initializes components
- [ ] WebSocket endpoint accepts connections
- [ ] Can decode base64 image
- [ ] Can process frame with YOLO
- [ ] Can send results back via WebSocket
- [ ] Error handling implemented

---

## 🚀 Next Steps (Day 2)

Once Day 1 is complete:
- Add narration endpoint (REST)
- Improve error handling
- Add logging
- Performance optimization
- API documentation

---

## 💡 Tips

1. **Start Simple:** Get basic WebSocket working first, then add processing
2. **Test Incrementally:** Test each piece before moving to next
3. **Use Print Statements:** Debug with `print()` before adding logging
4. **Read Error Messages:** They usually tell you what's wrong
5. **Check Existing Code:** Look at `src/main.py` to understand how components work together

---

**Ready to start?** Begin with Step 1 and work through each step. If you get stuck, ask questions!

Good luck! 🎉

