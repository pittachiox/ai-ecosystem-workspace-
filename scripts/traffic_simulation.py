#!/usr/bin/env python3
"""Traffic simulation for Assignment 9: sends inference requests to FastAPI and polls for results."""
import time
import uuid
import requests

API_URL = "http://localhost:8002/api/v1/inference/predict"
STATUS_URL = "http://localhost:8002/api/v1/inference/job/{job_id}"

SAMPLE_TEXTS = [
    "John lives in New York City and works at OpenAI.",
    "Paris is the capital of France.",
    "Microsoft acquired GitHub in 2018.",
    "The quick brown fox jumps over the lazy dog.",
]


def enqueue_and_wait(text: str, timeout: int = 30) -> dict:
    payload = {"text": text}
    resp = requests.post(API_URL, json=payload)
    resp.raise_for_status()
    data = resp.json()
    job_id = data.get("job_id")
    if not job_id:
        raise RuntimeError("No job_id returned")

    deadline = time.time() + timeout
    while time.time() < deadline:
        r = requests.get(STATUS_URL.format(job_id=job_id))
        if r.status_code == 200:
            res = r.json()
            if res.get("status") in ("completed", "failed"):
                return res
        time.sleep(1)
    raise TimeoutError("Job did not complete in time")


if __name__ == "__main__":
    print("Starting traffic simulation: sending sample inference requests...")
    results = []
    for text in SAMPLE_TEXTS:
        try:
            res = enqueue_and_wait(text, timeout=60)
            print(f"Job result: {res}")
            results.append(res)
        except Exception as exc:
            print(f"Error: {exc}")
    print("Simulation complete.")
