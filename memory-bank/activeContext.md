# Active Context

## Current Focus
Implementing the **Text-to-Speech (TTS)** functionality in the frontend and managing user expectations regarding the web implementation limitations.

## Recent Changes
- **Frontend TTS:** Implemented browser-native `window.speechSynthesis` in `NarrationPanel.tsx`. Added a "Play" button for manual playback and "Stop" button.
- **User Instructions:** Updated `CameraFeed.tsx` disclaimer dialog to include sections on:
    - **Webcam Constraints:** FOV, depth estimation.
    - **Audio:** Browser-based TTS limitations.
    - **Performance:** Real-time AI processing requirements.
- **Test Page:** Updated instructions in `frontend/app/test/page.tsx` to mention TTS testing.

## Next Steps
- Validate TTS across different browsers (Chrome, Safari, Firefox) if possible.
- Verify that the limitation dialog appears correctly when starting the camera.
- Continue refining the web application UI/UX based on the `WEB_APP_PLAN.md`.

## Active Decisions
- **TTS Strategy:** Chose **Browser Native (Web Speech API)** for zero latency and zero cost, accepting the trade-off of variable voice quality.
- **User Control:** TTS does *not* auto-play to respect user preferences; explicit user action (click) or system trigger (if implemented later) is preferred.

