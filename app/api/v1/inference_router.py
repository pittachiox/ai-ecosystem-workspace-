from __future__ import annotations

import json
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

import redis
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter(prefix="/api/v1", tags=["Inference"])


class InferenceRequest(BaseModel):
    model_name: str
    input: dict[str, Any]


@router.post("/inference", summary="Enqueue inference request")
async def enqueue_inference(req: InferenceRequest) -> dict[str, str]:
    r = redis.StrictRedis.from_url(settings.redis_url, decode_responses=True)
    job_id = str(uuid.uuid4())
    payload = {"id": job_id, "model_name": req.model_name, "input": req.input}
    r.rpush("inference_queue", json.dumps(payload))
    # set initial status
    r.hset(f"job:{job_id}", mapping={"status": "queued"})
    return {"job_id": job_id}


@router.get("/jobs/{job_id}", summary="Get job status")
async def get_job_status(job_id: str) -> dict[str, Any]:
    r = redis.StrictRedis.from_url(settings.redis_url, decode_responses=True)
    data = r.hgetall(f"job:{job_id}")
    if not data:
        raise HTTPException(status_code=404, detail="job not found")
    # try to return any result field stored
    return {"job_id": job_id, **data}
