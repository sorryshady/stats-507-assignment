"""Pydantic models for API requests/responses."""

from pydantic import BaseModel
from typing import List, Optional, Tuple


class DetectionModel(BaseModel):
    """Detection point."""

    track_id: Optional[int]
    class_name: str
    confidence: float
    box: Tuple[int, int, int, int]  # x1, y1, x2, y2
    center: Tuple[int, int]
    area: int


class HazardModel(BaseModel):
    """Hazard info."""

    object_id: int
    class_name: str
    priority: str  # "high", "medium", "low"
    reason: str


class FrameResultModel(BaseModel):
    """Frame processing result."""

    type: str = "frame_result"
    frame_id: int
    timestamp: float
    detections: List[DetectionModel]
    hazards: List[HazardModel]
    annotated_frame: Optional[str] = None  # base64 encoded


class NarrationRequestModel(BaseModel):
    """Narration request."""

    frame: Optional[str] = None  # base64 encoded image


class NarrationResponseModel(BaseModel):
    """Narration response."""

    narration: Optional[str]
    scene_description: str
    object_movements: List[str]
    processing_time_ms: Optional[float] = None
