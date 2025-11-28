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

- Next.js 16 (App Router)
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
  "frame": "base64_encoded_jpeg" // Optional: use current frame if not provided
}
```

**Response:**

```json
{
  "narration": "A person is walking towards you from the left.",
  "scene_description": "A living room with a couch and TV.",
  "object_movements": ["Person (ID: 4): Moving Left -> Right (Passing by)."],
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
    "type": "mps" // or "cuda", "cpu"
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

### 5. Interactive Test Page (`/test`)

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
