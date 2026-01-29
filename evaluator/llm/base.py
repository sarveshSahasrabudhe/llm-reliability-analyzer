from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ModelAdapter(ABC):
    @abstractmethod
    def generate(self, prompt: str, context: Optional[str] = None, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Generates text from the LLM.
        
        Args:
            prompt: The user prompt or instruction.
            context: Optional background context (system message or RAG context).
            params: Optional model parameters (temperature, max_tokens, etc).
            
        Returns:
            The generated text response.
        """
        pass
