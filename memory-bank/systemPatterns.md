# System Patterns

## Architecture: The Dual-Loop
The system creates a strict separation of concerns based on latency requirements:

```mermaid
graph TD
    Input[Camera Stream] --> Split{Splitter}
    
    subgraph "Reflex Loop (Fast / ~30Hz)"
        Split --> YOLO[Object Tracking]
        YOLO --> Physics[Trajectory/Hazard Calc]
        Physics --> Safety[Audio Alert]
    end
    
    subgraph "Cognitive Loop (Slow / On-Demand)"
        Split --> Sampler[Frame Sampler]
        Sampler --> VLM[BLIP (Scene Context)]
        Sampler --> History[Trajectory History]
        VLM & History --> LLM[Llama 3.2 (Narrator)]
        LLM --> TTS[Audio Description]
    end
```

## Web Application Architecture
- **Frontend:** Next.js (React)
    - Handles UI, Camera (WebRTC), and Audio Output.
    - Connects to Backend via WebSocket (for Reflex Stream) and REST (for Cognitive Trigger).
- **Backend:** FastAPI
    - Manages the `SystemManager` which orchestrates the Python-based ML loops.
    - **WebSocket `/ws/camera`:** Receives frames, runs YOLO, returns annotated frames + hazards.
    - **REST `/api/narration`:** Receives specific frame, runs BLIP+LLM, returns text.

## Key Technical Decisions
- **Local Inference:** All models (YOLO, BLIP, Llama/Ollama) run locally on the server (M4 Pro target).
- **WebSocket:** Chosen for low-latency video streaming and feedback loop.
- **Ollama:** Used for serving the LLM to take advantage of Metal acceleration on macOS.

## Design Patterns
- **Singleton System Manager:** The backend uses a singleton to maintain the state of the ML models and history buffer across API calls.
- **React Hooks:** Frontend uses custom hooks (`useCamera`, `useWebSocket`) to encapsulate complex logic.

