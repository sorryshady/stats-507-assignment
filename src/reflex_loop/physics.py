"""Physics engine for calculating velocity and expansion."""

from typing import Tuple, Optional, List
import numpy as np
import logging

from src.utils.data_structures import TrackedObject, DetectionPoint
from src.config import CENTER_ZONE_THRESHOLD, EXPANSION_TIME_WINDOW

logger = logging.getLogger(__name__)


class PhysicsEngine:
    """Calculates physical properties of tracked objects."""
    
    @staticmethod
    def calculate_velocity(tracked_object: TrackedObject) -> Tuple[float, float]:
        """
        Calculate velocity vector (delta_x, delta_y) in pixels per frame.
        
        Args:
            tracked_object: TrackedObject with detection history
        
        Returns:
            Tuple of (delta_x, delta_y) velocity components
        """
        history = tracked_object.get_trajectory()
        if len(history) < 2:
            return (0.0, 0.0)
        
        # Get first and last detection points
        first = history[0]
        last = history[-1]
        
        # Calculate displacement
        delta_x = last.center[0] - first.center[0]
        delta_y = last.center[1] - first.center[1]
        
        # Normalize by number of frames
        num_frames = len(history) - 1
        if num_frames > 0:
            delta_x /= num_frames
            delta_y /= num_frames
        
        return (delta_x, delta_y)
    
    @staticmethod
    def calculate_area_growth(tracked_object: TrackedObject, time_window: float = EXPANSION_TIME_WINDOW) -> float:
        """
        Calculate area growth percentage over time window.
        
        Args:
            tracked_object: TrackedObject with detection history
            time_window: Time window in seconds to check
        
        Returns:
            Area growth percentage (positive = growing, negative = shrinking)
        """
        history = tracked_object.get_trajectory()
        if len(history) < 2:
            return 0.0
        
        latest = history[-1]
        latest_time = latest.timestamp
        
        # Find detection points within time window
        window_start_time = latest_time - time_window
        relevant_points = [dp for dp in history if dp.timestamp >= window_start_time]
        
        if len(relevant_points) < 2:
            return 0.0
        
        # Get oldest and newest areas in window
        oldest_area = relevant_points[0].area
        newest_area = relevant_points[-1].area
        
        if oldest_area == 0:
            return 0.0
        
        # Calculate percentage growth
        growth_percentage = ((newest_area - oldest_area) / oldest_area) * 100.0
        
        return growth_percentage
    
    @staticmethod
    def is_in_center_zone(box: Tuple[int, int, int, int], frame_width: int, frame_height: int) -> bool:
        """
        Check if bounding box is in the center zone of the frame.
        
        Args:
            box: Bounding box (x1, y1, x2, y2)
            frame_width: Frame width in pixels
            frame_height: Frame height in pixels
        
        Returns:
            True if box center is in center zone
        """
        x1, y1, x2, y2 = box
        
        # Calculate box center
        box_center_x = (x1 + x2) / 2
        box_center_y = (y1 + y2) / 2
        
        # Calculate center zone boundaries (40% center)
        center_zone_width = frame_width * CENTER_ZONE_THRESHOLD
        center_zone_height = frame_height * CENTER_ZONE_THRESHOLD
        
        center_x = frame_width / 2
        center_y = frame_height / 2
        
        zone_left = center_x - center_zone_width / 2
        zone_right = center_x + center_zone_width / 2
        zone_top = center_y - center_zone_height / 2
        zone_bottom = center_y + center_zone_height / 2
        
        # Check if box center is in zone
        in_zone = (zone_left <= box_center_x <= zone_right and 
                  zone_top <= box_center_y <= zone_bottom)
        
        return in_zone
    
    @staticmethod
    def is_approaching_center(tracked_object: TrackedObject, frame_width: int, frame_height: int) -> bool:
        """
        Check if object center is moving toward the frame center (approaching camera).
        This helps distinguish between "person approaching" vs "person moving hands while stationary".
        
        Args:
            tracked_object: TrackedObject with detection history
            frame_width: Frame width in pixels
            frame_height: Frame height in pixels
        
        Returns:
            True if object center is moving toward frame center
        """
        history = tracked_object.get_trajectory()
        if len(history) < 2:
            return False
        
        # Get first and last detection points
        first = history[0]
        last = history[-1]
        
        # Calculate frame center
        frame_center_x = frame_width / 2
        frame_center_y = frame_height / 2
        
        # Calculate distance from object center to frame center
        first_dist_x = abs(first.center[0] - frame_center_x)
        first_dist_y = abs(first.center[1] - frame_center_y)
        first_distance = (first_dist_x ** 2 + first_dist_y ** 2) ** 0.5
        
        last_dist_x = abs(last.center[0] - frame_center_x)
        last_dist_y = abs(last.center[1] - frame_center_y)
        last_distance = (last_dist_x ** 2 + last_dist_y ** 2) ** 0.5
        
        # If distance is decreasing, object is moving toward center (approaching)
        # Require at least 10 pixels of movement toward center to avoid noise
        distance_change = first_distance - last_distance
        return distance_change > 10.0  # Moving at least 10 pixels closer to center
    
    @staticmethod
    def calculate_distance_estimate(box: Tuple[int, int, int, int], reference_area: Optional[int] = None) -> float:
        """
        Estimate distance to object based on bounding box area.
        Simple heuristic: larger area = closer object.
        
        Args:
            box: Bounding box (x1, y1, x2, y2)
            reference_area: Reference area for normalization (optional)
        
        Returns:
            Estimated distance (normalized, lower = closer)
        """
        x1, y1, x2, y2 = box
        area = (x2 - x1) * (y2 - y1)
        
        if reference_area is None:
            # Use area as inverse distance proxy
            return 1.0 / (area + 1)  # +1 to avoid division by zero
        
        # Normalize by reference
        return reference_area / (area + 1)

