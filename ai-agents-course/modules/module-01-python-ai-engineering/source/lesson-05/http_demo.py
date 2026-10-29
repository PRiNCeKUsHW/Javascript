# http_demo.py: make HTTP requests with httpx
import httpx

BASE = "http://127.0.0.1:8765"

response = httpx.get(f"{BASE}/usage_sample.json", timeout=5.0)
print(response.status_code, response.headers["content-type"])
response.raise_for_status()                # 4xx/5xx -> exception
records = response.json()                  # JSON body -> Python list
print(len(records), "records, first id:", records[0]["id"])

try:
    httpx.get(f"{BASE}/missing.json", timeout=5.0).raise_for_status()
except httpx.HTTPStatusError as err:
    print("request failed with status", err.response.status_code)
