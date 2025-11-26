# Active Context

## Current Focus

- Tuning the narration and trajectory analysis to reduce hallucinations and false positives.
- Improved `trajectory.py` thresholds to prevent "rapidly approaching" false alarms for stationary users.
- Updated `narrator.py` prompt to help the LLM resolve entity duplication (understanding that "person" entity = "man" in scene).
- Refactoring frontend to a minimalist "cool SaaS" aesthetic.
- Addressing specific hallucinations (e.g., "mirror" vs "camera") in the scene description pipeline.

## Recent Changes

- **Frontend**:
  - Complete redesign of `frontend/app/challenges/page.tsx` with a comprehensive list of technical challenges.
  - Minimalist refactor of `frontend/app/page.tsx`, `frontend/app/test/page.tsx`, and associated components (`CameraFeed`, `ComparisonView`, etc.).
  - Global style updates (`globals.css`) for a monochrome, high-contrast look.
  - Added "Challenges" to the navigation.
- **Backend**:
  - `src/cognitive_loop/scene_composer.py`: Added regex-based sanitization to replace "mirror" hallucinations with "camera" references.
  - `src/cognitive_loop/narrator.py`: Updated system prompt to explicitly instruct the LLM to treat "mirror" descriptions as hallucinations when appropriate.
  - `src/cognitive_loop/trajectory.py`: Increased stability requirements (min 5 frames), increased movement thresholds (velocity 2.0->5.0/2.0, area 5.0->15.0/10.0), and increased "rapid" threshold (20% -> 40%).

## Next Steps

- Validate the changes with the user.
- Monitor for any new edge cases in narration.
- Consider implementing "Long-term Memory" or "Privacy" features mentioned in the challenges if the project scope expands.
