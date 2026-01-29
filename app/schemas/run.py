from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class RunCreate(BaseModel):
    model_name: Optional[str] = None
    tags: Optional[List[str]] = None

class TestResultResponse(BaseModel):
    id: str
    test_name: str
    input_prompt: str
    output_text: str
    status: str
    failure_reasons: Optional[str] = None
    latency_ms: Optional[float] = None
    
    class Config:
        from_attributes = True

class RunResponse(BaseModel):
    id: str
    timestamp: datetime
    model_name: str
    provider: str
    tags: str
    pass_rate: Optional[float] = None
    avg_latency: Optional[float] = None
    
    class Config:
        from_attributes = True

class RunDetailResponse(RunResponse):
    results: List[TestResultResponse] = []
