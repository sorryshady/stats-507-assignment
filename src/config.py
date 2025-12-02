"""Configuration constants for the dual-loop system."""

# History Buffer
HISTORY_BUFFER_SIZE = 90  # 90 frames at 30 FPS = 3 seconds

# Safety Zone Configuration
CENTER_ZONE_THRESHOLD = 0.4  # 40% center of frame
EXPANSION_THRESHOLD = 0.4  # 40% growth triggers warning
MIN_APPROACH_DISTANCE = 15.0  # pixels object center must move toward frame center
EXPANSION_TIME_WINDOW = 1.5  # seconds for expansion check
GLOBAL_WARNING_COOLDOWN = 5.0  # seconds between ANY warnings

# Hazard Classes (COCO class names)
HAZARD_CLASSES = ["car", "truck", "bus", "bicycle", "motorcycle", "person"]

# Camera Configuration
CAMERA_DEVICE_ID = 0  # 0 for default webcam, 1 for iPhone continuity camera
CAMERA_FPS = 30
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

# Model Paths
YOLO_MODEL_PATH = "yolo11n.pt"
YOLO_CONFIDENCE_THRESHOLD = 0.7
BLIP_MODEL_NAME = "Salesforce/blip-image-captioning-base"

# Ollama Configuration
OLLAMA_API_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:3b"

# Audio Configuration
BEEP_FREQUENCY = 800  # Hz
BEEP_DURATION = 0.2  # seconds
TTS_RATE = 220  # words per minute
BEEP_COOLDOWN = 1.0  # seconds between beeps
HAZARD_BEEP_COOLDOWN = 3.0  # seconds between hazard beeps

# Threading Configuration
REFLEX_LOOP_FPS = 30
COGNITIVE_LOOP_TIMEOUT = 2.0  # seconds

# Logging
LOG_LEVEL = "INFO"

# Test Mode Settings
TEST_MODE_QUIET_HAZARDS = True
TEST_MODE_DISABLE_AUDIO = False

# Visualization Settings
SHOW_TRACKING_VISUALIZATION = True
VISUAL_WARNING_PERSISTENCE_DURATION = 1.0  # seconds to keep warning visible
