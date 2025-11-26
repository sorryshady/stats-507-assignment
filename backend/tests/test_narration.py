"""Tests for narration endpoint."""

import pytest
import base64
import cv2
import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_test_image_base64():
    """Get test image as base64 string."""
    test_image_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "test_images", "test_image_0.jpg"
    )
    
    if not os.path.exists(test_image_path):
        pytest.skip(f"Test image not found: {test_image_path}")
    
    img = cv2.imread(test_image_path)
    if img is None:
        pytest.skip("Failed to read test image")
    
    _, buffer = cv2.imencode('.jpg', img)
    return base64.b64encode(buffer).decode('utf-8')


def test_narration_endpoint_missing_frame():
    """Test narration endpoint with missing frame."""
    response = client.post("/api/narration", json={})
    # Returns 400 (Bad Request) because we explicitly check for missing frame
    assert response.status_code == 400
    assert "error" in response.json()


def test_narration_endpoint_invalid_frame():
    """Test narration endpoint with invalid frame data."""
    response = client.post(
        "/api/narration",
        json={"frame": "invalid_base64_data!!!"}
    )
    # Should return 400 (bad request) or 500 (server error)
    assert response.status_code in [400, 500]


@pytest.mark.slow
def test_narration_endpoint_valid_frame():
    """Test narration endpoint with valid frame."""
    frame_base64 = get_test_image_base64()
    
    # Note: timeout removed - TestClient doesn't support it
    # Narration can take time, but TestClient handles it internally
    response = client.post(
        "/api/narration",
        json={"frame": frame_base64}
    )
    
    # Should succeed (200) or fail gracefully (503 if Ollama not available)
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "narration" in data
        assert "scene_description" in data
        assert "object_movements" in data
        assert "processing_time_ms" in data
        assert isinstance(data["processing_time_ms"], (int, float))
        assert data["processing_time_ms"] > 0


def test_narration_endpoint_response_structure():
    """Test narration endpoint response structure."""
    frame_base64 = get_test_image_base64()
    
    # Note: timeout removed - TestClient doesn't support it
    response = client.post(
        "/api/narration",
        json={"frame": frame_base64}
    )
    
    if response.status_code == 200:
        data = response.json()
        
        # Check response structure
        assert isinstance(data["narration"], (str, type(None)))
        assert isinstance(data["scene_description"], str)
        assert isinstance(data["object_movements"], list)
        assert isinstance(data["processing_time_ms"], (int, float))

