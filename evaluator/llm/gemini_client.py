import os
import google.generativeai as genai
from typing import Dict, Any, Optional
from .base import ModelAdapter
import logging

logger = logging.getLogger(__name__)

class GeminiAdapter(ModelAdapter):
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.model_name = model_name
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.error("GOOGLE_API_KEY not found in environment variables.")
            raise ValueError("GOOGLE_API_KEY is missing")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def generate(self, prompt: str, context: Optional[str] = None, params: Optional[Dict[str, Any]] = None) -> str:
        
        # Combine system context if provided (Gemini supports system instructions in newer versions, 
        # but simple concatenation is robust for broad compatibility in this demo)
        if context:
            full_prompt = f"System Context: {context}\n\nUser Instruction: {prompt}"
        else:
            full_prompt = prompt

        try:
            # Default generation config
            generation_config = genai.types.GenerationConfig(
                temperature=params.get("temperature", 0.7) if params else 0.7
            )
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return f"Error: {str(e)}"
