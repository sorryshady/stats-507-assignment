# Usage Guide

## Setup

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Verify Ollama setup:**

   ```bash
   python verify_ollama.py
   ```

   If Ollama is not running or the model is missing:

   ```bash
   # Start Ollama (if not running)
   # Ollama automatically uses Metal GPU acceleration on Mac
   ollama serve

   # Pull Llama 3.2 3B model
   ollama pull llama3.2:3b

   # Verify GPU usage (should show Metal on Mac)
   ollama ps
   ```

3. **GPU Acceleration:**

   - **YOLO11**: Automatically uses MPS (Metal) on Mac, CUDA on NVIDIA GPUs
   - **BLIP**: Automatically uses MPS (Metal) on Mac, CUDA on NVIDIA GPUs
   - **Ollama/Llama**: Automatically uses Metal on Mac when available
   - All models will fall back to CPU if GPU is unavailable

4. **Ensure YOLO model is present:**
   The `yolo11n.pt` file should be in the project root.

## Running the System

### With Camera (Default)

```bash
python -m src.main
```

Normal mode with camera input. Press SPACE for narration, ESC to exit.

### Test Mode with Camera (Recommended for Testing)

```bash
python -m src.main --test --use-camera
```

Uses camera input with test mode features enabled:

- Detailed logging with source identification
- Reduced hazard warning noise
- Better debugging output

### With Test Video

```bash
python -m src.main --test --test-video path/to/test_video.mp4
```

Uses test video file instead of camera. Recommended for testing as it provides realistic temporal data for trajectory analysis.

### With Test Images (Fallback)

```bash
python -m src.main --test
```

Uses static test images from `test_images/` directory. Note: Using a video file or camera is recommended for better testing.

## Controls

- **SPACE**: Trigger cognitive loop narration
- **ESC**: Exit the system

## Architecture

The system runs two parallel loops:

1. **Reflex Loop (30 FPS)**: Continuously monitors for safety hazards

   - Detects objects using YOLO11 tracking
   - Calculates velocity and expansion
   - Triggers audio warnings for approaching hazards

2. **Cognitive Loop (On-Demand)**: Generates natural language descriptions
   - Triggered by SPACE key
   - Uses BLIP for scene understanding
   - Analyzes object trajectories
   - Generates narration via Llama 3.2

## Testing

Run unit tests:

```bash
python -m pytest tests/
```

Or run individual test files:

```bash
python tests/test_physics.py
python tests/test_trajectory.py
python tests/test_safety.py
```

## Troubleshooting

### Camera not working

- Check camera permissions (System Settings > Privacy & Security > Camera)
- **Find available cameras**: Run `python list_cameras.py` to see all available camera devices
- **iPhone Continuity Camera**:
  - Connect iPhone to Mac (USB or wirelessly)
  - Enable Continuity Camera on iPhone
  - Run `python list_cameras.py` to find the device ID (usually higher resolution like 1920x1080)
  - Update `CAMERA_DEVICE_ID` in `src/config.py` or use `--camera-id` flag
- Try different device IDs in `src/config.py` (`CAMERA_DEVICE_ID`)
- Use `--camera-id` command-line argument to override config: `python -m src.main --camera-id 1`
- Use `--test` flag to test with static images

### Ollama connection failed

- Ensure Ollama is running: `ollama serve`
- Check if model is available: `ollama list`
- Pull model if missing: `ollama pull llama3.2:3b`

### Audio not working

- Check system audio permissions
- On macOS, may need to grant microphone/audio permissions
- TTS may require system TTS engine setup

### Performance issues

- Reduce `REFLEX_LOOP_FPS` in `src/config.py`
- Use smaller BLIP model variant
- Ensure Metal acceleration is enabled for M4 Mac
