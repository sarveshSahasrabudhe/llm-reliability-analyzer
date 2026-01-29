"""
Semantic similarity metrics using sentence embeddings.
"""
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

class SimilarityCalculator:
    """
    Calculate semantic similarity between texts using sentence embeddings.
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize with a sentence transformer model.
        
        Args:
            model_name: HuggingFace model name for embeddings
        """
        self.model = SentenceTransformer(model_name)
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            float between 0-1, where 1 = identical meaning
        """
        # Get embeddings
        embeddings = self.model.encode([text1, text2])
        
        # Compute cosine similarity
        similarity = self._cosine_similarity(embeddings[0], embeddings[1])
        
        return float(similarity)
    
    def batch_similarities(self, texts: List[str], reference: str) -> List[float]:
        """
        Compute similarities between multiple texts and a reference.
        
        Args:
            texts: List of texts to compare
            reference: Reference text
        
        Returns:
            List of similarity scores
        """
        # Get all embeddings at once (more efficient)
        all_texts = [reference] + texts
        embeddings = self.model.encode(all_texts)
        
        ref_embedding = embeddings[0]
        text_embeddings = embeddings[1:]
        
        # Compute similarities
        similarities = [
            self._cosine_similarity(ref_embedding, text_emb)
            for text_emb in text_embeddings
        ]
        
        return [float(s) for s in similarities]
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Compute cosine similarity between two vectors.
        
        Args:
            vec1, vec2: Numpy arrays
        
        Returns:
            float similarity score
        """
        # Cosine similarity = dot product / (norm1 * norm2)
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
