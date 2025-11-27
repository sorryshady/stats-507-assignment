# Active Context

## Current Focus

- **Fixing Narration Hallucinations**: Addressed an issue where stale tracking history caused the LLM to narrate objects that were no longer present (e.g., "cell phone leaving").
- Tuning the narration and trajectory analysis to reduce hallucinations and false positives.
- Improved `trajectory.py` thresholds to prevent "rapidly approaching" false alarms for stationary users.
- Updated `narrator.py` prompt to help the LLM resolve entity duplication (understanding that "person" entity = "man" in scene).
- Refactoring frontend to a minimalist "cool SaaS" aesthetic.
- Addressing specific hallucinations (e.g., "mirror" vs "camera") and repetition loops in the scene description pipeline.

## Recent Changes

- **Backend**:

  - `backend/app/core/system.py`:
    - Added `cleanup_stale_objects(frame_id)` to `process_frame` (runs every 30 frames) to ensure `HistoryBuffer` doesn't retain old objects indefinitely during real-time tracking.
    - Added timestamp-based filtering to `generate_narration`. Now, only objects detected within the last 2 seconds are passed to the trajectory analyzer and LLM. This prevents "ghost" objects from previous sessions being described.
  - `src/reflex_loop/tracker.py`: Explicitly configured YOLO to use `tracker="bytetrack.yaml"` to ensure robust multi-object tracking.
  - `src/cognitive_loop/scene_composer.py`: Added `repetition_penalty=1.5` and `no_repeat_ngram_size=2` to BLIP generation.
  - `src/cognitive_loop/trajectory.py`: Increased movement thresholds to filter hand movements.
  - `src/cognitive_loop/narrator.py`: Updated system prompt to handle "mirror" hallucinations.

- **Frontend**:
  - `frontend/components/test/CameraFeed.tsx`: Added "Camera Limitations & Testing Guide" modal.
  - `frontend/components/test/ComparisonView.tsx`: Fixed flickering.
  - `frontend/hooks/useCamera.ts`: Fixed resource leaks.
  - `frontend/app/challenges/page.tsx`: Updated with technical challenges.

## Next Steps

- Validate the "stale history" fix with the user (verify if "cell phone leaving" persists).
- Monitor for any new edge cases in narration.
- Investigate the "Stream Freeze" issue.
