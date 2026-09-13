from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import (
    label_studio_router,
    nontimeseries_router,
    storage_router,
    timeseries_router,
)
from app.api.v1.inference_router import router as inference_router

app = FastAPI(
    title="AI Ecosystem API",
    description="Production-ready API for storage, labeling, time-series intelligence, and non-time-series model orchestration.",
    version="1.0.0",
    openapi_tags=[
        {"name": "Storage", "description": "MinIO object storage management and presigned access."},
        {"name": "Labeling", "description": "Label Studio project automation and annotation export."},
        {"name": "Time-Series", "description": "Queue-based time-series preprocessing, training, and forecasting."},
        {"name": "Non-Time-Series", "description": "Image preprocessing, training, and inference tasks."},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(storage_router.router)
app.include_router(label_studio_router.router)
app.include_router(timeseries_router.router)
app.include_router(nontimeseries_router.router)
app.include_router(inference_router)


@app.get("/", summary="Service root", description="Root endpoint for the AI ecosystem service.")
async def root() -> dict[str, str]:
    return {"message": "AI Ecosystem API is running"}


@app.get("/health", summary="Health check", description="Returns the HTTP service status for deployment and orchestration checks.")
async def health() -> dict[str, str]:
    return {"status": "ok"}
