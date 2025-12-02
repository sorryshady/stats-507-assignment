"""Tests for WebSocket endpoint."""

import pytest
import base64
import cv2
import os
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_test_image_base64():
    """Get test image as base64."""
    test_image_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "test_images", "test_image_0.jpg"
    )

    if not os.path.exists(test_image_path):
        pytest.skip(f"Test image not found: {test_image_path}")

    img = cv2.imread(test_image_path)
    if img is None:
        pytest.skip("Failed to read test image")

    _, buffer = cv2.imencode(".jpg", img)
    return base64.b64encode(buffer).decode("utf-8")


def test_websocket_connection():
    """Test WebSocket connection."""
    with client.websocket_connect("/api/ws/camera") as websocket:
        websocket.send_json({"type": "ping"})
        response = websocket.receive_json()
        assert response["type"] == "pong"


def test_websocket_frame_processing():
    """Test WebSocket frame processing."""
    frame_base64 = get_test_image_base64()

    with client.websocket_connect("/api/ws/camera") as websocket:
        message = {"type": "frame", "data": frame_base64, "timestamp": 1234567890.123}
        websocket.send_json(message)

        response = websocket.receive_json()

        assert response["type"] == "frame_result"
        assert "frame_id" in response
        assert "timestamp" in response
        assert "detections" in response
        assert "hazards" in response
        assert isinstance(response["detections"], list)
        assert isinstance(response["hazards"], list)


def test_websocket_invalid_message():
    """Test WebSocket with invalid message."""
    with client.websocket_connect("/api/ws/camera") as websocket:
        websocket.send_json({"type": "invalid_type"})

        response = websocket.receive_json()
        assert response["type"] == "error"
        assert "message" in response


def test_websocket_missing_frame_data():
    """Test WebSocket with missing frame data."""
    with client.websocket_connect("/api/ws/camera") as websocket:
        message = {"type": "frame", "timestamp": 1234567890.123}
        websocket.send_json(message)

        response = websocket.receive_json()
        assert response["type"] == "error"
