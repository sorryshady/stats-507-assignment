"""Trajectory analysis for movement classification."""

from typing import List, Optional
import logging

from src.utils.data_structures import TrackedObject, DetectionPoint
from src.reflex_loop.physics import PhysicsEngine

logger = logging.getLogger(__name__)


class TrajectoryAnalyzer:
    """Analyzes object movement trajectories."""
    
    def __init__(self):
        """Initialize trajectory analyzer."""
        self.physics_engine = PhysicsEngine()
    
    def analyze_movement(self, tracked_object: TrackedObject) -> str:
        """
        Analyze movement and return description.
        
        Args:
            tracked_object: TrackedObject with detection history
        
        Returns:
            Movement description string
        """
        history = tracked_object.get_trajectory()
        
        if len(history) < 2:
            return "Stationary"
        
        # Calculate velocity
        delta_x, delta_y = self.physics_engine.calculate_velocity(tracked_object)
        
        # Calculate area growth
        area_growth = self.physics_engine.calculate_area_growth(tracked_object)
        
        # Determine movement type
        movement_type = self._classify_movement(delta_x, delta_y, area_growth)
        
        # Format description
        description = self._format_description(
            tracked_object, delta_x, delta_y, area_growth, movement_type
        )
        
        return description
    
    def _classify_movement(self, delta_x: float, delta_y: float, area_growth: float) -> str:
        """
        Classify movement type.
        
        Args:
            delta_x: Horizontal velocity component
            delta_y: Vertical velocity component
            area_growth: Area growth percentage
        
        Returns:
            Movement type: "Approaching", "Leaving", "Passing By", "Stationary"
        """
        # Thresholds
        VELOCITY_THRESHOLD = 2.0  # pixels per frame
        AREA_GROWTH_THRESHOLD = 5.0  # percentage
        
        # Check if stationary
        speed = (delta_x ** 2 + delta_y ** 2) ** 0.5
        if speed < VELOCITY_THRESHOLD and abs(area_growth) < AREA_GROWTH_THRESHOLD:
            return "Stationary"
        
        # Check if approaching (area growing significantly)
        if area_growth > AREA_GROWTH_THRESHOLD:
            return "Approaching"
        
        # Check if leaving (area shrinking significantly)
        if area_growth < -AREA_GROWTH_THRESHOLD:
            return "Leaving"
        
        # Otherwise passing by (moving but not significantly changing size)
        return "Passing By"
    
    def _format_description(self, tracked_object: TrackedObject, delta_x: float, 
                           delta_y: float, area_growth: float, movement_type: str) -> str:
        """
        Format movement description (without IDs for natural language).
        
        Args:
            tracked_object: TrackedObject
            delta_x: Horizontal velocity
            delta_y: Vertical velocity
            area_growth: Area growth percentage
            movement_type: Classified movement type
        
        Returns:
            Formatted description string (natural language, no IDs)
        """
        class_name = tracked_object.class_name or "Object"
        
        if movement_type == "Stationary":
            return f"{class_name}: Stationary"
        
        elif movement_type == "Approaching":
            if abs(area_growth) > 20:
                return f"{class_name}: Approaching rapidly"
            else:
                return f"{class_name}: Approaching"
        
        elif movement_type == "Leaving":
            return f"{class_name}: Leaving"
        
        else:  # Passing By
            # Determine direction
            if abs(delta_x) > abs(delta_y):
                direction = "left to right" if delta_x > 0 else "right to left"
            else:
                direction = "top to bottom" if delta_y > 0 else "bottom to top"
            
            return f"{class_name}: Moving {direction} (passing by)"
    
    def analyze_all_objects(self, tracked_objects: dict) -> List[str]:
        """
        Analyze all tracked objects.
        
        Args:
            tracked_objects: Dictionary of object_id -> TrackedObject
        
        Returns:
            List of movement description strings
        """
        descriptions = []
        for obj_id, tracked_obj in tracked_objects.items():
            try:
                description = self.analyze_movement(tracked_obj)
                descriptions.append(description)
            except Exception as e:
                logger.error(f"Error analyzing object {obj_id}: {e}")
        
        return descriptions

