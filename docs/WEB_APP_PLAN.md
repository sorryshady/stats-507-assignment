# Web Application Implementation Plan

## Overview

Transform "Describe My Environment" from a CLI tool into a full-stack web application with a polished product website, allowing users to test the system through their browser.

---

## Architecture

### Tech Stack

**Backend:**
- FastAPI (already in requirements.txt)
- WebSockets for real-time camera feed
- Existing ML pipeline (YOLO, BLIP, Ollama)

**Frontend:**
- Next.js 14+ (App Router)
- TypeScript
- Tailwind CSS
- WebRTC for camera access
- React hooks for state management

**Communication:**
- WebSocket: Real-time frame processing, hazard alerts
- REST API: System status, configuration, demo videos metadata
- Server-Sent Events (SSE): Optional for narration streaming

---

## Project Structure

```
final/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── camera.py  # Camera/WebSocket endpoints
│   │   │   │   ├── narration.py  # Cognitive loop triggers
│   │   │   │   ├── status.py  # System health/status
│   │   │   │   └── demos.py   # Demo videos metadata
│   │   │   └── models.py      # Pydantic models
│   │   ├── core/
│   │   │   ├── system.py      # Wrapper around DualLoopSystem
│   │   │   └── websocket.py   # WebSocket connection manager
│   │   └── config.py          # Backend config
│   └── requirements.txt       # Backend dependencies
│
├── frontend/                   # Next.js frontend
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx           # Landing page
│   │   ├── about/
│   │   │   └── page.tsx       # About page
│   │   ├── roadmap/
│   │   │   └── page.tsx       # Roadmap page
│   │   ├── demo/
│   │   │   └── page.tsx       # Demo videos page
│   │   └── test/
│   │       └── page.tsx       # Interactive test page
│   ├── components/
│   │   ├── BetaBadge.tsx
│   │   ├── CameraFeed.tsx
│   │   ├── TrackingOverlay.tsx
│   │   ├── NarrationPanel.tsx
│   │   ├── HazardAlert.tsx
│   │   └── Navigation.tsx
│   ├── lib/
│   │   ├── api.ts             # API client
│   │   └── websocket.ts       # WebSocket client
│   ├── types/
│   │   └── index.ts           # TypeScript types
│   └── package.json
│
├── src/                        # Existing ML code (unchanged)
├── public/
│   └── demos/                  # Demo video files
└── README.md
```

---

## Backend API Design

### 1. WebSocket Endpoint: `/ws/camera`

**Purpose:** Real-time camera feed processing

**Connection Flow:**
```
Client → WebSocket Connection
  ↓
Send frame (base64 encoded JPEG)
  ↓
Backend processes frame (YOLO tracking)
  ↓
Send back:
  - Annotated frame (base64)
  - Detections JSON
  - Hazard alerts (if any)
```

**Message Format (Client → Server):**
```json
{
  "type": "frame",
  "data": "base64_encoded_jpeg",
  "timestamp": 1234567890.123
}
```

**Message Format (Server → Client):**
```json
{
  "type": "frame_result",
  "annotated_frame": "base64_encoded_jpeg",
  "detections": [
    {
      "track_id": 1,
      "class": "person",
      "confidence": 0.95,
      "box": [100, 200, 300, 400],
      "center": [200, 300]
    }
  ],
  "hazards": [
    {
      "priority": "high",
      "message": "STOP! Person in front of you",
      "object_id": 1
    }
  ],
  "frame_id": 1234
}
```

### 2. REST Endpoints

#### `POST /api/narration/trigger`
Trigger cognitive loop narration

**Request:**
```json
{
  "frame": "base64_encoded_jpeg"  // Optional: use current frame if not provided
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
  "processing_time_ms": 1500
}
```

#### `GET /api/status`
System health and status

**Response:**
```json
{
  "status": "running",
  "models": {
    "yolo": "loaded",
    "blip": "loaded",
    "ollama": "connected"
  },
  "gpu": {
    "available": true,
    "type": "mps"  // or "cuda", "cpu"
  },
  "version": "1.0.0-beta"
}
```

#### `GET /api/demos`
List available demo videos

**Response:**
```json
{
  "demos": [
    {
      "id": "demo-1",
      "title": "Indoor Navigation",
      "description": "Walking through a cluttered room",
      "thumbnail": "/demos/demo-1-thumb.jpg",
      "video_url": "/demos/demo-1.mp4",
      "duration_seconds": 30
    }
  ]
}
```

#### `POST /api/camera/start`
Initialize camera session (optional, for server-side camera)

**Response:**
```json
{
  "session_id": "abc123",
  "status": "ready"
}
```

#### `POST /api/camera/stop`
Stop camera session

---

## Frontend Pages

### 1. Landing Page (`/`)

**Sections:**
- Hero section with tagline
- Beta badge prominently displayed
- Key features (3-4 cards)
- Quick demo video embed
- CTA: "Try It Now" → `/test`
- Footer with links

**Design Notes:**
- Modern, accessible design
- Emphasize "Beta" status
- Clear value proposition

### 2. About Page (`/about`)

**Content:**
- Project mission and vision
- Dual-loop architecture explanation
- Technology stack
- Team/author info
- Course information (STATS 507)

**Design:**
- Informative, educational
- Diagrams/visualizations
- Tech stack badges

### 3. Roadmap Page (`/roadmap`)

**Content:**
- Current features (v1.0-beta)
- Planned features (from `future_expansion_plan.md`)
- Timeline (if applicable)
- Known limitations

**Design:**
- Timeline visualization
- Feature cards with status badges
- Clear "Beta" limitations section

### 4. Demo Videos Page (`/demo`)

**Content:**
- Grid of demo videos
- Each video card shows:
  - Thumbnail
  - Title
  - Description
  - Duration
  - Play button
- Video player modal/page

**Design:**
- Video gallery layout
- Responsive grid
- Modal player for fullscreen

### 5. Interactive Test Page (`/test`) ⭐

**Features:**
- Camera permission request
- Live camera feed display
- Tracking overlay (bounding boxes)
- Narration button
- Hazard alerts (visual + audio)
- Status panel (detections count, system status)
- Beta disclaimer banner

**Components:**
- `CameraFeed`: WebRTC camera access + display
- `TrackingOverlay`: Canvas overlay for bounding boxes
- `NarrationPanel`: Shows narration text + audio controls
- `HazardAlert`: Visual alert banner for hazards
- `StatusPanel`: System metrics

**User Flow:**
1. User clicks "Start Camera"
2. Browser requests camera permission
3. Camera feed starts
4. Frames sent to backend via WebSocket
5. Backend processes and returns annotated frames
6. Frontend displays annotated feed
7. User clicks "Describe Scene" → triggers narration
8. Narration displayed + audio played

---

## Implementation Phases

### Phase 1: Backend API Foundation (Week 1)

**Tasks:**
- [ ] Create FastAPI app structure
- [ ] Wrap `DualLoopSystem` for web use
- [ ] Implement WebSocket endpoint for camera frames
- [ ] Add REST endpoints (status, narration trigger)
- [ ] Handle base64 image encoding/decoding
- [ ] Add CORS middleware
- [ ] Error handling and logging

**Files to Create:**
- `backend/app/main.py`
- `backend/app/core/system.py`
- `backend/app/api/routes/camera.py`
- `backend/app/api/routes/narration.py`
- `backend/app/api/routes/status.py`
- `backend/app/api/models.py`

### Phase 2: Frontend Setup (Week 1-2)

**Tasks:**
- [ ] Initialize Next.js project
- [ ] Set up TypeScript
- [ ] Configure Tailwind CSS
- [ ] Create layout and navigation
- [ ] Build landing page
- [ ] Build about page
- [ ] Build roadmap page
- [ ] Build demo videos page

**Files to Create:**
- `frontend/app/layout.tsx`
- `frontend/app/page.tsx`
- `frontend/app/about/page.tsx`
- `frontend/app/roadmap/page.tsx`
- `frontend/app/demo/page.tsx`
- `frontend/components/Navigation.tsx`
- `frontend/components/BetaBadge.tsx`

### Phase 3: Interactive Test Page (Week 2)

**Tasks:**
- [ ] Implement WebRTC camera access
- [ ] Create WebSocket client
- [ ] Build camera feed component
- [ ] Implement tracking overlay (canvas)
- [ ] Add narration trigger button
- [ ] Build hazard alert component
- [ ] Add status panel
- [ ] Handle audio playback (TTS)

**Files to Create:**
- `frontend/app/test/page.tsx`
- `frontend/components/CameraFeed.tsx`
- `frontend/components/TrackingOverlay.tsx`
- `frontend/components/NarrationPanel.tsx`
- `frontend/components/HazardAlert.tsx`
- `frontend/lib/websocket.ts`
- `frontend/lib/api.ts`

### Phase 4: Integration & Polish (Week 3)

**Tasks:**
- [ ] Connect frontend to backend
- [ ] Test end-to-end flow
- [ ] Add error handling
- [ ] Improve UI/UX
- [ ] Add loading states
- [ ] Add beta disclaimers
- [ ] Performance optimization
- [ ] Mobile responsiveness

### Phase 5: Demo Content & Documentation (Week 3-4)

**Tasks:**
- [ ] Record demo videos
- [ ] Create thumbnails
- [ ] Add demo metadata
- [ ] Update README
- [ ] Create deployment guide
- [ ] Add API documentation

---

## Technical Considerations

### 1. Camera Feed Processing

**Challenge:** Browser → Backend → Browser latency

**Solution:**
- Use WebSocket for low-latency communication
- Process frames at reduced resolution (640x480) for speed
- Client-side frame rate limiting (15-20 FPS instead of 30)
- Optional: Client-side YOLO.js for even lower latency (future)

### 2. Audio Playback

**Challenge:** TTS audio from backend

**Options:**
- **Option A:** Backend generates audio, sends as base64 → Frontend plays
- **Option B:** Backend sends text → Frontend uses Web Speech API
- **Option C:** Backend streams audio via WebSocket

**Recommendation:** Option B (Web Speech API) for simplicity and lower bandwidth

### 3. State Management

**Approach:**
- React Context for global state (system status, session)
- Local state for component-specific data
- WebSocket messages update context

### 4. Error Handling

**Scenarios:**
- Camera permission denied
- WebSocket connection lost
- Backend model loading failed
- Ollama not running

**UI:**
- Clear error messages
- Retry buttons
- Fallback states

### 5. Performance

**Optimizations:**
- Frame compression (JPEG quality 70-80%)
- Throttle WebSocket messages (max 20 FPS)
- Debounce narration requests
- Lazy load demo videos
- Code splitting for routes

---

## Beta Version Messaging

### Key Messages

1. **"This is a beta version"**
   - Prominent badge on all pages
   - Disclaimer on test page

2. **"We're improving"**
   - Roadmap page shows planned features
   - Feedback form (optional)

3. **"Known Limitations"**
   - List on about/roadmap page
   - Show in test page sidebar

### Beta Limitations to Highlight

- Requires modern browser with camera support
- Best performance on Chrome/Edge (WebRTC)
- Requires Ollama running locally (for now)
- Limited to single user session
- Frame rate may vary based on hardware

---

## Deployment Options

### Development

**Backend:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

### Production

**Option 1: Vercel (Frontend) + Railway/Render (Backend)**
- Frontend: Vercel (free tier)
- Backend: Railway or Render (paid, but reasonable)

**Option 2: Single Server (Docker)**
- Docker Compose with nginx reverse proxy
- Frontend served as static files
- Backend as FastAPI service

**Option 3: Local Demo**
- Both run locally
- Good for course presentation

---

## API Client Example (TypeScript)

```typescript
// frontend/lib/api.ts

export interface Detection {
  track_id: number;
  class: string;
  confidence: number;
  box: [number, number, number, number];
  center: [number, number];
}

export interface FrameResult {
  type: 'frame_result';
  annotated_frame: string;
  detections: Detection[];
  hazards: Array<{
    priority: 'high' | 'medium';
    message: string;
    object_id: number;
  }>;
  frame_id: number;
}

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private onFrameResult?: (result: FrameResult) => void;
  private onError?: (error: Error) => void;

  connect(url: string) {
    this.ws = new WebSocket(url);
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'frame_result') {
        this.onFrameResult?.(data);
      }
    };
    this.ws.onerror = (error) => {
      this.onError?.(new Error('WebSocket error'));
    };
  }

  sendFrame(frameData: string, timestamp: number) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'frame',
        data: frameData,
        timestamp
      }));
    }
  }

  disconnect() {
    this.ws?.close();
  }
}
```

---

## Next Steps

1. **Review this plan** - Does this align with your vision?
2. **Prioritize features** - What's essential for the demo?
3. **Start Phase 1** - Begin with backend API
4. **Iterate** - Build incrementally, test frequently

---

## Questions to Consider

1. **Ollama Dependency**: Should we require users to run Ollama locally, or provide a cloud option?
2. **Authentication**: Do we need user accounts, or open access?
3. **Rate Limiting**: Should we limit API calls per user?
4. **Analytics**: Do we want to track usage?
5. **Mobile Support**: How important is mobile browser support?

---

**Ready to start?** Let me know which phase you'd like to begin with, and I'll help implement it!

