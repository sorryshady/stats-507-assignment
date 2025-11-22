"""Configuration constants for the dual-loop system."""

# History Buffer
HISTORY_BUFFER_SIZE = 90  # 90 frames at 30 FPS = 3 seconds

# Safety Zone Configuration
CENTER_ZONE_THRESHOLD = 0.4  # 40% center of frame
EXPANSION_THRESHOLD = 0.1  # 10% growth triggers warning
EXPANSION_TIME_WINDOW = 0.5  # 0.5 seconds for expansion check

# Hazard Classes (COCO class names)
HAZARD_CLASSES = ["car", "truck", "bus", "bicycle", "motorcycle", "person"]

# Camera Configuration
CAMERA_DEVICE_ID = 0  # Default webcam, adjust for iPhone
CAMERA_FPS = 30
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

# Model Paths
YOLO_MODEL_PATH = "yolo11n.pt"
BLIP_MODEL_NAME = "Salesforce/blip-image-captioning-base"

# Ollama Configuration
OLLAMA_API_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:3b"
# Note: Ollama automatically uses Metal GPU acceleration on Mac when available
# Ensure Ollama is running with GPU support: ollama serve

# Audio Configuration
BEEP_FREQUENCY = 800  # Hz
BEEP_DURATION = 0.2  # seconds
TTS_RATE = 180  # words per minute (faster = more natural)
BEEP_COOLDOWN = 1.0  # Minimum seconds between beeps (reduced spam)
HAZARD_BEEP_COOLDOWN = 2.0  # Minimum seconds between hazard beeps

# Threading Configuration
REFLEX_LOOP_FPS = 30
COGNITIVE_LOOP_TIMEOUT = 2.0  # seconds

# Logging
LOG_LEVEL = "INFO"

# Test Mode Settings
TEST_MODE_QUIET_HAZARDS = True  # Reduce hazard logging in test mode
TEST_MODE_DISABLE_AUDIO = (
    False  # Disable audio warnings in test mode (but allow narration audio)
)

# Visualization Settings
SHOW_TRACKING_VISUALIZATION = True  # Show live tracking feed with bounding boxes
