import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

def verify_api():
    print(f"Checking API health at {BASE_URL}...")
    try:
        resp = requests.get(f"{BASE_URL}/")
        print(f"Root: {resp.json()}")
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    print("\nTriggering Run (POST /runs)...")
    payload = {
        "tags": ["json"],
        "model_name": "gemini-flash-latest"
    }
    resp = requests.post(f"{BASE_URL}/runs", json=payload)
    if resp.status_code != 202:
        print(f"Failed to trigger run: {resp.text}")
        return
    
    run_data = resp.json()
    run_id = run_data["id"]
    print(f"Run triggered! ID: {run_id}")
    
    print("\nPolling for results (GET /runs/{id})...")
    for i in range(10):
        time.sleep(2)
        resp = requests.get(f"{BASE_URL}/runs/{run_id}")
        data = resp.json()
        
        # Check if results are populated
        results = data.get("results", [])
        print(f"Attempt {i+1}: Found {len(results)} results...")
        
        if len(results) > 0:
            print("Run completed (or partially completed)!")
            for res in results:
                print(f"- [{res['status']}] {res['test_name']}")
            break
    else:
        print("Timeout waiting for results.")

if __name__ == "__main__":
    verify_api()
