from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from app.services.redis_service import redis_service
from app.schemas.task_schema import TimeSeriesProcessRequest, TrainingRequest

router = APIRouter(prefix="/timeseries", tags=["Time-Series"])


@router.post("/process", summary="Queue time-series preprocessing", description="Send time-series preprocessing to the background worker queue.")
async def process_timeseries(payload: TimeSeriesProcessRequest) -> dict[str, Any]:
    try:
        job = await redis_service.enqueue("resample_timeseries", {"data": payload.data, "sample_rate": payload.sample_rate, "window_size": payload.window_size})
        return {"status": "queued", "job_id": str(job.job_id)}
    except Exception as exc:  # pragma: no cover - runtime external integration
        raise HTTPException(status_code=500, detail=f"Queue failed: {exc}") from exc


@router.post("/train", summary="Queue time-series training", description="Send a time-series training job to the background worker queue.")
async def train_timeseries(payload: TrainingRequest) -> dict[str, Any]:
    try:
        job = await redis_service.enqueue("train_timeseries_model", {"model_type": payload.model_type, "dataset_size": payload.dataset_size})
        return {"status": "queued", "job_id": str(job.job_id)}
    except Exception as exc:  # pragma: no cover - runtime external integration
        raise HTTPException(status_code=500, detail=f"Queue failed: {exc}") from exc


@router.post("/forecast", summary="Generate forecast", description="Run the forecasting job for time-series inference.")
async def forecast_timeseries(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        job = await redis_service.enqueue("forecast_timeseries", payload)
        return {"status": "queued", "job_id": str(job.job_id)}
    except Exception as exc:  # pragma: no cover - runtime external integration
        raise HTTPException(status_code=500, detail=f"Queue failed: {exc}") from exc
