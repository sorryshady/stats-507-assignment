import os
import time
from core.scene_composer import SceneComposer
from models.captioner import BlipCaptioner


def main():
    config = {
        "model_path": "yolo11n.pt",
        "conf_threshold": 0.5,
        "cap_model": "Salesforce/blip-image-captioning-base",
    }
    composer = SceneComposer(config=config)

    # Simulating a video feed (just re-using one image for demo)
    image_path = "test_images/test_image_0.jpg"

    print("🚀 Starting Navigation System...")
    print("   [Loop running at 30FPS] Scanning for hazards...")

    # --- 1. THE REFLEX LOOP (Fast) ---
    # In a real app, this runs constantly on the video feed
    # We only use the 'detector' part of the composer
    detections = composer.detector.predict(image_path)

    # Immediate Safety Check
    hazards = [d for d in detections if d.label in ["bus", "car", "truck"]]
    if hazards:
        print(f"⚠️  WARNING: {len(hazards)} vehicle(s) detected!")

    # --- 2. THE BRAIN LOOP (Slow/On-Demand) ---
    # User presses a button -> "What am I looking at?"
    print("\n[User Input] 'Describe scene' button pressed...")

    # Now we run the heavy full description
    full_analysis = composer.describe_scene(image_path)
    print(f"🤖 Audio: \"{full_analysis['text']}\"")


if __name__ == "__main__":
    main()
