import os
import time

import boto3
from botocore.client import Config


def main():
    endpoint = os.environ.get("MINIO_ENDPOINT", "http://minio:9000")
    access = os.environ.get("MINIO_ROOT_USER", "minioadmin")
    secret = os.environ.get("MINIO_ROOT_PASSWORD", "minioadmin")
    bucket = os.environ.get("MINIO_DEFAULT_BUCKET", "mlflow")

    # wait for minio
    for _ in range(20):
        try:
            s3 = boto3.resource('s3', endpoint_url=endpoint, aws_access_key_id=access, aws_secret_access_key=secret, config=Config(signature_version='s3v4'))
            s3.meta.client.list_buckets()
            break
        except Exception:
            time.sleep(1)

    try:
        s3 = boto3.resource('s3', endpoint_url=endpoint, aws_access_key_id=access, aws_secret_access_key=secret, config=Config(signature_version='s3v4'))
        if s3.Bucket(bucket) not in s3.buckets.all():
            s3.create_bucket(Bucket=bucket)
        print('bucket ensured:', bucket)
    except Exception as exc:
        print('failed to create bucket', exc)


if __name__ == '__main__':
    main()
