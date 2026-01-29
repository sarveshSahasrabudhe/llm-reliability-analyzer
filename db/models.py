from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func
import uuid

class Base(DeclarativeBase):
    pass

class Run(Base):
    __tablename__ = "runs"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    model_name = Column(String, index=True)
    provider = Column(String)
    tags = Column(String) # Comma-separated tags
    
    # Metrics
    pass_rate = Column(Float, nullable=True)
    avg_latency = Column(Float, nullable=True)
    
    results = relationship("TestResult", back_populates="run", cascade="all, delete-orphan")

class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, ForeignKey("runs.id"))
    test_id = Column(String, index=True)
    test_name = Column(String)
    
    input_prompt = Column(Text)
    output_text = Column(Text)
    
    status = Column(String) # PASS / FAIL
    failure_reasons = Column(Text) # JSON list or newline separated
    
    latency_ms = Column(Float, nullable=True)
    
    # LLM Judge Scores
    judge_score = Column(Float, nullable=True)  # 0-10 score from judge
    judge_reasoning = Column(Text, nullable=True)  # Judge's explanation
    judge_issues = Column(Text, nullable=True)  # JSON list of issues found
    
    run = relationship("Run", back_populates="results")
