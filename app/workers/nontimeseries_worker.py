from __future__ import annotations

from typing import Any


async def preprocess_images(ctx, payload: dict[str, Any]) -> dict[str, Any]:
    files = payload.get("files", [])
    return {
        "status": "preprocessed",
        "file_count": len(files),
        "augmentation": payload.get("augmentation", "horizontal_flip"),
    }


async def train_nontimeseries_model(ctx, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "training_complete",
        "model_type": payload.get("model_type", "image_classifier"),
        "dataset_size": payload.get("dataset_size", 1000),
    }


async def predict_image_class(ctx, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "prediction_complete",
        "result": {"label": "class_a", "confidence": 0.98},
        "source": payload.get("image_path", "unknown"),
    }
