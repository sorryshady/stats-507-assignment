from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class DetectionResult:
    """
    Standardized representation of a detected object.
    """

    label: str
    confidence: float
    box: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    track_id: Optional[int] = None  # Unique ID for tracking (e.g., Person #1)


@dataclass
class SceneAnalysis:
    """
    The full picture: combines structured detection data with
    unstructured semantic description.
    """

    detections: List[DetectionResult]
    caption: str
