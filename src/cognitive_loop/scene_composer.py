"""BLIP scene captioning for scene understanding."""

import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import numpy as np
import cv2
import logging

from src.config import BLIP_MODEL_NAME

logger = logging.getLogger(__name__)


class SceneComposer:
    """Generates scene descriptions using BLIP."""

    def __init__(self, model_name: str = BLIP_MODEL_NAME):
        """Initialize BLIP model."""
        self.model_name = model_name
        self.processor = None
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load BLIP model and processor."""
        try:
            logger.info(f"Loading BLIP model: {self.model_name}")
            self.processor = BlipProcessor.from_pretrained(self.model_name)
            self.model = BlipForConditionalGeneration.from_pretrained(self.model_name)

            if torch.cuda.is_available():
                self.device = "cuda"
                logger.info("Using CUDA GPU acceleration")
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                self.device = "mps"
                logger.info("Using Apple Metal (MPS) GPU acceleration")
            else:
                self.device = "cpu"
                logger.warning("GPU not available, using CPU (slower)")

            self.model.to(self.device)
            self.model.eval()

            logger.info(f"BLIP model loaded on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load BLIP model: {e}")
            raise

    def generate_scene_description(self, frame: np.ndarray) -> str:
        """Generate scene description from frame."""
        if self.model is None or self.processor is None:
            logger.warning("BLIP model not loaded, returning default description")
            return "A scene with various objects."

        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            inputs = self.processor(pil_image, return_tensors="pt").to(self.device)

            with torch.no_grad():
                out = self.model.generate(
                    **inputs,
                    max_length=50,
                    num_beams=3,
                    do_sample=False,
                    repetition_penalty=1.5,
                    no_repeat_ngram_size=2,
                )

            caption = self.processor.decode(out[0], skip_special_tokens=True)
            caption = self._sanitize_caption(caption)

            return caption

        except Exception as e:
            logger.error(f"Error generating scene description: {e}")
            return "Unable to describe scene."

    def _sanitize_caption(self, caption: str) -> str:
        """Sanitize BLIP caption to filter inappropriate or hallucinated content."""
        import re

        caption_lower = caption.lower()

        inappropriate_patterns = [
            r"\bcock\b",
            r"\bpenis\b",
            r"\bsex\b",
            r"\bnude\b",
            r"\bnaked\b",
            r"\bexplicit\b",
        ]

        if "mirror" in caption_lower:
            logger.info(f"Correcting 'mirror' hallucination in caption: {caption}")
            caption = re.sub(
                r"in front of a mirror",
                "facing the camera",
                caption,
                flags=re.IGNORECASE,
            )
            caption = re.sub(
                r"looking in a mirror",
                "looking at the camera",
                caption,
                flags=re.IGNORECASE,
            )
            caption = re.sub(
                r"looking into a mirror",
                "looking at the camera",
                caption,
                flags=re.IGNORECASE,
            )
            caption = re.sub(
                r"at a mirror", "at the camera", caption, flags=re.IGNORECASE
            )
            if "mirror" in caption.lower():
                caption = caption.replace("mirror", "camera")
            caption_lower = caption.lower()

        if "bathroom" in caption_lower:
            logger.info(f"Correcting 'bathroom' hallucination in caption: {caption}")
            caption = re.sub(
                r"in a bathroom", "in a room", caption, flags=re.IGNORECASE
            )
            caption = re.sub(
                r"in the bathroom", "in the room", caption, flags=re.IGNORECASE
            )
            caption = caption.replace("bathroom", "room")
            caption_lower = caption.lower()

        for pattern in inappropriate_patterns:
            if re.search(pattern, caption_lower):
                logger.warning(
                    f"BLIP generated inappropriate caption, filtering: {caption[:50]}..."
                )
                safe_keywords = []
                if "man" in caption_lower or "person" in caption_lower:
                    safe_keywords.append("a person")
                if "room" in caption_lower or "bathroom" in caption_lower:
                    safe_keywords.append("in a room")
                if "shirt" in caption_lower:
                    safe_keywords.append("wearing a shirt")

                if safe_keywords:
                    return " ".join(safe_keywords) + "."
                else:
                    return "A person in a room."

        suspicious_count = sum(
            1 for pattern in inappropriate_patterns if re.search(pattern, caption_lower)
        )

        if suspicious_count > 0:
            logger.warning(
                f"BLIP caption contains inappropriate content, sanitizing: {caption}"
            )
            if "person" in caption_lower or "man" in caption_lower:
                return "A person in the scene."
            return "A scene with various objects."

        return caption
