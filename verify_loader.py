from evaluator.loader import TestLoader
import logging

logging.basicConfig(level=logging.INFO)

def verify():
    print("Verifying TestLoader...")
    try:
        loader = TestLoader(base_path="datasets")
        tests = loader.load_test_suite()
        print(f"Successfully loaded {len(tests)} tests.")
        for t in tests:
            print(f"- [{t.id}] {t.name} (Tags: {t.tags})")
            
        print("\nVerifying Tag Filter (tags=['grounding'])...")
        grounding_tests = loader.load_test_suite(tags=["grounding"])
        print(f"Loaded {len(grounding_tests)} grounding tests.")
        assert len(grounding_tests) > 0, "Should have found grounding tests"
        
        print("\nLoader Verification PASSED ✅")
    except Exception as e:
        print(f"\nLoader Verification FAILED ❌: {e}")
        exit(1)

if __name__ == "__main__":
    verify()
