import httpx
import os
from typing import Dict, Any, Optional
from .base import ModelAdapter
import logging

logger = logging.getLogger(__name__)

class OllamaAdapter(ModelAdapter):
    def __init__(self, model_name: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = os.getenv("OLLAMA_BASE_URL", base_url)
        self.client = httpx.Client(timeout=float(os.getenv("TIMEOUT", "30.0")))

    def generate(self, prompt: str, context: Optional[str] = None, params: Optional[Dict[str, Any]] = None) -> str:
        url = f"{self.base_url}/api/generate"
        
        full_prompt = prompt
        if context:
            # Simple concatenation for now, can be improved with system roles if chat API is used
            full_prompt = f"Context: {context}\n\nInstruction: {prompt}"

        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False,
        }
        
        if params:
            if "temperature" in params:
                 payload["options"] = {"temperature": params["temperature"]}

        try:
            response = self.client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except httpx.RequestError as e:
            logger.error(f"Ollama request failed: {e}")
            return f"Error: {str(e)}"
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama returned error status: {e}")
            return f"Error: {e.response.text}"
