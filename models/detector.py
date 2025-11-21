import torch
from typing import List, Any, Optional
from ultralytics import YOLO
from .base import AIModel
from core.types import DetectionResult


class YOLODetector(AIModel):
    def __init__(self, model_path: str = "yolo11n.pt", conf_threshold: float = 0.5):
        self.conf_threshold = conf_threshold
        # Device selection
        # Check if Mac GPU (MPS) is available, otherwise fallback to CPU
        if torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda"  # For NVIDIA GPUs (Windows/Linux)
        else:
            self.device = "cpu"

        print(f"Device configured: {self.device.upper()}")
        super().__init__(model_path)

    def load_model(self) -> None:
        print(f"Loading YOLO model from: {self.model_path}...")
        self.model = YOLO(self.model_path)
        print(f"YOLO model loaded successfully.")

    def predict(
        self, image: Any, conf_threshold: Optional[float] = None
    ) -> List[DetectionResult]:
        threshold = (
            conf_threshold if conf_threshold is not None else self.conf_threshold
        )

        if not self.model:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        results = self.model(image, conf=threshold, verbose=False, device=self.device)
        result = results[0]

        detections = []
        for box in result.boxes:
            class_id = int(box.cls[0].item())
            label = result.names[class_id]
            confidence = box.conf[0].item()
            coords = box.xyxy[0].tolist()
            x1, y1, x2, y2 = map(int, coords)

            detections.append(
                DetectionResult(
                    label=label, confidence=confidence, box=(x1, y1, x2, y2)
                )
            )

        return detections
