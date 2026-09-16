from __future__ import annotations

import json
import uuid
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import redis
from mlflow.tracking import MlflowClient

from app.core.config import settings

router = APIRouter(prefix="/api/v1/inference", tags=["Inference"])


class PredictRequest(BaseModel):
    model_name: Optional[str] = "conll2003_ner"
    input: Optional[Any] = None
    text: Optional[str] = None

    model_config = {"extra": "allow"}


def get_redis_client() -> redis.Redis:
    return redis.Redis.from_url(settings.redis_url, decode_responses=True)


@router.post("/predict", summary="Enqueue inference prediction job")
@router.post("", summary="Enqueue inference prediction job (legacy alias)")
async def predict_endpoint(req: PredictRequest) -> dict[str, Any]:
    r = get_redis_client()
    job_id = str(uuid.uuid4())
    model_name = req.model_name or "conll2003_ner"
    input_data = req.input if req.input is not None else req.text

    payload = {
        "job_id": job_id,
        "id": job_id,
        "model_name": model_name,
        "input": input_data,
        "enqueued_at": uuid.uuid1().time,
    }

    # Set initial state in inference-result:{job_id}
    init_data = {
        "job_id": job_id,
        "status": "queued",
        "model": model_name,
    }
    r.set(f"inference-result:{job_id}", json.dumps(init_data))
    r.hset(f"job:{job_id}", mapping={"status": "queued"})

    # Push to task queue
    r.rpush("inference_queue", json.dumps(payload))

    return {
        "job_id": job_id,
        "status": "queued",
        "model_name": model_name,
    }


@router.get("/job/{job_id}", summary="Get inference job status and result")
@router.get("/jobs/{job_id}", summary="Get inference job status and result (alias)")
async def get_job_status(job_id: str) -> dict[str, Any]:
    r = get_redis_client()

    # 1. Primary check on key: inference-result:{job_id}
    raw_res = r.get(f"inference-result:{job_id}")
    if raw_res:
        try:
            return json.loads(raw_res)
        except Exception:
            return {"job_id": job_id, "raw_result": raw_res}

    # 2. Fallback check on hash: job:{job_id}
    data = r.hgetall(f"job:{job_id}")
    if data:
        res = data.get("result")
        if res:
            try:
                parsed_res = json.loads(res)
                return {"job_id": job_id, **data, "result": parsed_res}
            except Exception:
                pass
        return {"job_id": job_id, **data}

    raise HTTPException(status_code=404, detail="Job not found")


@router.get("/models", summary="List registered models from MLflow Registry")
async def list_registered_models() -> dict[str, Any]:
    try:
        client = MlflowClient(tracking_uri=settings.mlflow_tracking_uri)
        registered_models = client.search_registered_models()

        models_list = []
        for rm in registered_models:
            versions = []
            for v in getattr(rm, "latest_versions", []):
                versions.append({
                    "version": v.version,
                    "current_stage": getattr(v, "current_stage", None),
                    "status": getattr(v, "status", None),
                    "run_id": getattr(v, "run_id", None),
                    "aliases": getattr(v, "aliases", []),
                })
            models_list.append({
                "name": rm.name,
                "latest_versions": versions,
                "description": getattr(rm, "description", None),
                "creation_timestamp": getattr(rm, "creation_timestamp", None),
                "last_updated_timestamp": getattr(rm, "last_updated_timestamp", None),
            })

        return {
            "status": "ok",
            "count": len(models_list),
            "models": models_list,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch models from MLflow Model Registry: {exc}",
        )
