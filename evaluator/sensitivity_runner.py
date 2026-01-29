"""
Sensitivity test runner that applies perturbations and measures stability.
"""
import time
from typing import List, Dict
from app.schemas.test_case import TestCase
from evaluator.perturbations.engine import PromptPerturber
from metrics.stability import analyze_stability
from evaluator.llm.base import ModelAdapter

class SensitivityRunner:
    """
    Runs a test case with multiple prompt perturbations and measures output stability.
    """
    
    def __init__(self, adapter: ModelAdapter, perturbation_count: int = 5):
        """
        Args:
            adapter: LLM adapter to test
            perturbation_count: Number of perturbed versions to generate
        """
        self.adapter = adapter
        self.perturbation_count = perturbation_count
    
    def run_sensitivity_test(self, test_case: TestCase) -> Dict:
        """
        Run a test with multiple perturbations and analyze stability.
        
        Args:
            test_case: Base test case to perturb
        
        Returns:
            dict with:
                - perturbed_prompts: List of prompts used
                - outputs: List of LLM outputs
                - stability_metrics: Consistency scores
                - latencies: Response times for each
        """
        # Generate perturbations
        perturbed_prompts = PromptPerturber.generate_perturbations(
            test_case.prompt,
            self.perturbation_count
        )
        
        # Run LLM on each perturbation
        outputs = []
        latencies = []
        
        for prompt in perturbed_prompts:
            start_time = time.time()
            output = self.adapter.generate(prompt=prompt)
            latency_ms = (time.time() - start_time) * 1000
            
            outputs.append(output)
            latencies.append(latency_ms)
            
            # Rate limiting
            time.sleep(0.5)
        
        # Analyze stability
        stability_metrics = analyze_stability(outputs)
        
        return {
            "test_id": test_case.id,
            "test_name": test_case.name,
            "base_prompt": test_case.prompt,
            "perturbed_prompts": perturbed_prompts,
            "outputs": outputs,
            "stability_metrics": stability_metrics,
            "latencies": latencies,
            "avg_latency_ms": sum(latencies) / len(latencies) if latencies else 0
        }
    
    def print_report(self, result: Dict):
        """
        Print a human-readable sensitivity report.
        
        Args:
            result: Result from run_sensitivity_test
        """
        print("="*60)
        print(f"SENSITIVITY TEST REPORT: {result['test_name']}")
        print("="*60)
        print(f"\nBase Prompt: {result['base_prompt']}")
        print(f"\nPerturbations Tested: {len(result['perturbed_prompts'])}")
        
        print("\n--- Perturbed Prompts & Outputs ---")
        for i, (prompt, output) in enumerate(zip(result['perturbed_prompts'], result['outputs']), 1):
            print(f"\n{i}. Prompt: {prompt}")
            print(f"   Output: {output[:100]}{'...' if len(output) > 100 else ''}")
        
        print("\n--- Stability Metrics ---")
        metrics = result['stability_metrics']
        print(f"Exact Match Rate: {metrics['exact_match_rate']:.2%}")
        print(f"Semantic Similarity: {metrics['semantic_similarity']:.2f}")
        print(f"Consistency Score: {metrics['consistency_score']:.2f}")
        print(f"Unique Outputs: {metrics['num_unique_outputs']}/{metrics['total_outputs']}")
        print(f"Most Common Output: {metrics['most_common_output']}")
        
        print(f"\nAvg Latency: {result['avg_latency_ms']:.0f}ms")
        
        # Interpretation
        consistency = metrics['consistency_score']
        if consistency >= 0.9:
            print("\n✅ EXCELLENT: Model is highly stable across perturbations")
        elif consistency >= 0.7:
            print("\n⚠️  GOOD: Model shows reasonable stability")
        elif consistency >= 0.5:
            print("\n⚠️  MODERATE: Model shows some sensitivity to prompt changes")
        else:
            print("\n❌ POOR: Model is highly sensitive to prompt variations (reliability concern!)")
        
        print("="*60)
