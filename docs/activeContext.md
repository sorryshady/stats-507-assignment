# Active Context

## Current Focus
- Tuning the narration and trajectory analysis to reduce hallucinations and false positives.
- Improved `trajectory.py` thresholds to prevent "rapidly approaching" false alarms for stationary users.
- Updated `narrator.py` prompt to help the LLM resolve entity duplication (understanding that "person" entity = "man" in scene).

## Recent Changes
- **Frontend**: `HazardAlert.tsx` now persists alerts for 5 seconds.
- **Backend**:
  - `src/cognitive_loop/trajectory.py`: Increased stability requirements (min 5 frames), increased movement thresholds (velocity 2.0->5.0/2.0, area 5.0->15.0/10.0), and increased "rapid" threshold (20% -> 40%).
  - `src/cognitive_loop/narrator.py`: Updated LLM prompt to explicitly instruct it to merge Context and Entities if they refer to the same subject.

## Next Steps
- Validate the changes with the user.
- Monitor for any new edge cases in narration.

