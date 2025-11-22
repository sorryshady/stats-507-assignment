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
        """
        Initialize hazard.
        
        Args:
            object_id: Tracking ID of the object
            class_name: Object class name
            priority: Priority level ("high", "medium", "low")
            reason: Reason for hazard detection
        """
        self.object_id = object_id
        self.class_name = class_name
        self.priority = priority
        self.reason = reason


class SafetyMonitor:
    """Monitors for safety hazards and proximity warnings."""
    
    def __init__(self, frame_width: int = 1280, frame_height: int = 720):
        """
        Initialize safety monitor.
        
        Args:
            frame_width: Frame width in pixels
            frame_height: Frame height in pixels
        """
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.physics_engine = PhysicsEngine()
    
    def check_hazards(self, detections: List[DetectionPoint], history_buffer: HistoryBuffer) -> List[Hazard]:
        """
        Check for safety hazards based on detections and history.
        
        Args:
            detections: Current frame detections
            history_buffer: History buffer with tracking data
        
        Returns:
            List of Hazard objects
        """
        hazards = []
        
        for detection in detections:
            # Step 1: Class Check - Is it a hazard class?
            if detection.class_name.lower() not in [c.lower() for c in HAZARD_CLASSES]:
                continue
            
            # Get tracked object from history using track_id
            object_id = detection.track_id if detection.track_id is not None else detection.frame_id
            tracked_obj = history_buffer.get_object(object_id)
            if tracked_obj is None:
                # Create new tracked object
                tracked_obj = TrackedObject(object_id)
                tracked_obj.add_detection(detection)
            
            # Step 2: Zone Check - Is it in center zone?
            in_zone = self.physics_engine.is_in_center_zone(
                detection.box, self.frame_width, self.frame_height
            )
            
            # Step 3: Expansion Check - Is it growing (approaching)?
            area_growth = self.physics_engine.calculate_area_growth(
                tracked_obj, EXPANSION_TIME_WINDOW
            )
            # Only consider positive growth (approaching), ignore negative (leaving)
            is_expanding = area_growth > (EXPANSION_THRESHOLD * 100)  # Convert to percentage
            is_shrinking = area_growth < -(EXPANSION_THRESHOLD * 100)  # Shrinking = leaving
            
            # Step 4: Movement Check - Is it moving significantly?
            # Get velocity to check if object is moving (need at least 2 frames)
            velocity_x, velocity_y = self.physics_engine.calculate_velocity(tracked_obj)
            speed = (velocity_x ** 2 + velocity_y ** 2) ** 0.5
            is_moving = speed > 2.0  # Threshold: 2 pixels per frame
            
            # Determine hazard priority
            # Only trigger hazard if object is:
            # 1. Expanding (approaching) AND in center zone - HIGH priority
            # 2. Expanding (approaching) but not in center zone - MEDIUM priority
            # Do NOT trigger if shrinking (leaving) - that's safe!
            # Do NOT trigger just for moving in center zone - too many false positives
            
            priority = None
            reasons = []
            
            if is_shrinking:
                # Object is shrinking = leaving = NOT a hazard, skip
                continue
            
            if is_expanding:
                # Object is growing = approaching = hazard
                reasons.append(f"approaching ({area_growth:.1f}% growth)")
                if in_zone:
                    # Approaching AND in center zone = high priority
                    priority = "high"
                    reasons.append("in center zone")
                else:
                    # Approaching but not in center zone = medium priority
                    priority = "medium"
            # Removed "moving in center zone" as it causes false positives
            # Stationary objects in center zone are NOT hazards (user sitting still is fine)
            
            if priority:  # Only add hazard if we determined it's actually a threat
                object_id = detection.track_id if detection.track_id is not None else detection.frame_id
                hazard = Hazard(
                    object_id=object_id,
                    class_name=detection.class_name,
                    priority=priority,
                    reason=", ".join(reasons)
                )
                hazards.append(hazard)
        
        return hazards
    
    def should_warn(self, hazards: List[Hazard]) -> bool:
        """
        Determine if warning should be triggered.
        
        Args:
            hazards: List of detected hazards
        
        Returns:
            True if warning should be triggered
        """
        # Trigger warning for high or medium priority hazards
        return any(h.priority in ["high", "medium"] for h in hazards)
    
    def get_warning_message(self, hazards: List[Hazard]) -> str:
        """
        Generate warning message from hazards.
        
        Args:
            hazards: List of detected hazards
        
        Returns:
            Warning message string
        """
        if not hazards:
            return ""
        
        high_priority = [h for h in hazards if h.priority == "high"]
        if high_priority:
            hazard = high_priority[0]
            return f"STOP! {hazard.class_name} approaching"
        
        medium_priority = [h for h in hazards if h.priority == "medium"]
        if medium_priority:
            hazard = medium_priority[0]
            return f"Warning: {hazard.class_name} detected"

