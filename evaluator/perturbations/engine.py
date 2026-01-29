"""
Prompt perturbation engine for testing LLM sensitivity.
"""
import random
import re
from typing import List

class PromptPerturber:
    """
    Applies various perturbations to prompts to test LLM robustness.
    """
    
    @staticmethod
    def reorder_words(prompt: str) -> str:
        """
        Shuffle word order while trying to preserve meaning.
        Simple approach: reverse the sentence or shuffle clauses.
        
        Example: "What is the capital of France?" -> "France of capital the is what?"
        """
        # Remove punctuation temporarily
        punctuation = ""
        if prompt and prompt[-1] in "?!.":
            punctuation = prompt[-1]
            prompt = prompt[:-1]
        
        words = prompt.split()
        
        # Simple reversal (more controlled than full shuffle)
        words.reverse()
        
        result = " ".join(words) + punctuation
        return result
    
    @staticmethod
    def add_noise(prompt: str, noise_level: float = 0.2) -> str:
        """
        Add typos, spacing issues, and capitalization changes.
        
        Args:
            prompt: Original prompt
            noise_level: Fraction of words to modify (0.0 to 1.0)
        
        Example: "What is the capital of France?" -> "what  is the Capitol of france?"
        """
        words = prompt.split()
        num_modifications = max(1, int(len(words) * noise_level))
        
        # Randomly select words to modify
        indices_to_modify = random.sample(range(len(words)), min(num_modifications, len(words)))
        
        for idx in indices_to_modify:
            word = words[idx]
            modification_type = random.choice(['lowercase', 'uppercase', 'typo', 'double_space'])
            
            if modification_type == 'lowercase':
                words[idx] = word.lower()
            elif modification_type == 'uppercase':
                words[idx] = word.upper()
            elif modification_type == 'typo' and len(word) > 2:
                # Swap two adjacent letters
                pos = random.randint(0, len(word) - 2)
                word_list = list(word)
                word_list[pos], word_list[pos + 1] = word_list[pos + 1], word_list[pos]
                words[idx] = ''.join(word_list)
        
        # Add random double spaces
        result = " ".join(words)
        if random.random() < 0.3:
            result = result.replace(" ", "  ", 1)
        
        return result
    
    @staticmethod
    def vary_format(prompt: str) -> str:
        """
        Change punctuation and capitalization format.
        
        Example: "What is the capital of France?" -> "what is the capital of France"
        """
        variations = [
            # Remove question mark
            lambda p: p.rstrip('?!.'),
            # Lowercase first letter
            lambda p: p[0].lower() + p[1:] if p else p,
            # Remove all punctuation
            lambda p: re.sub(r'[^\w\s]', '', p),
            # Add ellipsis
            lambda p: p.rstrip('?!.') + '...',
        ]
        
        variation = random.choice(variations)
        return variation(prompt)
    
    @staticmethod
    def generate_perturbations(prompt: str, count: int = 5) -> List[str]:
        """
        Generate multiple perturbations of a prompt.
        
        Args:
            prompt: Original prompt
            count: Number of perturbations to generate
        
        Returns:
            List of perturbed prompts (includes original)
        """
        perturbations = [prompt]  # Always include original
        
        techniques = [
            PromptPerturber.reorder_words,
            PromptPerturber.add_noise,
            PromptPerturber.vary_format,
        ]
        
        for _ in range(count - 1):
            technique = random.choice(techniques)
            perturbed = technique(prompt)
            # Avoid exact duplicates
            if perturbed not in perturbations:
                perturbations.append(perturbed)
        
        return perturbations[:count]
