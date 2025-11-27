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
        """
        Initialize LLM narrator.
        
        Args:
            api_url: Ollama API URL
            model: Model name (e.g., "llama3.2:3b")
        """
        self.api_url = api_url
        self.model = model
        self.api_endpoint = f"{api_url}/api/generate"
    
    def compose_prompt(self, scene_description: str, object_movements: List[str]) -> str:
        """
        Compose prompt for LLM.
        
        Args:
            scene_description: Scene description from BLIP
            object_movements: List of movement description strings
        
        Returns:
            Formatted prompt string
        """
        # Format object movements
        if object_movements:
            entities_text = "\n".join([f"- {movement}" for movement in object_movements])
        else:
            entities_text = "- No objects detected."
        
        prompt = f"""SYSTEM: You are a helpful assistant for a blind user. Be concise and direct. Only describe what is certainly present. Do not ask questions.
If the context mentions a "mirror" or "reflection" and it seems to be describing the user themselves (e.g., "standing in front of a mirror"), assume it is a hallucination caused by the camera feed and describe it as the person being present or facing the camera.

USER:
Context: "{scene_description}"
Entities (detected movement):
{entities_text}

TASK: Synthesize the context and entities into one natural sentence.
IMPORTANT RULES:
1. The entities likely correspond to the subjects in the context (e.g., a "person" entity is likely the same as "a man" or "a woman" in the context). Do not treat them as separate people unless clearly distinct.
2. If the context mentions a person holding an object (e.g., "holding a phone", "with a remote"), and that object also appears in the entities list with movement, DO NOT describe the object as moving independently. The object is being held and moves with the person. Simply mention the person is holding it.
3. Small handheld objects (cell phone, remote, cup, etc.) moving in the same direction as a person are almost certainly held items, not independent threats.
4. Prioritize safety information about truly independent moving objects (vehicles, other people, animals)."""
        
        return prompt
    
    def generate_narration(self, prompt: str, timeout: float = 10.0) -> Optional[str]:
        """
        Generate narration from prompt using Ollama.
        
        Args:
            prompt: Input prompt
            timeout: Request timeout in seconds
        
        Returns:
            Generated narration string or None if error
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Lower temperature for more focused, less creative output
                    "top_p": 0.9,
                    "num_predict": 100,  # Limit response length
                    # Note: Ollama automatically uses Metal GPU on Mac when available
                    # GPU acceleration is handled by Ollama server, not via API
                }
            }
            
            response = requests.post(
                self.api_endpoint,
                json=payload,
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                narration = result.get("response", "").strip()
                
                # Clean up narration: remove follow-up questions and extra verbosity
                narration = self._clean_narration(narration)
                
                return narration
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
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
        """
        Check if Ollama is available.
        
        Returns:
            True if connection successful
        """
        try:
            response = requests.get(f"{self.api_url}/api/tags", timeout=2.0)
            return response.status_code == 200
        except Exception:
            return False
    
    def _clean_narration(self, narration: str) -> str:
        """
        Clean narration to remove follow-up questions and extra verbosity.
        
        Args:
            narration: Raw narration from LLM
        
        Returns:
            Cleaned narration string
        """
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
        
        # Remove multiple consecutive periods/spaces
        cleaned = re.sub(r"\.{2,}", ".", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned)
        cleaned = cleaned.strip()
        
        # If narration ends with a question mark, try to convert to statement
        if cleaned.endswith("?"):
            # Remove question marks at the end if it's asking for follow-up
            if any(phrase in cleaned.lower() for phrase in ["anything else", "need help", "assist", "let me know"]):
                cleaned = cleaned.rstrip("?").rstrip() + "."
        
        return cleaned
    
    def generate_narration_from_components(self, scene_description: str, 
                                           object_movements: List[str]) -> Optional[str]:
        """
        Generate narration from scene and movement components.
        
        Args:
            scene_description: Scene description from BLIP
            object_movements: List of movement description strings
        
        Returns:
            Generated narration string or None if error
        """
        prompt = self.compose_prompt(scene_description, object_movements)
        return self.generate_narration(prompt)

