import os
from core.scene_composer import SceneComposer


def main():
    config = {
        "model_path": "yolo11n.pt",
        "conf_threshold": 0.5,
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
    detections = composer.describe_scene(image_path)

    print(f"\nSuccessfully detected {len(detections)} objects:")
    print("-" * 40)
    for item in detections:
        # We can access .label, .confidence, .box because of our Dataclass!
        print(
            f"• {item.label.ljust(10)} | Conf: {item.confidence:.2f} | Box: {item.box}"
        )
    print("-" * 40)


if __name__ == "__main__":
    main()
