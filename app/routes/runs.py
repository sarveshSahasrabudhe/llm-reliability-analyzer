from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from db.session import get_db
from db.models import Run, TestResult
from app.schemas.run import RunCreate, RunResponse, RunDetailResponse
from app.services.runner_service import RunnerService
import os

router = APIRouter()

@router.post("/runs", response_model=RunResponse, status_code=202)
def create_run(run_in: RunCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Trigger a new test run in the background.
    """
    model_name = run_in.model_name or os.getenv("MODEL_NAME") or "gemini-flash-latest"
    provider = os.getenv("MODEL_PROVIDER", "google")
    
    # Create initial DB record
    db_run = Run(
        model_name=model_name,
        provider=provider,
        tags=",".join(run_in.tags) if run_in.tags else "all"
    )
    db.add(db_run)
    db.commit()
    db.refresh(db_run)
    
    # Enqueue background task
    background_tasks.add_task(RunnerService.execute_run, run_id=db_run.id, run_params=run_in)
    
    return db_run

@router.get("/runs", response_model=List[RunResponse])
def get_runs(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """
    Get a list of past runs.
    """
    return db.query(Run).order_by(Run.timestamp.desc()).offset(skip).limit(limit).all()

@router.get("/runs/{run_id}", response_model=RunDetailResponse)
def get_run_detail(run_id: str, db: Session = Depends(get_db)):
    """
    Get details for a specific run including test results.
    """
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run

@router.get("/compare")
def compare_runs(base_run: str, compare_run: str, db: Session = Depends(get_db)):
    """
    Compare two test runs to detect regressions and improvements.
    
    Args:
        base_run: ID of the baseline run
        compare_run: ID of the comparison run
    
    Returns:
        Comparison results with regressions, improvements, and metrics
    """
    from app.services.comparison_service import ComparisonService
    
    try:
        result = ComparisonService.compare_runs(db, base_run, compare_run)
        
        return {
            "base_run_id": result.base_run_id,
            "compare_run_id": result.compare_run_id,
            "base_model": result.base_model,
            "compare_model": result.compare_model,
            "base_pass_rate": result.base_pass_rate,
            "compare_pass_rate": result.compare_pass_rate,
            "pass_rate_delta": result.pass_rate_delta,
            "total_tests": result.total_tests,
            "regressions_count": len(result.regressions),
            "improvements_count": len(result.improvements),
            "unchanged_count": len(result.unchanged),
            "regressions": [
                {
                    "test_id": r.test_id,
                    "test_name": r.test_name,
                    "base_status": r.base_status,
                    "compare_status": r.compare_status
                }
                for r in result.regressions
            ],
            "improvements": [
                {
                    "test_id": i.test_id,
                    "test_name": i.test_name,
                    "base_status": i.base_status,
                    "compare_status": i.compare_status
                }
                for i in result.improvements
            ],
            "avg_latency_delta": result.avg_latency_delta
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
