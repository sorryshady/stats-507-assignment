"""History buffer for storing tracking data."""

from collections import deque
from typing import Dict, Optional, List
import threading
import logging

from src.utils.data_structures import DetectionPoint, TrackedObject
from src.config import HISTORY_BUFFER_SIZE

logger = logging.getLogger(__name__)


class HistoryBuffer:
    """Thread-safe history buffer for tracked objects."""

    def __init__(self, maxlen: int = HISTORY_BUFFER_SIZE):
        """Initialize history buffer."""
        self.maxlen = maxlen
        self.tracked_objects: Dict[int, TrackedObject] = {}
        self.lock = threading.Lock()
        self.frame_count = 0

    def add_detection(self, object_id: int, detection_point: DetectionPoint):
        """Add a detection point for an object."""
        with self.lock:
            if object_id not in self.tracked_objects:
                self.tracked_objects[object_id] = TrackedObject(
                    object_id, maxlen=self.maxlen
                )

            self.tracked_objects[object_id].add_detection(detection_point)
            self.frame_count = max(self.frame_count, detection_point.frame_id)

    def get_trajectory(
        self, object_id: int, frames_back: Optional[int] = None
    ) -> List[DetectionPoint]:
        """Get trajectory for an object."""
        with self.lock:
            if object_id not in self.tracked_objects:
                return []
            return self.tracked_objects[object_id].get_trajectory(frames_back)

    def get_all_objects(self) -> Dict[int, TrackedObject]:
        """Get all tracked objects."""
        with self.lock:
            return self.tracked_objects.copy()

    def get_object(self, object_id: int) -> Optional[TrackedObject]:
        """Get a specific tracked object."""
        with self.lock:
            return self.tracked_objects.get(object_id)

    def remove_object(self, object_id: int):
        """Remove a tracked object."""
        with self.lock:
            if object_id in self.tracked_objects:
                del self.tracked_objects[object_id]

    def cleanup_stale_objects(
        self, current_frame_id: int, max_frames_missing: int = 30
    ):
        """Remove objects that haven't been seen for a while."""
        with self.lock:
            stale_ids = []
            for obj_id, tracked_obj in self.tracked_objects.items():
                latest = tracked_obj.get_latest()
                if latest is None:
                    stale_ids.append(obj_id)
                elif current_frame_id - latest.frame_id > max_frames_missing:
                    stale_ids.append(obj_id)

            for obj_id in stale_ids:
                del self.tracked_objects[obj_id]

            if stale_ids:
                logger.debug(f"Cleaned up {len(stale_ids)} stale objects")
