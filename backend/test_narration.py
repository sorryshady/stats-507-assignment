"""Test script for narration endpoint."""

import requests
import base64
import cv2
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_narration_endpoint():
    """Test the narration REST endpoint."""
    url = "http://localhost:8000/api/narration"

    test_image_path = os.path.join(
        os.path.dirname(__file__), "..", "test_images", "test_image_0.jpg"
    )

    if not os.path.exists(test_image_path):
        print(f"❌ Test image not found: {test_image_path}")
        return

    img = cv2.imread(test_image_path)
    if img is None:
        print("❌ Failed to read test image")
        return

    _, buffer = cv2.imencode(".jpg", img)
    img_base64 = base64.b64encode(buffer).decode("utf-8")

    print("📤 Sending narration request...")
    print(f"   Image size: {len(img_base64)} bytes (base64)")

    try:
        response = requests.post(url, json={"frame": img_base64}, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print("\n✅ Narration generated successfully!")
            print(f"\n📝 Scene Description:")
            print(f"   {result['scene_description']}")

            if result["object_movements"]:
                print(f"\n🎯 Object Movements:")
                for movement in result["object_movements"]:
                    print(f"   - {movement}")
            else:
                print("\n🎯 Object Movements: None detected")

            print(f"\n💬 Narration:")
            print(f"   {result['narration']}")

            print(f"\n⏱️  Processing Time: {result['processing_time_ms']:.2f}ms")

        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")

    except requests.exceptions.ConnectionRefused:
        print("❌ Connection refused. Is the server running?")
        print(
            "   Start server with: cd backend && uvicorn app.main:app --reload --port 8000"
        )
    except requests.exceptions.Timeout:
        print("❌ Request timeout. Narration is taking too long.")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("🧪 Testing Narration Endpoint...")
    print("Make sure the server is running on http://localhost:8000\n")
    test_narration_endpoint()
