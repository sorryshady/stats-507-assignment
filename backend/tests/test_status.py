"""Tests for status endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "endpoints" in data


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_status_endpoint():
    """Test status endpoint."""
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields
    assert "initialized" in data
    assert "models" in data
    assert "gpu" in data
    
    # Check models structure
    assert "yolo" in data["models"]
    assert "blip" in data["models"]
    assert "ollama" in data["models"]
    
    # Check GPU structure
    assert "available" in data["gpu"]
    assert "type" in data["gpu"]

