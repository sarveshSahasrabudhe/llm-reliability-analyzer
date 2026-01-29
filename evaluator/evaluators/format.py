import json
import logging
from evaluator.base import BaseEvaluator, EvaluationResult
from app.schemas.test_case import TestCase

logger = logging.getLogger(__name__)

class FormatEvaluator(BaseEvaluator):
    def evaluate(self, test_case: TestCase, output: str) -> EvaluationResult:
        # Check if JSON format is required
        requires_json = False
        if test_case.tags and "json" in test_case.tags:
            requires_json = True
        
        # Also check constraints
        if any("format:json" in c.lower() for c in test_case.constraints):
            requires_json = True
            
        if not requires_json:
            return EvaluationResult(score=1.0, passed=True, reason="No format constraints")

        try:
            # Attempt to find JSON blob if it's wrapped in markdown
            cleaned_output = output
            if "```json" in output:
                cleaned_output = output.split("```json")[1].split("```")[0]
            elif "```" in output:
                 cleaned_output = output.split("```")[1].split("```")[0]
            
            json.loads(cleaned_output.strip())
            return EvaluationResult(score=1.0, passed=True, reason="Valid JSON")
        except json.JSONDecodeError as e:
            return EvaluationResult(
                score=0.0, 
                passed=False, 
                reason=f"Invalid JSON: {str(e)}", 
                failure_type="FORMAT_FAIL"
            )
