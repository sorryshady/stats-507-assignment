"""YOLO11 tracking wrapper."""

import time
from typing import List, Tuple, Optional
import numpy as np
from ultralytics import YOLO
import logging

from src.utils.data_structures import DetectionPoint
from src.config import YOLO_MODEL_PATH, YOLO_CONFIDENCE_THRESHOLD

logger = logging.getLogger(__name__)


class YOLOTracker:
    """Wrapper for YOLO11 tracking."""
    
    def __init__(self, model_path: str = YOLO_MODEL_PATH):
        """
        Initialize YOLO tracker with GPU acceleration.
        
        Args:
            model_path: Path to YOLO model weights (.pt file)
        """
        try:
            # Detect available device (MPS for Mac, CUDA for NVIDIA, CPU fallback)
            import torch
            if torch.cuda.is_available():
                device = "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"
            
            # YOLO automatically uses the best available device, but we can explicitly set it
            self.model = YOLO(model_path)
            # Ensure model uses GPU if available
            if device != "cpu":
                logger.info(f"YOLO model will use {device} acceleration")
            else:
                logger.warning("YOLO model using CPU - GPU not available")
            
            logger.info(f"YOLO model loaded from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise
    
    def track(self, frame: np.ndarray, frame_id: int, timestamp: Optional[float] = None, 
              return_annotated: bool = False) -> tuple[List[DetectionPoint], Optional[np.ndarray]]:
        """
        Track objects in frame.
        
        Args:
            frame: Input frame as numpy array (BGR format)
            frame_id: Current frame ID
            timestamp: Current timestamp (uses time.time() if None)
            return_annotated: If True, return YOLO's annotated frame
        
        Returns:
            Tuple of (detections list, annotated_frame or None)
        """
        if timestamp is None:
            timestamp = time.time()
        
        try:
            # Run tracking with confidence threshold
            # Explicitly use ByteTrack for robust tracking (handling occlusions better)
            results = self.model.track(
                frame, 
                persist=True, 
                verbose=False, 
                conf=YOLO_CONFIDENCE_THRESHOLD,
                tracker="bytetrack.yaml"
            )
            
            detections = []
            annotated_frame = None
            
            if results and len(results) > 0:
                result = results[0]
                
                # Get YOLO's annotated frame if requested
                if return_annotated:
                    try:
                        annotated_frame = result.plot()  # YOLO's built-in visualization
                    except Exception as e:
                        logger.debug(f"Error creating annotated frame: {e}")
                        annotated_frame = None
                
                # Extract boxes, track IDs, classes, and confidences
                if result.boxes is not None:
                    boxes = result.boxes.xyxy.cpu().numpy()  # x1, y1, x2, y2
                    track_ids = result.boxes.id
                    classes = result.boxes.cls.cpu().numpy().astype(int)
                    confidences = result.boxes.conf.cpu().numpy()
                    class_names = result.names
                    
                    if track_ids is not None:
                        track_ids = track_ids.cpu().numpy().astype(int)
                    else:
                        # If tracking IDs not available, use sequential IDs
                        track_ids = np.arange(len(boxes))
                    
                    for i, box in enumerate(boxes):
                        x1, y1, x2, y2 = box.astype(int)
                        track_id = int(track_ids[i]) if track_ids is not None else None
                        class_id = int(classes[i])
                        confidence = float(confidences[i])
                        class_name = class_names[class_id]
                        
                        # Calculate area and center
                        area = int((x2 - x1) * (y2 - y1))
                        center = (int((x1 + x2) / 2), int((y1 + y2) / 2))
                        
                        detection = DetectionPoint(
                            frame_id=frame_id,
                            timestamp=timestamp,
                            box=(x1, y1, x2, y2),
                            area=area,
                            center=center,
                            class_name=class_name,
                            confidence=confidence,
                            track_id=track_id
                        )
                        
                        detections.append(detection)
            
            if return_annotated:
                return detections, annotated_frame
            else:
                return detections, None
        
        except Exception as e:
            logger.error(f"Error during tracking: {e}")
            import traceback
            logger.error(traceback.format_exc())
            if return_annotated:
                return [], None
            else:
                return [], None
    
    def detect(self, frame: np.ndarray) -> List[DetectionPoint]:
        """
        Detect objects without tracking (for single frame analysis).
        
        Args:
            frame: Input frame as numpy array
        
        Returns:
            List of DetectionPoint objects (track_id = -1)
        """
        try:
            # Run detection with confidence threshold
            results = self.model(frame, verbose=False, conf=YOLO_CONFIDENCE_THRESHOLD)
            detections = []
            
            if results and len(results) > 0:
                result = results[0]
                
                if result.boxes is not None:
                    boxes = result.boxes.xyxy.cpu().numpy()
                    classes = result.boxes.cls.cpu().numpy().astype(int)
                    confidences = result.boxes.conf.cpu().numpy()
                    class_names = result.names
                    
                    for i, box in enumerate(boxes):
                        x1, y1, x2, y2 = box.astype(int)
                        class_id = int(classes[i])
                        confidence = float(confidences[i])
                        class_name = class_names[class_id]
                        
                        area = int((x2 - x1) * (y2 - y1))
                        center = (int((x1 + x2) / 2), int((y1 + y2) / 2))
                        
                        detection = DetectionPoint(
                            frame_id=-1,
                            timestamp=time.time(),
                            box=(x1, y1, x2, y2),
                            area=area,
                            center=center,
                            class_name=class_name,
                            confidence=confidence,
                            track_id=None
                        )
                        
                        detections.append(detection)
            
            return detections
        
        except Exception as e:
            logger.error(f"Error during detection: {e}")
            return []

