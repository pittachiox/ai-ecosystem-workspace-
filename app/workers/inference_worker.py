from __future__ import annotations

import json
import os
import time
import traceback
import logging
from typing import Any

import mlflow
import mlflow.pyfunc
from mlflow.tracking import MlflowClient
import redis
from opentelemetry import trace, metrics

from app.core.config import settings
from app.core.telemetry import setup_telemetry

_model_cache: dict[str, Any] = {}

logger = logging.getLogger(__name__)

# Initialize telemetry for the worker service
setup_telemetry(service_name=os.getenv("OTEL_SERVICE_NAME", "inference-worker"))

# Tracer & Meter for explicit spans and metrics
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# Metrics instruments
jobs_counter = meter.create_counter("inference_jobs_total")
jobs_latency = meter.create_histogram("inference_job_latency_ms")


def setup_mlflow_env() -> str:
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
    mlflow.set_tracking_uri(tracking_uri)
    os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin")
    os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin")
    os.environ["MLFLOW_S3_ENDPOINT_URL"] = os.getenv("MLFLOW_S3_ENDPOINT_URL", "http://minio:9000")
    return tracking_uri


def load_model_from_registry(model_name: str = "conll2003_ner"):
    if model_name in _model_cache:
        return _model_cache[model_name]

    tracking_uri = setup_mlflow_env()
    client = MlflowClient(tracking_uri=tracking_uri)

    candidate_uris = [
        f"models:/{model_name}/latest",
        f"models:/{model_name}/1",
        f"models:/{model_name}@latest",
    ]

    # Also resolve latest version dynamically from MLflow Client
    try:
        latest_versions = client.get_latest_versions(model_name)
        for lv in latest_versions:
            v_uri = f"models:/{model_name}/{lv.version}"
            if v_uri not in candidate_uris:
                candidate_uris.append(v_uri)
    except Exception as exc:
        print(f"[inference_worker] Could not query latest versions from client: {exc}")

    last_exc = None
    for uri in candidate_uris:
        try:
            print(f"[inference_worker] Loading model from URI: {uri}")
            model = mlflow.pyfunc.load_model(uri)
            print(f"[inference_worker] Successfully loaded model from {uri}")
            _model_cache[model_name] = model
            return model
        except Exception as exc:
            print(f"[inference_worker] Failed to load from {uri}: {exc}")
            last_exc = exc

    raise RuntimeError(
        f"Failed to load registered model '{model_name}' from any URI ({candidate_uris}): {last_exc}"
    )


def predict(model: Any, input_data: Any) -> Any:
    if isinstance(input_data, str):
        words = input_data.strip().split()
        if not words:
            return {"text": input_data, "tokens": [], "entities": []}
        preds = model.predict(words)
        tags = preds.tolist() if hasattr(preds, "tolist") else list(preds)
        entities = [{"token": w, "entity": str(t)} for w, t in zip(words, tags)]
        return {"text": input_data, "tokens": words, "entities": entities}

    elif isinstance(input_data, list):
        if not input_data:
            return []
        preds = model.predict(input_data)
        tags = preds.tolist() if hasattr(preds, "tolist") else list(preds)
        entities = [{"token": str(w), "entity": str(t)} for w, t in zip(input_data, tags)]
        return {"tokens": input_data, "entities": entities}

    elif isinstance(input_data, dict):
        values = list(input_data.values())
        preds = model.predict(values)
        return preds.tolist() if hasattr(preds, "tolist") else preds

    else:
        preds = model.predict([str(input_data)])
        return preds.tolist() if hasattr(preds, "tolist") else preds


def process_message(msg: str, r: redis.Redis) -> None:
    try:
        payload = json.loads(msg)
    except Exception as exc:
        print(f"[inference_worker] Invalid JSON message: {exc}")
        return

    job_id = payload.get("job_id") or payload.get("id")
    if not job_id:
        print("[inference_worker] Missing job_id in message payload")
        return

    model_name = payload.get("model_name") or "conll2003_ner"
    input_data = payload.get("input") if payload.get("input") is not None else payload.get("text")

    logger.info("Processing job", extra={"job_id": job_id, "model": model_name})

    # Set processing status in Redis
    r.set(
        f"inference-result:{job_id}",
        json.dumps({"job_id": job_id, "status": "processing", "model": model_name}),
    )
    r.hset(f"job:{job_id}", mapping={"status": "processing"})

    start_ts = time.time()
    try:
        # Top-level span for processing the inference job
        with tracer.start_as_current_span("process_inference_job") as job_span:
            job_span.set_attribute("job.id", str(job_id))
            job_span.set_attribute("model.name", model_name)

            model = load_model_from_registry(model_name)

            # Inner span for the actual NER execution
            with tracer.start_as_current_span("execute_ner_inference") as infer_span:
                infer_span.set_attribute("job.id", str(job_id))
                infer_span.set_attribute("model.name", model_name)

                infer_start = time.time()
                result = predict(model, input_data)
                infer_latency = (time.time() - infer_start) * 1000.0

                # Record attributes about result
                entities_count = 0
                try:
                    if isinstance(result, dict) and "entities" in result:
                        entities_count = len(result.get("entities", []))
                except Exception:
                    entities_count = 0

                infer_span.set_attribute("entities.count", int(entities_count))
                infer_span.set_attribute("latency_ms", float(infer_latency))

        total_latency = (time.time() - start_ts) * 1000.0

        # Update Prometheus/OpenTelemetry metrics
        jobs_counter.add(1, attributes={"model": model_name, "status": "completed"})
        jobs_latency.record(total_latency, attributes={"model": model_name})

        result_payload = {
            "job_id": job_id,
            "status": "completed",
            "model": model_name,
            "result": result,
            "completed_at": time.time(),
        }

        # Save result to key inference-result:{job_id}
        r.set(f"inference-result:{job_id}", json.dumps(result_payload))
        # Also set hash job:{job_id} for compatibility
        r.hset(
            f"job:{job_id}",
            mapping={
                "status": "completed",
                "result": json.dumps(result_payload),
            },
        )
        logger.info("Job completed", extra={"job_id": job_id, "latency_ms": total_latency})

    except Exception as exc:
        traceback.print_exc()
        error_payload = {
            "job_id": job_id,
            "status": "failed",
            "model": model_name,
            "error": str(exc),
            "failed_at": time.time(),
        }
        r.set(f"inference-result:{job_id}", json.dumps(error_payload))
        r.hset(f"job:{job_id}", mapping={"status": "failed", "error": str(exc)})

        jobs_counter.add(1, attributes={"model": model_name, "status": "failed"})
        logger.error("Job failed", extra={"job_id": job_id, "error": str(exc)})


def main():
    setup_mlflow_env()
    redis_url = os.getenv("REDIS_URL", settings.redis_url)
    r = redis.Redis.from_url(redis_url, decode_responses=True)

    print("[inference_worker] Listening for jobs on 'inference_queue'...")
    while True:
        try:
            item = r.blpop(["inference_queue", "inference:queue"], timeout=2)
            if not item:
                continue
            _, msg = item
            process_message(msg, r)
        except KeyboardInterrupt:
            break
        except Exception as exc:
            print("[inference_worker] Loop error:", exc)
            time.sleep(1)


if __name__ == "__main__":
    main()
