"""System manager for web API - wraps ML components."""

import sys
import os
import logging
from typing import List, Dict, Optional, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from src.reflex_loop.tracker import YOLOTracker
from src.reflex_loop.safety import SafetyMonitor, Hazard
from src.cognitive_loop.history import HistoryBuffer
from src.cognitive_loop.scene_composer import SceneComposer
from src.cognitive_loop.trajectory import TrajectoryAnalyzer
from src.cognitive_loop.narrator import LLMNarrator
from src.config import CAMERA_WIDTH, CAMERA_HEIGHT
from src.utils.data_structures import DetectionPoint
import numpy as np
import cv2
import time

logger = logging.getLogger(__name__)

# Global singleton instance
_system_manager_instance: Optional["SystemManager"] = None


def get_system_manager() -> "SystemManager":
    """Get or create the global SystemManager instance."""
    global _system_manager_instance
    if _system_manager_instance is None:
        _system_manager_instance = SystemManager()
    return _system_manager_instance


class SystemManager:
    """Manages the ML system for web requests."""

    def __init__(self):
        """Initialize system manager (lazy loading)."""
        self.tracker: Optional[YOLOTracker] = None
        self.safety_monitor: Optional[SafetyMonitor] = None
        self.history_buffer: Optional[HistoryBuffer] = None
        self.scene_composer: Optional[SceneComposer] = None
        self.trajectory_analyzer: Optional[TrajectoryAnalyzer] = None
        self.narrator: Optional[LLMNarrator] = None
        self.initialized = False
        self.frame_id = 0
        self._initialization_start_time: Optional[float] = None

    def initialize(self):
        """Load models and initialize components."""
        if self.initialized:
            return

        self._initialization_start_time = time.time()
        logger.info("Initializing SystemManager...")

        try:
            # Initialize tracking and safety
            logger.info("Loading YOLO tracker...")
            self.tracker = YOLOTracker()

            logger.info("Initializing safety monitor...")
            self.safety_monitor = SafetyMonitor(CAMERA_WIDTH, CAMERA_HEIGHT)

            logger.info("Creating history buffer...")
            self.history_buffer = HistoryBuffer()

            # Initialize cognitive components
            logger.info("Loading BLIP scene composer...")
            self.scene_composer = SceneComposer()

            logger.info("Initializing trajectory analyzer...")
            self.trajectory_analyzer = TrajectoryAnalyzer()

            logger.info("Initializing LLM narrator...")
            self.narrator = LLMNarrator()

            self.initialized = True
            init_time = time.time() - self._initialization_start_time
            logger.info(f"SystemManager initialized successfully in {init_time:.2f}s")
        except Exception as e:
            logger.error(f"Failed to initialize SystemManager: {e}", exc_info=True)
            raise

    def process_frame(
        self,
        frame: np.ndarray,
        frame_id: Optional[int] = None,
        timestamp: Optional[float] = None,
    ) -> Dict:
        """
        Process a single frame and return results.

        Args:
            frame: Input frame as numpy array (BGR format)
            frame_id: Optional frame ID (auto-increments if not provided)
            timestamp: Optional timestamp (uses current time if not provided)

        Returns:
            Dictionary with detections, hazards, and annotated frame
        """
        if not self.initialized:
            self.initialize()

        if frame_id is None:
            self.frame_id += 1
            frame_id = self.frame_id
        else:
            self.frame_id = max(self.frame_id, frame_id)

        if timestamp is None:
            timestamp = time.time()

        # Run tracking
        detections, annotated_frame = self.tracker.track(
            frame, frame_id, timestamp, return_annotated=True
        )

        # Update history buffer
        for detection in detections:
            object_id = (
                detection.track_id
                if detection.track_id is not None
                else detection.frame_id
            )
            self.history_buffer.add_detection(object_id, detection)

        # Cleanup stale objects periodically (every 30 frames)
        if frame_id % 30 == 0:
            self.history_buffer.cleanup_stale_objects(frame_id)

        # Check for hazards
        hazards = self.safety_monitor.check_hazards(detections, self.history_buffer)

        # Convert hazards to dict format
        # Convert numpy types to native Python types for JSON serialization
        hazards_list = []
        for hazard in hazards:
            hazards_list.append(
                {
                    "object_id": int(hazard.object_id),
                    "class_name": str(hazard.class_name),
                    "priority": str(hazard.priority),
                    "reason": str(hazard.reason),
                }
            )

        # Convert detections to dict format
        # Convert numpy types to native Python types for JSON serialization
        detections_list = []
        for detection in detections:
            detections_list.append(
                {
                    "track_id": (
                        int(detection.track_id)
                        if detection.track_id is not None
                        else None
                    ),
                    "class_name": str(detection.class_name),
                    "confidence": float(detection.confidence),
                    "box": tuple(int(x) for x in detection.box),
                    "center": tuple(int(x) for x in detection.center),
                    "area": int(detection.area),
                }
            )

        return {
            "frame_id": int(frame_id),
            "timestamp": float(timestamp),
            "detections": detections_list,
            "hazards": hazards_list,
            "annotated_frame": annotated_frame,  # Can be None
        }

    def generate_narration(self, frame: np.ndarray) -> Dict:
        """
        Generate narration for a frame.

        Args:
            frame: Input frame as numpy array (BGR format)

        Returns:
            Dictionary with narration, scene description, and object movements
        """
        if not self.initialized:
            self.initialize()

        # Get scene description
        scene_description = self.scene_composer.generate_scene_description(frame)

        # Analyze trajectories
        tracked_objects = self.history_buffer.get_all_objects()
        
        # Filter out stale objects (older than 2 seconds) to prevent describing past events
        current_time = time.time()
        active_objects = {}
        for obj_id, obj in tracked_objects.items():
            latest = obj.get_latest()
            # Check if object has a latest detection and if it's recent (< 2 seconds old)
            if latest and (current_time - latest.timestamp < 2.0):
                active_objects[obj_id] = obj
                
        object_movements = self.trajectory_analyzer.analyze_all_objects(active_objects)

        # Generate narration
        narration = self.narrator.generate_narration_from_components(
            scene_description, object_movements
        )

        return {
            "narration": narration,
            "scene_description": scene_description,
            "object_movements": object_movements,
        }

    def get_status(self) -> Dict:
        """Get system status information."""
        status = {
            "initialized": self.initialized,
            "models": {},
            "gpu": {},
        }

        if self.initialized:
            # Check GPU availability
            import torch

            if torch.cuda.is_available():
                status["gpu"] = {"available": True, "type": "cuda"}
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                status["gpu"] = {"available": True, "type": "mps"}
            else:
                status["gpu"] = {"available": False, "type": "cpu"}

            # Check model status
            status["models"]["yolo"] = "loaded" if self.tracker else "not_loaded"
            status["models"]["blip"] = "loaded" if self.scene_composer else "not_loaded"
            status["models"]["ollama"] = (
                "connected"
                if self.narrator and self.narrator.check_connection()
                else "disconnected"
            )
        else:
            status["gpu"] = {"available": False, "type": "unknown"}
            status["models"] = {
                "yolo": "not_loaded",
                "blip": "not_loaded",
                "ollama": "unknown",
            }

        return status
