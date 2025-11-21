import torch
from PIL import Image
from typing import Any
from transformers import BlipProcessor, BlipForConditionalGeneration
from models.base import BaseModel


class BlipCaptioner(BaseModel):

    def __init__(self, model_path: str = "Salesforce/blip-image-captioning-base"):
        if torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda"
        else:
            self.device = "cpu"

        print(f"Captioner Device configured: {self.device.upper()}")
        super().__init__(model_path)

    def load_model(self) -> None:
        print(f"Loading BLIP model from: {self.model_path}...")
        self.processor = BlipProcessor.from_pretrained(self.model_path)
        self.model = BlipForConditionalGeneration.from_pretrained(self.model_path)
        self.model.to(self.device)

        print("BLIP model loaded successfully.")

    def predict(self, image_path: str) -> str:
        if not self.model:
            raise RuntimeError("Model not loaded.")

        raw_image = Image.open(image_path).convert("RGB")
        inputs = self.processor(raw_image, return_tensors="pt").to(self.device)

        out = self.model.generate(**inputs, max_new_tokens=50)

        caption = self.processor.decode(out[0], skip_special_tokens=True)

        return caption
