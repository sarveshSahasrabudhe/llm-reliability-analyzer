from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List
from app.schemas.test_case import TestCase

@dataclass
class EvaluationResult:
    score: float  # 0.0 to 1.0
    passed: bool
    reason: str
    failure_type: Optional[str] = None  # FORMAT_FAIL, COMPLIANCE_FAIL, etc.

class BaseEvaluator(ABC):
    @abstractmethod
    def evaluate(self, test_case: TestCase, output: str) -> EvaluationResult:
        """
        Evaluates the LLM output against the test case definition.
        """
        pass
