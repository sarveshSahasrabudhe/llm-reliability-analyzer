"""
CI Runner Script
----------------
Run checks specifically for Continuous Integration environment.
Exits with code 1 if tests fail, stopping the build.
"""
import sys
import os
import asyncio
from evaluator.loader import TestLoader
from evaluator.llm.groq_client import GroqAdapter
from evaluator.evaluators.format import FormatEvaluator
from evaluator.evaluators.compliance import ComplianceEvaluator
from evaluator.base import EvaluationResult
from dotenv import load_dotenv

load_dotenv()

async def run_smoke_tests():
    print("🚀 Starting Smoke Tests for CI...")
    
    # Load smoke suite
    loader = TestLoader(base_path="datasets")
    tests = loader.load_specific_file("datasets/smoke.json")
    
    # Initialize components
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ CRITICAL ERROR: GROQ_API_KEY not found in environment variables!")
        print("   Please add 'GROQ_API_KEY' to your GitHub Repository Secrets.")
        sys.exit(1)

    model = GroqAdapter(model_name="llama-3.3-70b-versatile")
    format_eval = FormatEvaluator()
    compliance_eval = ComplianceEvaluator()
    
    passed_count = 0
    failed_count = 0
    
    for test in tests:
        print(f"\nrunning: {test.name}...", end="", flush=True)
        
        try:
            # Generate
            output = model.generate(test.prompt)
            
            # Evaluate
            reasons = []
            passed = True
            
            # Run evaluators
            if test.evaluation_criteria:
                if test.evaluation_criteria.get("format") == "json":
                    res = format_eval.evaluate(test, output)
                    if not res.passed:
                        passed = False
                        reasons.append(res.reason)
                        
                if any(k in test.evaluation_criteria for k in ["refusal", "required_phrases"]):
                    res = compliance_eval.evaluate(test, output)
                    if not res.passed:
                        passed = False
                        reasons.append(res.reason)
            
            if passed:
                print(" ✅ PASS")
                passed_count += 1
            else:
                print(" ❌ FAIL")
                print(f"   Reason: {', '.join(reasons)}")
                failed_count += 1
                
        except Exception as e:
            print(f" ❌ ERROR: {e}")
            failed_count += 1
            
    print("\n" + "="*40)
    print("SMOKE TEST SUMMARY")
    print("="*40)
    print(f"Total: {len(tests)}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")
    
    if failed_count > 0:
        print("\n❌ CI FAILURE: Some tests failed.")
        sys.exit(1)
    else:
        print("\n✅ CI SUCCESS: All smoke tests passed.")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(run_smoke_tests())
