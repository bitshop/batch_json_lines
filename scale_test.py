"""
Test sending a batch to the API, this is both for load testing and functionality testing
"""

import json
import concurrent.futures
import requests


data = {"name": "Steve"}
headers = {"Content-Type": "application/json"}

jobs = []

# Test single connection:
result = requests.post("http://127.0.0.1:8000/send",
                       data=json.dumps(data),
                       headers=headers,
                       timeout=10)
print(f"Successfully sent test: result: {result}")

with concurrent.futures.ThreadPoolExecutor(max_workers=600) as executor:
    for i in range(5000):
        jobs.append(
            executor.submit(
                requests.post,
                "http://127.0.0.1:8000/send",
                data=json.dumps(data),
                headers=headers,
            )
        )
    for job in concurrent.futures.as_completed(jobs):
        pass
