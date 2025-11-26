# Logging Documentation: Describe My Environment

This document explains how logging works throughout the system, with special focus on test mode behavior.

---

## Table of Contents

1. [Logging Configuration](#logging-configuration)
2. [Log Format](#log-format)
3. [Log Levels](#log-levels)
4. [Test Mode vs Normal Mode](#test-mode-vs-normal-mode)
5. [Component-Specific Logging](#component-specific-logging)
6. [Example Log Output](#example-log-output)
7. [Debugging Tips](#debugging-tips)

---

## Logging Configuration

### Basic Setup

Logging is configured in `src/main.py` at the module level:

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
```

**Key Points:**

- **Default Level**: `INFO` (set in `src/config.py` as `LOG_LEVEL = "INFO"`)
- **Format**: Timestamp, module name, level, message
- **Location**: All modules use `logger = logging.getLogger(__name__)` for module-specific loggers

### Module Loggers

Each module creates its own logger using the module name:

- `src.main` → `logger`
- `src.hardware.camera` → `logger`
- `src.hardware.audio` → `logger`
- `src.reflex_loop.tracker` → `logger`
- `src.reflex_loop.safety` → `logger`
- `src.reflex_loop.physics` → `logger`
- `src.cognitive_loop.history` → `logger`
- `src.cognitive_loop.scene_composer` → `logger`
- `src.cognitive_loop.trajectory` → `logger`
- `src.cognitive_loop.narrator` → `logger`

---

## Log Format

### Standard Format

```
YYYY-MM-DD HH:MM:SS,mmm - module.name - LEVEL - Message content
```

**Example:**

```
2024-01-15 14:23:45,123 - src.main - INFO - Dual-loop system started in TEST MODE.
```

### Format Components

- **`%(asctime)s`**: Timestamp (YYYY-MM-DD HH:MM:SS,mmm)
- **`%(name)s`**: Module name (e.g., `src.main`, `src.hardware.camera`)
- **`%(levelname)s`**: Log level (INFO, WARNING, ERROR, DEBUG)
- **`%(message)s`**: Actual log message

---

## Log Levels

### Levels Used in System

1. **`DEBUG`**: Detailed diagnostic information

   - Used for: Frame processing details, cooldown checks, internal state
   - Example: `"Skipping warning - global cooldown active (last warning 2.34s ago)"`

2. **`INFO`**: General informational messages

   - Used for: System startup, component initialization, user-triggered events, test mode details
   - Example: `"Cognitive loop triggered"`, `"Processing image: test_image_0.jpg"`

3. **`WARNING`**: Warning messages for non-critical issues

   - Used for: Failed frame reads, model fallbacks, hazard detection
   - Example: `"Failed to read frame from camera"`, `"HAZARD: Person in front of you"`

4. **`ERROR`**: Error messages for critical failures
   - Used for: Model loading failures, API errors, exceptions
   - Example: `"Failed to load BLIP model: ..."`, `"Ollama API error: 500"`

---

## Test Mode vs Normal Mode

### Test Mode Features

Test mode (`--test` flag) enables additional logging and modifies behavior:

#### 1. **Enhanced Source Identification**

**Test Mode:**

- Logs include image/video source names: `[test_image_0.jpg]`, `[test_video.mp4 (frame 42)]`, `[camera]`
- Helps track which input is being processed

**Normal Mode:**

- No source identifiers in logs (cleaner output)

#### 2. **Hazard Logging Reduction**

**Test Mode with `TEST_MODE_QUIET_HAZARDS = True`:**

- Only logs high-priority hazards
- Limits logging to every 30 frames maximum
- Format: `INFO` level with `[image_name]` tag
- Example: `"HAZARD (test mode [test_image_0.jpg]): STOP! Person in front of you"`

**Normal Mode:**

- Logs all hazards at `WARNING` level
- No frame limiting
- Format: `"HAZARD: STOP! Person in front of you"`

#### 3. **LLM Input Logging**

**Test Mode:**

- Logs complete inputs to Llama model before narration
- Shows scene description and object movements
- Format:
  ```
  --- INPUTS TO LLM ---
  Scene Description: A living room with a couch and TV.
  Detected Objects & Movements:
    - Person (ID: 4): Moving Left -> Right (Passing by).
    - Dog (ID: 7): Area grew 40% (Approaching rapidly).
  ---------------------
  ```

**Normal Mode:**

- No LLM input logging (only final narration)

#### 4. **Image Processing Logs**

**Test Mode:**

- Logs which image is being processed: `"Processing image: test_image_0.jpg"`
- Includes image name in narration logs: `"Narration [test_image_0.jpg]: A person is walking towards you"`

**Normal Mode:**

- No image name tracking

#### 5. **Audio Behavior**

**Test Mode with `TEST_MODE_DISABLE_AUDIO = False`:**

- Audio warnings still play (can be disabled)
- Narration audio always plays (user requested)

**Normal Mode:**

- All audio enabled

---

## Component-Specific Logging

### 1. Main Orchestrator (`src/main.py`)

#### Initialization

```
INFO - Starting dual-loop system...
INFO - Dual-loop system started in TEST MODE.
INFO - Using test video file for continuous frame processing.
INFO - Press Ctrl+C to exit.
INFO - Hazard warnings are reduced in test mode for cleaner output.
```

#### Thread Startup

```
INFO - Reflex loop started
INFO - Cognitive loop started
```

#### Cognitive Loop Trigger

```
INFO - Cognitive loop triggered
INFO - Processing image: test_image_0.jpg  # Test mode only
```

#### Hazard Detection

**Test Mode:**

```
INFO - HAZARD (test mode [test_image_0.jpg]): STOP! Person in front of you
```

**Normal Mode:**

```
WARNING - HAZARD: STOP! Person in front of you
```

#### Audio Actions

```
INFO - Playing hazard beep (cooldown: 3.45s)
INFO - Speaking hazard warning after beep: STOP! Person in front of you
INFO - Speaking narration: A person is walking towards you...
INFO - TTS call completed
```

#### Errors

```
ERROR - Error in reflex loop: ...
ERROR - Error in cognitive loop: ...
```

---

### 2. Camera Handler (`src/hardware/camera.py`)

#### Camera Initialization

```
INFO - Camera 0 initialized: 1280x720 @ 30.0 FPS (Backend: AVFoundation)
INFO - High resolution detected - this might be iPhone Continuity Camera
```

#### Test Video Loading

```
INFO - Loaded test video: test_video.mp4
INFO - Video properties: 1500 frames @ 30.00 FPS
```

#### Test Images Loading

```
INFO - Loaded 8 test images (fallback mode)
WARNING - Using static images - consider using a video file for better testing
```

#### Frame Read Failures

```
WARNING - Failed to read frame from camera
WARNING - Failed to read from test video
```

---

### 3. YOLO Tracker (`src/reflex_loop/tracker.py`)

#### Model Loading

```
INFO - YOLO model will use mps acceleration
INFO - YOLO model loaded from yolo11n.pt
WARNING - YOLO model using CPU - GPU not available
```

#### Tracking Errors

```
ERROR - Error during tracking: ...
ERROR - [traceback]
```

---

### 4. Safety Monitor (`src/reflex_loop/safety.py`)

**Note:** Safety monitor doesn't log directly. Hazards are logged by `main.py` after detection.

---

### 5. Scene Composer (`src/cognitive_loop/scene_composer.py`)

#### Model Loading

```
INFO - Loading BLIP model: Salesforce/blip-image-captioning-base
INFO - Using Apple Metal (MPS) GPU acceleration
INFO - BLIP model loaded on mps
WARNING - GPU not available, using CPU (slower)
```

#### Scene Generation

**Debug Level (not shown by default):**

```
DEBUG - Scene: A living room with a couch and TV.
```

#### Content Filtering

```
WARNING - BLIP generated inappropriate caption, filtering: ...
WARNING - BLIP caption contains inappropriate content, sanitizing: ...
```

#### Errors

```
ERROR - Error generating scene description: ...
WARNING - BLIP model not loaded, returning default description
```

---

### 6. LLM Narrator (`src/cognitive_loop/narrator.py`)

#### API Errors

```
ERROR - Ollama API error: 500 - Internal Server Error
ERROR - Ollama API timeout after 10.0s
ERROR - Failed to connect to Ollama at http://localhost:11434
ERROR - Error generating narration: ...
```

**Note:** Successful narrations are logged by `main.py`, not the narrator itself.

---

### 7. Audio Handler (`src/hardware/audio.py`)

#### TTS Engine Initialization

```
INFO - Initializing TTS engine...
INFO - TTS engine initialized successfully
WARNING - TTS engine initialization failed, using fallback (macOS 'say' command)
```

#### Speech Queue

```
DEBUG - Speech queue: 2 items pending
DEBUG - Processing speech request: Priority HIGH
```

#### Beep Actions

```
DEBUG - Beep on cooldown (1.23s < 3.0s)
DEBUG - Suppressing beep - object too close (area ratio: 0.45)
```

---

## Example Log Output

### Test Mode with Test Images

```
2024-01-15 14:23:45,123 - src.main - INFO - Starting dual-loop system...
2024-01-15 14:23:45,234 - src.hardware.camera - INFO - Loaded 8 test images (fallback mode)
2024-01-15 14:23:45,345 - src.reflex_loop.tracker - INFO - YOLO model will use mps acceleration
2024-01-15 14:23:45,456 - src.reflex_loop.tracker - INFO - YOLO model loaded from yolo11n.pt
2024-01-15 14:23:45,567 - src.cognitive_loop.scene_composer - INFO - Loading BLIP model: Salesforce/blip-image-captioning-base
2024-01-15 14:23:46,123 - src.cognitive_loop.scene_composer - INFO - Using Apple Metal (MPS) GPU acceleration
2024-01-15 14:23:46,234 - src.cognitive_loop.scene_composer - INFO - BLIP model loaded on mps
2024-01-15 14:23:46,345 - src.main - INFO - Dual-loop system started in TEST MODE.
2024-01-15 14:23:46,456 - src.main - INFO - Using test images (consider --test-video or --use-camera for better testing).
2024-01-15 14:23:46,567 - src.main - INFO - Press Ctrl+C to exit.
2024-01-15 14:23:46,678 - src.main - INFO - Hazard warnings are reduced in test mode for cleaner output.
2024-01-15 14:23:46,789 - src.main - INFO - Reflex loop started
2024-01-15 14:23:46,890 - src.main - INFO - Cognitive loop started
2024-01-15 14:23:47,001 - src.main - INFO - HAZARD (test mode [test_image_0.jpg]): STOP! Person in front of you
2024-01-15 14:23:47,112 - src.main - INFO - Playing hazard beep (cooldown: 0.00s)
2024-01-15 14:23:47,223 - src.main - INFO - Speaking hazard warning after beep: STOP! Person in front of you
2024-01-15 14:23:50,123 - src.main - INFO - Cognitive loop triggered
2024-01-15 14:23:50,234 - src.main - INFO - Processing image: test_image_0.jpg
2024-01-15 14:23:50,345 - src.main - INFO - --- INPUTS TO LLM ---
2024-01-15 14:23:50,456 - src.main - INFO - Scene Description: A living room with a couch and TV.
2024-01-15 14:23:50,567 - src.main - INFO - Detected Objects & Movements:
2024-01-15 14:23:50,678 - src.main - INFO -   - Person (ID: 4): Moving Left -> Right (Passing by).
2024-01-15 14:23:50,789 - src.main - INFO -   - Dog (ID: 7): Area grew 40% (Approaching rapidly).
2024-01-15 14:23:50,890 - src.main - INFO - ---------------------
2024-01-15 14:23:51,123 - src.main - INFO - Narration [test_image_0.jpg]: A person is walking towards you from the left.
2024-01-15 14:23:51,234 - src.main - INFO - Speaking narration: A person is walking towards you from the left...
2024-01-15 14:23:51,345 - src.main - INFO - TTS call completed
```

### Normal Mode (Production)

```
2024-01-15 14:23:45,123 - src.main - INFO - Starting dual-loop system...
2024-01-15 14:23:45,234 - src.hardware.camera - INFO - Camera 0 initialized: 1280x720 @ 30.0 FPS
2024-01-15 14:23:45,345 - src.reflex_loop.tracker - INFO - YOLO model will use mps acceleration
2024-01-15 14:23:45,456 - src.reflex_loop.tracker - INFO - YOLO model loaded from yolo11n.pt
2024-01-15 14:23:45,567 - src.cognitive_loop.scene_composer - INFO - Loading BLIP model: Salesforce/blip-image-captioning-base
2024-01-15 14:23:46,123 - src.cognitive_loop.scene_composer - INFO - Using Apple Metal (MPS) GPU acceleration
2024-01-15 14:23:46,234 - src.cognitive_loop.scene_composer - INFO - BLIP model loaded on mps
2024-01-15 14:23:46,345 - src.main - INFO - Dual-loop system started. Press SPACE for narration, ESC to exit.
2024-01-15 14:23:46,456 - src.main - INFO - Reflex loop started
2024-01-15 14:23:46,567 - src.main - INFO - Cognitive loop started
2024-01-15 14:23:47,123 - src.main - WARNING - HAZARD: STOP! Person in front of you
2024-01-15 14:23:47,234 - src.main - INFO - Playing hazard beep (cooldown: 0.00s)
2024-01-15 14:23:47,345 - src.main - INFO - Speaking hazard warning after beep: STOP! Person in front of you
2024-01-15 14:23:50,123 - src.main - INFO - Cognitive loop triggered
2024-01-15 14:23:50,234 - src.main - INFO - Narration: A person is walking towards you from the left.
2024-01-15 14:23:50,345 - src.main - INFO - Speaking narration: A person is walking towards you from the left...
2024-01-15 14:23:50,456 - src.main - INFO - TTS call completed
```

---

## Debugging Tips

### 1. **Enable Debug Logging**

To see `DEBUG` level logs, modify `src/main.py`:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

**What you'll see:**

- Frame processing details
- Cooldown checks
- Queue status
- Internal state transitions

### 2. **Filter by Module**

Use grep to filter logs by component:

```bash
python -m src.main --test 2>&1 | grep "src.reflex_loop"
python -m src.main --test 2>&1 | grep "src.cognitive_loop"
python -m src.main --test 2>&1 | grep "HAZARD"
```

### 3. **Save Logs to File**

```bash
python -m src.main --test 2>&1 | tee test_run.log
```

### 4. **Common Log Patterns**

**System Startup:**

- Look for: `"Starting dual-loop system"`, `"Reflex loop started"`, `"Cognitive loop started"`

**Hazard Detection:**

- Test mode: `"HAZARD (test mode [image]): ..."`
- Normal mode: `"HAZARD: ..."`

**LLM Processing:**

- Test mode: `"--- INPUTS TO LLM ---"` section
- Always: `"Narration: ..."` or `"Narration [image]: ..."`

**Errors:**

- Model loading: `"Failed to load ..."`
- API errors: `"Ollama API error: ..."`
- Frame errors: `"Failed to read frame ..."`

### 5. **Test Mode Verification**

Check if test mode is active:

- Look for: `"Dual-loop system started in TEST MODE."`
- Look for: Image names in logs: `[test_image_0.jpg]`
- Look for: `"--- INPUTS TO LLM ---"` section

### 6. **Performance Monitoring**

Key metrics logged:

- Frame processing: Check for `"Failed to read frame"` warnings
- Model inference: Check for timeout errors
- Audio: Check for `"TTS call completed"` after narration

---

## Configuration Options

### Test Mode Settings (`src/config.py`)

```python
# Test Mode Settings
TEST_MODE_QUIET_HAZARDS = True  # Reduce hazard logging in test mode
TEST_MODE_DISABLE_AUDIO = False  # Disable audio warnings in test mode

# Logging
LOG_LEVEL = "INFO"  # Change to "DEBUG" for more verbose output
```

### Modifying Log Behavior

**To disable test mode quiet hazards:**

```python
TEST_MODE_QUIET_HAZARDS = False  # In src/config.py
```

**To enable debug logging:**

```python
LOG_LEVEL = "DEBUG"  # In src/config.py
# And update main.py:
logging.basicConfig(level=logging.DEBUG, ...)
```

---

## Summary

### Key Differences: Test vs Normal Mode

| Feature                   | Test Mode                                     | Normal Mode             |
| ------------------------- | --------------------------------------------- | ----------------------- |
| **Source Identification** | ✅ Logs image/video names                     | ❌ No source names      |
| **Hazard Logging**        | Reduced (high priority only, every 30 frames) | Full (all hazards)      |
| **LLM Input Logging**     | ✅ Complete inputs shown                      | ❌ Only final narration |
| **Image Processing**      | ✅ Logs which image is processed              | ❌ No image tracking    |
| **Log Level**             | INFO (with test mode tags)                    | INFO/WARNING            |
| **Audio**                 | Configurable (can disable warnings)           | Always enabled          |

### Best Practices

1. **Use test mode for development**: `--test` flag enables detailed logging
2. **Use test video for realistic testing**: `--test-video` provides temporal data
3. **Check LLM inputs in test mode**: Verify what the model receives
4. **Monitor hazard logs**: Ensure warnings are appropriate
5. **Save logs for analysis**: Use `tee` to save output while viewing

---

**Last Updated:** 2024-01-15  
**Related Documents:** `CONTROL_FLOW.md`, `USAGE.md`
