"""Safety monitoring for proximity warnings."""

from typing import List, Dict, Optional
import logging

from src.utils.data_structures import DetectionPoint, TrackedObject
from src.cognitive_loop.history import HistoryBuffer
from src.reflex_loop.physics import PhysicsEngine
from src.config import HAZARD_CLASSES, EXPANSION_THRESHOLD, EXPANSION_TIME_WINDOW

logger = logging.getLogger(__name__)


class Hazard:
    """Represents a detected hazard."""

    def __init__(self, object_id: int, class_name: str, priority: str, reason: str):
        """Initialize hazard."""
        self.object_id = object_id
        self.class_name = class_name
        self.priority = priority
        self.reason = reason


class SafetyMonitor:
    """Monitors for safety hazards and proximity warnings."""

    def __init__(self, frame_width: int = 1280, frame_height: int = 720):
        """Initialize safety monitor."""
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.physics_engine = PhysicsEngine()

    def check_hazards(
        self, detections: List[DetectionPoint], history_buffer: HistoryBuffer
    ) -> List[Hazard]:
        """Check for safety hazards based on detections and history."""
        hazards = []

        for detection in detections:
            if detection.class_name.lower() not in [c.lower() for c in HAZARD_CLASSES]:
                continue

            object_id = (
                detection.track_id
                if detection.track_id is not None
                else detection.frame_id
            )
            tracked_obj = history_buffer.get_object(object_id)
            if tracked_obj is None:
                tracked_obj = TrackedObject(object_id)
                tracked_obj.add_detection(detection)

            in_zone = self.physics_engine.is_in_center_zone(
                detection.box, self.frame_width, self.frame_height
            )

            area_growth = self.physics_engine.calculate_area_growth(
                tracked_obj, EXPANSION_TIME_WINDOW
            )
            is_expanding = area_growth > (EXPANSION_THRESHOLD * 100)
            is_shrinking = area_growth < -(EXPANSION_THRESHOLD * 100)

            is_approaching_center = self.physics_engine.is_approaching_center(
                tracked_obj, self.frame_width, self.frame_height
            )

            velocity_x, velocity_y = self.physics_engine.calculate_velocity(tracked_obj)
            speed = (velocity_x**2 + velocity_y**2) ** 0.5
            is_moving = speed > 5.0

            priority = None
            reasons = []

            if is_shrinking:
                continue

            if is_expanding and is_approaching_center:
                reasons.append(
                    f"approaching ({area_growth:.1f}% growth, moving toward center)"
                )
                if in_zone:
                    priority = "high"
                    reasons.append("in center zone")
                else:
                    priority = "medium"

            if priority:
                object_id = (
                    detection.track_id
                    if detection.track_id is not None
                    else detection.frame_id
                )
                hazard = Hazard(
                    object_id=object_id,
                    class_name=detection.class_name,
                    priority=priority,
                    reason=", ".join(reasons),
                )
                hazards.append(hazard)

        return hazards

    def should_warn(self, hazards: List[Hazard]) -> bool:
        """Determine if warning should be triggered."""
        return any(h.priority in ["high", "medium"] for h in hazards)

    def get_warning_message(self, hazards: List[Hazard]) -> str:
        """Generate warning message from hazards."""
        if not hazards:
            return ""

        high_priority = [h for h in hazards if h.priority == "high"]
        if high_priority:
            hazard = high_priority[0]
            class_name_formatted = hazard.class_name.capitalize()
            return f"STOP! {class_name_formatted} in front of you"

        medium_priority = [h for h in hazards if h.priority == "medium"]
        if medium_priority:
            hazard = medium_priority[0]
            class_name_formatted = hazard.class_name.capitalize()
            return f"Warning: {class_name_formatted} detected"
