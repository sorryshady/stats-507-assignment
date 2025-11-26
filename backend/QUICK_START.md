# Day 1 Quick Start

## Step-by-Step Checklist

Follow `docs/DAY1_BACKEND_GUIDE.md` for detailed explanations. This is a quick reference.

### 1. Create Structure
```bash
mkdir -p backend/app/api/routes backend/app/core
touch backend/app/__init__.py
touch backend/app/api/__init__.py
touch backend/app/api/routes/__init__.py
touch backend/app/core/__init__.py
```

### 2. Create `backend/requirements.txt`
Add:
- fastapi
- uvicorn[standard]
- python-multipart

### 3. Create `backend/app/main.py`
- Import FastAPI
- Create app instance
- Add CORS middleware
- Add root endpoint (`@app.get("/")`)
- Test: `uvicorn app.main:app --reload`

### 4. Create `backend/app/api/routes/status.py`
- Create router
- Add `/status` endpoint
- Check Ollama connection
- Return JSON status
- Register in `main.py`

### 5. Create `backend/app/core/system.py`
- Import components from `src/`
- Create `SystemManager` class
- Initialize tracker, safety monitor, etc.
- Add `process_frame()` method

### 6. Create `backend/app/api/routes/camera.py`
- Create WebSocket router
- Accept connection
- Receive frame (base64)
- Decode image
- Process with SystemManager
- Send results back

### 7. Test
- Status: `curl http://localhost:8000/api/status`
- WebSocket: Use test script or browser

---

## Key Imports You'll Need

```python
# FastAPI
from fastapi import FastAPI, WebSocket, APIRouter
from fastapi.middleware.cors import CORSMiddleware

# Image processing
import cv2
import numpy as np
import base64

# Your existing code
from src.reflex_loop.tracker import YOLOTracker
from src.cognitive_loop.narrator import LLMNarrator
# ... etc
```

---

## Testing Commands

```bash
# Start server
cd backend
uvicorn app.main:app --reload --port 8000

# Test status (in another terminal)
curl http://localhost:8000/api/status

# Or visit in browser
http://localhost:8000/docs  # Auto-generated API docs!
```

---

**Remember:** Read `docs/DAY1_BACKEND_GUIDE.md` for explanations of WHY and HOW!

