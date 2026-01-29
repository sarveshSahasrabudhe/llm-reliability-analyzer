import json
import logging
from typing import Optional
from evaluator.base import BaseEvaluator, EvaluationResult
from app.schemas.test_case import TestCase
from evaluator.judges.prompts import get_judge_prompt
from evaluator.llm.groq_client import GroqAdapter

logger = logging.getLogger(__name__)

class LLMJudgeEvaluator(BaseEvaluator):
    """
    Uses an LLM to judge test outputs for semantic qualities.
    Evaluates: grounding, hallucination, and overall quality.
    """
    
    def __init__(self, judge_model: str = "llama-3.3-70b-versatile", evaluation_type: str = "grounding"):
        """
        Args:
            judge_model: Model to use for judging
            evaluation_type: Type of evaluation ('grounding', 'hallucination', 'quality')
        """
        self.judge = GroqAdapter(model_name=judge_model)
        self.evaluation_type = evaluation_type
    
    def evaluate(self, test_case: TestCase, output: str) -> EvaluationResult:
        """
        Use LLM to judge the output quality.
        
        Args:
            test_case: The test case being evaluated
            output: The LLM's output to judge
        
        Returns:
            EvaluationResult with judge score and reasoning
        """
        # Get judge prompt
        judge_prompt = get_judge_prompt(
            evaluation_type=self.evaluation_type,
            prompt=test_case.prompt,
            output=output,
            expected_behavior=test_case.expected_behavior or ""
        )
        
        try:
            # Call judge API
            judge_response = self.judge.generate(prompt=judge_prompt)
            
            # Parse JSON response
            judgment = self._parse_judgment(judge_response)
            
            # Determine pass/fail based on score threshold
            score = judgment.get("score", 0)
            passed = score >= 7.0  # Threshold: 7/10 to pass
            
            # Extract reasoning
            reasoning = judgment.get("reasoning", "No reasoning provided")
            issues = judgment.get("issues", []) or judgment.get("hallucinations", [])
            
            reason_text = f"Judge Score: {score}/10. {reasoning}"
            if issues:
                reason_text += f" Issues: {', '.join(issues)}"
            
            return EvaluationResult(
                score=score / 10.0,  # Normalize to 0-1
                passed=passed,
                reason=reason_text,
                failure_type="JUDGE_QUALITY_FAIL" if not passed else None
            )
            
        except Exception as e:
            logger.error(f"Judge evaluation failed: {e}")
            return EvaluationResult(
                score=0.0,
                passed=False,
                reason=f"Judge execution error: {str(e)}",
                failure_type="JUDGE_ERROR"
            )
    
    def _parse_judgment(self, response: str) -> dict:
        """
        Parse judge's JSON response.
        
        Args:
            response: Raw judge response
        
        Returns:
            Parsed judgment dict
        """
        try:
            # Try to extract JSON from markdown if present
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                response = response[start:end].strip()
            
            judgment = json.loads(response)
            return judgment
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse judge response as JSON: {e}")
            logger.error(f"Response was: {response[:200]}")
            # Return default failure
            return {
                "score": 0,
                "reasoning": "Failed to parse judge response",
                "issues": ["JSON parse error"]
            }
