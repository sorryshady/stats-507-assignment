from dataclasses import dataclass
from typing import Tuple, List


@dataclass
class DetectionResult:
    """
    A standard object representing a single detected item.
    """

    label: str
    confidence: float
    box: Tuple[float, float, float, float]  # x1, y1, x2, y2


@dataclass
class SceneAnalysis:
    """
    The full picture: combines structured detection data with
    unstructured semantic description.
    """

    detections: List[DetectionResult]
    caption: str
