"""List available camera devices (helps find iPhone Continuity Camera)."""

import cv2
import sys


def list_cameras():
    """List all available camera devices."""
    print("=" * 60)
    print("Available Camera Devices")
    print("=" * 60)
    print()

    available_cameras = []

    print("Scanning for cameras (checking IDs 0-10)...")
    print()

    for device_id in range(11):
        cap = cv2.VideoCapture(device_id)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                backend = cap.getBackendName()

                available_cameras.append(
                    {
                        "id": device_id,
                        "width": width,
                        "height": height,
                        "fps": fps,
                        "backend": backend,
                    }
                )

                print(f"✓ Camera {device_id}:")
                print(f"  Resolution: {width}x{height}")
                print(f"  FPS: {fps:.2f}")
                print(f"  Backend: {backend}")
                print()
            cap.release()

    if not available_cameras:
        print("✗ No cameras found!")
        print()
        print("Troubleshooting:")
        print("- Make sure your iPhone is connected via Continuity Camera")
        print("- Check System Settings > Privacy & Security > Camera")
        print("- Try disconnecting and reconnecting your iPhone")
        return

    print("=" * 60)
    print("How to use:")
    print("=" * 60)
    print()
    print("To use iPhone Continuity Camera:")
    print("1. Connect your iPhone to your Mac (via USB or wirelessly)")
    print("2. On your iPhone, enable Continuity Camera")
    print("3. Look for a camera with high resolution (likely 1920x1080 or higher)")
    print("4. Update CAMERA_DEVICE_ID in src/config.py to the device ID shown above")
    print()
    print("Example:")
    if available_cameras:
        highest_res = max(available_cameras, key=lambda x: x["width"] * x["height"])
        print(f"  If Camera {highest_res['id']} is your iPhone, set:")
        print(f"  CAMERA_DEVICE_ID = {highest_res['id']}")
    print()


if __name__ == "__main__":
    list_cameras()
