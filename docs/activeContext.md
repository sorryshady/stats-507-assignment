# Active Context

## Current Focus

- **Fixing Narration Hallucinations**: 
  - Addressed "stale object" hallucinations where the system described objects that had left the scene.
  - **Generalized Held Object Filtering**: Implemented a comprehensive filter for handheld objects (phones, remotes, cups, books, etc.).
    - If BLIP detects a person "holding/using/carrying" something, and YOLO detects a corresponding handheld object moving, the movement alert is suppressed.
    - This prevents the "flying remote" or "flying cup" effect when the user or another person moves a held object.
  - **Fixed "Self-Phone" Narration**: Specifically optimized filtering for "cell phone" when "selfie" or "camera" is mentioned.
- Tuning the narration and trajectory analysis.
- Refactoring frontend to a minimalist "cool SaaS" aesthetic.

## Recent Changes

- **Backend**:
  - `src/cognitive_loop/trajectory.py`: 
    - **Expanded Handheld Classes**: Added `cup`, `bottle`, `glass`, `wine glass`, `book`, `toothbrush`, `scissors`, etc. to `HANDHELD_CLASSES` set.
  - `backend/app/core/system.py`: 
    - **Generalized Context-Aware Filtering**:
      - Checks for interaction keywords: "holding", "using", "carrying", "taking a", "with a".
      - If present, iterates through all `object_movements`.
      - If a movement matches a `HANDHELD_CLASS` **AND** that class (or a synonym) appears in the scene description, it is filtered out.
      - Special handling remains for phones/cameras (selfie context).
    - Added `cleanup_stale_objects(frame_id)` to `process_frame` (runs every 30 frames).
    - Added timestamp-based filtering to `generate_narration` (only objects < 2s old are processed).
  - `src/cognitive_loop/narrator.py`: 
    - Updated system prompt with explicit **"Held Objects"** guidelines.
  - `src/reflex_loop/tracker.py`: Explicitly configured YOLO to use `tracker="bytetrack.yaml"`.

## Next Steps

- Validate the generalized "held object" filtering with various objects (remote, cup, book).
- Monitor for any false negatives (e.g., throwing a ball might be filtered if "holding a ball" was the previous context? - Unlikely as BLIP updates every frame).
- Investigate the "Stream Freeze" issue.
