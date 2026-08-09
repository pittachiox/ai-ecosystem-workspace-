from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class TimeSeriesProcessRequest(BaseModel):
    data: list[float] = Field(..., description="Time-series numeric data")
    sample_rate: str = Field(default="1H", description="Resampling interval")
    window_size: int = Field(default=24, description="Window length")


class TrainingRequest(BaseModel):
    model_type: str = Field(default="timeseries", description="Type of model to train")
    dataset_size: int = Field(default=1000, description="Number of training samples")
    horizon: Optional[int] = Field(default=7, description="Forecast horizon")


class PredictionRequest(BaseModel):
    image_path: str = Field(..., description="Image path for prediction")
    model_name: str = Field(default="default_classifier", description="Model name")
