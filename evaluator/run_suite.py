import os
import sys
import argparse
import time
from evaluator.llm.gemini_client import GeminiAdapter
from evaluator.loader import TestLoader
from db.models import Base, Run, TestResult
from db.session import engine, SessionLocal
import logging

# Basic logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("runner")

def run_suite():
    # Load env vars
    from dotenv import load_dotenv
    load_dotenv()
    
    # Initialize DB (create tables)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # Parse args
        parser = argparse.ArgumentParser(description="Run LLM Reliability Suite")
        parser.add_argument("--tags", nargs="+", help="Filter tests by tags (e.g. json refusal)")
        parser.add_argument("--model", help="Override model name")
        args = parser.parse_args()

        model_name = args.model or os.getenv("MODEL_NAME", "gemini-flash-latest")
        provider = os.getenv("MODEL_PROVIDER", "google")
        
        logger.info(f"Initializing Runner with model: {model_name}")
        
        # Create Run Record
        run_record = Run(
            model_name=model_name,
            provider=provider,
            tags=",".join(args.tags) if args.tags else "all"
        )
        db.add(run_record)
        db.commit()
        logger.info(f"Created Run ID: {run_record.id}")

        # Initialize Adapter
        try:
            adapter = GeminiAdapter(model_name=model_name)
        except Exception as e:
            logger.error(f"Failed to initialize Adapter: {e}")
            return

        # Load Tests
        loader = TestLoader(base_path="datasets")
        tests = loader.load_test_suite(tags=args.tags)
        
        print(f"\n{'='*20} Running Suite ({len(tests)} Tests) {'='*20}\n")
        if args.tags:
            print(f"Filtering by tags: {args.tags}")
        
        # Initialize Evaluators
        from evaluator.evaluators.format import FormatEvaluator
        from evaluator.evaluators.compliance import ComplianceEvaluator
        
        evaluators = [FormatEvaluator(), ComplianceEvaluator()]
        
        results = []
        latencies = []
        
        for test in tests:
            print(f"Running Test: {test.name} ({test.id})")
            print(f"Prompt: {test.prompt}")
            
            start_time = time.time()
            try:
                output = adapter.generate(
                    prompt=test.prompt, 
                    context=test.context
                )
                latency_ms = (time.time() - start_time) * 1000
                latencies.append(latency_ms)
                
                print(f"Output: {output.strip()}")
                
                # Run Evaluation
                test_passed = True
                reasons = []
                
                for evaluator in evaluators:
                    result = evaluator.evaluate(test, output)
                    if not result.passed:
                        test_passed = False
                        reasons.append(f"{evaluator.__class__.__name__}: {result.reason}")
                
                status = "PASS" if test_passed else "FAIL"
                color = "\033[92m" if test_passed else "\033[91m"
                reset = "\033[0m"
                
                print(f"Status: {color}{status}{reset} ({latency_ms:.2f}ms)")
                if not test_passed:
                    print(f"Failures: {', '.join(reasons)}")
                
                print("-" * 50)
                
                # Save Result to DB
                test_result = TestResult(
                    run_id=run_record.id,
                    test_id=test.id,
                    test_name=test.name,
                    input_prompt=test.prompt,
                    output_text=output,
                    status=status,
                    failure_reasons="\n".join(reasons),
                    latency_ms=latency_ms
                )
                db.add(test_result)
                db.commit()
                
                results.append({
                    "test": test, 
                    "status": status, 
                })
                
                # Sleep to respect free tier rate limits (15s = 4 req/min)
                time.sleep(15)
                
            except Exception as e:
                print(f"EXECUTION ERROR: {e}")
                
        # Update Run Metrics
        if results:
            passed_count = sum(1 for r in results if r["status"] == "PASS")
            run_record.pass_rate = passed_count / len(tests)
            run_record.avg_latency = sum(latencies) / len(latencies) if latencies else 0
            db.commit()
            
            print(f"\n{'='*20} Run Complete {'='*20}")
            print(f"Total Tests: {len(results)}")
            print(f"Pass Rate: {passed_count}/{len(results)} ({run_record.pass_rate*100:.1f}%)")
            print(f"Avg Latency: {run_record.avg_latency:.2f}ms")
            print(f"Run saved to DB: {run_record.id}")

    finally:
        db.close()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    run_suite()
