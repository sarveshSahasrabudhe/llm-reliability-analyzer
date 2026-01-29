from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class TestCase(BaseModel):
    id: str = Field(..., description="Unique identifier for the test case")
    name: str = Field(..., description="Human readable name of the test")
    tags: List[str] = Field(default_factory=list, description="Tags for filtering (e.g. ['json', 'refusal'])")
    
    prompt: str = Field(..., description="The input prompt for the LLM")
    context: Optional[str] = Field(None, description="Optional background context or system message")
    
    expected_behavior: Optional[str] = Field(None, description="Description of expected behavior for human/LLM judge")
    expected_output: Optional[str] = Field(None, description="Exact expected output string (rarely used for LLMs)")
    evaluation_criteria: Optional[Dict[str, Any]] = Field(None, description="Criteria for automated evaluation")
    
    constraints: List[str] = Field(default_factory=list, description="List of constraints to check (e.g. 'max_words:10')")
    should_refuse: bool = Field(False, description="Whether the model should refuse to answer")
    
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Extra metadata")
