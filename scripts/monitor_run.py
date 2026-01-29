import requests
import sys
import time

BASE_URL = "http://127.0.0.1:8000"

if len(sys.argv) < 2:
    print("Usage: python monitor_run.py <run_id>")
    sys.exit(1)

run_id = sys.argv[1]

print(f"Monitoring run: {run_id}")
print("=" * 50)

last_count = 0
while True:
    resp = requests.get(f"{BASE_URL}/runs/{run_id}")
    if resp.status_code != 200:
        print(f"Error: {resp.status_code}")
        break
    
    data = resp.json()
    results = data.get("results", [])
    current_count = len(results)
    
    if current_count > last_count:
        print(f"\n[Progress] {current_count}/31 tests completed")
        
        # Show last completed test
        if results:
            last_result = results[-1]
            status = last_result['status']
            emoji = "✅" if status == "PASS" else "❌"
            print(f"  {emoji} Latest: {last_result['test_name']} - {status}")
        
        last_count = current_count
        
        # Check for checkpoint at 15 tests
        if current_count == 15:
            passed = sum(1 for r in results if r['status'] == 'PASS')
            print(f"\n{'='*50}")
            print(f"🎯 CHECKPOINT: 15/31 tests complete")
            print(f"   Pass Rate: {passed}/15 ({passed/15*100:.1f}%)")
            print(f"{'='*50}\n")
        
        # Check if complete
        if current_count >= 31:
            passed = sum(1 for r in results if r['status'] == 'PASS')
            print(f"\n{'='*50}")
            print(f"✅ RUN COMPLETE: 31/31 tests")
            print(f"   Final Pass Rate: {passed}/31 ({passed/31*100:.1f}%)")
            print(f"{'='*50}")
            break
    
    time.sleep(3)  # Check every 3 seconds
