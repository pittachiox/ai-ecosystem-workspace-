from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class StorageUploadRequest(BaseModel):
    bucket_name: Optional[str] = Field(default=None, description="Target MinIO bucket")
    object_name: str = Field(..., description="Object key to store in MinIO")
    file_path: str = Field(..., description="Local file path to upload")


class StorageObjectResponse(BaseModel):
    object_name: str
    bucket_name: str
    url: Optional[str] = None
