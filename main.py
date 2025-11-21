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
    print("=" * 40)
    print("Initializing Scene Composer...")
    print("=" * 40)
    composer = SceneComposer(config)

    image_path = "test_images/test_image_0.jpg"
    if not os.path.exists(image_path):
        print(f"Error: Test image not found at {image_path}")
        # Create a dummy file prompt or download logic could go here
        return
    print("=" * 40)
    print(f"\nProcessing {image_path}...")
    # Measure Speed
    start = time.time()
    result = composer.describe_scene(image_path)
    end = time.time()

    print("\n" + "=" * 50)
    print(f"🗣️  FINAL AUDIO OUTPUT")
    print("=" * 50)
    print(f"\"{result['text']}\"")
    print("=" * 50)

    print(f"\n⚡ Processing Time: {end - start:.2f} seconds")
    print(f"FPS: {1.0 / (end - start):.2f}")


if __name__ == "__main__":
    main()
