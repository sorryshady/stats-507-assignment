"""Tests for physics engine calculations."""

import unittest
import time
from src.reflex_loop.physics import PhysicsEngine
from src.utils.data_structures import TrackedObject, DetectionPoint


class TestPhysicsEngine(unittest.TestCase):
    """Test physics engine calculations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.physics = PhysicsEngine()
    
    def test_calculate_velocity(self):
        """Test velocity calculation."""
        tracked_obj = TrackedObject(object_id=1)
        
        # Add detection points moving right
        base_time = time.time()
        for i in range(5):
            detection = DetectionPoint(
                frame_id=i,
                timestamp=base_time + i * 0.033,  # ~30 FPS
                box=(i * 10, 100, i * 10 + 50, 150),
                area=2500,
                center=(i * 10 + 25, 125),
                class_name="person",
                confidence=0.9
            )
            tracked_obj.add_detection(detection)
        
        delta_x, delta_y = self.physics.calculate_velocity(tracked_obj)
        
        # Should be moving right (positive delta_x)
        self.assertGreater(delta_x, 0)
        self.assertAlmostEqual(delta_y, 0, places=1)
    
    def test_calculate_area_growth(self):
        """Test area growth calculation."""
        tracked_obj = TrackedObject(object_id=1)
        
        # Add detection points with growing area
        base_time = time.time()
        base_area = 1000
        for i in range(5):
            area = base_area + i * 200  # Growing area
            detection = DetectionPoint(
                frame_id=i,
                timestamp=base_time + i * 0.1,
                box=(100, 100, 100 + int(area**0.5), 100 + int(area**0.5)),
                area=area,
                center=(100 + int(area**0.5)//2, 100 + int(area**0.5)//2),
                class_name="car",
                confidence=0.9
            )
            tracked_obj.add_detection(detection)
        
        growth = self.physics.calculate_area_growth(tracked_obj, time_window=1.0)
        
        # Should show positive growth
        self.assertGreater(growth, 0)
    
    def test_is_in_center_zone(self):
        """Test center zone detection."""
        frame_width = 1280
        frame_height = 720
        
        # Box in center
        center_box = (600, 350, 680, 370)
        self.assertTrue(self.physics.is_in_center_zone(center_box, frame_width, frame_height))
        
        # Box on edge
        edge_box = (0, 0, 100, 100)
        self.assertFalse(self.physics.is_in_center_zone(edge_box, frame_width, frame_height))


if __name__ == '__main__':
    unittest.main()

