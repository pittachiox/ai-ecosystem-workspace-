from __future__ import annotations

from datetime import timedelta
from typing import Any

from minio import Minio
from minio.error import S3Error

from app.core.config import settings


class MinioService:
    def __init__(self) -> None:
        self.client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )

    def ensure_bucket(self, bucket_name: str | None = None) -> str:
        bucket = bucket_name or settings.minio_default_bucket
        if not self.client.bucket_exists(bucket):
            self.client.make_bucket(bucket)
        return bucket

    def upload_file(self, file_path: str, object_name: str, bucket_name: str | None = None) -> str:
        bucket = self.ensure_bucket(bucket_name)
        self.client.fput_object(bucket, object_name, file_path)
        return object_name

    def list_objects(self, bucket_name: str | None = None) -> list[str]:
        bucket = self.ensure_bucket(bucket_name)
        return [obj.object_name for obj in self.client.list_objects(bucket, recursive=True)]

    def get_presigned_url(self, object_name: str, bucket_name: str | None = None, expires: int = 3600) -> str:
        bucket = self.ensure_bucket(bucket_name)
        return self.client.presigned_get_object(bucket, object_name, expires=timedelta(seconds=expires))

    def download_file(self, object_name: str, destination_path: str, bucket_name: str | None = None) -> str:
        bucket = self.ensure_bucket(bucket_name)
        self.client.fget_object(bucket, object_name, destination_path)
        return destination_path


minio_service = MinioService()
