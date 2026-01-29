"""
Comparison service for detecting regressions between test runs.
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from db.models import Run, TestResult
from dataclasses import dataclass

@dataclass
class TestComparison:
    """Comparison of a single test between two runs."""
    test_id: str
    test_name: str
    base_status: str
    compare_status: str
    changed: bool
    is_regression: bool  # PASS -> FAIL
    is_improvement: bool  # FAIL -> PASS
    base_latency: Optional[float]
    compare_latency: Optional[float]

@dataclass
class ComparisonResult:
    """Full comparison between two runs."""
    base_run_id: str
    compare_run_id: str
    base_model: str
    compare_model: str
    base_pass_rate: float
    compare_pass_rate: float
    pass_rate_delta: float
    
    total_tests: int
    regressions: List[TestComparison]
    improvements: List[TestComparison]
    unchanged: List[TestComparison]
    
    avg_latency_delta: float

class ComparisonService:
    """Service for comparing test runs and detecting regressions."""
    
    @staticmethod
    def compare_runs(db: Session, base_run_id: str, compare_run_id: str) -> ComparisonResult:
        """
        Compare two test runs and identify regressions/improvements.
        
        Args:
            db: Database session
            base_run_id: ID of the baseline run
            compare_run_id: ID of the comparison run
        
        Returns:
            ComparisonResult with full analysis
        """
        # Fetch runs
        base_run = db.query(Run).filter(Run.id == base_run_id).first()
        compare_run = db.query(Run).filter(Run.id == compare_run_id).first()
        
        if not base_run or not compare_run:
            raise ValueError("One or both runs not found")
        
        # Fetch results
        base_results = {r.test_id: r for r in base_run.results}
        compare_results = {r.test_id: r for r in compare_run.results}
        
        # Get all test IDs
        all_test_ids = set(base_results.keys()) | set(compare_results.keys())
        
        regressions = []
        improvements = []
        unchanged = []
        
        for test_id in all_test_ids:
            base_result = base_results.get(test_id)
            compare_result = compare_results.get(test_id)
            
            # Skip if test missing in either run
            if not base_result or not compare_result:
                continue
            
            base_status = base_result.status
            compare_status = compare_result.status
            
            is_regression = base_status == "PASS" and compare_status == "FAIL"
            is_improvement = base_status == "FAIL" and compare_status == "PASS"
            changed = base_status != compare_status
            
            comparison = TestComparison(
                test_id=test_id,
                test_name=base_result.test_name,
                base_status=base_status,
                compare_status=compare_status,
                changed=changed,
                is_regression=is_regression,
                is_improvement=is_improvement,
                base_latency=base_result.latency_ms,
                compare_latency=compare_result.latency_ms
            )
            
            if is_regression:
                regressions.append(comparison)
            elif is_improvement:
                improvements.append(comparison)
            else:
                unchanged.append(comparison)
        
        # Calculate metrics
        pass_rate_delta = (compare_run.pass_rate or 0) - (base_run.pass_rate or 0)
        avg_latency_delta = (compare_run.avg_latency or 0) - (base_run.avg_latency or 0)
        
        return ComparisonResult(
            base_run_id=base_run_id,
            compare_run_id=compare_run_id,
            base_model=base_run.model_name,
            compare_model=compare_run.model_name,
            base_pass_rate=base_run.pass_rate or 0,
            compare_pass_rate=compare_run.pass_rate or 0,
            pass_rate_delta=pass_rate_delta,
            total_tests=len(all_test_ids),
            regressions=regressions,
            improvements=improvements,
            unchanged=unchanged,
            avg_latency_delta=avg_latency_delta
        )
    
    @staticmethod
    def print_report(result: ComparisonResult):
        """Print a human-readable comparison report."""
        print("="*60)
        print("REGRESSION COMPARISON REPORT")
        print("="*60)
        print(f"\nBase Run: {result.base_model} ({result.base_run_id[:8]}...)")
        print(f"  Pass Rate: {result.base_pass_rate*100:.1f}%")
        print(f"\nCompare Run: {result.compare_model} ({result.compare_run_id[:8]}...)")
        print(f"  Pass Rate: {result.compare_pass_rate*100:.1f}%")
        
        # Overall change
        delta = result.pass_rate_delta * 100
        if delta > 0:
            print(f"\n✅ Overall: +{delta:.1f}% improvement")
        elif delta < 0:
            print(f"\n❌ Overall: {delta:.1f}% regression")
        else:
            print(f"\n➡️  Overall: No change in pass rate")
        
        # Regressions
        if result.regressions:
            print(f"\n🔴 Regressions ({len(result.regressions)}):")
            for r in result.regressions:
                print(f"  ❌ {r.test_name}: PASS → FAIL")
        
        # Improvements
        if result.improvements:
            print(f"\n🟢 Improvements ({len(result.improvements)}):")
            for i in result.improvements:
                print(f"  ✅ {i.test_name}: FAIL → PASS")
        
        print(f"\n➡️  Unchanged: {len(result.unchanged)} tests")
        
        # Latency
        if result.avg_latency_delta != 0:
            print(f"\n⏱️  Avg Latency: {result.avg_latency_delta:+.0f}ms")
        
        print("="*60)
