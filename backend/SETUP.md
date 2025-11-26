# Backend Setup Guide

Complete setup instructions for the Describe My Environment backend API.

## Prerequisites

- Python 3.12+
- pip
- Ollama (for LLM narration) - [Installation Guide](https://ollama.ai)

## Installation

### 1. Install Python Dependencies

**From project root:**
```bash
# Install main project dependencies (includes ML libraries)
pip install -r requirements.txt
```

**From backend directory:**
```bash
cd backend
pip install -r requirements.txt
```

### 2. Install Ollama

**macOS:**
```bash
brew install ollama
```

**Or download from:** https://ollama.ai

**Start Ollama:**
```bash
ollama serve
```

**Pull Llama 3.2 model:**
```bash
ollama pull llama3.2:3b
```

**Verify:**
```bash
ollama ps
```

### 3. Verify YOLO Model

Ensure `yolo11n.pt` is in the project root:
```bash
ls yolo11n.pt
```

If missing, YOLO will download it automatically on first run.

## Running the Server

### Development Mode (with auto-reload)

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Production Mode

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### With Custom Port

```bash
uvicorn app.main:app --reload --port 8080
```

## Testing

### Run All Tests

**From backend directory:**
```bash
cd backend
python -m pytest
```

**Or using pytest directly:**
```bash
cd backend
pytest
```

### Run Specific Test File

```bash
cd backend
python -m pytest tests/test_status.py
python -m pytest tests/test_narration.py
python -m pytest tests/test_websocket.py
```

### Run Tests Without Slow Tests

```bash
cd backend
python -m pytest -m "not slow"
```

### Run with Verbose Output

```bash
cd backend
python -m pytest -v
```

### Collect Tests (See What Will Run)

```bash
cd backend
python -m pytest --collect-only
```

### Manual Testing

**Status Endpoint:**
```bash
curl http://localhost:8000/api/status
```

**Health Check:**
```bash
curl http://localhost:8000/api/health
```

**Narration Endpoint:**
```bash
python backend/test_narration.py
```

**WebSocket:**
```bash
python backend/test_websocket.py
```

## API Documentation

Once the server is running, visit:

- **Interactive API Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc

## Environment Variables

Currently, all configuration is in `src/config.py`. Future versions may support environment variables:

```bash
export OLLAMA_API_URL=http://localhost:11434
export OLLAMA_MODEL=llama3.2:3b
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Ollama Not Running

```bash
# Start Ollama
ollama serve

# Verify connection
curl http://localhost:11434/api/tags
```

### Models Not Loading

Check logs for errors. Common issues:
- GPU not available (will fall back to CPU)
- Model files missing (will download automatically)
- Insufficient memory

### Import Errors

Make sure you're running from the correct directory:
```bash
cd backend
python -m pytest  # Use module syntax
```

### WebSocket Connection Refused

Ensure server is running:
```bash
uvicorn app.main:app --reload --port 8000
```

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app
│   ├── api/
│   │   ├── routes/          # API endpoints
│   │   └── models.py        # Pydantic models
│   ├── core/
│   │   └── system.py        # System manager
│   └── middleware/
│       └── error_handler.py  # Error handlers
├── tests/                    # Test files
├── requirements.txt          # Dependencies
└── pytest.ini               # Pytest config
```

## Performance Notes

- **First Request:** May take 5-10 seconds (model loading)
- **Subsequent Requests:** Much faster (models cached)
- **Narration:** Typically 1-3 seconds per request
- **Frame Processing:** ~50-100ms per frame

## Next Steps

- See [README.md](README.md) for API usage
- See [DAY2_SUMMARY.md](DAY2_SUMMARY.md) for implementation details
- See [docs/DAY1_BACKEND_GUIDE.md](../docs/DAY1_BACKEND_GUIDE.md) for learning guide

