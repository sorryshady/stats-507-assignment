# Describe My Environment: Project Master Plan (v2.0)

**Course:** STATS 507  
**Focus:** Full-Stack ML Engineering / Edge Computing  
**Target Hardware:** Apple Silicon (M4 Pro) & iPhone 17 Pro (Ultra-Wide)

---

## 1. 🎯 Core Mission

To build a **wearable-simulated AI assistant** for visually impaired users that creates a comprehensive understanding of the physical world. Unlike traditional tools that simply list objects ("Person, Chair"), this system provides **spatial and temporal context** ("A person is walking towards you from the left").

### The "Dual-Loop" Philosophy

The human brain processes vision in two modes: **Reflexes** (fast, survival-based) and **Cognition** (slow, detail-based). This project mimics that biology:

1.  **The Reflex Loop (Safety):** Runs at 30 FPS. Instantly warns of physical collision risks.
2.  **The Cognitive Loop (Narrator):** Runs On-Demand. Synthesizes history and vision into natural language stories.

---

## 2. 🏗️ Architectural Blueprint

### High-Level Data Flow

```mermaid
graph TD
    %% Hardware Layer
    Input["iPhone 17 Pro Camera (0.5x Ultra-Wide)"] -->|Raw Frame Stream| AppEntryPoint

    %% The Dual-Loop Split
    AppEntryPoint -->|Stream Copy| SafetyLoop
    AppEntryPoint -->|Snapshot| CognitiveLoop

    %% 1. The Reflex Loop (Fast)
    subgraph "Reflex Loop (30 FPS)"
        SafetyLoop[YOLO11 Tracking]
        SafetyLoop -->|BBox Data| PhysicsEngine["Physics Engine (Velocity/Expansion Calc)"]
        PhysicsEngine -->|Hazard Detected?| AudioReflex["Audio Beep / 'STOP'"]
    end

    %% 2. The Cognitive Loop (Slow/Smart)
    subgraph "Cognitive Loop (On-Demand)"
        CognitiveLoop[Input Handler]
        CognitiveLoop -->|Current Frame| BLIP["BLIP Model (Scene Context)"]
        CognitiveLoop -->|Last 90 Frames| History["History Buffer (Trajectory Analysis)"]

        BLIP -->|Context String| Fusion
        History -->|Movement String| Fusion

        Fusion["Llama 3.2 3B (Narrator Agent)"] -->|Natural Language| TTS[Text-to-Speech]
    end

    %% Outputs
    AudioReflex --> User((User))
    TTS --> User
```

---

## 3. 🛠️ The Tech Stack (v2.0)

We have upgraded the stack to leverage the M4 Pro's neural engine and the iPhone's advanced optics.

| Component         | Technology             | Role               | Reason for Choice                                                              |
| :---------------- | :--------------------- | :----------------- | :----------------------------------------------------------------------------- |
| **Input**         | **iPhone 17 Pro**      | Vision Sensor      | The **48MP Ultra-Wide (0.5x)** lens eliminates blind spots crucial for safety. |
| **Tracking**      | **YOLO11n-track**      | Object Persistence | Tracks unique IDs to calculate trajectory (Velocity & Direction).              |
| **Vision**        | **BLIP**               | Scene Captioning   | Provides the "Gist" of the scene (e.g., "A messy bedroom").                    |
| **Reasoning**     | **Llama 3.2 (3B)**     | Data Fusion        | Converts raw JSON data into human-like, helpful narration.                     |
| **Inference**     | **Ollama (Metal)**     | LLM Runner         | Optimized for Mac M4 GPU/NPU; runs locally with zero latency penalty.          |
| **Orchestration** | **Python (Threading)** | Controller         | Manages the async relationship between the fast and slow loops.                |

---

## 4. ✅ Concrete Functionalities

### Feature 1: The Proximity Warning (Safety)

- **Status:** _Always Active (Background)_
- **Trigger:** Automatic.
- **Logic:**
  1.  **Zone Check:** Is the object in the center 40% of the frame?
  2.  **Expansion Check:** Did the bounding box width increase by >10% in the last 0.5 seconds? (Visual Looping effect).
  3.  **Class Check:** Is it a vehicle, bike, or running person?
- **Output:** Immediate high-priority audio interrupt (Beep or "STOP").
- **Latency Target:** < 50ms.

### Feature 2: The "Narrator" (Context)

- **Status:** _On-Demand_
- **Trigger:** User presses `SPACE` or Voice Command.
- **Logic:**
  1.  **Snapshot:** Freezes current state.
  2.  **Trajectory Analysis:** specific logic determines if objects are "Approaching", "Leaving", or "Passing By".
  3.  **Fusion:** Sends `[Scene Description]` + `[Object Movements]` to Llama 3.2.
- **Output:** "You are standing on a sidewalk. A car is waiting at the light, and two people are walking past you on the right."
- **Latency Target:** ~1.5 - 2.0 seconds.

### Feature 3: Semantic Search (Find Object)

- **Status:** _Mode Switch_
- **Trigger:** "Find my keys."
- **Logic:**
  1.  Lowers detection threshold for the specific class (`keys`).
  2.  Scans frame.
- **Output:** Spatial guidance: "Keys detected, 10 o'clock, about 1 meter away."

---

## 5. 💾 Data Structures (The Contract)

To ensure modularity, our components communicate via these strict data definitions.

### 1. The Tracked Object (Internal)

Stored in the **90-frame History Buffer**.

```python
@dataclass
class DetectionPoint:
    frame_id: int
    timestamp: float
    box: Tuple[int, int, int, int]  # x1, y1, x2, y2
    area: int                        # w * h (used for depth estimation)
    center: Tuple[int, int]          # Center coordinates
```

### 2. The Prompt Payload (LLM Input)

This is the exact JSON-like structure we generate for Llama 3.2.

```text
SYSTEM: You are a helpful assistant for a blind user. Be concise.

USER:
Context: "A living room with a couch and TV."
Entities:
- Person (ID: 4): Moving Left -> Right (Passing by).
- Dog (ID: 7): Area grew 40% (Approaching rapidly).
- Chair (ID: 2): Stationary.

TASK: Summarize this in one natural sentence, prioritizing safety.
```

---

## 6. 🗓️ Implementation Roadmap

### Phase 1: The Hardware Handshake (Current)

- [ ] **Input:** Secure 0.5x video feed from iPhone 17 Pro (via Desk View hack or Camo).
- [ ] **Environment:** Verify Ollama + Llama 3.2 is running on M4 Metal.

### Phase 2: The "Memory" Core

- [ ] **History Buffer:** Implement `deque(maxlen=90)` to store tracking data.
- [ ] **Physics Engine:** Write the logic to calculate `delta_x` and `area_growth`.

### Phase 3: The Brain

- [ ] **Prompt Engineering:** Tune the Llama 3.2 system prompt for brevity.
- [ ] **Integration:** Connect `SceneComposer` to `LLMNarrator`.

### Phase 4: The Polish

- [ ] **Threading:** Ensure Llama inference does not block the Safety Loop.
- [ ] **TTS:** Integrate a low-latency speech engine.
