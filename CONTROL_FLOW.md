# Control Flow Documentation: Describe My Environment

This document provides a comprehensive overview of the system's control flow, initialization sequence, component interactions, and data flow.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Initialization Sequence](#initialization-sequence)
3. [Thread Architecture](#thread-architecture)
4. [Main Loop Flow](#main-loop-flow)
5. [Reflex Loop Flow](#reflex-loop-flow)
6. [Cognitive Loop Flow](#cognitive-loop-flow)
7. [Audio System Flow](#audio-system-flow)
8. [Data Structures & Queues](#data-structures--queues)
9. [Event Handling](#event-handling)
10. [Shutdown Sequence](#shutdown-sequence)

---

## System Overview

The system operates on a **dual-loop architecture**:

- **Reflex Loop (30 FPS)**: Fast, safety-critical monitoring for immediate hazard warnings
- **Cognitive Loop (On-Demand)**: Detailed scene narration triggered by user (SPACE key)

Both loops run in separate threads, coordinated by a main thread that captures camera frames.

---

## Initialization Sequence

### 1. Entry Point (`main()` function)

```python
# Location: src/main.py, line ~519
def main():
    # Parse command-line arguments
    # --test: Enable test mode
    # --test-video: Use video file instead of camera
    # --use-camera: Use camera even in test mode
    # --camera-id: Specify camera device ID

    # Create DualLoopSystem instance
    system = DualLoopSystem(test_mode, test_video_path, use_camera, camera_id)

    # Start the system
    system.start()

    # Run until ESC key pressed
    system.run()

    # Cleanup
    system.stop()
```

### 2. DualLoopSystem.**init**()

**Location:** `src/main.py`, lines 42-111

**Initialization Order:**

1. **Hardware Components:**

   ```python
   self.camera = CameraHandler(test_mode, test_video_path, use_camera, device_id)
   # - Opens camera/video file
   # - Configures resolution (1280x720)
   # - Sets FPS (30)

   self.audio = AudioHandler()
   # - Initializes pyttsx3 TTS engine
   # - Sets up sounddevice for beeps
   # - Starts speech worker thread (priority queue)
   ```

2. **Tracking & Safety:**

   ```python
   self.tracker = YOLOTracker()
   # - Loads YOLO11n.pt model
   # - Configures GPU (MPS for Mac, CUDA for NVIDIA, CPU fallback)
   # - Sets confidence threshold (0.7)

   self.safety_monitor = SafetyMonitor(CAMERA_WIDTH, CAMERA_HEIGHT)
   # - Initializes PhysicsEngine
   # - Sets frame dimensions (1280x720)
   ```

3. **Cognitive Components:**

   ```python
   self.history_buffer = HistoryBuffer()
   # - Creates deque-based storage (maxlen=90 frames)
   # - Thread-safe operations

   self.scene_composer = SceneComposer()
   # - Loads BLIP model (Salesforce/blip-image-captioning-base)
   # - Configures GPU (MPS/CUDA/CPU)

   self.trajectory_analyzer = TrajectoryAnalyzer()
   # - Uses PhysicsEngine for calculations

   self.narrator = LLMNarrator()
   # - Sets Ollama API URL (http://localhost:11434)
   # - Sets model name (llama3.2:3b)
   ```

4. **Threading Infrastructure:**

   ```python
   self.reflex_queue = ThreadSafeQueue(maxsize=5)
   # - Queue for frames to reflex loop
   # - Max 5 frames buffered (prevents lag)

   self.cognitive_queue = ThreadSafeQueue(maxsize=1)
   # - Queue for cognitive loop triggers
   # - Max 1 trigger (only latest matters)

   self.frame_lock = threading.Lock()
   # - Protects current_frame, annotated_frame, frame_id
   ```

5. **State Variables:**
   ```python
   self.running = False
   self.frame_id = 0
   self.current_frame = None
   self.annotated_frame = None
   self.last_warning_time = 0
   self.global_warning_cooldown = 5.0  # seconds
   self.last_warned_hazard_id = None
   ```

### 3. DualLoopSystem.start()

**Location:** `src/main.py`, lines 113-160

**Startup Sequence:**

1. **Check Ollama Connection:**

   ```python
   if not self.narrator.check_connection():
       logger.warning("Ollama not available...")
   # - Makes HTTP GET request to http://localhost:11434/api/tags
   # - Warns if Ollama is not running (narration will fail)
   ```

2. **Start Threads:**

   ```python
   self.running = True

   # Reflex Loop Thread (runs _reflex_loop method)
   self.reflex_thread = threading.Thread(target=self._reflex_loop, daemon=True)
   self.reflex_thread.start()

   # Cognitive Loop Thread (runs _cognitive_loop method)
   self.cognitive_thread = threading.Thread(target=self._cognitive_loop, daemon=True)
   self.cognitive_thread.start()
   ```

3. **Start Keyboard Listener:**

   ```python
   self.keyboard_listener = keyboard.Listener(on_press=self._on_key_press)
   self.keyboard_listener.start()
   # - Listens for SPACE (trigger narration) and ESC (exit)
   ```

4. **Start Main Loop:**
   ```python
   self._main_loop()  # Blocks until self.running = False
   ```

---

## Thread Architecture

### Thread Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Main Thread                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  _main_loop()                                         │  │
│  │  - Captures frames from camera                        │  │
│  │  - Puts frames into reflex_queue                       │  │
│  │  - Updates current_frame (with lock)                   │  │
│  │  - Displays visualization (OpenCV)                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ├─────────────────┐
                            │                 │
                            ▼                 ▼
        ┌──────────────────────────┐  ┌──────────────────────────┐
        │   Reflex Loop Thread     │  │  Cognitive Loop Thread   │
        │   (30 FPS, Continuous)   │  │  (On-Demand, Triggered)  │
        │                          │  │                          │
        │  _reflex_loop()          │  │  _cognitive_loop()       │
        │  - Gets frame from queue │  │  - Waits for trigger     │
        │  - Runs YOLO tracking    │  │  - Gets frame snapshot   │
        │  - Updates history       │  │  - Runs BLIP             │
        │  - Checks hazards        │  │  - Analyzes trajectories │
        │  - Triggers audio        │  │  - Calls LLM             │
        │                          │  │  - Speaks narration     │
        └──────────────────────────┘  └──────────────────────────┘
                            │                 │
                            └────────┬────────┘
                                     │
                                     ▼
                        ┌──────────────────────────┐
                        │   Audio Worker Thread    │
                        │   (Priority Queue)       │
                        │                          │
                        │  _start_speech_worker()  │
                        │  - Processes speech queue│
                        │  - Plays beeps           │
                        │  - Speaks TTS            │
                        └──────────────────────────┘
```

### Thread Communication

- **Main → Reflex:** `reflex_queue.put((frame_id, frame, timestamp, image_name))`
- **Main → Cognitive:** `cognitive_queue.put("trigger")` (via keyboard)
- **Reflex → Audio:** `audio.play_beep()`, `audio.speak_text(text, priority=True)`
- **Cognitive → Audio:** `audio.speak_text(text, priority=False)`
- **Shared State:** `current_frame`, `annotated_frame`, `frame_id` (protected by `frame_lock`)

---

## Main Loop Flow

**Location:** `src/main.py`, lines 162-208

### Flow Diagram

```
START _main_loop()
│
├─> Calculate frame_time = 1.0 / REFLEX_LOOP_FPS  (≈ 0.033s)
│
└─> WHILE self.running:
    │
    ├─> start_time = time.time()
    │
    ├─> success, frame, image_name = camera.read_frame()
    │   │
    │   ├─> IF test_mode AND test_video_path:
    │   │   └─> Read from video file (loops when finished)
    │   │
    │   ├─> ELIF test_mode AND use_camera:
    │   │   └─> Read from camera (image_name = "camera")
    │   │
    │   └─> ELSE:
    │       └─> Read from camera (normal mode)
    │
    ├─> IF success:
    │   │
    │   ├─> frame_id += 1
    │   │
    │   ├─> WITH frame_lock:
    │   │   ├─> current_frame = frame.copy()
    │   │   └─> current_image_name = image_name
    │   │
    │   ├─> timestamp = time.time()
    │   │
    │   ├─> reflex_queue.put((frame_id, frame, timestamp, image_name), block=False)
    │   │   └─> Non-blocking (drops frame if queue full)
    │   │
    │   └─> IF show_visualization:
    │       │
    │       └─> WITH frame_lock:
    │           └─> IF annotated_frame is not None:
    │               └─> cv2.imshow("Tracking", annotated_frame)
    │                   └─> cv2.waitKey(1)  # Non-blocking
    │
    └─> Sleep to maintain FPS:
        └─> elapsed = time.time() - start_time
            └─> sleep_time = max(0, frame_time - elapsed)
            └─> time.sleep(sleep_time)
```

### Key Points

- **Frame Rate:** Maintains 30 FPS (one frame every ~33ms)
- **Non-Blocking Queue:** If reflex loop is slow, frames are dropped (prevents lag)
- **Visualization:** Only displayed in main thread (OpenCV requirement)
- **Thread Safety:** `frame_lock` protects shared frame data

---

## Reflex Loop Flow

**Location:** `src/main.py`, lines 210-389

### Flow Diagram

```
START _reflex_loop()
│
└─> WHILE self.running:
    │
    ├─> TRY:
    │   │
    │   ├─> item = reflex_queue.get(timeout=0.1)
    │   │   └─> Blocks up to 100ms waiting for frame
    │   │
    │   ├─> IF item is None:
    │   │   └─> continue  # Skip this iteration
    │   │
    │   ├─> Unpack: frame_id, frame, timestamp, image_name = item
    │   │
    │   ├─> result = tracker.track(frame, frame_id, timestamp, return_annotated)
    │   │   │
    │   │   └─> YOLOTracker.track() [src/reflex_loop/tracker.py]
    │   │       │
    │   │       ├─> results = model.track(frame, persist=True, conf=0.7)
    │   │       │   └─> YOLO11n-track inference (GPU accelerated)
    │   │       │
    │   │       ├─> Extract detections:
    │   │       │   ├─> For each detection:
    │   │       │   │   ├─> box = (x1, y1, x2, y2)
    │   │       │   │   ├─> class_name = COCO class name
    │   │       │   │   ├─> confidence = detection score
    │   │       │   │   ├─> track_id = YOLO tracking ID (or None)
    │   │       │   │   └─> Create DetectionPoint(frame_id, timestamp, box, area, center, class_name, confidence, track_id)
    │   │       │   │
    │   │       └─> IF return_annotated:
    │   │           └─> annotated_frame = results[0].plot()
    │   │               └─> YOLO's built-in visualization
    │   │
    │   ├─> detections, annotated_frame = result
    │   │
    │   ├─> IF show_visualization AND annotated_frame:
    │   │   └─> WITH frame_lock:
    │   │       └─> self.annotated_frame = annotated_frame.copy()
    │   │           └─> Main thread will display this
    │   │
    │   ├─> FOR each detection:
    │   │   │
    │   │   ├─> object_id = detection.track_id OR hash(box, class_name)
    │   │   │
    │   │   └─> history_buffer.add_detection(object_id, detection)
    │   │       │
    │   │       └─> HistoryBuffer.add_detection() [src/cognitive_loop/history.py]
    │   │           │
    │   │           ├─> IF object_id not in buffer:
    │   │           │   └─> Create TrackedObject(object_id)
    │   │           │
    │   │           └─> tracked_object.add_detection(detection)
    │   │               └─> Adds to deque (maxlen=90, auto-drops oldest)
    │   │
    │   ├─> hazards = safety_monitor.check_hazards(detections, history_buffer)
    │   │   │
    │   │   └─> SafetyMonitor.check_hazards() [src/reflex_loop/safety.py]
    │   │       │
    │   │       ├─> FOR each detection:
    │   │       │   │
    │   │       │   ├─> Step 1: Class Check
    │   │       │   │   └─> IF class_name NOT in HAZARD_CLASSES:
    │   │       │   │       └─> continue  # Skip non-hazard objects
    │   │       │   │
    │   │       │   ├─> Step 2: Get TrackedObject from history
    │   │       │   │   └─> tracked_obj = history_buffer.get_object(object_id)
    │   │       │   │
    │   │       │   ├─> Step 3: Zone Check
    │   │       │   │   └─> in_zone = PhysicsEngine.is_in_center_zone(box, width, height)
    │   │       │   │       └─> Checks if center 40% of frame
    │   │       │   │
    │   │       │   ├─> Step 4: Expansion Check
    │   │       │   │   └─> area_growth = PhysicsEngine.calculate_area_growth(tracked_obj, 1.5s)
    │   │       │   │       └─> Calculates % growth over last 1.5 seconds
    │   │       │   │
    │   │       │   ├─> Step 5: Movement Check
    │   │       │   │   ├─> velocity = PhysicsEngine.calculate_velocity(tracked_obj)
    │   │       │   │   ├─> is_moving = |velocity| > 5.0 pixels/frame
    │   │       │   │   └─> is_approaching_center = PhysicsEngine.is_approaching_center(tracked_obj, width, height)
    │   │       │   │       └─> Checks if object center is moving toward frame center
    │   │       │   │
    │   │       │   └─> Step 6: Hazard Classification
    │   │       │       │
    │   │       │       ├─> IF is_expanding AND is_approaching_center:
    │   │       │       │   ├─> IF in_zone:
    │   │       │       │   │   └─> priority = "high"
    │   │       │       │   └─> ELSE:
    │   │       │       │       └─> priority = "medium"
    │   │       │       │
    │   │       │       └─> Create Hazard(object_id, class_name, priority, reason)
    │   │       │
    │   │       └─> RETURN list of Hazard objects
    │   │
    │   ├─> IF safety_monitor.should_warn(hazards):
    │   │   │
    │   │   └─> SafetyMonitor.should_warn() [src/reflex_loop/safety.py]
    │   │       └─> RETURN True if any hazard has priority "high" or "medium"
    │   │
    │   └─> IF should_warn:
    │       │
    │       ├─> current_time = time.time()
    │       │
    │       ├─> GLOBAL COOLDOWN CHECK:
    │       │   └─> IF (current_time - last_warning_time) < 5.0 seconds:
    │       │       └─> continue  # Skip warning (prevents spam)
    │       │
    │       ├─> warning_msg = safety_monitor.get_warning_message(hazards)
    │       │   └─> Returns: "STOP! Person in front of you" or similar
    │       │
    │       ├─> current_hazard_id = hazards[0].object_id
    │       │
    │       ├─> Check same hazard cooldown:
    │       │   └─> IF same hazard AND within 3 seconds:
    │       │       └─> continue  # Skip (redundant check)
    │       │
    │       ├─> Play beep (if cooldown allows):
    │       │   └─> IF (current_time - audio.last_hazard_beep_time) >= 3.0:
    │       │       └─> audio.play_beep()
    │       │           └─> Plays 800Hz beep for 0.2s (in background thread)
    │       │
    │       └─> Speak warning (after beep):
    │           └─> audio.speak_text(warning_msg, priority=True)
    │               └─> Adds to speech queue (HIGH priority)
    │               └─> Speech worker will process after beep finishes
    │
    └─> Cleanup (every 30 frames):
        └─> IF frame_id % 30 == 0:
            └─> history_buffer.cleanup_stale_objects(frame_id)
                └─> Removes objects not seen in last 90 frames
```

### Key Points

- **Speed:** Runs at 30 FPS (one iteration every ~33ms)
- **Hazard Detection:** Multi-step logic (class → zone → expansion → movement)
- **Rate Limiting:** Global 5-second cooldown prevents warning spam
- **Audio Priority:** Beep plays first, then speech (speech waits for beep)

---

## Cognitive Loop Flow

**Location:** `src/main.py`, lines 391-472

### Flow Diagram

```
START _cognitive_loop()
│
└─> WHILE self.running:
    │
    ├─> TRY:
    │   │
    │   ├─> item = cognitive_queue.get(timeout=0.5)
    │   │   └─> Blocks up to 500ms waiting for trigger (SPACE key)
    │   │
    │   ├─> IF item is None:
    │   │   └─> continue  # No trigger, keep waiting
    │   │
    │   ├─> logger.info("Cognitive loop triggered")
    │   │
    │   ├─> Get frame snapshot (with lock):
    │   │   └─> WITH frame_lock:
    │   │       ├─> frame = current_frame.copy()
    │   │       ├─> current_frame_id = frame_id
    │   │       └─> current_image_name = image_name
    │   │
    │   ├─> IF test_mode:
    │   │   └─> logger.info(f"Processing image: {current_image_name}")
    │   │
    │   ├─> Step 1: Generate Scene Description
    │   │   └─> scene_description = scene_composer.generate_scene_description(frame)
    │   │       │
    │   │       └─> SceneComposer.generate_scene_description() [src/cognitive_loop/scene_composer.py]
    │   │           │
    │   │           ├─> Convert frame (BGR) → PIL Image (RGB)
    │   │           │
    │   │           ├─> caption = blip_model.generate(image)
    │   │           │   └─> BLIP inference (GPU accelerated)
    │   │           │   └─> Returns: "A person sitting in a room" (example)
    │   │           │
    │   │           └─> caption = _sanitize_caption(caption)
    │   │               └─> Filters inappropriate content (e.g., explicit words)
    │   │               └─> Returns safe caption
    │   │
    │   ├─> Step 2: Analyze Trajectories
    │   │   └─> tracked_objects = history_buffer.get_all_objects()
    │   │       └─> Returns dict of {object_id: TrackedObject}
    │   │
    │   │   └─> object_movements = trajectory_analyzer.analyze_all_objects(tracked_objects)
    │   │       │
    │   │       └─> TrajectoryAnalyzer.analyze_all_objects() [src/cognitive_loop/trajectory.py]
    │   │           │
    │   │           ├─> Detect camera shake:
    │   │           │   └─> _detect_camera_shake(tracked_objects)
    │   │           │       └─> Checks if multiple objects move in same direction
    │   │           │
    │   │           ├─> FOR each tracked_object:
    │   │           │   │
    │   │           │   ├─> movement = analyze_movement(tracked_object)
    │   │           │   │   │
    │   │           │   │   └─> TrajectoryAnalyzer.analyze_movement()
    │   │           │   │       │
    │   │           │   │       ├─> Get trajectory (last 90 frames)
    │   │           │   │       │
    │   │           │   │       ├─> Calculate velocity:
    │   │           │   │       │   └─> velocity = PhysicsEngine.calculate_velocity(tracked_object)
    │   │           │   │       │       └─> Returns (delta_x, delta_y) pixels/frame
    │   │           │   │       │
    │   │           │   │       ├─> Calculate area growth:
    │   │           │   │       │   └─> area_growth = PhysicsEngine.calculate_area_growth(tracked_object, 1.5s)
    │   │           │   │       │
    │   │           │   │       └─> Classify movement:
    │   │           │   │           │
    │   │           │   │           ├─> IF area_growth > 25% AND velocity > 5:
    │   │           │   │           │   └─> "Approaching"
    │   │           │   │           │
    │   │           │   │           ├─> ELIF area_growth < -25% AND velocity > 5:
    │   │           │   │           │   └─> "Leaving"
    │   │           │   │           │
    │   │           │   │           ├─> ELIF velocity > 5:
    │   │           │   │           │   └─> "Passing by"
    │   │           │   │           │
    │   │           │   │           └─> ELSE:
    │   │           │   │               └─> "Stationary"
    │   │           │   │
    │   │           │   └─> Format: "person: Approaching (center moving closer, 30% growth)"
    │   │           │
    │   │           └─> IF camera_shake detected:
    │   │               └─> Apply stricter thresholds (filter out false movements)
    │   │
    │   ├─> Step 3: Log Inputs (test mode only)
    │   │   └─> IF test_mode:
    │   │       ├─> logger.info("--- INPUTS TO LLM ---")
    │   │       ├─> logger.info(f"Scene Description: {scene_description}")
    │   │       └─> logger.info("Detected Objects & Movements:")
    │   │           └─> FOR each movement: logger.info(f"  - {movement}")
    │   │
    │   ├─> Step 4: Generate Narration
    │   │   └─> narration = narrator.generate_narration_from_components(scene_description, object_movements)
    │   │       │
    │   │       └─> LLMNarrator.generate_narration_from_components() [src/cognitive_loop/narrator.py]
    │   │           │
    │   │           ├─> prompt = compose_prompt(scene_description, object_movements)
    │   │           │   │
    │   │           │   └─> Formats prompt:
    │   │           │       """
    │   │           │       SYSTEM: You are a helpful assistant for a blind user. Be concise and direct.
    │   │           │
    │   │           │       USER:
    │   │           │       Context: "{scene_description}"
    │   │           │       Entities:
    │   │           │       - {movement1}
    │   │           │       - {movement2}
    │   │           │
    │   │           │       TASK: Summarize in one natural sentence, prioritizing safety.
    │   │           │       """
    │   │           │
    │   │           ├─> narration = generate_narration(prompt)
    │   │           │   │
    │   │           │   └─> HTTP POST to http://localhost:11434/api/generate
    │   │           │       │
    │   │           │       ├─> Payload:
    │   │           │       │   {
    │   │           │       │     "model": "llama3.2:3b",
    │   │           │       │     "prompt": "...",
    │   │           │       │     "stream": false,
    │   │           │       │     "options": {
    │   │           │       │       "temperature": 0.3,
    │   │           │       │       "top_p": 0.9,
    │   │           │       │       "num_predict": 100
    │   │           │       │     }
    │   │           │       │   }
    │   │           │       │
    │   │           │       └─> Response: {"response": "A person is sitting in a room..."}
    │   │           │
    │   │           └─> narration = _clean_narration(narration)
    │   │               └─> Removes conversational elements ("Sure!", "Let me...", etc.)
    │   │
    │   ├─> Step 5: Speak Narration
    │   │   └─> IF narration:
    │   │       │
    │   │       ├─> logger.info(f"Narration: {narration}")
    │   │       │
    │   │       └─> audio.speak_text(narration, priority=False)
    │   │           └─> Adds to speech queue (LOW priority)
    │   │           └─> Speech worker will process sequentially
    │   │
    │   └─> ELSE (narration failed):
    │       └─> Fallback: audio.speak_text(f"Scene: {scene_description}", priority=False)
    │
    └─> EXCEPT Empty:
        └─> continue  # No trigger, keep waiting
```

### Key Points

- **Trigger:** Only runs when SPACE key pressed (or manual trigger)
- **Snapshot:** Takes a copy of current frame (doesn't interfere with reflex loop)
- **Multi-Step:** Scene description → Trajectory analysis → LLM fusion → TTS
- **Test Mode:** Logs LLM inputs for debugging

---

## Audio System Flow

**Location:** `src/hardware/audio.py`

### Initialization

```python
AudioHandler.__init__()
│
├─> _init_tts()
│   └─> Initialize pyttsx3 engine
│       ├─> Set voice (prefer "Samantha" on macOS)
│       ├─> Set rate (220 WPM)
│       └─> Set volume (0.9)
│
├─> _init_sounddevice()
│   └─> Check sounddevice availability
│       └─> Fallback to system beep if unavailable
│
└─> _start_speech_worker()
    └─> Start background thread running _process_speech()
```

### Speech Worker Thread

```
START _process_speech()
│
└─> WHILE speech_worker_running:
    │
    ├─> request = speech_queue.get(block=True)
    │   └─> Blocks until request available
    │   └─> Priority queue: HIGH priority (hazards) processed first
    │
    ├─> IF request.priority == HIGH:
    │   └─> Wait for beep to finish (up to 0.5s)
    │       └─> Prevents speech from cutting off beep
    │
    ├─> _speak_pyttsx3(request.text)
    │   │
    │   └─> tts_engine.say(text)
    │       └─> tts_engine.runAndWait()  # Blocks until speech completes
    │
    └─> OR _speak_system(request.text)  # Fallback
        └─> subprocess.run(["say", text])  # macOS system command
```

### Beep Playback

```python
play_beep()
│
├─> Check cooldown:
│   └─> IF (current_time - last_beep_time) < beep_cooldown:
│       └─> return  # Skip beep
│
├─> Generate wave:
│   └─> wave = numpy.sin(2 * π * 800Hz * t) for t in [0, 0.2s]
│
└─> Play in background thread:
    └─> threading.Thread(target=_play_beep_thread, args=(wave,))
        └─> sounddevice.play(wave, samplerate=44100)
        └─> sounddevice.wait()  # Wait for playback to finish
```

### Priority Queue Logic

- **HIGH Priority (2):** Hazard warnings (processed first)
- **LOW Priority (1):** Regular narration (processed after hazards)
- **Queue Order:** Lower number = higher priority (Python PriorityQueue)

---

## Data Structures & Queues

### DetectionPoint

**Location:** `src/utils/data_structures.py`

```python
@dataclass
class DetectionPoint:
    frame_id: int
    timestamp: float
    box: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    area: int  # pixels²
    center: Tuple[int, int]  # (x, y)
    class_name: str  # COCO class name
    confidence: float  # 0.0-1.0
    track_id: Optional[int]  # YOLO tracking ID
```

### TrackedObject

**Location:** `src/utils/data_structures.py`

```python
class TrackedObject:
    object_id: int
    class_name: str
    detections: deque  # Maxlen=90, stores DetectionPoint objects
    first_seen: int  # frame_id
    last_seen: int  # frame_id

    def get_trajectory(self) -> List[DetectionPoint]:
        return list(self.detections)
```

### HistoryBuffer

**Location:** `src/cognitive_loop/history.py`

```python
class HistoryBuffer:
    objects: Dict[int, TrackedObject]  # {object_id: TrackedObject}

    def add_detection(self, object_id: int, detection: DetectionPoint):
        # Adds detection to TrackedObject's deque

    def get_object(self, object_id: int) -> Optional[TrackedObject]:
        # Returns TrackedObject or None

    def get_all_objects(self) -> Dict[int, TrackedObject]:
        # Returns all tracked objects
```

### Queues

- **`reflex_queue`:** `ThreadSafeQueue(maxsize=5)`

  - Items: `(frame_id, frame, timestamp, image_name)`
  - Producer: Main loop
  - Consumer: Reflex loop

- **`cognitive_queue`:** `ThreadSafeQueue(maxsize=1)`

  - Items: `"trigger"` (string)
  - Producer: Keyboard listener (SPACE key)
  - Consumer: Cognitive loop

- **`speech_queue`:** `queue.PriorityQueue()`
  - Items: `SpeechRequest(text, priority, timestamp)`
  - Producer: Reflex loop (hazards), Cognitive loop (narration)
  - Consumer: Audio worker thread

---

## Event Handling

### Keyboard Listener

**Location:** `src/main.py`, lines 474-487

```python
def _on_key_press(self, key):
    IF key == keyboard.Key.space:
        └─> cognitive_queue.put("trigger", block=False)
            └─> Triggers cognitive loop narration

    ELIF key == keyboard.Key.esc:
        └─> self.running = False
            └─> Exits main loop (system stops)
```

### Keyboard Listener Thread

- **Library:** `pynput.keyboard`
- **Thread:** Runs in background, calls `_on_key_press` callback
- **Non-Blocking:** Doesn't interfere with main loop

---

## Shutdown Sequence

**Location:** `src/main.py`, lines 489-516

### Flow

```
stop()
│
├─> logger.info("Stopping dual-loop system...")
│
├─> self.running = False
│   └─> Signals all threads to exit
│
├─> audio.stop()
│   │
│   └─> AudioHandler.stop()
│       ├─> speech_worker_running = False
│       ├─> speech_queue.put(None)  # Wake worker thread
│       └─> speech_worker_thread.join(timeout=2.0)
│
├─> IF show_visualization:
│   └─> cv2.destroyAllWindows()
│
├─> Wait for threads:
│   ├─> reflex_thread.join(timeout=2.0)
│   └─> cognitive_thread.join(timeout=2.0)
│
├─> keyboard_listener.stop()
│
├─> camera.release()
│   └─> Closes camera/video file
│
└─> logger.info("Dual-loop system stopped")
```

### Graceful Shutdown

- **Threads:** Given 2 seconds to finish current operation
- **Audio:** Worker thread processes remaining queue items before exit
- **Resources:** Camera and OpenCV windows are properly released

---

## Summary: Complete Call Chain

### Example: Hazard Warning Flow

```
1. Main Loop
   └─> camera.read_frame()
       └─> Returns frame

2. Main Loop
   └─> reflex_queue.put(frame)

3. Reflex Loop
   └─> tracker.track(frame)
       └─> YOLO11n-track inference
           └─> Returns detections

4. Reflex Loop
   └─> history_buffer.add_detection()
       └─> Updates TrackedObject history

5. Reflex Loop
   └─> safety_monitor.check_hazards()
       └─> PhysicsEngine.calculate_area_growth()
       └─> PhysicsEngine.calculate_velocity()
       └─> PhysicsEngine.is_approaching_center()
       └─> Returns Hazard objects

6. Reflex Loop
   └─> audio.play_beep()
       └─> Plays beep in background thread

7. Reflex Loop
   └─> audio.speak_text("STOP! Person in front of you", priority=True)
       └─> speech_queue.put(SpeechRequest(..., HIGH))

8. Audio Worker Thread
   └─> speech_queue.get()
       └─> Waits for beep to finish
       └─> tts_engine.say("STOP! Person in front of you")
           └─> Speech plays
```

### Example: Cognitive Narration Flow

```
1. User presses SPACE key
   └─> keyboard_listener._on_key_press()
       └─> cognitive_queue.put("trigger")

2. Cognitive Loop
   └─> cognitive_queue.get()
       └─> Receives trigger

3. Cognitive Loop
   └─> scene_composer.generate_scene_description(frame)
       └─> BLIP model inference
           └─> Returns "A person sitting in a room"

4. Cognitive Loop
   └─> trajectory_analyzer.analyze_all_objects()
       └─> PhysicsEngine.calculate_velocity()
       └─> PhysicsEngine.calculate_area_growth()
       └─> Returns ["person: Stationary"]

5. Cognitive Loop
   └─> narrator.generate_narration_from_components()
       └─> compose_prompt()
       └─> HTTP POST to Ollama API
           └─> Returns "A person is sitting in a room."

6. Cognitive Loop
   └─> audio.speak_text("A person is sitting in a room.", priority=False)
       └─> speech_queue.put(SpeechRequest(..., LOW))

7. Audio Worker Thread
   └─> speech_queue.get()
       └─> tts_engine.say("A person is sitting in a room.")
           └─> Speech plays
```

---

## End of Control Flow Documentation

This document provides a complete reference for understanding how the system operates, from initialization to shutdown, including all component interactions and data flows.
