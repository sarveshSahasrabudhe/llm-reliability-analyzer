import os
from typing import Dict, Any, Optional
from .base import ModelAdapter
from groq import Groq, GroqError
import logging

logger = logging.getLogger(__name__)

class GroqAdapter(ModelAdapter):
    def __init__(self, model_name: str = "llama3-70b-8192"):
        self.model_name = model_name
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("GROQ_API_KEY not found in environment variables.")
        
        self.client = Groq(api_key=self.api_key)

    def generate(self, prompt: str, context: Optional[str] = None, params: Optional[Dict[str, Any]] = None) -> str:
        messages = []
        
        if context:
            messages.append({"role": "system", "content": context})
            
        messages.append({"role": "user", "content": prompt})

        # Default params
        temperature = 0.7
        if params and "temperature" in params:
            temperature = params["temperature"]

        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model_name,
                temperature=temperature,
            )
            return chat_completion.choices[0].message.content
        except GroqError as e:
            logger.error(f"Groq API error: {e}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error calling Groq: {e}")
            return f"Error: {str(e)}"
