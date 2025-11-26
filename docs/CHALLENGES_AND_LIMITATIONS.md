# Project Challenges & Limitations

This document outlines the current technical limitations, challenges, and known issues in the "Describe My Environment" project. It serves as a roadmap for future improvements and a transparent record of the current system's capabilities.

## 1. Computer Vision & Perception

### Monocular Depth Ambiguity
- **Issue**: The system relies on a single camera input (monocular vision).
- **Impact**: True depth perception is impossible. Distance estimation relies on 2D bounding box heuristics (size/position), which can be easily fooled by object size variations or camera angles.
- **Consequence**: "Rapid approach" warnings may be triggered false-positively if a large object simply appears in the frame, or false-negatively if a small object approaches quickly.

### Relative Motion Detection
- **Issue**: Distinguishing between the user moving towards an object and an object moving towards the user is mathematically difficult with a single camera without IMU data.
- **Impact**: The system may interpret the user walking forward as the entire world "rushing" towards them.
- **Current Workaround**: High velocity thresholds in `trajectory.py`, but this reduces sensitivity to genuine hazards.

### Low Light Performance
- **Issue**: Standard RGB cameras and the YOLO model degrade significantly in low light.
- **Impact**: Potential safety hazards (steps, obstacles) may go undetected in dim corridors or at night.

## 2. AI Models & Hallucinations

### Pretrained Model Limitations
- **Issue**: We use off-the-shelf pretrained models (YOLOv11, BLIP, Llama 3.2) without fine-tuning.
- **Impact**: 
  - **YOLO**: May miss specific assistive hazards like "wet floor signs" or "drop-offs" (stairs going down).
  - **BLIP**: Lacks temporal context and specific training for blind assistance scenarios.

### VLM Hallucinations (The "Mirror" Problem)
- **Issue**: The Scene Description model (BLIP) treats the camera view as a third-person photo.
- **Impact**: It frequently describes the user holding the camera as "a person standing in front of a mirror" or "a person looking at a screen."
- **Current Fix**: Regex-based sanitization in `scene_composer.py` and prompt engineering in `narrator.py` to suppress these specific hallucinations, but the underlying model bias remains.

### Robotic Text-to-Speech (TTS)
- **Issue**: The system currently relies on basic browser/OS-level TTS or simple synthesis.
- **Impact**: Warnings like "CAR APPROACHING FAST" sound the same as "A chair is on your left," failing to convey emotional urgency.

## 3. System Architecture & Performance

### Client-Server Latency
- **Issue**: The current demo architecture streams frames from Frontend -> Backend (Python) -> Frontend via WebSocket.
- **Impact**: Introduces network latency (round-trip time) that would be unacceptable in a critical safety device.
- **Target Architecture**: The final product must run purely on edge hardware (e.g., NVIDIA Jetson or mobile NPU) to eliminate network lag.

### Resource Intensity
- **Issue**: Running three models simultaneously (YOLO for detection, BLIP for captioning, Ollama/Llama for narration) is computationally heavy.
- **Impact**: 
  - High CPU/GPU usage.
  - Potential thermal throttling on portable devices.
  - Battery drain on mobile implementations.

### Sequential Processing Bottleneck
- **Issue**: The cognitive loop currently waits for detection -> captioning -> LLM generation in a semi-sequential manner.
- **Impact**: The "Narration" loop runs much slower (e.g., 0.5 - 1 FPS) than the "Reflex" loop (detection only, ~30 FPS). Fast-changing scenes may be described after they have already passed.

## 4. Frontend & User Experience

### Browser Restrictions
- **Issue**: Web browsers have strict autoplay and hardware access policies.
- **Impact**: Users must manually interact with the page to start audio contexts, and mobile browsers may throttle background processing if the screen turns off.

### "Black Box" State
- **Issue**: If the backend stalls (e.g., Ollama is generating a long response), the frontend gives limited feedback beyond a loading spinner.
- **Impact**: A blind user might think the system has frozen if audio feedback stops for more than a few seconds.

## 5. Deployment & Hardware

### GPU Dependency
- **Issue**: The backend heavily implies the presence of a CUDA or MPS (Mac) capable GPU.
- **Impact**: Performance on standard CPU-only cloud instances or older laptops is significantly degraded (1-2 FPS max).

### Lack of Specialized Sensors
- **Issue**: Reliance solely on RGB visual data.
- **Impact**: No thermal data (detecting hot stoves), no LiDAR (precise distance), and no ultrasonic sensors (glass door detection).

---

## Future Roadmap to Address Limitations

1. **Hardware**: Move to stereo cameras or DepthAPI-capable phones (iPhone Pro with LiDAR).
2. **Edge AI**: Quantize models to INT8/FP16 and deploy on device using TensorRT/CoreML.
3. **Fine-tuning**: Curate a dataset of "hazard scenarios" to fine-tune YOLO and the VLM.
4. **Sensor Fusion**: Integrate IMU (Accelerometer/Gyroscope) data to solve the relative motion problem.
5. **Emotive TTS**: Integrate ElevenLabs or similar low-latency emotive TTS API.

