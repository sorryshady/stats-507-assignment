# Project Brief

## Core Mission
To build a **wearable-simulated AI assistant** for visually impaired users that creates a comprehensive understanding of the physical world. Unlike traditional tools that simply list objects, this system provides **spatial and temporal context** ("A person is walking towards you from the left").

## Dual-Loop Philosophy
The system mimics human vision processing:
1.  **Reflex Loop (Safety):** Runs at ~30 FPS. Instantly warns of physical collision risks using object tracking (YOLO).
2.  **Cognitive Loop (Narrator):** Runs On-Demand. Synthesizes history and vision into natural language stories using VLM/LLM (BLIP + Llama 3.2).

## Scope
- **Input:** Camera feed (simulating smart glasses/wearable).
- **Processing:** Local inference (M4 Pro optimized) or Edge server.
- **Output:** Audio (Safety Alerts + Narration).
- **Platform:** Full-stack Web Application (Next.js Frontend + FastAPI Backend).

## Success Metrics
- **Latency:** Reflex loop < 50ms, Cognitive loop < 3s (target).
- **Accuracy:** High precision for hazard detection.
- **Experience:** Natural, non-intrusive audio feedback.

