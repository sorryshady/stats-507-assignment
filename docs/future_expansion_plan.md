# Future Expansion Plan: Describe My Environment

This document outlines the roadmap for future enhancements to the "Describe My Environment" AI assistant. These features aim to improve accuracy, safety, and usability for visually impaired users by leveraging advanced hardware capabilities and expanding software functionality.

## 1. Sensor Fusion & Advanced Motion Detection

**Goal:** Distinguish between user movement and object movement to provide more accurate context (e.g., "You are approaching a person" vs. "A person is approaching you").

### 1.1 IMU Integration (Accelerometer/Gyroscope)
- **Hardware:** iPhone (via Continuity Camera or custom app), External IMU.
- **Concept:** Use accelerometer data to detect if the camera itself is moving.
- **Logic:**
  - If IMU detects movement + Object size increases → **User is moving towards object**.
  - If IMU is stable + Object size increases → **Object is approaching user**.
- **Implementation:** Integrate CoreMotion framework (iOS/macOS) to stream IMU data alongside video feed.

### 1.2 LiDAR & Depth Sensing
- **Hardware:** iPhone Pro models (12 Pro and later), iPad Pro.
- **Concept:** Use LiDAR to measure absolute distance to objects in meters, rather than estimating from bounding box size.
- **Benefits:**
  - Precise distance warnings ("Person is 2 meters away").
  - Accurate obstacle detection in low light.
  - 3D spatial mapping of the environment.
- **Implementation:** Use ARKit to access depth map and fuse with YOLO detections.

### 1.3 Optical Flow Analysis (Software Only)
- **Concept:** Analyze background motion vs. foreground object motion.
- **Logic:**
  - If background features (walls, floor) move → Camera is moving.
  - If background is static but object moves → Object is moving.
- **Benefit:** Works with standard webcams without extra sensors.

---

## 2. "Find My Object" Mode (Object Search)

**Goal:** Allow users to ask the system to locate specific items (e.g., "Where are my keys?", "Find a chair").

### 2.1 Targeted Detection
- **Functionality:** User speaks a target object name.
- **Process:**
  1. System enters "Search Mode".
  2. Filters YOLO detections for the requested class (or uses a Zero-Shot detector like OWL-ViT for open-vocabulary search).
  3. Provides audio feedback:
     - "Scanning..."
     - "Keys detected to your right."
     - "Getting closer... Stop. Keys are directly in front of you."
- **Audio Guidance:** Use spatial audio or varying beep frequencies (Geiger counter style) to guide the user to the object.

### 2.2 Persistent Memory
- **Functionality:** Remember where objects were last seen.
- **Scenario:** User asks "Where did I leave my phone?". System replies "I last saw a phone on the brown table 5 minutes ago."
- **Implementation:** Store `(object_class, location_description, timestamp)` in a vector database or simple log.

---

## 3. Advanced Context & Navigation

### 3.1 Indoor Navigation Assistant
- **Goal:** Guide user through indoor spaces.
- **Features:**
  - Door detection and handle location ("Door is 2 meters ahead, handle is on the left").
  - Corridor centering ("Drifting left, move right to stay in center").
  - Obstacle avoidance pathing.

### 3.2 Text Reading (OCR)
- **Goal:** Read signs, labels, and documents on demand.
- **Implementation:** Integrate OCR (Tesseract or Apple Vision framework).
- **Usage:** User points at a sign, system reads: "Meeting Room B", "Exit", or reads a menu/mail.

### 3.3 Facial Recognition (Optional/Privacy-Focused)
- **Goal:** Identify known people (friends, family).
- **Feature:** Instead of "Person in front of you", say "John is in front of you".
- **Privacy:** Local-only processing, explicit user enrollment required.

---

## 4. Interface Enhancements

### 4.1 Voice Control
- **Goal:** Replace keyboard interactions with voice commands.
- **Commands:** "Describe scene", "Stop warnings", "Find keys", "Read text".
- **Implementation:** Whisper (OpenAI) for fast, local speech-to-text.

### 4.2 Haptic Feedback
- **Goal:** Provide silent, tactile warnings.
- **Implementation:**
  - Watch/Phone vibration for hazards.
  - Vibration intensity scales with proximity.
  - Directional haptics (left/right vibration) if supported by hardware.

### 4.3 3D Audio (Spatial Sound)
- **Goal:** Use spatial audio to indicate object direction.
- **Feature:** Hazard sound comes from the direction of the hazard (requires stereo headphones/AirPods).

---

## 5. Hardware Evolution

### 5.1 Wearable Integration
- **Form Factor:** Smart glasses (e.g., Ray-Ban Meta, Brilliant Labs Frame) or a chest-mounted camera.
- **Benefit:** Hands-free operation, camera looks where user looks.

### 5.2 Edge Device (Raspberry Pi / Jetson)
- **Goal:** Standalone device without needing a laptop.
- **Implementation:** Optimize models (YOLO-Nano, quantized LLMs) to run on portable hardware with a battery pack.

---

## Summary of Phases

1.  **Phase 1 (Current):** Camera-based Reflex/Cognitive Loops (YOLO + LLM).
2.  **Phase 2 (Navigation & Search):** "Find My..." feature, Optical Flow, OCR.
3.  **Phase 3 (Sensor Fusion):** IMU/LiDAR integration for precise movement tracking.
4.  **Phase 4 (Wearable/Standalone):** Porting to wearable or edge hardware for true mobility.

