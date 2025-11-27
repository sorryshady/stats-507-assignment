# Active Context

## Current Focus

- **Fixing Narration Hallucinations**: 
  - Addressed "stale object" hallucinations where the system described objects that had left the scene.
  - **Generalized Held Object Filtering**: Implemented a comprehensive filter for handheld objects.
  - **Fixed "Self-Phone" Narration**: Optimized filtering for "cell phone" in selfie/camera contexts.
- **Frontend Stability**:
  - **Fixed Camera Resource Leak**: Resolved an issue where the camera light remained on after stopping the feed in "Split View" and switching tabs. Implemented robust stream cloning and cleanup using a dedicated `clonedStreamRef` to manage the lifecycle of cloned media tracks independent of UI component mounting.

## Recent Changes

- **Backend**:
  - `src/cognitive_loop/trajectory.py`: Expanded Handheld Classes.
  - `backend/app/core/system.py`: Implemented context-aware held object filtering.
  
- **Frontend**:
  - `frontend/hooks/useCamera.ts`: Added explicit `track.enabled = false` to stopCamera to ensure hardware release.
  - `frontend/components/test/ComparisonView.tsx`: Refactored stream cloning logic to use `clonedStreamRef`. This ensures that cloned media tracks are properly stopped/released even if the video element they were attached to has been unmounted (e.g., when switching tabs).

## Next Steps

- Validate the camera cleanup fix in all tab switching scenarios.
- Validate the generalized "held object" filtering with various objects (remote, cup, book).
- Monitor for any false negatives in narration.
