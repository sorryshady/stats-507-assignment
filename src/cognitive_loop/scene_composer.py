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
        """
        Initialize BLIP model.

        Args:
            model_name: HuggingFace model name for BLIP
        """
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

            # Use GPU if available (Metal/MPS on Mac, CUDA on NVIDIA)
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
        """
        Generate scene description from frame.

        Args:
            frame: Input frame as numpy array (BGR format from OpenCV)

        Returns:
            Scene description string
        """
        if self.model is None or self.processor is None:
            logger.warning("BLIP model not loaded, returning default description")
            return "A scene with various objects."

        try:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert to PIL Image
            pil_image = Image.fromarray(frame_rgb)

            # Process and generate (unconditional image captioning)
            inputs = self.processor(pil_image, return_tensors="pt").to(self.device)

            with torch.no_grad():
                # Use lower temperature-like behavior with do_sample=False for more deterministic output
                out = self.model.generate(
                    **inputs, max_length=50, num_beams=3, do_sample=False
                )

            caption = self.processor.decode(out[0], skip_special_tokens=True)

            # Sanitize caption to filter inappropriate content
            caption = self._sanitize_caption(caption)

            return caption

        except Exception as e:
            logger.error(f"Error generating scene description: {e}")
            return "Unable to describe scene."

    def _sanitize_caption(self, caption: str) -> str:
        """
        Sanitize BLIP caption to filter inappropriate or hallucinated content.

        Args:
            caption: Raw caption from BLIP

        Returns:
            Sanitized caption string
        """
        import re

        caption_lower = caption.lower()

        # List of inappropriate keywords/phrases to filter
        inappropriate_patterns = [
            r"\bcock\b",  # Explicit content
            r"\bpenis\b",
            r"\bsex\b",
            r"\bnude\b",
            r"\bnaked\b",
            r"\bexplicit\b",
            # Add more patterns as needed
        ]

        # Fix common hallucinations for webcam feeds
        # BLIP often mistakes a person looking at a webcam for a person looking in a mirror
        if "mirror" in caption_lower:
            logger.info(f"Correcting 'mirror' hallucination in caption: {caption}")
            caption = re.sub(r"in front of a mirror", "facing the camera", caption, flags=re.IGNORECASE)
            caption = re.sub(r"looking in a mirror", "looking at the camera", caption, flags=re.IGNORECASE)
            caption = re.sub(r"looking into a mirror", "looking at the camera", caption, flags=re.IGNORECASE)
            caption = re.sub(r"at a mirror", "at the camera", caption, flags=re.IGNORECASE)
            # General fallback if phrase structure is different
            if "mirror" in caption.lower():
                 caption = caption.replace("mirror", "camera")
            # Update caption_lower for subsequent checks
            caption_lower = caption.lower()

        # Check if caption contains inappropriate content
        for pattern in inappropriate_patterns:
            if re.search(pattern, caption_lower):
                logger.warning(
                    f"BLIP generated inappropriate caption, filtering: {caption[:50]}..."
                )
                # Return a generic, safe description instead
                # Try to extract safe parts if possible
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

        # Additional check: if caption seems nonsensical or contains multiple inappropriate words
        # Count suspicious words
        suspicious_count = sum(
            1 for pattern in inappropriate_patterns if re.search(pattern, caption_lower)
        )

        if suspicious_count > 0:
            logger.warning(
                f"BLIP caption contains inappropriate content, sanitizing: {caption}"
            )
            # Extract basic safe description
            if "person" in caption_lower or "man" in caption_lower:
                return "A person in the scene."
            return "A scene with various objects."

        return caption
