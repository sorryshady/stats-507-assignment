"""Verify Ollama setup and Llama 3.2 3B model availability."""

import requests
import json
import sys
from src.config import OLLAMA_API_URL, OLLAMA_MODEL


def check_ollama_connection():
    """Check if Ollama is running."""
    try:
        response = requests.get(f"{OLLAMA_API_URL}/api/tags", timeout=2.0)
        if response.status_code == 200:
            return True, "Ollama is running"
        else:
            return False, f"Ollama returned status {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, f"Cannot connect to Ollama at {OLLAMA_API_URL}. Is Ollama running?"
    except Exception as e:
        return False, f"Error checking Ollama: {e}"


def check_model_availability():
    """Check if Llama 3.2 3B model is available."""
    try:
        response = requests.get(f"{OLLAMA_API_URL}/api/tags", timeout=5.0)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            
            # Check for exact match or partial match
            target_model = OLLAMA_MODEL
            if target_model in model_names:
                return True, f"Model {target_model} is available"
            
            # Check for partial matches
            partial_matches = [m for m in model_names if "llama3.2" in m.lower() or "llama3" in m.lower()]
            if partial_matches:
                return False, f"Model {target_model} not found. Available Llama models: {partial_matches}"
            
            return False, f"Model {target_model} not found. Available models: {model_names}"
    except Exception as e:
        return False, f"Error checking models: {e}"


def test_model_inference():
    """Test model inference."""
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": "Say 'Hello' if you can hear me.",
            "stream": False
        }
        
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json=payload,
            timeout=10.0
        )
        
        if response.status_code == 200:
            result = response.json()
            output = result.get("response", "").strip()
            return True, f"Model inference successful. Response: {output[:50]}..."
        else:
            return False, f"Inference failed with status {response.status_code}: {response.text}"
    except Exception as e:
        return False, f"Error testing inference: {e}"


def main():
    """Run verification checks."""
    print("=" * 60)
    print("Ollama Setup Verification")
    print("=" * 60)
    print(f"Ollama URL: {OLLAMA_API_URL}")
    print(f"Target Model: {OLLAMA_MODEL}")
    print()
    
    # Check connection
    print("1. Checking Ollama connection...")
    success, message = check_ollama_connection()
    print(f"   {'✓' if success else '✗'} {message}")
    if not success:
        print("\n   Please start Ollama: ollama serve")
        sys.exit(1)
    
    # Check model availability
    print("\n2. Checking model availability...")
    success, message = check_model_availability()
    print(f"   {'✓' if success else '✗'} {message}")
    if not success:
        print(f"\n   Please pull the model: ollama pull {OLLAMA_MODEL}")
        sys.exit(1)
    
    # Test inference
    print("\n3. Testing model inference...")
    success, message = test_model_inference()
    print(f"   {'✓' if success else '✗'} {message}")
    if not success:
        print("\n   Model inference failed. Check Ollama logs.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("All checks passed! Ollama is ready.")
    print("=" * 60)


if __name__ == "__main__":
    main()

