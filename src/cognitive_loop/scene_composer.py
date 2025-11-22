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
            
            # Use GPU if available (Metal on M4)
            self.device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
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
            
            # Process and generate
            inputs = self.processor(pil_image, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                out = self.model.generate(**inputs, max_length=50, num_beams=3)
            
            caption = self.processor.decode(out[0], skip_special_tokens=True)
            
            return caption
        
        except Exception as e:
            logger.error(f"Error generating scene description: {e}")
            return "Unable to describe scene."

