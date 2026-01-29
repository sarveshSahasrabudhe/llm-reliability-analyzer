from db.session import SessionLocal
from db.models import Run, TestResult

def verify_db():
    db = SessionLocal()
    try:
        print("Querying DB for Runs...")
        runs = db.query(Run).order_by(Run.timestamp.desc()).all()
        print(f"Found {len(runs)} runs.")
        
        if runs:
            latest_run = runs[0]
            print(f"Latest Run ID: {latest_run.id}")
            print(f"Timestamp: {latest_run.timestamp}")
            print(f"Model: {latest_run.model_name}")
            print(f"Pass Rate: {latest_run.pass_rate}")
            print(f"Avg Latency: {latest_run.avg_latency} ms")
            
            print("\nQuerying DB for Results...")
            results = db.query(TestResult).filter(TestResult.run_id == latest_run.id).all()
            print(f"Found {len(results)} results for this run.")
            for r in results:
                print(f"- [{r.status}] {r.test_name}: {r.latency_ms:.2f}ms")
    finally:
        db.close()

if __name__ == "__main__":
    verify_db()
