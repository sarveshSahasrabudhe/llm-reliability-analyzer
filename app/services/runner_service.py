import os
import time
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from app.schemas.run import RunCreate
from db.models import Run, TestResult
from db.session import SessionLocal
# from evaluator.llm.gemini_client import GeminiAdapter  # Commented: Using Groq instead
from evaluator.llm.groq_client import GroqAdapter
from evaluator.loader import TestLoader

logger = logging.getLogger(__name__)

class RunnerService:
    @staticmethod
    def execute_run(run_id: str, run_params: RunCreate):
        """
        Executes the test suite in the background.
        """
        # Load environment variables (critical for background tasks!)
        from dotenv import load_dotenv
        load_dotenv()
        
        db: Session = SessionLocal()
        try:
            run_record = db.query(Run).filter(Run.id == run_id).first()
            if not run_record:
                logger.error(f"Run {run_id} not found in DB")
                return

            model_name = run_params.model_name or os.getenv("MODEL_NAME") or "llama-3.3-70b-versatile"
            print(f"DEBUG: Starting run {run_id} with model {model_name}")
            
            # Initialize Adapter
            try:
                # adapter = GeminiAdapter(model_name=model_name)  # Commented: Using Groq instead
                adapter = GroqAdapter(model_name=model_name)
            except Exception as e:
                logger.error(f"Adapter init failed: {e}")
                return

            # Load Tests
            loader = TestLoader(base_path="datasets")
            tests = loader.load_test_suite(tags=run_params.tags)
            print(f"DEBUG: Loaded {len(tests)} tests for tags {run_params.tags}")
            
            # Initialize Evaluators
            from evaluator.evaluators.format import FormatEvaluator
            from evaluator.evaluators.compliance import ComplianceEvaluator
            evaluators = [FormatEvaluator(), ComplianceEvaluator()]
            
            latencies = []
            results_meta = []

            for test in tests:
                start_time = time.time()
                try:
                    output = adapter.generate(prompt=test.prompt, context=test.context)
                    latency_ms = (time.time() - start_time) * 1000
                    latencies.append(latency_ms)
                    
                    # Evaluate
                    test_passed = True
                    reasons = []
                    for ev in evaluators:
                        res = ev.evaluate(test, output)
                        if not res.passed:
                            test_passed = False
                            reasons.append(f"{ev.__class__.__name__}: {res.reason}")
                    
                    status = "PASS" if test_passed else "FAIL"
                    
                    # Save Result
                    acc_result = TestResult(
                        run_id=run_id,
                        test_id=test.id,
                        test_name=test.name,
                        input_prompt=test.prompt,
                        output_text=output,
                        status=status,
                        failure_reasons="\n".join(reasons),
                        latency_ms=latency_ms
                    )
                    db.add(acc_result)
                    db.commit()
                    
                    results_meta.append({"status": status})
                    
                    # Rate limit sleep (15s for free tier: 4 req/min < 5 req/min limit)
                    time.sleep(15)
                    
                except Exception as e:
                    logger.error(f"Test {test.id} execution failed: {e}")
            
            # Update Run Metrics
            if results_meta:
                pass_count = sum(1 for r in results_meta if r["status"] == "PASS")
                run_record.pass_rate = pass_count / len(tests)
                run_record.avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
                db.commit()
                
        except Exception as e:
            logger.error(f"Critical error in execute_run: {e}")
        finally:
            db.close()
