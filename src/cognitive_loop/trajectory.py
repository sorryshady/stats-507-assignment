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
    
    def analyze_movement(self, tracked_object: TrackedObject, filter_shake: bool = False) -> str:
        """
        Analyze movement and return description.
        
        Args:
            tracked_object: TrackedObject with detection history
            filter_shake: If True, be more conservative about movement detection (camera shake filtering)
        
        Returns:
            Movement description string
        """
        history = tracked_object.get_trajectory()
        
        if len(history) < 5:  # Require at least 5 frames for stable analysis
            return "Stationary"
        
        # Calculate velocity
        delta_x, delta_y = self.physics_engine.calculate_velocity(tracked_object)
        
        # Calculate area growth
        area_growth = self.physics_engine.calculate_area_growth(tracked_object)
        
        # If camera shake detected, use stricter thresholds
        if filter_shake:
            # Require more significant movement to classify as non-stationary
            movement_type = self._classify_movement(
                delta_x, delta_y, area_growth, 
                velocity_threshold=5.0,
                area_threshold=15.0  # Increased to avoid false positives
            )
        else:
            # Defaults: velocity > 2.0, area > 10.0 (increased from 5.0)
            movement_type = self._classify_movement(
                delta_x, delta_y, area_growth,
                velocity_threshold=2.0,
                area_threshold=10.0
            )
        
        # Format description
        description = self._format_description(
            tracked_object, delta_x, delta_y, area_growth, movement_type
        )
        
        return description
    
    def _classify_movement(self, delta_x: float, delta_y: float, area_growth: float,
                          velocity_threshold: float = 2.0, area_threshold: float = 10.0) -> str:
        """
        Classify movement type.
        
        Args:
            delta_x: Horizontal velocity component
            delta_y: Vertical velocity component
            area_growth: Area growth percentage
            velocity_threshold: Minimum speed to consider non-stationary (pixels per frame)
            area_threshold: Minimum area change to consider significant (percentage)
        
        Returns:
            Movement type: "Approaching", "Leaving", "Passing By", "Stationary"
        """
        # Check if stationary
        speed = (delta_x ** 2 + delta_y ** 2) ** 0.5
        if speed < velocity_threshold and abs(area_growth) < area_threshold:
            return "Stationary"
        
        # Check if approaching (area growing significantly)
        if area_growth > area_threshold:
            return "Approaching"
        
        # Check if leaving (area shrinking significantly)
        if area_growth < -area_threshold:
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
            if abs(area_growth) > 40:  # Require 40% growth for "rapid"
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
    
    def _detect_camera_shake(self, tracked_objects: dict) -> bool:
        """
        Detect if camera shake is causing false movement detections.
        If multiple objects are moving in similar directions, it's likely camera shake.
        
        Args:
            tracked_objects: Dictionary of object_id -> TrackedObject
        
        Returns:
            True if camera shake is detected
        """
        if len(tracked_objects) < 2:
            return False  # Need at least 2 objects to detect shake
        
        velocities = []
        for obj_id, tracked_obj in tracked_objects.items():
            history = tracked_obj.get_trajectory()
            if len(history) < 2:
                continue
            
            delta_x, delta_y = self.physics_engine.calculate_velocity(tracked_obj)
            speed = (delta_x ** 2 + delta_y ** 2) ** 0.5
            
            # Only consider objects with significant movement
            if speed > 1.0:  # At least 1 pixel/frame
                velocities.append((delta_x, delta_y))
        
        if len(velocities) < 2:
            return False  # Not enough moving objects
        
        # Calculate average direction
        avg_delta_x = sum(v[0] for v in velocities) / len(velocities)
        avg_delta_y = sum(v[1] for v in velocities) / len(velocities)
        
        # Check if most velocities are aligned with average (camera shake)
        aligned_count = 0
        for vx, vy in velocities:
            # Calculate dot product to check alignment
            dot_product = vx * avg_delta_x + vy * avg_delta_y
            mag_v = (vx ** 2 + vy ** 2) ** 0.5
            mag_avg = (avg_delta_x ** 2 + avg_delta_y ** 2) ** 0.5
            
            if mag_v > 0 and mag_avg > 0:
                # Cosine similarity (normalized dot product)
                similarity = dot_product / (mag_v * mag_avg)
                # If similarity > 0.7, velocities are aligned (same direction)
                if similarity > 0.7:
                    aligned_count += 1
        
        # If >70% of moving objects are aligned, it's camera shake
        alignment_ratio = aligned_count / len(velocities)
        return alignment_ratio > 0.7
    
    def analyze_all_objects(self, tracked_objects: dict) -> List[str]:
        """
        Analyze all tracked objects, filtering out camera shake.
        
        Args:
            tracked_objects: Dictionary of object_id -> TrackedObject
        
        Returns:
            List of movement description strings
        """
        # Detect camera shake first
        is_camera_shake = self._detect_camera_shake(tracked_objects)
        
        if is_camera_shake:
            logger.debug("Camera shake detected - filtering out false movements")
        
        descriptions = []
        for obj_id, tracked_obj in tracked_objects.items():
            try:
                description = self.analyze_movement(tracked_obj, filter_shake=is_camera_shake)
                # Only add non-stationary descriptions if not camera shake
                if not is_camera_shake or "Stationary" in description:
                    descriptions.append(description)
            except Exception as e:
                logger.error(f"Error analyzing object {obj_id}: {e}")
        
        return descriptions

