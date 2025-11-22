"""Tests for trajectory analysis."""

import unittest
import time
from src.cognitive_loop.trajectory import TrajectoryAnalyzer
from src.utils.data_structures import TrackedObject, DetectionPoint


class TestTrajectoryAnalyzer(unittest.TestCase):
    """Test trajectory analysis."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = TrajectoryAnalyzer()
    
    def test_stationary_object(self):
        """Test stationary object detection."""
        tracked_obj = TrackedObject(object_id=1)
        
        base_time = time.time()
        for i in range(5):
            detection = DetectionPoint(
                frame_id=i,
                timestamp=base_time + i * 0.033,
                box=(100, 100, 150, 150),
                area=2500,
                center=(125, 125),
                class_name="chair",
                confidence=0.9
            )
            tracked_obj.add_detection(detection)
        
        description = self.analyzer.analyze_movement(tracked_obj)
        self.assertIn("Stationary", description)
    
    def test_approaching_object(self):
        """Test approaching object detection."""
        tracked_obj = TrackedObject(object_id=1)
        
        base_time = time.time()
        base_area = 1000
        for i in range(5):
            area = base_area + i * 300  # Growing area
            size = int(area ** 0.5)
            detection = DetectionPoint(
                frame_id=i,
                timestamp=base_time + i * 0.033,
                box=(100, 100, 100 + size, 100 + size),
                area=area,
                center=(100 + size//2, 100 + size//2),
                class_name="person",
                confidence=0.9
            )
            tracked_obj.add_detection(detection)
        
        description = self.analyzer.analyze_movement(tracked_obj)
        self.assertIn("Approaching", description)
    
    def test_passing_object(self):
        """Test passing object detection."""
        tracked_obj = TrackedObject(object_id=1)
        
        base_time = time.time()
        for i in range(5):
            detection = DetectionPoint(
                frame_id=i,
                timestamp=base_time + i * 0.033,
                box=(i * 20, 100, i * 20 + 50, 150),
                area=2500,  # Constant area
                center=(i * 20 + 25, 125),
                class_name="person",
                confidence=0.9
            )
            tracked_obj.add_detection(detection)
        
        description = self.analyzer.analyze_movement(tracked_obj)
        self.assertIn("Passing", description)


if __name__ == '__main__':
    unittest.main()

