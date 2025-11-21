from dataclasses import dataclass
from typing import Tuple


@dataclass
class DetectionResult:
    """
    A standard object representing a single detected item.
    """

    label: str
    confidence: float
    box: Tuple[float, float, float, float]  # x1, y1, x2, y2
