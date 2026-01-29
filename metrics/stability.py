"""
Stability metrics for measuring LLM output consistency.
"""
from typing import List
from collections import Counter

def calculate_exact_match_rate(outputs: List[str]) -> float:
    """
    Calculate the proportion of outputs that are exactly the same.
    
    Args:
        outputs: List of outputs from perturbed prompts
    
    Returns:
        float between 0-1, where 1 = all outputs identical
    """
    if not outputs:
        return 0.0
    
    # Find most common output
    counter = Counter(outputs)
    most_common_count = counter.most_common(1)[0][1] if counter else 0
    
    # Exact match rate = frequency of most common / total
    return most_common_count / len(outputs)

def calculate_semantic_similarity(outputs: List[str]) -> float:
    """
    Calculate semantic similarity between outputs.
    For now, uses a simple normalized edit distance approach.
    
    In production, this would use embeddings (e.g., sentence transformers).
    
    Args:
        outputs: List of outputs
    
    Returns:
        float between 0-1, where 1 = very similar
    """
    if not outputs or len(outputs) < 2:
        return 1.0
    
    # Simple approach: average pairwise string similarity
    similarities = []
    
    for i in range(len(outputs)):
        for j in range(i + 1, len(outputs)):
            sim = _simple_similarity(outputs[i], outputs[j])
            similarities.append(sim)
    
    return sum(similarities) / len(similarities) if similarities else 0.0

def _simple_similarity(s1: str, s2: str) -> float:
    """
    Simple string similarity based on common words.
    
    Args:
        s1, s2: Strings to compare
    
    Returns:
        float between 0-1
    """
    words1 = set(s1.lower().split())
    words2 = set(s2.lower().split())
    
    if not words1 and not words2:
        return 1.0
    if not words1 or not words2:
        return 0.0
    
    intersection = words1 & words2
    union = words1 | words2
    
    # Jaccard similarity
    return len(intersection) / len(union) if union else 0.0

def calculate_consistency_score(outputs: List[str]) -> float:
    """
    Combined consistency metric.
    
    Combines exact match rate and semantic similarity.
    
    Args:
        outputs: List of outputs from perturbed prompts
    
    Returns:
        float between 0-1, where 1 = perfect consistency
    """
    exact_match = calculate_exact_match_rate(outputs)
    semantic_sim = calculate_semantic_similarity(outputs)
    
    # Weighted average (exact match weighted more heavily)
    return 0.6 * exact_match + 0.4 * semantic_sim

def analyze_stability(outputs: List[str]) -> dict:
    """
    Comprehensive stability analysis.
    
    Args:
        outputs: List of outputs from perturbed prompts
    
    Returns:
        dict with all metrics
    """
    return {
        "exact_match_rate": calculate_exact_match_rate(outputs),
        "semantic_similarity": calculate_semantic_similarity(outputs),
        "consistency_score": calculate_consistency_score(outputs),
        "num_unique_outputs": len(set(outputs)),
        "total_outputs": len(outputs),
        "most_common_output": Counter(outputs).most_common(1)[0][0] if outputs else None
    }
