"""Tests for safety monitoring."""

import unittest
import time
from src.reflex_loop.safety import SafetyMonitor, Hazard
from src.cognitive_loop.history import HistoryBuffer
from src.utils.data_structures import DetectionPoint


class TestSafetyMonitor(unittest.TestCase):
    """Test safety monitoring logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.monitor = SafetyMonitor(frame_width=1280, frame_height=720)
        self.history = HistoryBuffer()
    
    def test_hazard_detection_center_zone(self):
        """Test hazard detection in center zone."""
        # Create detection in center zone
        detection = DetectionPoint(
            frame_id=1,
            timestamp=time.time(),
            box=(600, 350, 680, 370),  # Center zone
            area=1600,
            center=(640, 360),
            class_name="car",
            confidence=0.9,
            track_id=1
        )
        
        self.history.add_detection(1, detection)
        hazards = self.monitor.check_hazards([detection], self.history)
        
        # Should detect hazard
        self.assertGreater(len(hazards), 0)
        self.assertIn("center zone", hazards[0].reason.lower())
    
    def test_hazard_detection_expansion(self):
        """Test hazard detection with expansion."""
        # Create detections with growing area
        base_time = time.time()
        base_area = 1000
        for i in range(5):
            area = base_area + i * 300
            size = int(area ** 0.5)
            detection = DetectionPoint(
                frame_id=i,
                timestamp=base_time + i * 0.1,
                box=(100, 100, 100 + size, 100 + size),
                area=area,
                center=(100 + size//2, 100 + size//2),
                class_name="car",
                confidence=0.9,
                track_id=1
            )
            self.history.add_detection(1, detection)
        
        latest = self.history.get_object(1).get_latest()
        hazards = self.monitor.check_hazards([latest], self.history)
        
        # Should detect expansion hazard
        self.assertGreater(len(hazards), 0)
        self.assertIn("expanding", hazards[0].reason.lower())
    
    def test_non_hazard_class(self):
        """Test that non-hazard classes are ignored."""
        detection = DetectionPoint(
            frame_id=1,
            timestamp=time.time(),
            box=(600, 350, 680, 370),
            area=1600,
            center=(640, 360),
            class_name="chair",  # Not a hazard class
            confidence=0.9,
            track_id=1
        )
        
        hazards = self.monitor.check_hazards([detection], self.history)
        
        # Should not detect hazard
        self.assertEqual(len(hazards), 0)
    
    def test_should_warn(self):
        """Test warning trigger logic."""
        hazards = [
            Hazard(1, "car", "high", "expanding, in center zone"),
            Hazard(2, "person", "low", "in center zone")
        ]
        
        self.assertTrue(self.monitor.should_warn(hazards))
        
        low_hazards = [Hazard(2, "person", "low", "in center zone")]
        self.assertFalse(self.monitor.should_warn(low_hazards))


if __name__ == '__main__':
    unittest.main()

