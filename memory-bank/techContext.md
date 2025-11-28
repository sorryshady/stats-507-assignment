# Technical Context

## Tech Stack
- **Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS, Lucide Icons.
- **Backend:** FastAPI, Python 3.12+, Uvicorn.
- **ML/Vision:** 
    - **YOLO11n:** Object detection and tracking (`ultralytics`).
    - **BLIP:** Image captioning (`transformers`).
    - **Llama 3.2 3B:** Narration generation (via Ollama).
- **Infrastructure:** Local execution (Mac Studio M4 Pro / MacBook Pro).

## Development Setup
- **Package Managers:** `npm` (Frontend), `pip` (Backend).
- **Environment:**
    - Python virtual environment (`venv`).
    - Node.js environment.
- **Dependencies:**
    - `ollama` must be installed and running (`ollama serve`).
    - `llama3.2:3b` model must be pulled.

## Constraints
- **Webcam:** Single camera limitation affects depth perception accuracy.
- **Browser TTS:** Voice quality and availability depend on the client browser/OS.
- **Latency:** Network latency between Frontend and Backend (even if local) adds overhead compared to the pure CLI version.

