from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.schemas.storage_schema import StorageObjectResponse, StorageUploadRequest
from app.services.minio_service import minio_service

router = APIRouter(prefix="/storage", tags=["Storage"])


@router.post("/upload", summary="Upload file to MinIO", description="Upload a local file into a MinIO bucket.", response_model=StorageObjectResponse)
async def upload_file(payload: StorageUploadRequest) -> StorageObjectResponse:
    try:
        object_name = minio_service.upload_file(payload.file_path, payload.object_name, payload.bucket_name)
        return StorageObjectResponse(object_name=object_name, bucket_name=payload.bucket_name or "datasets", url=minio_service.get_presigned_url(object_name, payload.bucket_name))
    except Exception as exc:  # pragma: no cover - runtime external integration
        raise HTTPException(status_code=500, detail=f"Upload failed: {exc}") from exc


@router.get("/files", summary="List files in bucket", description="Returns object names available in the configured MinIO bucket.")
async def list_files(bucket_name: str | None = Query(default=None, description="Bucket name")) -> dict[str, Any]:
    try:
        return {"bucket_name": bucket_name or "datasets", "objects": minio_service.list_objects(bucket_name)}
    except Exception as exc:  # pragma: no cover - runtime external integration
        raise HTTPException(status_code=500, detail=f"List failed: {exc}") from exc


@router.get("/presigned-url", summary="Create a temporary presigned URL", description="Generate a temporary access URL for an object stored in MinIO.")
async def presigned_url(bucket_name: str | None = Query(default=None, description="Bucket name"), object_name: str = Query(..., description="Object key")) -> dict[str, str]:
    try:
        return {"url": minio_service.get_presigned_url(object_name, bucket_name)}
    except Exception as exc:  # pragma: no cover - runtime external integration
        raise HTTPException(status_code=500, detail=f"Presigned URL failed: {exc}") from exc
