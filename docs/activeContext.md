# Active Context

## Current Focus

- Tuning the narration and trajectory analysis to reduce hallucinations and false positives.
- Improved `trajectory.py` thresholds to prevent "rapidly approaching" false alarms for stationary users.
- Updated `narrator.py` prompt to help the LLM resolve entity duplication (understanding that "person" entity = "man" in scene).
- Refactoring frontend to a minimalist "cool SaaS" aesthetic.
- Addressing specific hallucinations (e.g., "mirror" vs "camera") and repetition loops in the scene description pipeline.

## Recent Changes

- **Frontend**:
  - `frontend/components/test/ComparisonView.tsx`: Fixed flickering issue in the "Raw Input" view by tracking the stream ID to prevent unnecessary re-cloning of the media stream.
  - `frontend/hooks/useCamera.ts`: 
    - Fixed camera resource leak by explicitly stopping media tracks.
    - Removed `video.load()` calls which were causing flickering in the raw input feed.
  - `frontend/app/challenges/page.tsx`: 
    - Updated "Monocular Depth & Motion" challenge to explain the mitigation strategy (limiting tracking to significant movements).
    - Added "Stream Freeze on Generation" challenge to document the latency/blocking issue when triggering manual generation.
  - `frontend/components/test/CameraFeed.tsx`: Fixed lint error related to prop mutation by safely handling ref assignments and adding necessary suppressions.
  - Complete redesign of `frontend/app/challenges/page.tsx` with a comprehensive list of technical challenges.
  - Minimalist refactor of `frontend/app/page.tsx`, `frontend/app/test/page.tsx`, and associated components (`CameraFeed`, `ComparisonView`, etc.).
  - Global style updates (`globals.css`) for a monochrome, high-contrast look.
  - Added "Challenges" to the navigation.

- **Backend**:
  - `src/reflex_loop/tracker.py`: Explicitly configured YOLO to use `tracker="bytetrack.yaml"` to ensure robust multi-object tracking (validating the "Solved" status in Challenges).
  - `src/cognitive_loop/scene_composer.py`: Added `repetition_penalty=1.5` and `no_repeat_ngram_size=2` to BLIP generation to prevent infinite repetition loops (e.g., "self self self").
  - `src/cognitive_loop/trajectory.py`: Further increased movement thresholds (velocity 5.0, area 25.0) and "rapidly approaching" threshold (60%) to filter false positives from hand movements (e.g., waving).
  - `src/cognitive_loop/scene_composer.py`: Added regex-based sanitization to replace "mirror" hallucinations with "camera" references.
  - `src/cognitive_loop/narrator.py`: Updated system prompt to explicitly instruct the LLM to treat "mirror" descriptions as hallucinations when appropriate.

## Next Steps

- Validate the changes with the user.
- Monitor for any new edge cases in narration.
- Investigate the "Stream Freeze" issue (likely synchronous blocking in backend inference or WebSocket loop).
- Consider implementing "Long-term Memory" or "Privacy" features mentioned in the challenges if the project scope expands.
