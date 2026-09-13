from __future__ import annotations

import json
import time

import mlflow
import redis

from app.core.config import settings


def process_message(msg: str, r: redis.Redis) -> None:
    payload = json.loads(msg)
    job_id = payload.get("id")
    model_name = payload.get("model_name")
    input_data = payload.get("input")

    r.hset(f"job:{job_id}", mapping={"status": "processing"})

    # try to load latest model run mapping from Redis to avoid registry API calls
    try:
        run_id = r.get(f"model_latest_run:{model_name}")
        if run_id:
            try:
                model = mlflow.pyfunc.load_model(f"runs:/{run_id}/model")
            except Exception:
                # fallback to local file-backed mlruns volume
                import os

                os.environ.setdefault("MLFLOW_ALLOW_FILE_STORE", "true")
                mlflow.set_tracking_uri("file:///mlruns")
                model = mlflow.pyfunc.load_model(f"runs:/{run_id}/model")
        else:
            # fallback to model registry URI (may require registry API)
            try:
                model = mlflow.pyfunc.load_model(f"models:/{model_name}/latest")
            except Exception:
                import os

                os.environ.setdefault("MLFLOW_ALLOW_FILE_STORE", "true")
                mlflow.set_tracking_uri("file:///mlruns")
                # try to resolve latest run for this model from local mlruns
                latest_run = r.get(f"model_latest_run:{model_name}")
                if latest_run:
                    model = mlflow.pyfunc.load_model(f"runs:/{latest_run}/model")
                else:
                    raise
        # model expects a pandas-friendly input; here we assume a dict or list
        if isinstance(input_data, dict):
            data = [list(input_data.values())]
        elif isinstance(input_data, list):
            data = [input_data]
        else:
            data = [[input_data]]

        result = model.predict(data)
        r.hset(f"job:{job_id}", mapping={"status": "done", "result": json.dumps(result.tolist() if hasattr(result, 'tolist') else result)})
    except Exception as exc:
        r.hset(f"job:{job_id}", mapping={"status": "failed", "error": str(exc)})


def main():
    r = redis.StrictRedis.from_url(settings.redis_url, decode_responses=True)
    print("[inference_worker] waiting for messages on 'inference_queue'...")
    while True:
        try:
            item = r.blpop(["inference_queue"], timeout=5)
            if not item:
                time.sleep(1)
                continue
            _, msg = item
            process_message(msg, r)
        except KeyboardInterrupt:
            break
        except Exception as exc:
            print("Inference worker error:", exc)
            time.sleep(1)


if __name__ == "__main__":
    main()

