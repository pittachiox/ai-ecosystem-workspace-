import gzip
import logging
import logging.handlers
import os
import shutil
import threading
from pathlib import Path
import boto3
from botocore.client import Config

# Fallback configuration loading
try:
    from core.config import settings
    MINIO_ENDPOINT = settings.minio_endpoint
    MINIO_ACCESS_KEY = settings.minio_access_key
    MINIO_SECRET_KEY = settings.minio_secret_key
    MINIO_SECURE = settings.minio_secure
except ImportError:
    try:
        from backend.core.config import settings
        MINIO_ENDPOINT = settings.minio_endpoint
        MINIO_ACCESS_KEY = settings.minio_access_key
        MINIO_SECRET_KEY = settings.minio_secret_key
        MINIO_SECURE = settings.minio_secure
    except ImportError:
        MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin_pass")
        MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() in ("true", "1", "yes")

class MinioCompressedRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """
    Custom RotatingFileHandler that compresses rotated logs (Cold Storage)
    and uploads them to MinIO (S3 bucket: logs-archive).
    """
    def __init__(self, filename, maxBytes=0, backupCount=0, encoding=None, delay=False, 
                 minio_endpoint=MINIO_ENDPOINT, minio_access_key=MINIO_ACCESS_KEY, 
                 minio_secret_key=MINIO_SECRET_KEY, minio_secure=MINIO_SECURE, 
                 bucket_name="logs-archive"):
        
        super().__init__(filename, maxBytes=maxBytes, backupCount=backupCount, 
                         encoding=encoding, delay=delay)
        
        self.minio_endpoint = minio_endpoint
        self.minio_access_key = minio_access_key
        self.minio_secret_key = minio_secret_key
        self.minio_secure = minio_secure
        self.bucket_name = bucket_name
        self.s3_client = None
        self._init_s3_bucket()

    def _init_s3_bucket(self):
        try:
            self.s3_client = boto3.client(
                "s3",
                endpoint_url=f"http://{self.minio_endpoint}" if not self.minio_secure else f"https://{self.minio_endpoint}",
                aws_access_key_id=self.minio_access_key,
                aws_secret_access_key=self.minio_secret_key,
                config=Config(signature_version="s3v4")
            )
            # Create bucket if it doesn't exist
            try:
                self.s3_client.head_bucket(Bucket=self.bucket_name)
            except Exception:
                self.s3_client.create_bucket(Bucket=self.bucket_name)
                print(f"[Logger S3 Init] Created MinIO bucket '{self.bucket_name}' for Cold Storage.")
        except Exception as e:
            print(f"[Logger S3 Warning] Could not connect to MinIO: {e}. Cold storage upload will be bypassed.")
            self.s3_client = None

    def rotate(self, source, dest):
        # 1. Perform standard local rotation (renaming source to dest)
        super().rotate(source, dest)
        
        # 2. Compress and upload to S3 (MinIO) in a background thread
        thread = threading.Thread(target=self._compress_and_upload, args=(dest,))
        thread.daemon = True
        thread.start()

    def _compress_and_upload(self, rotated_file):
        if not os.path.exists(rotated_file):
            return
        
        compressed_file = rotated_file + ".gz"
        try:
            # Compress the rotated log file to .gz
            with open(rotated_file, "rb") as f_in:
                with gzip.open(compressed_file, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            print(f"[Cold Storage] Compressed {rotated_file} -> {compressed_file}")
            
            # Upload to MinIO
            if self.s3_client:
                object_name = os.path.basename(compressed_file)
                self.s3_client.upload_file(compressed_file, self.bucket_name, object_name)
                print(f"[Cold Storage] Uploaded {object_name} to MinIO bucket '{self.bucket_name}'")
                
                # Delete the temporary local compressed file
                if os.path.exists(compressed_file):
                    os.remove(compressed_file)
            else:
                print(f"[Cold Storage Warning] MinIO client not ready. Archive saved locally at {compressed_file}")
        except Exception as e:
            print(f"[Cold Storage Error] Failed to compress/upload log {rotated_file}: {e}")


def get_logger(name="app", log_dir="storage/log", log_file="app.log", max_bytes=10*1024*1024, backup_count=5):
    """
    Initializes a custom logger with:
    1. StreamHandler (Stdout - Hot console logging)
    2. MinioCompressedRotatingFileHandler (Local file rotation - Hot local logging + Cold MinIO backup)
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers if logger already initialized
    if logger.handlers:
        return logger

    # Ensure log directory exists
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    full_log_file = log_path / log_file

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Stream Handler (Hot Storage Console)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # Rotating File Handler (Hot Storage File + Cold Storage MinIO)
    file_handler = MinioCompressedRotatingFileHandler(
        filename=str(full_log_file),
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
