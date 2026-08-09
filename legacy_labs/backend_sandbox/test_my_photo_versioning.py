import os
import sys
import shutil
from pathlib import Path

# Add project root directory to sys.path to allow importing from backend
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sandbox_minio import MinioSandbox

def main():
    minio = MinioSandbox()
    bucket_name = "user-photos"
    object_name = "my-profile-pic.jpg"
    
    # 1. Path to your real photo (checks project root first, then backend folder)
    file_v1 = os.path.join(project_root, "IMG_6996.JPG")
    if not os.path.exists(file_v1):
        file_v1 = os.path.join(project_root, "backend", "IMG_6996.JPG")
    
    if not os.path.exists(file_v1):
        print("Error: Could not find 'IMG_6996.JPG' in either the project root or backend folder.")
        print("Please copy your image 'IMG_6996.JPG' into one of these directories.")
        return

    # 2. Path to the second version of the photo (created next to V1)
    file_v2 = file_v1.replace(".JPG", "_v2.JPG")
    if not os.path.exists(file_v2):
        # If the second photo is not found, copy V1 to simulate V2
        shutil.copyfile(file_v1, file_v2)
        print(f"V2 image '{os.path.basename(file_v2)}' not found. Cloned V1 to simulate a V2 update.")

    print("\n--- Step 1: Create Bucket and Enable Versioning ---")
    minio.create_bucket(bucket_name, enable_versioning=True)

    print("\n--- Step 2: Uploading Version 1 (Original Photo) ---")
    v1_id = minio.upload_file(file_v1, bucket_name, object_name)

    print("\n--- Step 3: Uploading Version 2 (Updated Photo) ---")
    v2_id = minio.upload_file(file_v2, bucket_name, object_name)

    print("\n--- Step 4: Listing All Versions in MinIO Bucket ---")
    versions = minio.list_object_versions(bucket_name, object_name)
    for v in versions:
        print(f"- Version ID: {v['VersionId']}, IsLatest: {v['IsLatest']}, Size: {v['Size']} bytes")

    print("\n--- Step 5: Download WITHOUT specifying Version (Latest Version V2) ---")
    dest_no_version = os.path.join(project_root, "download_no_version.jpg")
    minio.download_file(bucket_name, object_name, dest_no_version)
    print(f"Saved latest version to: {dest_no_version}")

    print("\n--- Step 6: Download SPECIFYING Version 1 ID ---")
    dest_v1 = os.path.join(project_root, "download_v1.jpg")
    minio.download_file(bucket_name, object_name, dest_v1, version_id=v1_id)
    print(f"Saved Version 1 to: {dest_v1}")

    print("\n--- Step 7: Download SPECIFYING Version 2 ID ---")
    dest_v2 = os.path.join(project_root, "download_v2.jpg")
    minio.download_file(bucket_name, object_name, dest_v2, version_id=v2_id)
    print(f"Saved Version 2 to: {dest_v2}")

if __name__ == "__main__":
    main()
