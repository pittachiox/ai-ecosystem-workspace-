import os
import sys
import time
from pathlib import Path
import boto3
from botocore.client import Config

# Add project root directory to sys.path to allow importing utils
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.logging_utils import get_logger, MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_SECURE

def test_hot_and_cold_logging():
    # 1. Clean up any previous log files from previous runs
    log_dir = Path(project_root) / "storage" / "log"
    if log_dir.exists():
        for log_file in log_dir.glob("test_app.log*"):
            try:
                log_file.unlink()
            except Exception as e:
                print(f"Failed to clean old log file {log_file}: {e}")

    print("--- Step 1: Initializing Logger (max_bytes=1000 for easy rotation) ---")
    # We set max_bytes=1000 to trigger rotation quickly
    logger = get_logger(
        name="test_logger",
        log_dir=str(log_dir),
        log_file="test_app.log",
        max_bytes=1000,
        backup_count=3
    )

    print("--- Step 2: Writing Logs (Verifying Hot Storage) ---")
    # Write enough logs to trigger rotation multiple times (each log is ~100 bytes)
    for i in range(50):
        logger.info(f"Log message number {i} - This is a test log message to force size rotation.")
        time.sleep(0.05) # Small sleep to ensure threads can process rotation in order

    # Wait a bit for the background threads to complete compression and S3 upload
    print("Waiting 5 seconds for S3 background upload to complete...")
    time.sleep(5)

    print("--- Step 3: Verifying Hot Storage (Local Log Files) ---")
    log_files = list(log_dir.glob("test_app.log*"))
    print("Local log files found:")
    for f in log_files:
        print(f"- {f.name} (Size: {f.stat().st_size} bytes)")

    # Verify that the active log file exists
    active_log = log_dir / "test_app.log"
    if active_log.exists():
        print("Success: Active local log file exists.")
    else:
        print("Error: Active local log file does not exist!")

    print("--- Step 4: Verifying Cold Storage (MinIO S3 Bucket) ---")
    s3_client = boto3.client(
        "s3",
        endpoint_url=f"http://{MINIO_ENDPOINT}" if not MINIO_SECURE else f"https://{MINIO_ENDPOINT}",
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        config=Config(signature_version="s3v4")
    )
    
    try:
        response = s3_client.list_objects_v2(Bucket="logs-archive")
        if "Contents" in response:
            print("Uploaded archives in MinIO bucket 'logs-archive':")
            for obj in response["Contents"]:
                print(f"- Object Name: {obj['Key']}, Size: {obj['Size']} bytes, Last Modified: {obj['LastModified']}")
        else:
            print("No objects found in MinIO bucket 'logs-archive'.")
    except Exception as e:
        print(f"Error checking MinIO bucket: {e}")

if __name__ == "__main__":
    test_hot_and_cold_logging()
