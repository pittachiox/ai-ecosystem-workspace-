from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from app.schemas.task_schema import PredictionRequest, TrainingRequest
from app.services.redis_service import redis_service

router = APIRouter(prefix="/nontimeseries", tags=["Non-Time-Series"])


@router.post("/train", summary="Queue image model training", description="Send a non-time-series training job for image preprocessing and model training.")
async def train_nontimeseries(payload: TrainingRequest) -> dict[str, Any]:
    try:
        job = await redis_service.enqueue("train_nontimeseries_model", {"model_type": payload.model_type, "dataset_size": payload.dataset_size})
        return {"status": "queued", "job_id": str(job.job_id)}
    except Exception as exc:  # pragma: no cover - runtime external integration
        raise HTTPException(status_code=500, detail=f"Queue failed: {exc}") from exc


@router.post("/predict", summary="Predict image class", description="Queue a prediction job for image classification inference.")
async def predict_nontimeseries(payload: PredictionRequest) -> dict[str, Any]:
    try:
        job = await redis_service.enqueue("predict_image_class", {"image_path": payload.image_path, "model_name": payload.model_name})
        return {"status": "queued", "job_id": str(job.job_id)}
    except Exception as exc:  # pragma: no cover - runtime external integration
        raise HTTPException(status_code=500, detail=f"Queue failed: {exc}") from exc
