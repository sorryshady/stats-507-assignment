"""LLM narrator for generating natural language descriptions."""

import requests
import json
import logging
from typing import List, Optional

from src.config import OLLAMA_API_URL, OLLAMA_MODEL

logger = logging.getLogger(__name__)


class LLMNarrator:
    """Generates narration using Llama 3.2 via Ollama."""

    def __init__(self, api_url: str = OLLAMA_API_URL, model: str = OLLAMA_MODEL):
        """Initialize LLM narrator."""
        self.api_url = api_url
        self.model = model
        self.api_endpoint = f"{api_url}/api/generate"

    def compose_prompt(
        self, scene_description: str, object_movements: List[str]
    ) -> str:
        """Compose prompt for LLM."""
        # Format object movements
        if object_movements:
            entities_text = "\n".join(
                [f"- {movement}" for movement in object_movements]
            )
        else:
            entities_text = "- No objects detected."

        prompt = f"""SYSTEM: You are a helpful assistant for a blind user. Be concise and direct. Only describe what is certainly present. Do not ask questions.
If the context mentions a "mirror" or "reflection" and it seems to be describing the user themselves (e.g., "standing in front of a mirror"), assume it is a hallucination caused by the camera feed and describe it as the person being present or facing the camera.

USER:
Context: "{scene_description}"
Entities (detected by object detection system):
{entities_text}

TASK: Synthesize the context and entities into one natural sentence.
IMPORTANT RULES:
1. PRIORITIZE ENTITY COUNT: The "Entities" list contains accurate object detections from a computer vision system. If the Context says "two cars" but the Entities list shows 4 car entries, use the count from Entities (4 cars). The Entities list is more reliable for counting objects.
2. MERGE SUBJECTS: When the same object type appears multiple times in Entities, count them separately (e.g., "car: Stationary" and "car: Approaching" = 2 cars). Only merge if the Context explicitly describes the same single object.
3. If the context mentions a person holding an object, and that object also appears in the entities list, DO NOT describe the object as moving independently. It moves with the person.
4. Small handheld objects moving in the same direction as a person are almost certainly held items, not independent threats.
5. Prioritize safety information about truly independent moving objects (vehicles, other people, animals).
6. Ignore any coordinates or bounding box numbers (e.g., "box (100, 200, ...)") mentioned in the entities list. They are technical data. If an entity is described as "at box", simply treat it as "present" or "in front of you". Do NOT say "at a box", "near a box", or "at the location"."""

        return prompt

    def generate_narration(self, prompt: str, timeout: float = 10.0) -> Optional[str]:
        """Generate narration from prompt using Ollama."""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 100,
                },
            }

            response = requests.post(self.api_endpoint, json=payload, timeout=timeout)

            if response.status_code == 200:
                result = response.json()
                narration = result.get("response", "").strip()

                narration = self._clean_narration(narration)

                return narration
            else:
                logger.error(
                    f"Ollama API error: {response.status_code} - {response.text}"
                )
                return None

        except requests.exceptions.Timeout:
            logger.error(f"Ollama API timeout after {timeout}s")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Failed to connect to Ollama at {self.api_url}")
            return None
        except Exception as e:
            logger.error(f"Error generating narration: {e}")
            return None

    def check_connection(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = requests.get(f"{self.api_url}/api/tags", timeout=2.0)
            return response.status_code == 200
        except Exception:
            return False

    def _clean_narration(self, narration: str) -> str:
        """Clean narration to remove follow-up questions and extra verbosity."""
        # Remove common follow-up patterns
        patterns_to_remove = [
            r"Is there anything else I can assist you with\?.*",
            r"Let me know if you need.*",
            r"Feel free to ask.*",
            r"Would you like.*",
            r"I can help.*",
            r"Please let me know.*",
        ]

        import re

        cleaned = narration
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.DOTALL)

        cleaned = re.sub(r"\.{2,}", ".", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned)
        cleaned = cleaned.strip()

        if cleaned.endswith("?"):
            if any(
                phrase in cleaned.lower()
                for phrase in ["anything else", "need help", "assist", "let me know"]
            ):
                cleaned = cleaned.rstrip("?").rstrip() + "."

        return cleaned

    def generate_narration_from_components(
        self, scene_description: str, object_movements: List[str]
    ) -> Optional[str]:
        """Generate narration from scene and movement components."""
        prompt = self.compose_prompt(scene_description, object_movements)
        return self.generate_narration(prompt)
