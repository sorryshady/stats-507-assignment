"""Test script for WebSocket endpoint."""

import asyncio
import websockets
import json
import base64
import cv2
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


async def test_websocket():
    """Test WebSocket camera endpoint."""
    uri = "ws://localhost:8000/api/ws/camera"

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket")

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

            print("📤 Sending frame...")

            message = {"type": "frame", "data": img_base64, "timestamp": 1234567890.123}
            await websocket.send(json.dumps(message))

            response = await websocket.recv()
            result = json.loads(response)

            print("📥 Received response:")
            print(f"  Type: {result.get('type')}")
            print(f"  Frame ID: {result.get('frame_id')}")
            print(f"  Detections: {len(result.get('detections', []))}")
            print(f"  Hazards: {len(result.get('hazards', []))}")

            if result.get("detections"):
                print("\n  Detections:")
                for det in result["detections"][:3]:
                    print(
                        f"    - {det['class_name']} (confidence: {det['confidence']:.2f})"
                    )

            if result.get("hazards"):
                print("\n  Hazards:")
                for hazard in result["hazards"]:
                    print(
                        f"    - {hazard['class_name']} ({hazard['priority']}): {hazard['reason']}"
                    )

            print("\n✅ Test completed successfully!")

    except websockets.exceptions.ConnectionRefused:
        print("❌ Connection refused. Is the server running?")
        print(
            "   Start server with: cd backend && uvicorn app.main:app --reload --port 8000"
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("🧪 Testing WebSocket endpoint...")
    print("Make sure the server is running on http://localhost:8000\n")
    asyncio.run(test_websocket())
