# Utility Scripts

This directory contains utility scripts for development and testing.

## Scripts

### `list_cameras.py`
Lists available camera devices and their properties. Useful for finding the correct camera ID.

**Usage:**
```bash
python scripts/list_cameras.py
```

### `verify_ollama.py`
Verifies Ollama installation and connection. Checks if the Llama 3.2 model is available.

**Usage:**
```bash
python scripts/verify_ollama.py
```

### `verify_tts.py`
Tests the text-to-speech system. Verifies audio output functionality.

**Usage:**
```bash
python scripts/verify_tts.py
```

## Running Scripts

All scripts should be run from the project root:

```bash
# From project root
python scripts/script_name.py
```

Or activate virtual environment first:

```bash
source venv/bin/activate
python scripts/script_name.py
```

