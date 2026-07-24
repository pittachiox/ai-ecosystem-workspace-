import os
from pathlib import Path
import boto3
from botocore.client import Config

# Dynamic configuration loading from core.config
try:
    from core.config import settings
    MINIO_ENDPOINT = settings.minio_endpoint
    MINIO_ACCESS_KEY = settings.minio_access_key
    MINIO_SECRET_KEY = settings.minio_secret_key
    MINIO_SECURE = settings.minio_secure
except ImportError:
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "pittachiox")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "pitta15418")
    MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() in ("true", "1", "yes")

class MinioSandbox:
    """
    MinIO Sandbox wrapper class using boto3.
    Supports upload, download, and listing object versions.
    """
    def __init__(self, endpoint=MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=MINIO_SECURE):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.secure = secure
        
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=f"http://{self.endpoint}" if not self.secure else f"https://{self.endpoint}",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version="s3v4")
        )

    def create_bucket(self, bucket_name: str, enable_versioning: bool = True):
        """
        Creates a bucket if it doesn't exist and enables S3 versioning if requested.
        """
        try:
            # Create Bucket
            try:
                self.s3_client.head_bucket(Bucket=bucket_name)
                print(f"Bucket '{bucket_name}' already exists.")
            except Exception:
                self.s3_client.create_bucket(Bucket=bucket_name)
                print(f"Created bucket: '{bucket_name}'")

            # Enable Versioning
            if enable_versioning:
                self.s3_client.put_bucket_versioning(
                    Bucket=bucket_name,
                    VersioningConfiguration={'Status': 'Enabled'}
                )
                print(f"Data Versioning enabled for bucket '{bucket_name}'.")
        except Exception as e:
            print(f"Error creating bucket or enabling versioning: {e}")
            raise

    def upload_file(self, file_path: str, bucket_name: str, object_name: str) -> str:
        """
        Uploads a local file to MinIO and returns the VersionId of the uploaded object.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Local file {file_path} not found.")

        try:
            response = self.s3_client.put_object(
                Bucket=bucket_name,
                Key=object_name,
                Body=open(file_path, 'rb')
            )
            # Fetch version ID from put response
            version_id = response.get('VersionId')
            print(f"Successfully uploaded {file_path} as '{object_name}' (Version ID: {version_id})")
            return version_id
        except Exception as e:
            print(f"Error uploading file: {e}")
            raise

    def download_file(self, bucket_name: str, object_name: str, dest_path: str, version_id: str = None):
        """
        Downloads a file from MinIO. If version_id is provided, downloads that specific version.
        """
        try:
            extra_args = {}
            if version_id:
                extra_args['VersionId'] = version_id
            
            # Use get_object or download_file. download_file supports extra args via ExtraArgs parameter
            self.s3_client.download_file(
                Bucket=bucket_name,
                Key=object_name,
                Filename=dest_path,
                ExtraArgs=extra_args
            )
            version_info = f"version {version_id}" if version_id else "latest version"
            print(f"Successfully downloaded '{object_name}' ({version_info}) -> {dest_path}")
        except Exception as e:
            print(f"Error downloading file '{object_name}': {e}")
            raise

    def list_object_versions(self, bucket_name: str, object_name: str) -> list:
        """
        Lists all versions of an object in MinIO.
        """
        try:
            response = self.s3_client.list_object_versions(Bucket=bucket_name, Prefix=object_name)
            versions = []
            if 'Versions' in response:
                for v in response['Versions']:
                    if v['Key'] == object_name:
                        versions.append({
                            'VersionId': v['VersionId'],
                            'IsLatest': v['IsLatest'],
                            'LastModified': v['LastModified'],
                            'Size': v['Size']
                        })
            return versions
        except Exception as e:
            print(f"Error listing versions of '{object_name}': {e}")
            raise
