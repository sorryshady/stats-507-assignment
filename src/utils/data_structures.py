"""Data structures for tracking and detection."""

from dataclasses import dataclass
from typing import Tuple, List, Optional
from collections import deque


@dataclass
class DetectionPoint:
    """Represents a single detection point in time."""
    frame_id: int
    timestamp: float
    box: Tuple[int, int, int, int]  # x1, y1, x2, y2
    area: int  # w * h (used for depth estimation)
    center: Tuple[int, int]  # Center coordinates
    class_name: str  # Object class name
    confidence: float  # Detection confidence
    track_id: Optional[int] = None  # Tracking ID from YOLO


class TrackedObject:
    """Manages detection history for a single tracked object."""
    
    def __init__(self, object_id: int, maxlen: int = 90):
        """Initialize a tracked object."""
        self.object_id = object_id
        self.history: deque = deque(maxlen=maxlen)
        self.first_seen: Optional[float] = None
        self.last_seen: Optional[float] = None
        self.class_name: Optional[str] = None
    
    def add_detection(self, detection_point: DetectionPoint):
        """Add a new detection point to the history."""
        self.history.append(detection_point)
        if self.first_seen is None:
            self.first_seen = detection_point.timestamp
        self.last_seen = detection_point.timestamp
        if self.class_name is None:
            self.class_name = detection_point.class_name
    
    def get_trajectory(self, frames_back: Optional[int] = None) -> List[DetectionPoint]:
        """Get trajectory points."""
        if frames_back is None:
            return list(self.history)
        return list(self.history)[-frames_back:]
    
    def get_latest(self) -> Optional[DetectionPoint]:
        """Get the most recent detection point."""
        if len(self.history) == 0:
            return None
        return self.history[-1]
    
    def get_oldest(self) -> Optional[DetectionPoint]:
        """Get the oldest detection point in current buffer."""
        if len(self.history) == 0:
            return None
        return self.history[0]

