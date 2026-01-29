import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("Triggering full test suite run...")
payload = {
    "model_name": "llama-3.3-70b-versatile"
}

resp = requests.post(f"{BASE_URL}/runs", json=payload)
if resp.status_code == 202:
    run_data = resp.json()
    print(f"✅ Run triggered successfully!")
    print(f"Run ID: {run_data['id']}")
    print(f"Model: {run_data['model_name']}")
    print(f"\nCheck dashboard at: http://localhost:8501")
    print(f"Or monitor via API: GET {BASE_URL}/runs/{run_data['id']}")
else:
    print(f"❌ Failed: {resp.status_code} - {resp.text}")
