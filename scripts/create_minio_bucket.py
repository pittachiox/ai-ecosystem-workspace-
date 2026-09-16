import os
import time
import boto3
from botocore.client import Config


def main():
    endpoint = os.environ.get("MINIO_ENDPOINT", "http://minio:9000")
    access = os.environ.get("MINIO_ROOT_USER", "minioadmin")
    secret = os.environ.get("MINIO_ROOT_PASSWORD", "minioadmin")
    bucket = os.environ.get("MINIO_DEFAULT_BUCKET", "mlflow")

    print(f"Waiting for MinIO at {endpoint}...")
    s3 = None
    for attempt in range(1, 31):
        try:
            s3 = boto3.resource(
                "s3",
                endpoint_url=endpoint,
                aws_access_key_id=access,
                aws_secret_access_key=secret,
                config=Config(signature_version="s3v4"),
            )
            s3.meta.client.list_buckets()
            print(f"Connected to MinIO successfully on attempt {attempt}")
            break
        except Exception as e:
            time.sleep(1)

    if not s3:
        print("Could not connect to MinIO after 30 attempts")
        return

    try:
        existing_buckets = [b.name for b in s3.buckets.all()]
        for b_name in [bucket, "datasets"]:
            if b_name not in existing_buckets:
                s3.create_bucket(Bucket=b_name)
                print(f"Created bucket: {b_name}")
            else:
                print(f"Bucket already exists: {b_name}")
    except Exception as exc:
        print("Failed to ensure buckets:", exc)


if __name__ == "__main__":
    main()
